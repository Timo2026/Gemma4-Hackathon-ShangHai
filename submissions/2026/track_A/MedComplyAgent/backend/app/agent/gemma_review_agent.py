import json
import logging
from typing import Any

from app.agent.schemas import GEMMA_AGENT_SYSTEM_PROMPT, GEMMA_AGENT_TOOLS
from app.agent.tools import AgentToolError, execute_agent_tool, payload_from_memory
from app.core.config import settings
from app.services.llm_provider import ChatCompletionRequest, LLMProviderError, chat_completion

logger = logging.getLogger("uvicorn.error").getChild("app.agent.gemma_review_agent")
logger.setLevel(logging.INFO)


class GemmaAgentError(Exception):
    pass


def _parse_tool_arguments(raw_arguments: Any) -> dict[str, Any]:
    if isinstance(raw_arguments, dict):
        return raw_arguments
    if isinstance(raw_arguments, str) and raw_arguments.strip():
        try:
            parsed = json.loads(raw_arguments)
        except ValueError as error:
            raise GemmaAgentError(f"Invalid tool arguments JSON: {error}") from error
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _tool_call_parts(tool_call: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    function = tool_call.get("function") if isinstance(tool_call.get("function"), dict) else {}
    name = str(function.get("name") or "").strip()
    if not name:
        raise GemmaAgentError("Tool call missing function name")
    tool_call_id = str(tool_call.get("id") or name)
    arguments = _parse_tool_arguments(function.get("arguments"))
    return tool_call_id, name, arguments


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _tool_names() -> str:
    names: list[str] = []
    for tool in GEMMA_AGENT_TOOLS:
        function = tool.get("function") if isinstance(tool.get("function"), dict) else {}
        name = str(function.get("name") or "").strip()
        if name:
            names.append(name)
    return ",".join(names)


def _tool_call_log_items(tool_calls: list[Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for tool_call in tool_calls:
        if not isinstance(tool_call, dict):
            continue
        try:
            tool_call_id, name, arguments = _tool_call_parts(tool_call)
        except GemmaAgentError:
            continue
        items.append({"id": tool_call_id, "name": name, "arguments": arguments})
    return items


def _result_summary(result: dict[str, Any]) -> str:
    if "encounter_type" in result:
        eligible = result.get("eligible")
        suffix = "eligible" if eligible is True else "excluded" if eligible is False else "unknown eligibility"
        return f"Encounter {result.get('encounter_type') or 'Unknown'} on {result.get('date_of_service') or 'unknown date'} ({suffix})"
    if "blood_pressure_readings" in result:
        count = len(result.get("blood_pressure_readings") if isinstance(result.get("blood_pressure_readings"), list) else [])
        return f"Collected {count} blood pressure reading(s)"
    if "a1c_readings" in result:
        count = len(result.get("a1c_readings") if isinstance(result.get("a1c_readings"), list) else [])
        return f"Collected {count} HbA1c reading(s)"
    if "error" in result:
        return str(result["error"])
    return "Tool completed"


def _evidence_ids_from_result(result: dict[str, Any]) -> list[str]:
    evidence_ids: list[str] = []
    for key in ("blood_pressure_readings", "a1c_readings", "nssd_candidates"):
        items = result.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            evidence_id = str(item.get("evidence_id") or "").strip()
            if evidence_id and evidence_id not in evidence_ids:
                evidence_ids.append(evidence_id)
    return evidence_ids


def _memory_summary(memory: dict[str, Any]) -> str:
    parts: list[str] = []
    encounter = memory.get("encounter_info") if isinstance(memory.get("encounter_info"), dict) else None
    if encounter:
        parts.append(
            f"encounter={encounter.get('encounter_type', 'Unknown')} eligible={encounter.get('eligible', 'unknown')}"
        )
    bp_count = len(memory.get("blood_pressure_readings") if isinstance(memory.get("blood_pressure_readings"), list) else [])
    if bp_count:
        parts.append(f"bp_readings={bp_count}")
    a1c_count = len(memory.get("a1c_readings") if isinstance(memory.get("a1c_readings"), list) else [])
    if a1c_count:
        parts.append(f"a1c_readings={a1c_count}")
    return "; ".join(parts) if parts else "No evidence collected yet."


def _update_memory_from_result(memory: dict[str, Any], name: str, result: dict[str, Any]) -> None:
    if name == "get_encounter_info":
        memory["encounter_info"] = result
    if "blood_pressure_readings" in result and isinstance(result["blood_pressure_readings"], list):
        memory["blood_pressure_readings"] = result["blood_pressure_readings"]
    if "a1c_readings" in result and isinstance(result["a1c_readings"], list):
        memory["a1c_readings"] = result["a1c_readings"]


def _merge_tool_results(tool_results: list[dict[str, Any]], measure_code: str) -> dict[str, Any]:
    encounter_info: dict[str, Any] = {}
    bp_readings: list[dict[str, Any]] = []
    a1c_readings: list[dict[str, Any]] = []

    for result in tool_results:
        if "date_of_service" in result or "encounter_type" in result:
            encounter_info = result
        bp_readings.extend(item for item in result.get("blood_pressure_readings", []) if isinstance(item, dict))
        a1c_readings.extend(item for item in result.get("a1c_readings", []) if isinstance(item, dict))

    nssd_candidates: list[dict[str, Any]] = []
    for reading in bp_readings:
        nssd_candidates.append(
            {
                "patient_name": encounter_info.get("patient_name", ""),
                "dob": encounter_info.get("dob", ""),
                "result_value": f"{reading.get('systolic')}/{reading.get('diastolic')}",
                "dos": reading.get("date") or encounter_info.get("date_of_service", ""),
                "rendering_provider": encounter_info.get("provider", ""),
                "place_of_service": reading.get("encounter_type") or encounter_info.get("encounter_type", ""),
                "encounter_type": reading.get("encounter_type") or encounter_info.get("encounter_type", ""),
                "measure_hint": measure_code,
                "snippet": reading.get("snippet", ""),
                "encounter_snippet": reading.get("encounter_snippet") or encounter_info.get("source_text", ""),
                "date_snippet": reading.get("date_snippet") or encounter_info.get("date_of_service", ""),
            }
        )
    for lab in a1c_readings:
        nssd_candidates.append(
            {
                "patient_name": encounter_info.get("patient_name", ""),
                "dob": encounter_info.get("dob", ""),
                "result_value": f"{lab.get('value')}%",
                "dos": lab.get("date") or encounter_info.get("date_of_service", ""),
                "rendering_provider": encounter_info.get("provider", ""),
                "place_of_service": lab.get("encounter_type") or encounter_info.get("encounter_type", ""),
                "encounter_type": lab.get("encounter_type") or encounter_info.get("encounter_type", ""),
                "measure_hint": measure_code,
                "snippet": lab.get("snippet", ""),
                "encounter_snippet": lab.get("encounter_snippet") or encounter_info.get("source_text", ""),
                "date_snippet": lab.get("date_snippet") or encounter_info.get("date_of_service", ""),
            }
        )

    return {
        "blood_pressure_readings": bp_readings,
        "a1c_readings": a1c_readings,
        "nssd_candidates": nssd_candidates,
    }


def _build_agent_trace(tool_steps: list[dict[str, Any]], final_content: str | None) -> dict[str, Any]:
    return {
        "schema_version": "agent_trace.v1",
        "steps": tool_steps,
        "final_summary": final_content or "",
    }


def _tool_actions(tool_steps: list[dict[str, Any]]) -> set[str]:
    return {
        str(step.get("action"))
        for step in tool_steps
        if isinstance(step, dict) and step.get("status") == "completed"
    }


def _evidence_collection_complete(measure_code: str, tool_steps: list[dict[str, Any]]) -> bool:
    actions = _tool_actions(tool_steps)
    if "get_encounter_info" not in actions:
        return False
    if measure_code in {"CBP", "BPD"}:
        return "get_bp_readings" in actions
    if measure_code == "GSD":
        return "get_lab_values" in actions
    return False


def _local_final_summary(measure_code: str, memory: dict[str, Any]) -> str:
    if measure_code in {"CBP", "BPD"}:
        bp_count = len(memory.get("blood_pressure_readings") if isinstance(memory.get("blood_pressure_readings"), list) else [])
        return f"Evidence collection complete for {measure_code}: collected encounter context and {bp_count} blood pressure reading(s)."
    if measure_code == "GSD":
        a1c_count = len(memory.get("a1c_readings") if isinstance(memory.get("a1c_readings"), list) else [])
        return f"Evidence collection complete for GSD: collected encounter context and {a1c_count} HbA1c reading(s)."
    return f"Evidence collection complete for {measure_code}."


def _record_tool_step(
    tool_steps: list[dict[str, Any]],
    name: str,
    arguments: dict[str, Any],
    result: dict[str, Any],
    memory: dict[str, Any],
    tool_call_id: str,
    actor: str,
) -> None:
    step_summary = _result_summary(result)
    memory_snapshot = _memory_summary(memory)
    tool_steps.append(
        {
            "step_id": f"step-{len(tool_steps) + 1}",
            "actor": actor,
            "action": name,
            "status": "completed",
            "tool_call_id": tool_call_id,
            "arguments": arguments,
            "summary": step_summary,
            "output_evidence_ids": _evidence_ids_from_result(result),
            "memory": memory_snapshot,
        }
    )
    logger.info(
        "agent step=%s actor=%s action=%s memory=%s summary=%s arguments=%s",
        len(tool_steps),
        actor,
        name,
        memory_snapshot,
        step_summary,
        arguments,
    )


def run_gemma_review_agent(document_text: str, measure_code: str, max_steps: int = 5) -> dict[str, Any]:
    normalized_measure = measure_code.upper()
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": GEMMA_AGENT_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Review the {normalized_measure} measure. The chart text is available to tools. "
                "Start by calling get_encounter_info."
            ),
        },
    ]
    memory: dict[str, Any] = {}
    tool_results: list[dict[str, Any]] = []
    tool_steps: list[dict[str, Any]] = []
    final_content: str | None = None

    for step_number in range(1, max_steps + 1):
        logger.info(
            "agent loop measure=%s planner_step=%s/%s",
            normalized_measure,
            step_number,
            max_steps,
        )
        logger.info(
            "agent llm_request measure=%s planner_step=%s model=%s tool_choice=auto tools=%s",
            normalized_measure,
            step_number,
            settings.llm_model_name,
            _tool_names(),
        )
        try:
            message = chat_completion(
                ChatCompletionRequest(
                    messages=messages,
                    tools=GEMMA_AGENT_TOOLS,
                    tool_choice="auto",
                    max_tokens=400,
                )
            )
        except LLMProviderError as error:
            raise GemmaAgentError(str(error)) from error

        messages.append(message)
        tool_calls = message.get("tool_calls") if isinstance(message.get("tool_calls"), list) else []
        logger.info(
            "agent llm_tool_calls measure=%s planner_step=%s count=%s calls=%s",
            normalized_measure,
            step_number,
            len(tool_calls),
            _json_dumps(_tool_call_log_items(tool_calls)),
        )
        if not tool_calls:
            final_content = message.get("content") if isinstance(message.get("content"), str) else None
            logger.info(
                "agent stop measure=%s planner_step=%s tool_steps=%s final_summary=%s",
                normalized_measure,
                step_number,
                len(tool_steps),
                (final_content or "")[:200],
            )
            break

        for tool_call in tool_calls:
            if not isinstance(tool_call, dict):
                continue
            tool_call_id, name, arguments = _tool_call_parts(tool_call)
            try:
                result = execute_agent_tool(name, arguments, document_text, normalized_measure, memory)
            except AgentToolError as error:
                raise GemmaAgentError(str(error)) from error

            _update_memory_from_result(memory, name, result)
            tool_results.append(result)
            _record_tool_step(tool_steps, name, arguments, result, memory, tool_call_id, "gemma")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": name,
                    "content": _json_dumps(result),
                }
            )

        if _evidence_collection_complete(normalized_measure, tool_steps):
            final_content = _local_final_summary(normalized_measure, memory)
            logger.info(
                "agent local_stop measure=%s planner_step=%s tool_steps=%s final_summary=%s",
                normalized_measure,
                step_number,
                len(tool_steps),
                final_content,
            )
            break

        messages.append({"role": "system", "content": f"[Memory] Evidence so far: {_memory_summary(memory)}"})
    else:
        raise GemmaAgentError(f"Gemma agent reached max_steps={max_steps} before stopping")

    if not tool_results:
        raise GemmaAgentError("Gemma did not return tool calls")

    payload = _merge_tool_results(tool_results, normalized_measure)
    fallback_payload = payload_from_memory(memory, normalized_measure)
    if not payload["blood_pressure_readings"] and fallback_payload["blood_pressure_readings"]:
        payload["blood_pressure_readings"] = fallback_payload["blood_pressure_readings"]
    if not payload["a1c_readings"] and fallback_payload["a1c_readings"]:
        payload["a1c_readings"] = fallback_payload["a1c_readings"]
    if not payload["nssd_candidates"] and fallback_payload["nssd_candidates"]:
        payload["nssd_candidates"] = fallback_payload["nssd_candidates"]
    payload["agent_trace"] = _build_agent_trace(tool_steps, final_content)
    return payload
