from openai import OpenAI
import json
import re
from dotenv import load_dotenv
import os

load_dotenv()
OPEN_ROUTER_API_KEY = os.getenv("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")
MODEL = os.getenv("MODEL")


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


def ask_open_router(prompt, model=MODEL, api_key=OPEN_ROUTER_API_KEY):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    completion = client.chat.completions.create(
        extra_body={},
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    response = completion.choices[0].message.content or ""
    # Always convert to a Python dict or raise a clear error
    return _parse_json_from_text(response)
