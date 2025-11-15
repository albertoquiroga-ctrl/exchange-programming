from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from open_router_client import ask_open_router

BASE_DIR = Path(__file__).resolve().parent
LISTINGS_CSV = BASE_DIR / "listings.csv"
OUTPUT_SAMPLE = BASE_DIR / "categorized_listings_sample.csv"
DEFAULT_SAMPLE_SIZE = 20
RATE_LIMIT_DELAY_SECONDS = 10

FIELD_DEFINITIONS = [
    ("district", "district_present", "district_value"),
    ("bedrooms", "bedrooms_present", "bedrooms_value"),
    ("size", "size_present", "size_value"),
    ("transportation_proximity", "transportation_proximity_present", "transportation_proximity_value"),
    ("attraction_proximity", "attraction_proximity_present", "attraction_proximity_value"),
    ("view", "view_present", "view_value"),
]


def gen_prompt(title: str) -> str:
    return f"""
You are analyzing an Airbnb listing title in Hong Kong.

Title: {title}

Your task:
Determine whether the title explicitly contains each of the following elements, and extract the exact phrase from the title when possible:

1. District
2. Number of bedrooms
3. Size of the room (e.g. in ft^2, m^2, or descriptive size such as "studio")
4. How close it is to transportation (e.g. MTR, bus, tram, airport)
5. How close it is to major attractions (e.g. Disneyland, Harbour, Tsim Sha Tsui, Central)
6. Whether a view is advertised (e.g. harbour view, city view)

Important:
- Do **not** guess or infer information that is not clearly stated in the title.
- If an element is not present, set its value to `null`.
- Do not provide explanations.
- Translate all output to English.

Output your answer **only** in valid JSON with this exact structure:

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
"""


def _initialize_columns(frame: pd.DataFrame) -> list[str]:
    new_columns: list[str] = []
    for _, present_col, value_col in FIELD_DEFINITIONS:
        frame[present_col] = None
        frame[value_col] = None
        new_columns.extend([present_col, value_col])
    return new_columns


def _apply_result(frame: pd.DataFrame, idx: str, result: dict) -> None:
    for field, present_col, value_col in FIELD_DEFINITIONS:
        section = result.get(field)
        if isinstance(section, dict):
            frame.at[idx, present_col] = section.get("present")
            frame.at[idx, value_col] = section.get("value")


def annotate_titles(frame: pd.DataFrame, delay_seconds: float) -> None:
    for idx, row in frame.iterrows():
        title = row.get("name")
        if not isinstance(title, str) or not title.strip():
            continue

        prompt = gen_prompt(title)
        try:
            result = ask_open_router(prompt)
        except Exception as exc:  # pragma: no cover - depends on network/model
            print(f"Error while categorizing '{title}': {exc}")
            continue

        _apply_result(frame, idx, result)
        time.sleep(delay_seconds)


def main(sample_size: int = DEFAULT_SAMPLE_SIZE, delay_seconds: float = RATE_LIMIT_DELAY_SECONDS) -> None:
    if not LISTINGS_CSV.exists():
        print(f"Listings file not found: {LISTINGS_CSV}")
        return

    df = pd.read_csv(LISTINGS_CSV, header=0, dtype={"id": str}, index_col="id")
    subset = df.head(sample_size).copy()
    new_columns = _initialize_columns(subset)

    annotate_titles(subset, delay_seconds)

    output_columns = ["name"] + new_columns
    subset.loc[:, output_columns].to_csv(OUTPUT_SAMPLE, index=True)
    print(f"Wrote categorized sample to {OUTPUT_SAMPLE}")


if __name__ == "__main__":
    main()
