from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlmodel import select

from app.models.document import Document
from app.models.extraction_result import ExtractionResult, ExtractionStatus
from app.models.measure import Measure
from app.models.measure_evaluation import MeasureEvaluation
from app.schemas.tasks import ConfirmRequest, ConfirmResponse
from app.services.linked_measure_service import suggest_linked_open_bp_tasks
from app.services.task_status import latest_evaluation, parse_measure_codes


def _resolve_measure_for_confirm(session: Session, document: Document, requested_code: str | None) -> Measure:
    normalized_code = str(requested_code or "").strip().upper()
    candidate_codes = [code for code in [normalized_code, *parse_measure_codes(document.target_measure_codes)] if code]

    for code in candidate_codes:
        measure = session.execute(select(Measure).where(Measure.code == code)).scalars().first()
        if measure is not None:
            return measure

    first_measure = session.execute(select(Measure).order_by(Measure.id.asc())).scalars().first()
    if first_measure is None:
        raise HTTPException(status_code=400, detail="No measure configured in database")
    return first_measure


def _create_manual_review_evaluation(
    session: Session,
    document: Document,
    measure: Measure,
    reviewer_conclusion: dict[str, Any],
) -> MeasureEvaluation:
    decision = str(reviewer_conclusion.get("decision") or "").strip()
    pass_flag = decision == "GAP_CLOSED"
    measure_code = measure.code.value if hasattr(measure.code, "value") else str(measure.code)

    extraction = ExtractionResult(
        patient_id=document.patient_id,
        document_id=document.id,
        status=ExtractionStatus.SUCCEEDED,
        extracted_payload={
            "schema_version": "manual_review.v1",
            "task_id": document.id,
            "patient_id": document.patient_id,
            "manual_review": True,
            "source_meta": {
                "provider": "manual",
                "model": "manual-review",
                "source_txt_path": document.source_txt_path,
            },
        },
        model_name="manual-review",
        is_valid=True,
    )
    session.add(extraction)
    session.flush()

    evaluation = MeasureEvaluation(
        patient_id=document.patient_id,
        measure_id=measure.id,
        document_id=document.id,
        extraction_result_id=extraction.id,
        pass_flag=pass_flag,
        evidence_payload={
            "measure_code": measure_code,
            "manual_review": True,
            "reason_codes": [],
        },
    )
    session.add(evaluation)
    session.flush()
    return evaluation


def confirm_task_review(session: Session, document: Document, payload: ConfirmRequest) -> ConfirmResponse:
    evaluation = latest_evaluation(session, document.id)
    if evaluation is None:
        requested_measure_code = payload.reviewer_conclusion.get("measure_code") if isinstance(payload.reviewer_conclusion, dict) else None
        measure = _resolve_measure_for_confirm(session, document, requested_measure_code if isinstance(requested_measure_code, str) else None)
        evaluation = _create_manual_review_evaluation(session, document, measure, payload.reviewer_conclusion)

    nssd_payload = dict(payload.nssd_payload)
    if not nssd_payload:
        reviewer_form = payload.reviewer_conclusion.get("nssd_form")
        if isinstance(reviewer_form, dict):
            nssd_payload = dict(reviewer_form)

    confirmed_at = datetime.now(timezone.utc).isoformat()

    evidence_payload = dict(evaluation.evidence_payload or {})
    evidence_payload["reviewer_conclusion"] = payload.reviewer_conclusion
    evidence_payload["nssd_payload"] = nssd_payload
    evidence_payload["is_confirmed"] = payload.is_confirmed
    evidence_payload["confirmed_at"] = confirmed_at
    evaluation.evidence_payload = evidence_payload
    session.add(evaluation)

    linked_closed_measures: list[dict[str, Any]] = []
    decision = payload.reviewer_conclusion.get("decision")
    should_auto_close_linked = payload.is_confirmed and decision == "GAP_CLOSED"
    if should_auto_close_linked:
        linked_closed_measures = suggest_linked_open_bp_tasks(
            session,
            document,
            evaluation,
        )

    session.commit()
    session.refresh(evaluation)

    status = "CONFIRMED" if payload.is_confirmed else "EXTRACTED"
    return ConfirmResponse(
        task_id=document.id,
        status=status,
        measure_evaluation_id=evaluation.id,
        reviewer_conclusion=payload.reviewer_conclusion,
        evidence_payload=evidence_payload,
        linked_closed_measures=linked_closed_measures,
    )
