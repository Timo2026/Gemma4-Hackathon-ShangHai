from datetime import datetime, timezone
from typing import Any

GSD_HBA1C_TARGET = 8.0
GSD_MISSING_HBA1C_DEFAULT = 9.1
GSD_HBA1C_TEST_TYPES = {
    "a1c",
    "glycatedhemoglobin",
    "hba1c",
    "hba1ctest",
    "hba1clab",
    "hgba1c",
    "hemoglobina1c",
    "poca1c",
}


def is_hba1c_test_type(test_type: object) -> bool:
    normalized = "".join(character for character in str(test_type).lower() if character.isalnum())
    return normalized in GSD_HBA1C_TEST_TYPES


def evaluate_gsd(payload: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    reason_codes: list[str] = []
    valid_a1c = [
        reading
        for reading in payload.get("a1c_readings", [])
        if is_hba1c_test_type(reading.get("test_type", ""))
    ]
    valid_a1c_sorted = sorted(valid_a1c, key=lambda item: str(item.get("date", "")), reverse=True)
    latest_a1c = valid_a1c_sorted[0] if valid_a1c_sorted else None

    if latest_a1c is None:
        selected_value = None
        pass_flag = False
        reason_codes.append("MISSING_HBA1C_DEFAULT_FAIL")
    else:
        selected_value = latest_a1c.get("value")
        pass_flag = bool(isinstance(selected_value, (int, float)) and selected_value < GSD_HBA1C_TARGET)
        if not pass_flag:
            reason_codes.append("HBA1C_ABOVE_TARGET")

    selected_observation = {
        "evidence_id": latest_a1c.get("evidence_id") if latest_a1c else None,
        "date": latest_a1c.get("date") if latest_a1c else None,
        "test_type": "HbA1c",
        "encounter_type": latest_a1c.get("encounter_type") if latest_a1c else None,
        "value": selected_value,
        "snippet": latest_a1c.get("snippet") if latest_a1c else "",
        "encounter_snippet": latest_a1c.get("encounter_snippet") if latest_a1c else "",
        "date_snippet": latest_a1c.get("date_snippet") if latest_a1c else "",
        "is_default_value": latest_a1c is None,
        "fallback_value": GSD_MISSING_HBA1C_DEFAULT if latest_a1c is None else None,
    }
    used_evidence_ids = [str(latest_a1c.get("evidence_id"))] if latest_a1c and latest_a1c.get("evidence_id") else []

    evidence_payload = {
        "measure_code": "GSD",
        "selected_observation": selected_observation,
        "used_evidence_ids": used_evidence_ids,
        "reason_codes": reason_codes,
        "rule_result": {
            "target": f"most recent HbA1c < {GSD_HBA1C_TARGET}",
            "used_evidence_ids": used_evidence_ids,
            "excluded_test_types": ["Fasting glucose", "Random glucose", "Finger-stick glucose"],
            "latest_hba1c": latest_a1c,
            "missing_hba1c_default_value": GSD_MISSING_HBA1C_DEFAULT if latest_a1c is None else None,
            "selected_pass_flag": pass_flag,
        },
        "is_confirmed": False,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }
    return pass_flag, evidence_payload
