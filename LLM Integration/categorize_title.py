import pandas as pd
import time
import json
import sys
from pathlib import Path

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

from open_router_client import ask_open_router
LISTINGS_CSV = BASE_DIR / 'listings.csv'
OUTPUT_SAMPLE = BASE_DIR / 'categorized_listings_sample.csv'

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


for idx, row in df.head(20).iterrows():
    title = row['name']
    prompt = gen_prompt(title)
    try:
        result = ask_open_router(prompt)
    except RuntimeError as exc:
        _handle_open_router_failure(exc)
    except ValueError as exc:
        print("Received an invalid JSON payload from OpenRouter:")
        print(str(exc))
        sys.exit(1)

    # Update DataFrame columns with LLM outputs for this row
    if "district" in result:
        df.at[idx, 'district_present'] = result["district"]["present"]
        df.at[idx, 'district_value'] = result["district"]["value"]
    if "bedrooms" in result:
        df.at[idx, 'bedrooms_present'] = result["bedrooms"]["present"]
        df.at[idx, 'bedrooms_value'] = result["bedrooms"]["value"]
    if "size" in result:
        df.at[idx, 'size_present'] = result["size"]["present"]
        df.at[idx, 'size_value'] = result["size"]["value"]
    if "transportation_proximity" in result:
        df.at[idx, 'transportation_proximity_present'] = result["transportation_proximity"]["present"]
        df.at[idx, 'transportation_proximity_value'] = result["transportation_proximity"]["value"]
    if "attraction_proximity" in result:
        df.at[idx, 'attraction_proximity_present'] = result["attraction_proximity"]["present"]
        df.at[idx, 'attraction_proximity_value'] = result["attraction_proximity"]["value"]
    if "view" in result:
        df.at[idx, 'view_present'] = result["view"]["present"]
        df.at[idx, 'view_value'] = result["view"]["value"]


    time.sleep(10)


# Print the first 10 rows, showing the 'name' (title) and updated columns
df.loc[:, ['name'] + new_columns].head(10).to_csv(OUTPUT_SAMPLE, index=True)
