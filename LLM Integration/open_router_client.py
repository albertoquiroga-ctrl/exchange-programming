from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

DEFAULT_MODEL = "deepseek/deepseek-r1-0528-qwen3-8b:free"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


def _require_env_var(name: str) -> str:
    """Return the value of `name` or raise a helpful error if unset."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable '{name}' is missing. "
            "Double-check your .env file before running the scripts."
        )
    return value


OPEN_ROUTER_API_KEY = _require_env_var("OPEN_ROUTER_API_KEY")
MODEL = os.getenv("MODEL") or DEFAULT_MODEL
API_BASE_URL = os.getenv("OPEN_ROUTER_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _extract_first_balanced_json_object(text: str) -> str | None:
    """
    Find the first balanced {...} JSON object substring.
    Returns the substring if found, else None.
    """
    if not text:
        return None
    n = len(text)
    i = 0
    while i < n:
        if text[i] == "{":
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                ch = text[j]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                j += 1
            if depth == 0:
                return text[i:j]
        i += 1
    return None


def _parse_json_from_text(text: str) -> dict:
    """
    Attempt to parse a dict from possibly noisy LLM text output.
    - Prefer fenced ```json blocks.
    - Try direct parse.
    - Try first balanced {...} block.
    Raise ValueError if parsing fails or the parsed root is not a dict.
    """
    if text is None:
        raise ValueError("Empty response from model.")
    raw = text.strip()

    # 1) Prefer fenced code blocks labeled json; try all code fences if multiple
    fence_pattern = re.compile(r"```(?:json|JSON)?\s*(.*?)```", re.DOTALL)
    fenced_blocks = [m.group(1).strip() for m in fence_pattern.finditer(raw)]
    for block in fenced_blocks:
        try:
            obj = json.loads(block)
            if isinstance(obj, dict):
                return obj
            raise ValueError(f"Parsed JSON is not an object (got {type(obj).__name__}).")
        except Exception:
            # try next block
            pass

    # 2) Try direct parse of the full text (may work if it's plain JSON)
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
        raise ValueError(f"Parsed JSON is not an object (got {type(obj).__name__}).")
    except Exception:
        pass

    # 3) Try first balanced {...} block anywhere in the text
    candidate = _extract_first_balanced_json_object(raw)
    if candidate:
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
            raise ValueError(f"Parsed JSON is not an object (got {type(obj).__name__}).")
        except Exception:
            pass

    # If we reach here, parsing failed
    preview = raw if len(raw) < 1000 else raw[:1000] + "...(truncated)"
    raise ValueError(f"Failed to parse JSON object from response. Preview:\n{preview}")


def _post_chat_completion(
    messages: Iterable[Mapping[str, str]] | Sequence[Mapping[str, str]],
    *,
    model: str,
    api_key: str,
    extra_body: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Low-level helper to send a chat completion request to OpenRouter."""
    payload: Dict[str, Any] = {"model": model, "messages": list(messages)}
    if extra_body:
        payload.update(extra_body)
    response = requests.post(
        f"{API_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(
            f"OpenRouter API error {response.status_code}: {response.text.strip()}"
        )
    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("OpenRouter returned a non-JSON response.") from exc


def chat_completion_text(
    messages: Iterable[Mapping[str, str]],
    model: str | None = None,
    api_key: str | None = None,
    extra_body: Mapping[str, Any] | None = None,
) -> str:
    """Send an arbitrary message list and return the assistant's reply text."""
    selected_model = model or MODEL
    if not selected_model:
        raise RuntimeError(
            "No OpenRouter model configured. Set MODEL in your .env or pass `model=`."
        )
    completion = _post_chat_completion(
        messages,
        model=selected_model,
        api_key=api_key or OPEN_ROUTER_API_KEY,
        extra_body=extra_body,
    )
    try:
        return completion["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("OpenRouter response missing assistant content.") from exc


def ask_open_router(
    prompt: str,
    model: str | None = None,
    api_key: str | None = None,
) -> Dict[str, Any]:
    """Send a prompt to OpenRouter and return the parsed JSON response."""
    response_text = chat_completion_text(
        [{"role": "user", "content": prompt}],
        model=model,
        api_key=api_key,
    )
    # Always convert to a Python dict or raise a clear error
    return _parse_json_from_text(response_text)
