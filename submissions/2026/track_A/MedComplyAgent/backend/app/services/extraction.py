import logging
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from sqlalchemy.orm import Session
from sqlmodel import select

from app.core.config import settings
from app.models.document import Document
from app.models.extraction_result import ExtractionResult, ExtractionStatus
from app.models.measure import Measure
from app.models.measure_evaluation import MeasureEvaluation
from app.agent.gemma_review_agent import GemmaAgentError, run_gemma_review_agent
from app.rules.bpd import evaluate_bpd
from app.rules.cbp import evaluate_cbp
from app.rules.gsd import evaluate_gsd
from app.services.llm_provider import ChatJsonRequest, LLMProviderError, chat_json

logger = logging.getLogger("uvicorn.error").getChild("app.services.extraction")
logger.setLevel(logging.INFO)


class NoMeasureConfiguredError(Exception):
    pass


class UnsupportedMeasureError(Exception):
    pass


class LLMExtractionError(Exception):
    pass


@dataclass
class MeasureEvaluationResult:
    evaluation: MeasureEvaluation
    measure_code: str
    pass_flag: bool
    evidence_payload: dict[str, Any]


@dataclass
class ExtractionFlowResult:
    extraction: ExtractionResult
    evaluations: list[MeasureEvaluationResult]
    raw_extraction: dict[str, Any]


_MEASURE_EVALUATORS: dict[str, Callable[[dict[str, Any]], tuple[bool, dict[str, Any]]]] = {
    "CBP": evaluate_cbp,
    "BPD": evaluate_bpd,
    "GSD": evaluate_gsd,
}

_PROMPT_FILES_BY_MEASURE: dict[str, str] = {
    "CBP": "cbp_extraction.txt",
    "BPD": "bpd_extraction.txt",
    "GSD": "gsd_extraction.txt",
}

_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def _clean_text(value: Any) -> str:
    return str(value or "").replace("\x00", "").strip()


def _sanitize_jsonb_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("\x00", "")
    if isinstance(value, list):
        return [_sanitize_jsonb_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_jsonb_value(item) for key, item in value.items()}
    return value


def _normalize_encounter_type(value: Any) -> str:
    text = _clean_text(value)
    if not text:
        return "Unknown"

    normalized = " ".join(text.lower().replace("/", " ").replace("-", " ").split())
    if normalized in {"office visit", "telehealth", "remote monitoring", "ed", "inpatient"}:
        return {
            "office visit": "Office Visit",
            "telehealth": "Telehealth",
            "remote monitoring": "Remote Monitoring",
            "ed": "ED",
            "inpatient": "Inpatient",
        }[normalized]

    if "emergency" in normalized or " er " in f" {normalized} " or normalized.startswith("er ") or normalized.endswith(" er") or " ed " in f" {normalized} ":
        return "ED"
    if "inpatient" in normalized or "hospitalization" in normalized or "hospitalisation" in normalized or "hospital admission" in normalized:
        return "Inpatient"
    if "telehealth" in normalized or "telemedicine" in normalized or "virtual" in normalized or "video visit" in normalized:
        return "Telehealth"
    if "remote" in normalized or "monitoring" in normalized or "home bp" in normalized or "home blood pressure" in normalized:
        return "Remote Monitoring"
    if "office" in normalized or "clinic" in normalized or "outpatient" in normalized or "in person" in normalized:
        return "Office Visit"
    return "Unknown"


def _normalize_bp_readings(items: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        date = _clean_text(item.get("date", ""))
        encounter_type = _normalize_encounter_type(item.get("encounter_type"))
        systolic = item.get("systolic")
        diastolic = item.get("diastolic")
        if not isinstance(systolic, (int, float)) or not isinstance(diastolic, (int, float)):
            continue
        normalized.append(
            {
                "evidence_id": f"bp-{len(normalized) + 1}",
                "date": date,
                "systolic": int(systolic),
                "diastolic": int(diastolic),
                "encounter_type": encounter_type,
                "snippet": _clean_text(item.get("snippet", "")),
                "encounter_snippet": _clean_text(item.get("encounter_snippet", "")),
                "date_snippet": _clean_text(item.get("date_snippet", "")),
            }
        )
    return normalized


def _normalize_a1c_readings(items: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        date = _clean_text(item.get("date", ""))
        test_type = _clean_text(item.get("test_type", "")) or "Unknown"
        encounter_type = _normalize_encounter_type(item.get("encounter_type"))
        value = item.get("value")
        if not isinstance(value, (int, float)):
            continue
        normalized.append(
            {
                "evidence_id": f"a1c-{len(normalized) + 1}",
                "date": date,
                "value": float(value),
                "test_type": test_type,
                "encounter_type": encounter_type,
                "snippet": _clean_text(item.get("snippet", "")),
                "encounter_snippet": _clean_text(item.get("encounter_snippet", "")),
                "date_snippet": _clean_text(item.get("date_snippet", "")),
            }
        )
    return normalized


def _normalize_nssd_candidates(items: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        encounter_type = _normalize_encounter_type(item.get("encounter_type"))
        place_of_service = _clean_text(item.get("place_of_service", "")) or encounter_type
        normalized.append(
            {
                "evidence_id": f"nssd-{len(normalized) + 1}",
                "patient_name": _clean_text(item.get("patient_name", "")),
                "dob": _clean_text(item.get("dob", "")),
                "result_value": _clean_text(item.get("result_value", "")),
                "dos": _clean_text(item.get("dos", "")),
                "rendering_provider": _clean_text(item.get("rendering_provider", "")),
                "place_of_service": place_of_service,
                "encounter_type": encounter_type,
                "measure_hint": _clean_text(item.get("measure_hint", "")).upper(),
                "snippet": _clean_text(item.get("snippet", "")),
                "encounter_snippet": _clean_text(item.get("encounter_snippet", "")),
                "date_snippet": _clean_text(item.get("date_snippet", "")),
            }
        )
    return normalized


def _evidence_ids(*groups: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for group in groups:
        for item in group:
            evidence_id = str(item.get("evidence_id") or "").strip()
            if evidence_id and evidence_id not in ids:
                ids.append(evidence_id)
    return ids


def _build_agent_trace(
    bp_readings: list[dict[str, Any]],
    a1c_readings: list[dict[str, Any]],
    nssd_candidates: list[dict[str, Any]],
    prior_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    extracted_evidence_ids = _evidence_ids(bp_readings, a1c_readings, nssd_candidates)
    prior_steps = prior_trace.get("steps") if isinstance(prior_trace, dict) else []
    steps = list(prior_steps) if isinstance(prior_steps, list) else []
    next_step_number = len(steps) + 1
    steps.extend(
        [
            {
                "step_id": f"step-{next_step_number}",
                "actor": "llm",
                "action": "extract_clinical_evidence",
                "status": "completed",
                "output_evidence_ids": extracted_evidence_ids,
            },
            {
                "step_id": f"step-{next_step_number + 1}",
                "actor": "backend",
                "action": "normalize_extraction_payload",
                "status": "completed",
                "output_evidence_ids": extracted_evidence_ids,
            },
        ]
    )
    return {
        "schema_version": "agent_trace.v1",
        "steps": steps,
        "final_summary": prior_trace.get("final_summary", "") if isinstance(prior_trace, dict) else "",
    }


def normalize_extracted_payload(raw_payload: dict[str, Any], document: Document) -> dict[str, Any]:
    bp_readings = _normalize_bp_readings(list(raw_payload.get("blood_pressure_readings", [])))
    a1c_readings = _normalize_a1c_readings(list(raw_payload.get("a1c_readings", [])))
    nssd_candidates = _normalize_nssd_candidates(list(raw_payload.get("nssd_candidates", [])))
    evidence_ids = _evidence_ids(bp_readings, a1c_readings, nssd_candidates)
    prior_agent_trace = raw_payload.get("agent_trace") if isinstance(raw_payload.get("agent_trace"), dict) else None
    payload = {
        "schema_version": "evidence.v2",
        "task_id": document.id,
        "patient_id": document.patient_id,
        "evidence_ids": evidence_ids,
        "blood_pressure_readings": bp_readings,
        "a1c_readings": a1c_readings,
        "nssd_candidates": nssd_candidates,
        "nssd_default": nssd_candidates[0] if nssd_candidates else None,
        "agent_trace": _build_agent_trace(bp_readings, a1c_readings, nssd_candidates, prior_agent_trace),
        "source_meta": {
            "provider": settings.llm_provider,
            "model": settings.llm_model_name,
            "source_txt_path": document.source_txt_path,
        },
    }
    sanitized = _sanitize_jsonb_value(payload)
    return sanitized if isinstance(sanitized, dict) else payload


def _prompt_path_for_measure(measure_code: str) -> Path:
    prompt_filename = _PROMPT_FILES_BY_MEASURE.get(measure_code)
    if prompt_filename is None:
        raise UnsupportedMeasureError(measure_code)
    return _PROMPTS_DIR / prompt_filename


def _load_system_prompt(measure_code: str) -> str:
    prompt_path = _prompt_path_for_measure(measure_code)
    try:
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except OSError as error:
        raise LLMExtractionError(f"Failed to read prompt file for {measure_code}: {error}") from error


def _build_user_prompt(document_text: str) -> str:
    return f"Clinical note:\n{document_text}"


def _read_document_text(document: Document) -> tuple[str, float]:
    read_started = perf_counter()
    try:
        txt_path = Path(document.source_txt_path)
        if not txt_path.is_absolute():
            txt_path = Path(settings.data_dir) / txt_path
        with open(txt_path, "r", encoding="utf-8") as file:
            document_text = file.read().replace("\x00", "")
    except OSError as error:
        raise LLMExtractionError(f"Failed to read source txt: {error}") from error
    return document_text, perf_counter() - read_started


def call_llm_extract(document: Document, measure_code: str) -> dict[str, Any]:
    document_text, read_elapsed = _read_document_text(document)

    system_prompt = _load_system_prompt(measure_code)
    logger.info(
        "extraction timing task_id=%s measure=%s phase=read_file seconds=%.3f input_chars=%s prompt_chars=%s",
        document.id,
        measure_code,
        read_elapsed,
        len(document_text),
        len(system_prompt),
    )

    llm_started = perf_counter()
    try:
        parsed = chat_json(
            ChatJsonRequest(
                system_prompt=system_prompt,
                user_prompt=_build_user_prompt(document_text),
            )
        )
    except LLMProviderError as error:
        llm_elapsed = perf_counter() - llm_started
        logger.info(
            "extraction timing task_id=%s measure=%s phase=call_llm seconds=%.3f status=error detail=%s",
            document.id,
            measure_code,
            llm_elapsed,
            error,
        )
        raise LLMExtractionError(str(error)) from error
    llm_elapsed = perf_counter() - llm_started
    logger.info(
        "extraction timing task_id=%s measure=%s phase=call_llm seconds=%.3f",
        document.id,
        measure_code,
        llm_elapsed,
    )

    return parsed


def call_gemma_agent_extract(document: Document, measure_code: str) -> dict[str, Any]:
    document_text, read_elapsed = _read_document_text(document)
    logger.info(
        "extraction timing task_id=%s measure=%s mode=gemma_agent phase=read_file seconds=%.3f input_chars=%s",
        document.id,
        measure_code,
        read_elapsed,
        len(document_text),
    )

    agent_started = perf_counter()
    try:
        parsed = run_gemma_review_agent(document_text=document_text, measure_code=measure_code)
    except GemmaAgentError as error:
        agent_elapsed = perf_counter() - agent_started
        logger.info(
            "extraction timing task_id=%s measure=%s mode=gemma_agent phase=call_agent seconds=%.3f status=error detail=%s",
            document.id,
            measure_code,
            agent_elapsed,
            error,
        )
        raise LLMExtractionError(str(error)) from error
    agent_elapsed = perf_counter() - agent_started
    logger.info(
        "extraction timing task_id=%s measure=%s mode=gemma_agent phase=call_agent seconds=%.3f",
        document.id,
        measure_code,
        agent_elapsed,
    )
    return parsed


def _use_gemma_agent() -> bool:
    return settings.llm_review_mode.strip().lower() == "gemma_agent"


def _infer_measure_codes_from_text(text: str) -> list[str]:
    context = text.lower()

    if "gsd" in context:
        return ["GSD"]
    if "cbp" in context:
        return ["CBP"]
    if "bpd" in context:
        return ["BPD"]
    if "mmx" in context:
        return ["CBP", "BPD"]

    return []


def _infer_measure_codes_from_document(document: Document) -> list[str]:
    return _infer_measure_codes_from_text(f"{document.source_pdf_path} {document.source_txt_path}")


def _target_measure_codes_from_document(document: Document) -> list[str]:
    value = getattr(document, "target_measure_codes", None)
    if not value:
        return []
    return [item.strip().upper() for item in value.split(",") if item.strip()]


def select_measures_for_document(
    session: Session,
    document: Document,
    measure_ids: list[int] | None = None,
) -> list[Measure]:
    measures = session.execute(select(Measure).order_by(Measure.id.asc())).scalars().all()
    if not measures:
        raise NoMeasureConfiguredError()

    target_codes = set(_target_measure_codes_from_document(document))

    if measure_ids:
        selected_ids = set(measure_ids)
        selected = [measure for measure in measures if measure.id in selected_ids]
        if not selected:
            raise UnsupportedMeasureError("No requested measures are configured")
        if target_codes:
            selected = [measure for measure in selected if measure.code.value in target_codes]
            if not selected:
                raise UnsupportedMeasureError("Requested measure does not match document target measure")
        return selected[:1]

    if target_codes:
        targeted = [measure for measure in measures if measure.code.value in target_codes]
        if targeted:
            return targeted[:1]
        raise UnsupportedMeasureError(",".join(sorted(target_codes)))

    inferred_codes = set(_infer_measure_codes_from_document(document))
    if inferred_codes:
        inferred = [measure for measure in measures if measure.code.value in inferred_codes]
        if inferred:
            return inferred[:1]
        raise UnsupportedMeasureError(",".join(sorted(inferred_codes)))

    raise NoMeasureConfiguredError()


def evaluate_payload_for_measure(payload: dict[str, Any], measure_code: str) -> tuple[bool, dict[str, Any]]:
    evaluator = _MEASURE_EVALUATORS.get(measure_code)
    if evaluator is None:
        raise UnsupportedMeasureError(measure_code)
    return evaluator(payload)


def record_failed_extraction(session: Session, document: Document, detail: str) -> ExtractionResult:
    extraction = ExtractionResult(
        patient_id=document.patient_id,
        document_id=document.id,
        status=ExtractionStatus.FAILED,
        extracted_payload={
            "error_message": detail,
            "source_meta": {
                "provider": settings.llm_provider,
                "model": settings.llm_model_name,
                "source_txt_path": document.source_txt_path,
            },
        },
        model_name=settings.llm_model_name,
        is_valid=False,
    )
    session.add(extraction)
    session.commit()
    session.refresh(extraction)
    return extraction


def run_extraction_flow(
    session: Session,
    document: Document,
    measure_ids: list[int] | None = None,
) -> ExtractionFlowResult:
    flow_started = perf_counter()
    measures = select_measures_for_document(session, document, measure_ids=measure_ids)
    prompt_measure_code = measures[0].code.value
    raw_payload = call_gemma_agent_extract(document, measure_code=prompt_measure_code) if _use_gemma_agent() else call_llm_extract(document, measure_code=prompt_measure_code)

    normalize_started = perf_counter()
    extracted_payload = normalize_extracted_payload(raw_payload, document)
    normalize_elapsed = perf_counter() - normalize_started
    logger.info(
        "extraction timing task_id=%s measure=%s phase=normalize_payload seconds=%.3f",
        document.id,
        prompt_measure_code,
        normalize_elapsed,
    )

    db_prepare_started = perf_counter()
    extraction = ExtractionResult(
        patient_id=document.patient_id,
        document_id=document.id,
        status=ExtractionStatus.SUCCEEDED,
        extracted_payload=extracted_payload,
        model_name=settings.llm_model_name,
        is_valid=True,
    )
    session.add(extraction)
    session.flush()
    db_prepare_elapsed = perf_counter() - db_prepare_started
    logger.info(
        "extraction timing task_id=%s measure=%s phase=prepare_extraction_record seconds=%.3f",
        document.id,
        prompt_measure_code,
        db_prepare_elapsed,
    )

    evaluations: list[MeasureEvaluationResult] = []
    evaluate_started = perf_counter()
    for measure in measures:
        measure_code = measure.code.value
        pass_flag, evidence_payload = evaluate_payload_for_measure(extracted_payload, measure_code)
        evaluation = MeasureEvaluation(
            patient_id=document.patient_id,
            measure_id=measure.id,
            document_id=document.id,
            extraction_result_id=extraction.id,
            pass_flag=pass_flag,
            evidence_payload=evidence_payload,
        )
        session.add(evaluation)
        session.flush()
        evaluations.append(
            MeasureEvaluationResult(
                evaluation=evaluation,
                measure_code=measure_code,
                pass_flag=pass_flag,
                evidence_payload=evidence_payload,
            )
        )
    evaluate_elapsed = perf_counter() - evaluate_started
    logger.info(
        "extraction timing task_id=%s measure=%s phase=evaluate_rules seconds=%.3f evaluations=%s",
        document.id,
        prompt_measure_code,
        evaluate_elapsed,
        len(evaluations),
    )

    commit_started = perf_counter()
    session.commit()
    session.refresh(extraction)
    for item in evaluations:
        session.refresh(item.evaluation)
    commit_elapsed = perf_counter() - commit_started
    total_elapsed = perf_counter() - flow_started
    logger.info(
        "extraction timing task_id=%s measure=%s phase=db_commit seconds=%.3f",
        document.id,
        prompt_measure_code,
        commit_elapsed,
    )
    logger.info(
        "extraction timing task_id=%s measure=%s phase=total seconds=%.3f",
        document.id,
        prompt_measure_code,
        total_elapsed,
    )

    return ExtractionFlowResult(
        extraction=extraction,
        evaluations=evaluations,
        raw_extraction=extracted_payload,
    )
