import re
from typing import Any

from sqlalchemy.orm import Session
from sqlmodel import select

from app.models.document import Document
from app.models.extraction_result import ExtractionResult, ExtractionStatus
from app.models.measure import Measure
from app.models.measure_evaluation import MeasureEvaluation
from app.models.patient import Patient
from app.schemas.tasks import TaskSummary


def parse_measure_codes(value: str | None) -> list[str]:
    if not value:
        return []
    codes: list[str] = []
    for item in re.split(r"[,\s]+", value.upper()):
        if item and item not in codes:
            codes.append(item)
    return codes


def split_patient_name(value: str | None) -> tuple[str, str] | None:
    text = str(value or "").strip()
    if not text:
        return None

    if "," in text:
        last, first = [part.strip() for part in text.split(",", 1)]
        if first and last:
            return first, last

    parts = [part for part in text.split() if part]
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def patient_display_name(patient: Patient | None) -> str:
    if patient is None:
        return "Unknown patient"

    first_name = (patient.first_name or "").strip()
    last_name = (patient.last_name or "").strip()
    full_name = " ".join(part for part in [first_name, last_name] if part)
    return full_name or "Unknown patient"


def sync_patient_identity_from_extraction(session: Session, patient: Patient | None, extraction: ExtractionResult | None) -> None:
    if patient is None or extraction is None:
        return

    payload = extraction.extracted_payload if isinstance(extraction.extracted_payload, dict) else {}
    nssd_default = payload.get("nssd_default")
    nssd_data = nssd_default if isinstance(nssd_default, dict) else {}
    extracted_name = str(nssd_data.get("patient_name") or "").strip()
    split_name = split_patient_name(extracted_name)
    if split_name is None:
        return

    first_name, last_name = split_name
    current_first = (patient.first_name or "").strip()
    current_last = (patient.last_name or "").strip()
    if current_first == first_name and current_last == last_name:
        return

    patient.first_name = first_name
    patient.last_name = last_name
    session.add(patient)


def latest_extraction(session: Session, document_id: int) -> ExtractionResult | None:
    statement = (
        select(ExtractionResult)
        .where(ExtractionResult.document_id == document_id)
        .order_by(ExtractionResult.created_at.desc(), ExtractionResult.id.desc())
    )
    return session.execute(statement).scalars().first()


def latest_evaluation(session: Session, document_id: int) -> MeasureEvaluation | None:
    statement = (
        select(MeasureEvaluation)
        .where(MeasureEvaluation.document_id == document_id)
        .order_by(MeasureEvaluation.created_at.desc(), MeasureEvaluation.id.desc())
    )
    return session.execute(statement).scalars().first()


def latest_successful_extraction(session: Session, document_id: int) -> ExtractionResult | None:
    statement = (
        select(ExtractionResult)
        .where(
            ExtractionResult.document_id == document_id,
            ExtractionResult.status == ExtractionStatus.SUCCEEDED,
        )
        .order_by(ExtractionResult.created_at.desc(), ExtractionResult.id.desc())
    )
    return session.execute(statement).scalars().first()


def measure_codes_for_document(session: Session, document: Document, extraction_id: int | None) -> list[str]:
    if extraction_id is None:
        return parse_measure_codes(document.target_measure_codes)
    statement = (
        select(Measure.code)
        .join(MeasureEvaluation, MeasureEvaluation.measure_id == Measure.id)
        .where(
            MeasureEvaluation.document_id == document.id,
            MeasureEvaluation.extraction_result_id == extraction_id,
        )
        .distinct()
    )
    codes = [code.value if hasattr(code, "value") else str(code) for code in session.execute(statement).scalars().all()]
    return codes or parse_measure_codes(document.target_measure_codes)


def is_suggested_evaluation(evaluation: MeasureEvaluation | None) -> bool:
    payload = evaluation.evidence_payload if evaluation and isinstance(evaluation.evidence_payload, dict) else {}
    return payload.get("is_suggested") is True and payload.get("is_confirmed") is not True


def task_status(extraction: ExtractionResult | None, evaluation: MeasureEvaluation | None) -> str:
    if evaluation and isinstance(evaluation.evidence_payload, dict) and evaluation.evidence_payload.get("is_confirmed") is True:
        return "CONFIRMED"
    if is_suggested_evaluation(evaluation):
        return "PENDING"
    if evaluation:
        return "EXTRACTED"
    if extraction and extraction.status == ExtractionStatus.SUCCEEDED:
        return "EXTRACTED"
    return "PENDING"


def serialize_extraction(extraction: ExtractionResult | None) -> dict[str, Any] | None:
    if extraction is None:
        return None
    return {
        "id": extraction.id,
        "status": extraction.status.value,
        "model_name": extraction.model_name,
        "is_valid": extraction.is_valid,
        "created_at": extraction.created_at.isoformat() if extraction.created_at else None,
        "extracted_payload": extraction.extracted_payload,
    }


def serialize_evaluation(evaluation: MeasureEvaluation | None) -> dict[str, Any] | None:
    if evaluation is None:
        return None
    return {
        "id": evaluation.id,
        "measure_id": evaluation.measure_id,
        "extraction_result_id": evaluation.extraction_result_id,
        "pass_flag": evaluation.pass_flag,
        "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None,
        "evidence_payload": evaluation.evidence_payload,
    }


def build_review_state(extraction: ExtractionResult | None, evaluation: MeasureEvaluation | None, measures: list[str]) -> dict[str, Any]:
    extraction_payload = extraction.extracted_payload if extraction and isinstance(extraction.extracted_payload, dict) else None
    evidence_payload = evaluation.evidence_payload if evaluation and isinstance(evaluation.evidence_payload, dict) else {}
    raw_measure_code = evidence_payload.get("measure_code")
    if not raw_measure_code and measures:
        raw_measure_code = measures[0]
    measure_code = str(raw_measure_code or "").strip() or None

    current_evaluation = None
    if evaluation is not None:
        current_evaluation = {
            "measure_code": measure_code or "LATEST",
            "pass_flag": evaluation.pass_flag,
            "evidence_payload": evidence_payload,
            "measure_evaluation_id": evaluation.id,
        }

    nssd_payload = evidence_payload.get("nssd_payload")
    reviewer_conclusion = evidence_payload.get("reviewer_conclusion")
    reviewer_data = reviewer_conclusion if isinstance(reviewer_conclusion, dict) else {}
    legacy_nssd_form = reviewer_data.get("nssd_form")

    return {
        "current_measure_code": measure_code,
        "current_evaluation": current_evaluation,
        "extraction_payload": extraction_payload,
        "is_suggested": evidence_payload.get("is_suggested") is True,
        "is_confirmed": evidence_payload.get("is_confirmed") is True,
        "reviewer_conclusion": reviewer_conclusion if isinstance(reviewer_conclusion, dict) else None,
        "nssd_payload": nssd_payload if isinstance(nssd_payload, dict) else legacy_nssd_form if isinstance(legacy_nssd_form, dict) else None,
    }


def gap_status(evaluation: MeasureEvaluation | None) -> str | None:
    if evaluation is None:
        return "Open"

    payload = evaluation.evidence_payload if isinstance(evaluation.evidence_payload, dict) else {}
    is_confirmed = payload.get("is_confirmed") is True
    reviewer_conclusion = payload.get("reviewer_conclusion")
    if is_confirmed and isinstance(reviewer_conclusion, dict):
        decision = reviewer_conclusion.get("decision")
        if decision == "GAP_CLOSED":
            return "Closed"
        return "Open"

    if is_confirmed and evaluation.pass_flag:
        return "Closed"

    return "Open"


def build_task_summary(
    document: Document,
    patient: Patient | None,
    extraction: ExtractionResult | None,
    evaluation: MeasureEvaluation | None,
    measures: list[str] | None = None,
) -> TaskSummary:
    return TaskSummary(
        task_id=document.id,
        patient_id=document.patient_id,
        patient_name=patient_display_name(patient),
        source_pdf_path=document.source_pdf_path,
        source_txt_path=document.source_txt_path,
        status=task_status(extraction, evaluation),
        gap_status=gap_status(evaluation),
        measures=measures or [],
    )
