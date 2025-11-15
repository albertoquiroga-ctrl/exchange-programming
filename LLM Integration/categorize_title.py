from __future__ import annotations

import pandas as pd
import time
import json
import sys
from pathlib import Path
from typing import Mapping, NotRequired, TypedDict

from dotenv import load_dotenv

def gen_prompt(title):
    return f'''
        You are analyzing an Airbnb listing title in Hong Kong.

        Title: {title}

        Your task:
        Determine whether the title explicitly contains each of the following elements, and extract the exact phrase from the title when possible:

        1. District
        2. Number of bedrooms
        3. Size of the room (e.g. in ft², m², or descriptive size such as "studio")
        4. How close it is to transportation (e.g. MTR, bus, tram, airport)
        5. How close it is to major attractions (e.g. Disneyland, Harbour, Tsim Sha Tsui, Central)

        Important:
        - Do **not** guess or infer information that is not clearly stated in the title.
        - If an element is not present, set its value to `null`.
        - No need to give explanation
        - Translate all output in english

        Output your answer **only** in valid JSON with this exact structure (all curly braces are escaped with double braces to indicate literal braces):

        {{
            "district": {{
                "present": boolean,
                "value": string | null
            }},
            "bedrooms": {{
                "present": boolean,
                "value": string | null
            }},
            "size": {{
                "present": boolean,
                "value": string | null
            }},
            "transportation_proximity": {{
                "present": boolean,
                "value": string | null
            }},
            "attraction_proximity": {{
                "present": boolean,
                "value": string | null
            }},
            "view": {{
                "present": boolean,
                "value": string | null
            }}
        }}
    '''

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)


class FieldCategorization(TypedDict, total=False):
    present: bool
    value: str | None


class CategorizationResponse(TypedDict, total=False):
    district: NotRequired[FieldCategorization]
    bedrooms: NotRequired[FieldCategorization]
    size: NotRequired[FieldCategorization]
    transportation_proximity: NotRequired[FieldCategorization]
    attraction_proximity: NotRequired[FieldCategorization]
    view: NotRequired[FieldCategorization]


def _extract_field_values(
    field_result: Mapping[str, object] | None,
) -> tuple[bool | None, str | None]:
    """Return normalized present/value pairs for a single field."""

    if not isinstance(field_result, Mapping):
        return None, None

    present_value = field_result.get("present")
    normalized_present = present_value if isinstance(present_value, bool) else None

    value_entry = field_result.get("value")
    normalized_value = value_entry if isinstance(value_entry, str) or value_entry is None else None

    return normalized_present, normalized_value


from open_router_client import ask_open_router
LISTINGS_CSV = BASE_DIR / 'listings.csv'
OUTPUT_SAMPLE = BASE_DIR / 'categorized_listings_sample.csv'
MAX_RATE_LIMIT_RETRIES = 4
RATE_LIMIT_BACKOFF_SECONDS = 20

df = pd.read_csv(LISTINGS_CSV, header=0, dtype={'id': str}, index_col='id')

# Prepare new columns for each category value
new_columns = [
    'district_present', 'district_value',
    'bedrooms_present', 'bedrooms_value',
    'size_present', 'size_value',
    'transportation_proximity_present', 'transportation_proximity_value',
    'attraction_proximity_present', 'attraction_proximity_value',
    'view_present', 'view_value'
]
for col in new_columns:
    df[col] = None

CATEGORIZATION_FIELDS = {
    "district": ("district_present", "district_value"),
    "bedrooms": ("bedrooms_present", "bedrooms_value"),
    "size": ("size_present", "size_value"),
    "transportation_proximity": (
        "transportation_proximity_present",
        "transportation_proximity_value",
    ),
    "attraction_proximity": (
        "attraction_proximity_present",
        "attraction_proximity_value",
    ),
    "view": ("view_present", "view_value"),
}


def _handle_open_router_failure(error: Exception) -> None:
    """Provide actionable feedback when the OpenRouter request fails."""
    message = str(error)
    print("Failed to retrieve categorization from OpenRouter.")
    if "401" in message or "User not found" in message:
        print(
            "OpenRouter responded with 401 Unauthorized. "
            "Verify the OPEN_ROUTER_API_KEY stored in "
            f"{BASE_DIR / '.env'} and ensure the key is active."
        )
    else:
        print(message)
    sys.exit(1)


def _is_rate_limit_error(message: str) -> bool:
    lowered = message.lower()
    return "429" in lowered or "rate limit" in lowered


def _fetch_categorization(prompt: str) -> CategorizationResponse:
    """Call OpenRouter and retry automatically when it is temporarily rate-limited."""
    attempts = MAX_RATE_LIMIT_RETRIES + 1  # initial try + retries
    for attempt in range(1, attempts + 1):
        try:
            return ask_open_router(prompt)
        except RuntimeError as exc:
            message = str(exc)
            if _is_rate_limit_error(message):
                if attempt == attempts:
                    break
                wait_seconds = RATE_LIMIT_BACKOFF_SECONDS * attempt
                print(
                    "OpenRouter rate limit encountered. "
                    f"Attempt {attempt}/{attempts}. "
                    f"Retrying in {wait_seconds} seconds..."
                )
                time.sleep(wait_seconds)
                continue
            _handle_open_router_failure(exc)
        except ValueError as exc:
            print("Received an invalid JSON payload from OpenRouter:")
            print(str(exc))
            sys.exit(1)

    print(
        "OpenRouter kept returning rate limit responses. "
        "Please try again later or configure a different MODEL in .env."
    )
    sys.exit(1)


for idx, row in df.head(20).iterrows():
    title = row['name']
    prompt = gen_prompt(title)
    result = _fetch_categorization(prompt)

    if not isinstance(result, dict):
        print(
            f"Skipping listing {idx} because the model returned "
            f"{type(result).__name__} instead of an object: {result!r}"
        )
        continue

    # Update DataFrame columns with LLM outputs for this row
    for field, (present_col, value_col) in CATEGORIZATION_FIELDS.items():
        field_result = result.get(field)
        normalized_present, normalized_value = _extract_field_values(field_result)

        # Guard against malformed responses so we can keep processing rows.
        df.at[idx, present_col] = normalized_present
        df.at[idx, value_col] = normalized_value


    time.sleep(10)


# Print the first 10 rows, showing the 'name' (title) and updated columns
df.loc[:, ['name'] + new_columns].head(10).to_csv(OUTPUT_SAMPLE, index=True)
