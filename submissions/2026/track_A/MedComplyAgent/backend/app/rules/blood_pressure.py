from datetime import datetime, timezone
from typing import Any

BP_ALLOWED_ENCOUNTER_TYPES = {"Office Visit", "Telehealth", "Remote Monitoring"}


def evaluate_bp_measure(
    payload: dict[str, Any],
    measure_code: str,
    systolic_target: int,
    diastolic_target: int,
) -> tuple[bool, dict[str, Any]]:
    reason_codes: list[str] = []
    bp_readings = payload.get("blood_pressure_readings", [])
    all_bp = [reading for reading in bp_readings if isinstance(reading, dict)]
    kept_bp = [
        reading
        for reading in all_bp
        if str(reading.get("encounter_type", "")).strip() in BP_ALLOWED_ENCOUNTER_TYPES
    ]
    excluded_bp = [reading for reading in all_bp if reading not in kept_bp]

    grouped_by_date: dict[str, list[dict[str, Any]]] = {}
    for reading in kept_bp:
        reading_date = str(reading.get("date", "")).strip()
        if not reading_date:
            continue
        grouped_by_date.setdefault(reading_date, []).append(reading)

    per_date_lows: list[dict[str, Any]] = []
    for reading_date in sorted(grouped_by_date.keys()):
        day_readings = grouped_by_date[reading_date]
        systolic_values = [r.get("systolic") for r in day_readings if isinstance(r.get("systolic"), (int, float))]
        diastolic_values = [r.get("diastolic") for r in day_readings if isinstance(r.get("diastolic"), (int, float))]
        if not systolic_values or not diastolic_values:
            continue
        systolic_reading = min(
            (r for r in day_readings if isinstance(r.get("systolic"), (int, float))),
            key=lambda item: item["systolic"],
        )
        diastolic_reading = min(
            (r for r in day_readings if isinstance(r.get("diastolic"), (int, float))),
            key=lambda item: item["diastolic"],
        )
        lowest_systolic = systolic_reading["systolic"]
        lowest_diastolic = diastolic_reading["diastolic"]
        used_evidence_ids = [
            str(reading.get("evidence_id"))
            for reading in day_readings
            if str(reading.get("evidence_id") or "").strip()
        ]
        per_date_lows.append(
            {
                "date": reading_date,
                "used_evidence_ids": used_evidence_ids,
                "dos": reading_date,
                "lowest_systolic": lowest_systolic,
                "lowest_diastolic": lowest_diastolic,
                "conclusion_reading": f"{lowest_systolic}/{lowest_diastolic}",
                "evidence_readings": [
                    {
                        "label": str(index),
                        "evidence_id": reading.get("evidence_id"),
                        "reading": f"{reading.get('systolic')}/{reading.get('diastolic')}",
                        "date": reading_date,
                        "encounter_type": reading.get("encounter_type"),
                        "snippet": reading.get("snippet") or "",
                        "encounter_snippet": reading.get("encounter_snippet") or "",
                        "date_snippet": reading.get("date_snippet") or "",
                    }
                    for index, reading in enumerate(day_readings, start=1)
                    if isinstance(reading.get("systolic"), (int, float))
                    and isinstance(reading.get("diastolic"), (int, float))
                ],
                "encounter_type": systolic_reading.get("encounter_type") or diastolic_reading.get("encounter_type"),
                "snippet": systolic_reading.get("snippet") or diastolic_reading.get("snippet") or "",
                "encounter_snippet": systolic_reading.get("encounter_snippet") or diastolic_reading.get("encounter_snippet") or "",
                "date_snippet": reading_date,
            }
        )

    selected_observation = None
    pass_flag = False
    if per_date_lows:
        selected_observation = sorted(per_date_lows, key=lambda item: item["date"], reverse=True)[0]
        pass_flag = (
            selected_observation["lowest_systolic"] < systolic_target
            and selected_observation["lowest_diastolic"] < diastolic_target
        )
    else:
        reason_codes.append("NO_VALID_BP_AFTER_EXCLUSION")

    if not pass_flag and per_date_lows:
        reason_codes.append("BP_ABOVE_TARGET")
    used_evidence_ids = selected_observation.get("used_evidence_ids", []) if isinstance(selected_observation, dict) else []

    evidence_payload = {
        "measure_code": measure_code,
        "selected_observation": selected_observation,
        "used_evidence_ids": used_evidence_ids,
        "reason_codes": reason_codes,
        "rule_result": {
            "target": f"systolic < {systolic_target} and diastolic < {diastolic_target}",
            "used_evidence_ids": used_evidence_ids,
            "allowed_encounter_types": sorted(BP_ALLOWED_ENCOUNTER_TYPES),
            "bp_candidates_all": all_bp,
            "bp_candidates_kept": kept_bp,
            "bp_candidates_excluded": excluded_bp,
            "per_date_lows": per_date_lows,
            "selected_pass_flag": pass_flag,
        },
        "is_confirmed": False,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }
    return pass_flag, evidence_payload
