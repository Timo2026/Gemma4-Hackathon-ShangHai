import re
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from sqlmodel import select

from app.core.config import settings
from app.db.session import get_session
from app.models.document import Document
from app.models.measure import MeasureCode
from app.models.patient import Patient
from app.schemas.tasks import ConfirmRequest, ConfirmResponse, ExtractRequest, ExtractResponse, TaskDetail, TaskSummary
from app.services.confirm_service import confirm_task_review
from app.services.extraction import (
    LLMExtractionError,
    NoMeasureConfiguredError,
    UnsupportedMeasureError,
    _infer_measure_codes_from_text,
    record_failed_extraction,
    run_extraction_flow,
)
from app.services.linked_measure_service import build_history_items
from app.services.task_status import (
    build_review_state,
    build_task_summary,
    latest_evaluation,
    latest_extraction,
    latest_successful_extraction,
    measure_codes_for_document,
    parse_measure_codes,
    serialize_evaluation,
    serialize_extraction,
    sync_patient_identity_from_extraction,
)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

_SUPPORTED_MEASURE_CODES = {item.value for item in MeasureCode}


def _measure_codes_from_filename(filename: str) -> list[str]:
    return _infer_measure_codes_from_text(Path(filename).stem)


def _validate_measure_codes(codes: list[str]) -> list[str]:
    invalid = [code for code in codes if code not in _SUPPORTED_MEASURE_CODES]
    if invalid:
        raise HTTPException(status_code=422, detail=f"Unsupported measure code: {', '.join(invalid)}")
    return codes


def _safe_upload_filename(filename: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(filename).stem).strip("._") or "document"
    return f"{stem}.pdf"


def _upload_storage_root() -> Path:
    root = Path(settings.upload_storage_dir)
    if root.is_absolute():
        return root
    return Path(settings.data_dir) / root


def _pdf_without_title_bytes(pdf_path: Path) -> bytes | None:
    try:
        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(str(pdf_path))
        metadata = dict(reader.metadata or {})
        if not metadata.get("/Title"):
            return None

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        sanitized_metadata = {key: value for key, value in metadata.items() if key != "/Title"}
        if sanitized_metadata:
            writer.add_metadata(sanitized_metadata)

        buffer = BytesIO()
        writer.write(buffer)
        return buffer.getvalue()
    except Exception:
        return None


def _patient_name_from_filename(filename: str) -> tuple[str, str]:
    tokens = [token for token in re.split(r"[_\-\s]+", Path(filename).stem) if token]
    stop_tokens = {
        "CBP",
        "BPD",
        "GSD",
        "ED",
        "IP",
        "INPATIENT",
        "OUTPATIENT",
        "TEL",
        "TELEHEALTH",
        "REMOTE",
        "RPM",
    }
    name_tokens: list[str] = []
    for token in tokens:
        upper = token.upper()
        if upper in stop_tokens:
            break
        if upper.isdigit():
            break
        name_tokens.append(token)

    parts = [part for part in " ".join(name_tokens).split() if part]
    if not parts:
        return "Uploaded", "Patient"
    if len(parts) == 1:
        return parts[0], "Patient"
    return parts[0], " ".join(parts[1:])


def _extract_pdf_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        parts = [page.extract_text() or "" for page in reader.pages]
    except Exception as error:
        raise HTTPException(status_code=422, detail=f"Unable to read text from PDF: {error}") from error

    text = "\n\n".join(part.strip() for part in parts if part.strip()).strip()
    if len(text) < 20:
        raise HTTPException(status_code=422, detail="Text-based PDF required; OCR/scanned PDF is not supported")
    return text


def _rollback_session(session: Session) -> None:
    rollback = getattr(session, "rollback", None)
    if callable(rollback):
        rollback()


@router.get("", response_model=list[TaskSummary])
def list_tasks(session: Session = Depends(get_session)) -> list[TaskSummary]:
    documents = session.execute(select(Document).order_by(Document.id.asc())).scalars().all()
    results: list[TaskSummary] = []
    for document in documents:
        patient = session.get(Patient, document.patient_id)
        extraction = latest_extraction(session, document.id)
        evaluation = latest_evaluation(session, document.id)
        successful_extraction = latest_successful_extraction(session, document.id)
        measure_extraction_id = evaluation.extraction_result_id if evaluation else successful_extraction.id if successful_extraction else None
        measures = measure_codes_for_document(session, document, measure_extraction_id)
        results.append(build_task_summary(document, patient, extraction, evaluation, measures))
    return results


@router.post("/import", response_model=TaskSummary)
async def import_task(request: Request, session: Session = Depends(get_session)) -> TaskSummary:
    form = await request.form()
    upload = form.get("file")
    if upload is None or not hasattr(upload, "filename"):
        raise HTTPException(status_code=422, detail="PDF file is required")

    filename = str(upload.filename or "")
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are supported")

    measure_codes = _validate_measure_codes(parse_measure_codes(str(form.get("measure_codes") or "")))
    if not measure_codes:
        measure_codes = _validate_measure_codes(_measure_codes_from_filename(filename))
    if not measure_codes:
        raise HTTPException(status_code=422, detail="Unable to infer measure from filename; select a measure manually")

    first_name, last_name = _patient_name_from_filename(filename)
    patient = Patient(member_id=f"UPLOAD-{uuid4().hex[:12]}", first_name=first_name, last_name=last_name)
    session.add(patient)
    session.flush()

    document = Document(patient_id=patient.id, source_pdf_path="pending", source_txt_path="pending", target_measure_codes=",".join(measure_codes))
    session.add(document)
    session.flush()

    upload_dir = _upload_storage_root() / "documents" / str(document.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = upload_dir / _safe_upload_filename(filename)
    txt_path = upload_dir / f"{pdf_path.stem}.txt"

    contents = await upload.read()
    if not contents:
        raise HTTPException(status_code=422, detail="Uploaded PDF is empty")
    pdf_path.write_bytes(contents)
    sanitized_pdf = _pdf_without_title_bytes(pdf_path)
    if sanitized_pdf is not None:
        pdf_path.write_bytes(sanitized_pdf)
    txt_path.write_text(_extract_pdf_text(pdf_path), encoding="utf-8")

    document.source_pdf_path = str(pdf_path.relative_to(Path(settings.data_dir)))
    document.source_txt_path = str(txt_path.relative_to(Path(settings.data_dir)))
    session.add(document)
    session.commit()
    session.refresh(document)

    return build_task_summary(document, patient, None, None, measure_codes)


@router.get("/{task_id}", response_model=TaskDetail)
def get_task(task_id: int, session: Session = Depends(get_session)) -> TaskDetail:
    document = session.get(Document, task_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Task not found")

    patient = session.get(Patient, document.patient_id)
    extraction = latest_extraction(session, document.id)
    evaluation = latest_evaluation(session, document.id)
    successful_extraction = latest_successful_extraction(session, document.id)
    measure_extraction_id = evaluation.extraction_result_id if evaluation else successful_extraction.id if successful_extraction else None
    measures = measure_codes_for_document(session, document, measure_extraction_id)
    summary = build_task_summary(document, patient, extraction, evaluation, measures)
    reviewer_conclusion_history = build_history_items(session, document)

    return TaskDetail(
        task_id=summary.task_id,
        patient_id=summary.patient_id,
        patient_name=summary.patient_name,
        source_pdf_path=summary.source_pdf_path,
        source_txt_path=summary.source_txt_path,
        status=summary.status,
        gap_status=summary.gap_status,
        measures=summary.measures,
        latest_extraction=serialize_extraction(extraction),
        latest_evaluation=serialize_evaluation(evaluation),
        review_state=build_review_state(extraction, evaluation, measures),
        reviewer_conclusion_history=reviewer_conclusion_history,
    )



@router.get("/{task_id}/pdf")
def get_task_pdf(task_id: int, session: Session = Depends(get_session)) -> Response:
    document = session.get(Document, task_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Task not found")
    pdf_path = Path(document.source_pdf_path)
    if not pdf_path.is_absolute():
        pdf_path = Path(settings.data_dir) / pdf_path
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    sanitized_pdf = _pdf_without_title_bytes(pdf_path)
    if sanitized_pdf is not None:
        return Response(
            content=sanitized_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": 'inline; filename="chart.pdf"'},
        )

    return FileResponse(pdf_path, media_type="application/pdf")


@router.post("/{task_id}/extract", response_model=ExtractResponse)
def extract_task(task_id: int, payload: ExtractRequest | None = None, session: Session = Depends(get_session)) -> ExtractResponse:
    document = session.get(Document, task_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Task not found")

    patient = session.get(Patient, document.patient_id)

    current_evaluation = latest_evaluation(session, document.id)
    if current_evaluation and isinstance(current_evaluation.evidence_payload, dict) and current_evaluation.evidence_payload.get("is_confirmed") is True:
        raise HTTPException(status_code=409, detail="Task already confirmed; reopen before re-running extract")

    try:
        result = run_extraction_flow(
            session,
            document,
            measure_ids=payload.measure_ids if payload else None,
        )
    except NoMeasureConfiguredError:
        _rollback_session(session)
        raise HTTPException(status_code=400, detail="No measure configured in database") from None
    except UnsupportedMeasureError as error:
        _rollback_session(session)
        raise HTTPException(status_code=400, detail=f"Unsupported measure: {error}") from None
    except LLMExtractionError as error:
        _rollback_session(session)
        record_failed_extraction(session, document, str(error))
        raise HTTPException(status_code=502, detail=f"LLM extraction failed: {error}") from None

    sync_patient_identity_from_extraction(session, patient, result.extraction)
    session.commit()

    system_evaluated_results = [
        {
            "measure_code": item.measure_code,
            "pass_flag": item.pass_flag,
            "evidence_payload": item.evidence_payload,
            "measure_evaluation_id": item.evaluation.id,
        }
        for item in result.evaluations
    ]

    first_result = system_evaluated_results[0]
    return ExtractResponse(
        task_id=document.id,
        extraction_result_id=result.extraction.id,
        measure_evaluation_id=first_result["measure_evaluation_id"],
        raw_extraction=result.raw_extraction,
        system_evaluated_result={
            "measure_code": first_result["measure_code"],
            "pass_flag": first_result["pass_flag"],
            "evidence_payload": first_result["evidence_payload"],
        },
        measure_evaluation_ids=[item["measure_evaluation_id"] for item in system_evaluated_results],
        system_evaluated_results=system_evaluated_results,
    )


@router.post("/{task_id}/confirm", response_model=ConfirmResponse)
def confirm_task(task_id: int, payload: ConfirmRequest, session: Session = Depends(get_session)) -> ConfirmResponse:
    document = session.get(Document, task_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return confirm_task_review(session, document, payload)
