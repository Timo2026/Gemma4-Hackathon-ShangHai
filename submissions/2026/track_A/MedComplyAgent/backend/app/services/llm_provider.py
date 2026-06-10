import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings


class LLMProviderError(Exception):
    pass


@dataclass(frozen=True)
class ChatJsonRequest:
    system_prompt: str
    user_prompt: str


@dataclass(frozen=True)
class ChatCompletionRequest:
    messages: list[dict[str, Any]]
    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, Any] | None = None
    response_format: dict[str, Any] | None = None
    temperature: float = 0
    max_tokens: int | None = None


def chat_completion(request: ChatCompletionRequest) -> dict[str, Any]:
    if not settings.llm_api_key:
        raise LLMProviderError("Missing llm_api_key")

    request_body = {
        "model": settings.llm_model_name,
        "messages": request.messages,
        "temperature": request.temperature,
    }
    if request.tools is not None:
        request_body["tools"] = request.tools
    if request.tool_choice is not None:
        request_body["tool_choice"] = request.tool_choice
    if request.response_format is not None:
        request_body["response_format"] = request.response_format
    if request.max_tokens is not None:
        request_body["max_tokens"] = request.max_tokens

    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=request_body)
            response.raise_for_status()
    except httpx.HTTPError as error:
        raise LLMProviderError(f"LLM request failed: {error}") from error

    try:
        data = response.json()
        message = data["choices"][0]["message"]
    except (ValueError, KeyError, TypeError, IndexError) as error:
        raise LLMProviderError(f"Invalid LLM response payload: {error}") from error

    if not isinstance(message, dict):
        raise LLMProviderError("LLM response message is not an object")

    return message


def chat_json(request: ChatJsonRequest) -> dict[str, Any]:
    message = chat_completion(
        ChatCompletionRequest(
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            response_format={"type": "json_object"},
        )
    )

    try:
        content = message["content"]
        parsed = json.loads(content)
    except (ValueError, KeyError, TypeError) as error:
        raise LLMProviderError(f"Invalid LLM response payload: {error}") from error

    if not isinstance(parsed, dict):
        raise LLMProviderError("LLM response is not a JSON object")

    return parsed
