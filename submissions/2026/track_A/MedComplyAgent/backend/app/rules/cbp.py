from typing import Any

from app.rules.blood_pressure import evaluate_bp_measure

CBP_SYSTOLIC_TARGET = 140
CBP_DIASTOLIC_TARGET = 90


def evaluate_cbp(payload: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    return evaluate_bp_measure(payload, "CBP", CBP_SYSTOLIC_TARGET, CBP_DIASTOLIC_TARGET)
