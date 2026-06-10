import json
import re
from typing import Any

from app.services.llm_provider import ChatCompletionRequest, LLMProviderError, chat_completion


class AgentToolError(Exception):
    pass


BP_ALLOWED_ENCOUNTER_TYPES = {"Office Visit", "Telehealth", "Remote Monitoring"}
_BP_PATTERN = re.compile(r"\b(?:bp|blood pressure)?\s*:?\s*\d{2,3}\s*/\s*\d{2,3}\b", re.IGNORECASE)


def _string(value: Any) -> str:
    return str(value or "").replace("\x00", "").strip()


def _number(value: Any) -> int | float | None:
    return value if isinstance(value, (int, float)) else None


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _json_object_from_text(text: str) -> dict[str, Any]:
    stripped = text.strip().lstrip("\ufeff")
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)

    try:
        parsed = json.loads(stripped, strict=False)
    except ValueError:
        match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
        if not match:
            raise
        parsed = json.loads(match.group(0), strict=False)

    if not isinstance(parsed, dict):
        raise AgentToolError("Gemma extraction response is not a JSON object")
    return parsed


def _normalize_encounter_type(value: Any) -> str:
    text = _string(value)
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

    if "emergency" in normalized or " er " in f" {normalized} " or " ed " in f" {normalized} ":
        return "ED"
    if "inpatient" in normalized or "hospital" in normalized or "admission" in normalized:
        return "Inpatient"
    if "telehealth" in normalized or "telemedicine" in normalized or "virtual" in normalized:
        return "Telehealth"
    if "remote" in normalized or "home bp" in normalized or "home blood pressure" in normalized:
        return "Remote Monitoring"
    if "office" in normalized or "clinic" in normalized or "outpatient" in normalized:
        return "Office Visit"
    return "Unknown"


def _looks_like_bp_text(value: str) -> bool:
    return bool(_BP_PATTERN.search(value))


def _looks_like_encounter_text(value: str) -> bool:
    normalized = value.lower()
    return any(
        token in normalized
        for token in (
            "encounter",
            "office",
            "visit",
            "primary care",
            "follow-up",
            "follow up",
            "clinic",
            "outpatient",
            "telehealth",
            "remote monitoring",
            "emergency",
            "department",
            "inpatient",
        )
    )


def _encounter_snippet(value: Any, fallback: str) -> str:
    candidate = _string(value)
    if candidate and _looks_like_encounter_text(candidate) and not _looks_like_bp_text(candidate):
        return candidate
    return fallback


def _compact_extraction_system_prompt(measure_code: str) -> str:
    measure = measure_code.upper()
    if measure in {"CBP", "BPD"}:
        evidence_rules = """
- Extract encounter_info: patient_name, dob, provider, encounter_type, date_of_service, source_text.
- Extract blood_pressure_readings only for the current visit/current encounter when present.
- Do not extract historical/prior comparison BP values when a current/today BP exists.
- Do not extract HbA1c or glucose for CBP/BPD.
- Normalize encounter_type to exactly one of Office Visit, Telehealth, Remote Monitoring, ED, Inpatient, Unknown.
- snippet must quote the BP result source, such as "BP: 132/84 mmHg".
- encounter_snippet must quote only visit/setting source text, such as "Encounter Type: Office Visit - Primary Care Follow-up"; never put BP result text in encounter_snippet.
- date_snippet must quote only date/DOS source text.
""".strip()
    else:
        evidence_rules = """
- Extract encounter_info: patient_name, dob, provider, encounter_type, date_of_service, source_text.
- Extract HbA1c values only. Do not treat fasting glucose, random glucose, or finger-stick glucose as HbA1c.
- Canonicalize HbA1c test_type to HbA1c.
- Do not extract blood pressure for GSD.
- Normalize encounter_type to exactly one of Office Visit, Telehealth, Remote Monitoring, ED, Inpatient, Unknown.
- snippet must quote the HbA1c result source.
- encounter_snippet must quote only visit/setting source text; never put lab result text in encounter_snippet.
- date_snippet must quote only date/DOS source text.
""".strip()

    return f"""
You are a clinical evidence extraction tool used by MedComply Agent.
Extract facts only from the chart text for the {measure} measure. Do not decide whether a HEDIS gap is closed.

Return JSON only with this object shape:
{{
  "encounter_info": {{
    "encounter_type": "",
    "date_of_service": "",
    "provider": "",
    "patient_name": "",
    "dob": "",
    "source_text": ""
  }},
  "blood_pressure_readings": [
    {{
      "date": "",
      "systolic": 0,
      "diastolic": 0,
      "encounter_type": "",
      "snippet": "",
      "encounter_snippet": "",
      "date_snippet": ""
    }}
  ],
  "a1c_readings": [
    {{
      "date": "",
      "value": 0.0,
      "test_type": "HbA1c",
      "encounter_type": "",
      "snippet": "",
      "encounter_snippet": "",
      "date_snippet": ""
    }}
  ],
  "missing": [],
  "confidence": 0.0,
  "notes": []
}}

Rules:
{evidence_rules}
- Use empty arrays when evidence is missing.
- Leave unknown string fields as "".
- confidence must be a number from 0 to 1.
""".strip()


def _extract_bundle(document_text: str, measure_code: str) -> dict[str, Any]:
    try:
        message = chat_completion(
            ChatCompletionRequest(
                messages=[
                    {"role": "system", "content": _compact_extraction_system_prompt(measure_code)},
                    {"role": "user", "content": f"Clinical chart text:\n{document_text}"},
                ],
                temperature=0,
                max_tokens=2400,
            )
        )
    except LLMProviderError as error:
        raise AgentToolError(str(error)) from error

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise AgentToolError("Gemma extraction tool returned empty content")

    try:
        return _json_object_from_text(content)
    except ValueError as error:
        raise AgentToolError(f"Invalid Gemma extraction JSON: {error}") from error


def _bundle(memory: dict[str, Any], document_text: str, measure_code: str) -> dict[str, Any]:
    cached = memory.get("extraction_bundle")
    if isinstance(cached, dict):
        return cached

    extracted = _extract_bundle(document_text, measure_code)
    memory["extraction_bundle"] = extracted
    return extracted


def _encounter_info(bundle: dict[str, Any]) -> dict[str, Any]:
    raw = bundle.get("encounter_info") if isinstance(bundle.get("encounter_info"), dict) else {}
    encounter_type = _normalize_encounter_type(raw.get("encounter_type"))
    return {
        "encounter_type": encounter_type,
        "date_of_service": _string(raw.get("date_of_service")),
        "provider": _string(raw.get("provider")),
        "patient_name": _string(raw.get("patient_name")),
        "dob": _string(raw.get("dob")),
        "source_text": _string(raw.get("source_text")),
    }


def _bp_readings(bundle: dict[str, Any], fallback_encounter_type: str, fallback_encounter_snippet: str = "") -> list[dict[str, Any]]:
    readings: list[dict[str, Any]] = []
    for item in _list(bundle.get("blood_pressure_readings")):
        if not isinstance(item, dict):
            continue
        systolic = _number(item.get("systolic"))
        diastolic = _number(item.get("diastolic"))
        if systolic is None or diastolic is None:
            continue
        readings.append(
            {
                "date": _string(item.get("date")),
                "systolic": int(systolic),
                "diastolic": int(diastolic),
                "encounter_type": _normalize_encounter_type(item.get("encounter_type")) or fallback_encounter_type,
                "snippet": _string(item.get("snippet")),
                "encounter_snippet": _encounter_snippet(item.get("encounter_snippet"), fallback_encounter_snippet),
                "date_snippet": _string(item.get("date_snippet")),
            }
        )
    return readings


def _a1c_readings(bundle: dict[str, Any], fallback_encounter_type: str, fallback_encounter_snippet: str = "") -> list[dict[str, Any]]:
    readings: list[dict[str, Any]] = []
    for item in _list(bundle.get("a1c_readings")):
        if not isinstance(item, dict):
            continue
        value = _number(item.get("value"))
        if value is None:
            continue
        readings.append(
            {
                "date": _string(item.get("date")),
                "value": float(value),
                "test_type": _string(item.get("test_type")) or "HbA1c",
                "encounter_type": _normalize_encounter_type(item.get("encounter_type")) or fallback_encounter_type,
                "snippet": _string(item.get("snippet")),
                "encounter_snippet": _encounter_snippet(item.get("encounter_snippet"), fallback_encounter_snippet),
                "date_snippet": _string(item.get("date_snippet")),
            }
        )
    return readings


def execute_agent_tool(
    name: str,
    arguments: dict[str, Any],
    document_text: str,
    measure_code: str,
    memory: dict[str, Any],
) -> dict[str, Any]:
    measure = _string(arguments.get("measure")) or measure_code
    extracted = _bundle(memory, document_text, measure)
    encounter = _encounter_info(extracted)
    missing = [item for item in _list(extracted.get("missing")) if isinstance(item, str)]
    confidence = extracted.get("confidence") if isinstance(extracted.get("confidence"), (int, float)) else None
    notes = [item for item in _list(extracted.get("notes")) if isinstance(item, str)]

    if name == "get_encounter_info":
        bp_measure = measure.upper() in {"CBP", "BPD"}
        eligible = not bp_measure or encounter["encounter_type"] in BP_ALLOWED_ENCOUNTER_TYPES or encounter["encounter_type"] == "Unknown"
        result = {
            **encounter,
            "eligible": eligible,
            "evidence": [
                {
                    "type": "encounter",
                    "source_text": encounter.get("source_text", ""),
                    "encounter_type": encounter.get("encounter_type", "Unknown"),
                    "date_of_service": encounter.get("date_of_service", ""),
                }
            ],
            "missing": missing,
            "confidence": confidence,
            "notes": notes,
        }
        if bp_measure and encounter["encounter_type"] in {"ED", "Inpatient"}:
            result["eligible"] = False
            result["notes"] = [*notes, f"{encounter['encounter_type']} encounter is excluded for BP measures."]
        return result

    if name == "get_bp_readings":
        prior_encounter = memory.get("encounter_info") if isinstance(memory.get("encounter_info"), dict) else {}
        readings = _bp_readings(extracted, encounter["encounter_type"], encounter.get("source_text", ""))
        prior_notes = [item for item in _list(prior_encounter.get("notes")) if isinstance(item, str)]
        audit_notes = prior_notes if prior_encounter.get("eligible") is False else []
        return {
            "blood_pressure_readings": readings,
            "evidence": [
                {
                    "type": "blood_pressure",
                    "value": f"{item['systolic']}/{item['diastolic']}",
                    "date": item.get("date", ""),
                    "source_text": item.get("snippet", ""),
                }
                for item in readings
            ],
            "missing": missing if readings else [*missing, "blood_pressure_readings"],
            "confidence": confidence,
            "notes": [*notes, *audit_notes],
        }

    if name == "get_lab_values":
        readings = _a1c_readings(extracted, encounter["encounter_type"], encounter.get("source_text", ""))
        return {
            "a1c_readings": readings,
            "evidence": [
                {
                    "type": "hba1c",
                    "value": item.get("value"),
                    "date": item.get("date", ""),
                    "source_text": item.get("snippet", ""),
                }
                for item in readings
            ],
            "missing": missing if readings else [*missing, "a1c_readings"],
            "confidence": confidence,
            "notes": notes,
        }

    raise AgentToolError(f"Unsupported tool: {name}")


def _nssd_candidates(
    measure_code: str,
    encounter: dict[str, Any],
    bp_readings: list[dict[str, Any]],
    a1c_readings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for reading in bp_readings:
        candidates.append(
            {
                "patient_name": encounter.get("patient_name", ""),
                "dob": encounter.get("dob", ""),
                "result_value": f"{reading.get('systolic')}/{reading.get('diastolic')}",
                "dos": reading.get("date") or encounter.get("date_of_service", ""),
                "rendering_provider": encounter.get("provider", ""),
                "place_of_service": reading.get("encounter_type") or encounter.get("encounter_type", ""),
                "encounter_type": reading.get("encounter_type") or encounter.get("encounter_type", ""),
                "measure_hint": measure_code,
                "snippet": reading.get("snippet", ""),
                "encounter_snippet": reading.get("encounter_snippet") or encounter.get("source_text", ""),
                "date_snippet": reading.get("date_snippet") or encounter.get("date_of_service", ""),
            }
        )
    for lab in a1c_readings:
        candidates.append(
            {
                "patient_name": encounter.get("patient_name", ""),
                "dob": encounter.get("dob", ""),
                "result_value": f"{lab.get('value')}%",
                "dos": lab.get("date") or encounter.get("date_of_service", ""),
                "rendering_provider": encounter.get("provider", ""),
                "place_of_service": lab.get("encounter_type") or encounter.get("encounter_type", ""),
                "encounter_type": lab.get("encounter_type") or encounter.get("encounter_type", ""),
                "measure_hint": measure_code,
                "snippet": lab.get("snippet", ""),
                "encounter_snippet": lab.get("encounter_snippet") or encounter.get("source_text", ""),
                "date_snippet": lab.get("date_snippet") or encounter.get("date_of_service", ""),
            }
        )
    return candidates


def payload_from_memory(memory: dict[str, Any], measure_code: str) -> dict[str, Any]:
    bundle = memory.get("extraction_bundle") if isinstance(memory.get("extraction_bundle"), dict) else {}
    encounter = _encounter_info(bundle) if bundle else {}
    if isinstance(memory.get("encounter_info"), dict):
        encounter = {**encounter, **memory["encounter_info"]}

    bp_readings = memory.get("blood_pressure_readings")
    if not isinstance(bp_readings, list):
        bp_readings = (
            _bp_readings(
                bundle,
                str(encounter.get("encounter_type") or "Unknown"),
                str(encounter.get("source_text") or ""),
            )
            if bundle
            else []
        )

    a1c_readings = memory.get("a1c_readings")
    if not isinstance(a1c_readings, list):
        a1c_readings = (
            _a1c_readings(
                bundle,
                str(encounter.get("encounter_type") or "Unknown"),
                str(encounter.get("source_text") or ""),
            )
            if bundle
            else []
        )

    return {
        "blood_pressure_readings": [item for item in bp_readings if isinstance(item, dict)],
        "a1c_readings": [item for item in a1c_readings if isinstance(item, dict)],
        "nssd_candidates": _nssd_candidates(
            measure_code,
            encounter,
            [item for item in bp_readings if isinstance(item, dict)],
            [item for item in a1c_readings if isinstance(item, dict)],
        ),
    }
