"""
Class 11 assignment: simple script to talk to OpenRouter.

Usage examples:
    python Class_11_Open_Router.py "Tell me a fun fact about llamas."
    python Class_11_Open_Router.py
        (prompts for input if no argument is provided)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

API_BASE_URL = os.getenv("OPEN_ROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
MODEL = os.getenv("MODEL", "deepseek/deepseek-r1-0528-qwen3-8b:free")
APP_TITLE = os.getenv("OPEN_ROUTER_APP_TITLE", "Class 11 Assignment")
HTTP_REFERER = os.getenv("OPEN_ROUTER_HTTP_REFERER", "https://exchange-programming.local")


def _require_env(value: str | None, name: str) -> str:
    if value:
        return value
    raise RuntimeError(
        f"Environment variable '{name}' is missing. "
        "Make sure your LLM Integration/.env file is configured."
    )


def ask_open_router(prompt: str) -> str:
    """Send a prompt to OpenRouter and return the assistant's reply text."""
    payload = {
        "model": _require_env(MODEL, "MODEL"),
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "Authorization": f"Bearer {_require_env(API_KEY, 'OPEN_ROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "X-Title": APP_TITLE,
    }
    if HTTP_REFERER:
        headers["HTTP-Referer"] = HTTP_REFERER

    response = requests.post(
        f"{API_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    try:
        return (data["choices"][0]["message"]["content"] or "").strip()
    except (KeyError, IndexError, TypeError) as exc:  # pragma: no cover - defensive
        raise RuntimeError("OpenRouter response missing assistant content.") from exc


def main(prompt_arg: str | None = None) -> None:
    prompt = prompt_arg or input("Enter a prompt for OpenRouter: ")
    try:
        reply = ask_open_router(prompt)
    except Exception as exc:  # noqa: BLE001 - keep script simple for assignment
        print(f"Failed to reach OpenRouter: {exc}")
        return
    print("\n=== OpenRouter replied ===")
    print(reply)


if __name__ == "__main__":
    arg_prompt = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""
    main(arg_prompt or None)
