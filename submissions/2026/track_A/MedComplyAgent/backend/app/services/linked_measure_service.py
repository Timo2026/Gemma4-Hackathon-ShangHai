import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session
from sqlmodel import select

from app.models.document import Document
from app.models.extraction_result import ExtractionResult, ExtractionStatus
from app.models.measure import Measure
from app.models.measure_evaluation import MeasureEvaluation
from app.models.patient import Patient
from app.services.task_status import (
    latest_evaluation,
    latest_extraction,
    parse_measure_codes,
    patient_display_name,
    task_status,
)


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None

    text = value.strip()
    if not text:
        return None

    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def _normalize_identity_text(value: str | None) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", (value or "").lower())
    return " ".join(text.split())


def _history_fields(evidence_payload: dict[str, Any]) -> tuple[str, str, str, str, str, str, str]:
    reviewer_conclusion = evidence_payload.get("reviewer_conclusion")
    reviewer_data = reviewer_conclusion if isinstance(reviewer_conclusion, dict) else {}

    nssd_payload = evidence_payload.get("nssd_payload")
    nssd_data = nssd_payload if isinstance(nssd_payload, dict) else {}

    nssd_form = reviewer_data.get("nssd_form")
    nssd_form_data = nssd_form if isinstance(nssd_form, dict) else {}

    decision = str(reviewer_data.get("decision", "")).strip()
    note = str(reviewer_data.get("note", "")).strip()

    result_value = str(nssd_data.get("result_value") or nssd_form_data.get("result_value") or "").strip()
    dos = str(nssd_data.get("dos") or nssd_form_data.get("dos") or "").strip()
    patient_name = str(nssd_data.get("patient_name") or nssd_form_data.get("patient_name") or "").strip()
    dob = str(nssd_data.get("dob") or nssd_form_data.get("dob") or "").strip()

    confirmed_at = str(evidence_payload.get("confirmed_at") or "").strip()

    return decision, note, result_value, dos, patient_name, dob, confirmed_at


def _is_confirmed_evaluation(evaluation: MeasureEvaluation) -> bool:
    payload = evaluation.evidence_payload if isinstance(evaluation.evidence_payload, dict) else {}
    return payload.get("is_confirmed") is True


def _document_identity(session: Session, document: Document) -> tuple[str, str]:
    patient = session.get(Patient, document.patient_id)
    patient_name = patient_display_name(patient)
    patient_dob = str(patient.date_of_birth or "").strip() if patient else ""

    extraction = latest_extraction(session, document.id)
    payload = extraction.extracted_payload if extraction and isinstance(extraction.extracted_payload, dict) else {}
    candidates = [payload.get("nssd_default"), *(payload.get("nssd_candidates") if isinstance(payload.get("nssd_candidates"), list) else [])]
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        candidate_name = str(candidate.get("patient_name") or "").strip()
        candidate_dob = str(candidate.get("dob") or "").strip()
        if candidate_name:
            return _normalize_identity_text(candidate_name), candidate_dob

    return _normalize_identity_text(patient_name), patient_dob


def _document_matches_identity(session: Session, document: Document, anchor_name: str, anchor_dob: str) -> bool:
    candidate_name, candidate_dob = _document_identity(session, document)
    if not anchor_name or candidate_name != anchor_name:
        return False
    return not anchor_dob or not candidate_dob or candidate_dob == anchor_dob


def _target_measure_for_linked_suggestion(session: Session, document: Document) -> Measure | None:
    for code in parse_measure_codes(document.target_measure_codes):
        if code not in {"CBP", "BPD"}:
            continue
        measure = session.execute(select(Measure).where(Measure.code == code)).scalars().first()
        if measure is not None:
            return measure
    return None


def _create_linked_suggestion_evaluation(
    session: Session,
    document: Document,
    measure: Measure,
    source_evaluation: MeasureEvaluation,
) -> MeasureEvaluation:
    measure_code = measure.code.value if hasattr(measure.code, "value") else str(measure.code)
    extraction = ExtractionResult(
        patient_id=document.patient_id,
        document_id=document.id,
        status=ExtractionStatus.SUCCEEDED,
        extracted_payload={
            "schema_version": "linked_suggestion.v1",
            "task_id": document.id,
            "patient_id": document.patient_id,
            "source_task_id": source_evaluation.document_id,
            "source_measure_evaluation_id": source_evaluation.id,
            "source_meta": {
                "provider": "linked-history",
                "model": "same-patient-reviewer-history",
                "source_txt_path": document.source_txt_path,
            },
        },
        model_name="linked-history",
        is_valid=True,
    )
    session.add(extraction)
    session.flush()

    evaluation = MeasureEvaluation(
        patient_id=document.patient_id,
        measure_id=measure.id,
        document_id=document.id,
        extraction_result_id=extraction.id,
        pass_flag=True,
        evidence_payload={
            "measure_code": measure_code,
            "is_suggested": True,
            "suggestion_source": {
                "task_id": source_evaluation.document_id,
                "measure_evaluation_id": source_evaluation.id,
            },
            "suggested_decision": "GAP_CLOSED",
            "reason_codes": [],
        },
    )
    session.add(evaluation)
    session.flush()
    return evaluation


def suggest_linked_open_bp_tasks(
    session: Session,
    current_document: Document,
    source_evaluation: MeasureEvaluation,
) -> list[dict[str, Any]]:
    anchor_name, anchor_dob = _document_identity(session, current_document)
    if not anchor_name:
        return []

    documents = session.execute(select(Document).order_by(Document.id.asc())).scalars().all()
    suggested: list[dict[str, Any]] = []
    for document in documents:
        if document.id == current_document.id:
            continue
        if not _document_matches_identity(session, document, anchor_name, anchor_dob):
            continue

        latest_document_extraction = latest_extraction(session, document.id)
        latest_document_evaluation = latest_evaluation(session, document.id)
        if task_status(latest_document_extraction, latest_document_evaluation) != "PENDING":
            continue

        measure = _target_measure_for_linked_suggestion(session, document)
        if measure is None:
            continue

        evaluation = _create_linked_suggestion_evaluation(
            session,
            document,
            measure,
            source_evaluation,
        )
        measure_code = measure.code.value if hasattr(measure.code, "value") else str(measure.code)
        suggested.append(
            {
                "measure_evaluation_id": evaluation.id,
                "measure_code": measure_code,
                "was_auto_closed": True,
            }
        )

    return suggested


def build_history_items(
    session: Session,
    current_document: Document,
) -> list[dict[str, Any]]:
    primary_statement = (
        select(MeasureEvaluation, Measure.code, Document.id)
        .join(Measure, Measure.id == MeasureEvaluation.measure_id)
        .join(Document, Document.id == MeasureEvaluation.document_id)
        .where(MeasureEvaluation.patient_id == current_document.patient_id)
        .order_by(MeasureEvaluation.id.desc())
    )

    rows = session.execute(primary_statement).all()
    seen_ids = {evaluation.id for evaluation, _, _ in rows}

    anchor_name, anchor_dob = _document_identity(session, current_document)
    for evaluation, _, _ in rows:
        if not _is_confirmed_evaluation(evaluation):
            continue
        payload = evaluation.evidence_payload if isinstance(evaluation.evidence_payload, dict) else {}
        _, _, _, _, patient_name, dob, _ = _history_fields(payload)
        if patient_name or dob:
            anchor_name = _normalize_identity_text(patient_name)
            anchor_dob = dob.strip()
            break

    if anchor_name:
        fallback_statement = (
            select(MeasureEvaluation, Measure.code, Document.id)
            .join(Measure, Measure.id == MeasureEvaluation.measure_id)
            .join(Document, Document.id == MeasureEvaluation.document_id)
            .where(MeasureEvaluation.patient_id != current_document.patient_id)
            .order_by(MeasureEvaluation.id.desc())
        )
        fallback_rows = session.execute(fallback_statement).all()
        for evaluation, measure_code, task_id in fallback_rows:
            if evaluation.id in seen_ids:
                continue
            if not _is_confirmed_evaluation(evaluation):
                continue
            payload = evaluation.evidence_payload if isinstance(evaluation.evidence_payload, dict) else {}
            _, _, _, _, patient_name, dob, _ = _history_fields(payload)
            candidate_name = _normalize_identity_text(patient_name)
            candidate_dob = dob.strip()
            if candidate_name != anchor_name:
                continue
            if anchor_dob and candidate_dob != anchor_dob:
                continue
            rows.append((evaluation, measure_code, task_id))
            seen_ids.add(evaluation.id)

    history_items: list[dict[str, Any]] = []
    for evaluation, measure_code, task_id in rows:
        if not _is_confirmed_evaluation(evaluation):
            continue

        payload = evaluation.evidence_payload if isinstance(evaluation.evidence_payload, dict) else {}
        decision, note, result_value, dos, patient_name, dob, confirmed_at = _history_fields(payload)
        if not decision:
            continue

        created_at = evaluation.created_at.isoformat() if evaluation.created_at else None
        history_items.append(
            {
                "measure_evaluation_id": evaluation.id,
                "task_id": task_id,
                "patient_id": evaluation.patient_id,
                "measure_code": measure_code.value if hasattr(measure_code, "value") else str(measure_code),
                "decision": decision,
                "note": note,
                "result_value": result_value,
                "dos": dos,
                "patient_name": patient_name,
                "dob": dob,
                "confirmed_at": confirmed_at or None,
                "created_at": created_at,
                "is_current_active_status": False,
            }
        )

    history_items.sort(
        key=lambda item: (
            _parse_datetime(item["dos"]) is not None,
            _parse_datetime(item["dos"]) or datetime.min.replace(tzinfo=timezone.utc),
            _parse_datetime(item["confirmed_at"]) or datetime.min.replace(tzinfo=timezone.utc),
            item["measure_evaluation_id"],
        ),
        reverse=True,
    )

    if history_items:
        history_items[0]["is_current_active_status"] = True

    return history_items
