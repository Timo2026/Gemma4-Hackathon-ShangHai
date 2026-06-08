from typing import Any


GEMMA_AGENT_SYSTEM_PROMPT = """
You are MedComply Agent, a clinical evidence review agent for HEDIS chart review.
Use tools to collect chart evidence step by step. Do not decide whether a HEDIS gap is Closed, Open, or Needs Review.
The backend deterministic rule engine will make the final compliance decision.

Workflow:
1. Always call get_encounter_info first.
2. For CBP or BPD, call get_bp_readings even when the encounter is ED or inpatient. ED/inpatient evidence is still needed for reviewer audit and NSSD draft autofill; the backend rule engine will exclude it later.
3. If the chart has no BP evidence after get_bp_readings, then stop and summarize what is missing.
4. For GSD, call get_lab_values after encounter review.
5. When the necessary evidence has been collected, stop calling tools and summarize the evidence collected.

Efficiency:
- When possible, return all required tool calls in one assistant response.
- For CBP/BPD, you may call get_encounter_info and get_bp_readings in the same response.
- For GSD, you may call get_encounter_info and get_lab_values in the same response.

Never apply HEDIS thresholds. Never output Closed/Open/Needs Review.
""".strip()


GEMMA_AGENT_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_encounter_info",
            "description": (
                "Collect encounter type, date of service, provider, patient name, and DOB. "
                "Call this FIRST. If the encounter is ED or inpatient for a BP measure, still call "
                "get_bp_readings afterward so the reviewer can audit the BP evidence and NSSD draft fields."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "measure": {
                        "type": "string",
                        "description": "The HEDIS measure code being reviewed, such as CBP, BPD, or GSD.",
                    }
                },
                "required": ["measure"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bp_readings",
            "description": (
                "Collect blood pressure evidence for CBP or BPD after encounter review. "
                "Call this even for ED or inpatient encounters; those readings are retained for audit "
                "and reviewer form autofill, then excluded by the backend rule engine."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "measure": {
                        "type": "string",
                        "description": "The HEDIS BP measure code, CBP or BPD.",
                    },
                    "date_range": {
                        "type": "string",
                        "description": "The chart period to review, usually current_measurement_year.",
                    },
                },
                "required": ["measure"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_lab_values",
            "description": "Collect HbA1c lab evidence for GSD. Do not extract glucose as HbA1c.",
            "parameters": {
                "type": "object",
                "properties": {
                    "measure": {
                        "type": "string",
                        "description": "The HEDIS measure code, expected to be GSD.",
                    },
                    "test_name": {
                        "type": "string",
                        "description": "The lab test to collect. Use HbA1c for GSD.",
                    },
                    "date_range": {
                        "type": "string",
                        "description": "The chart period to review, usually current_measurement_year.",
                    },
                },
                "required": ["measure", "test_name"],
            },
        },
    },
]
