from typing import Any

from app.rules.blood_pressure import evaluate_bp_measure

BPD_SYSTOLIC_TARGET = 140
BPD_DIASTOLIC_TARGET = 90


def evaluate_bpd(payload: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    return evaluate_bp_measure(payload, "BPD", BPD_SYSTOLIC_TARGET, BPD_DIASTOLIC_TARGET)
