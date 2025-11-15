from __future__ import annotations

import os
import time
from typing import Iterable

import requests
from dotenv import load_dotenv

from open_router_client import ask_open_router

load_dotenv()

DEFAULT_USER_ID = "44196397"
DEFAULT_TWEET_COUNT = 20
RATE_LIMIT_DELAY_SECONDS = 10
RAPIDAPI_KEY_ENV = "RAPIDAPI_KEY"
RAPIDAPI_HOST = "twitter241.p.rapidapi.com"


def gen_prompt(content: str) -> str:
    return f"""
You are an expert annotator analyzing individual tweets by Elon Musk.

Tweet:
{content}

Your tasks:

1. Assign the tweet to exactly ONE of the following categories (choose the best fit):
   - "Tesla"                  - anything about Tesla, its products, stock, management, factories, etc.
   - "SpaceX"                 - rockets, Starship, Starlink, launches, satellites, etc.
   - "X"                      - X (formerly Twitter), product features, policies, moderation, company issues.
   - "xAI / Grok"             - xAI, Grok, AI model capabilities, AI safety comments tied to xAI.
   - "Other Elon Musk Company" - Neuralink, The Boring Company, SolarCity, OpenAI (historical), or other Musk ventures not covered above.
   - "US Politics"            - US government, elections, US politicians, US political parties, US public policy.
   - "Global Politics"        - non-US governments, geopolitics, wars, diplomacy, global policy issues.
   - "Cryptocurrency"         - Bitcoin, Dogecoin, other coins, crypto markets, blockchain talk.
   - "Fun or Entertainment"   - memes, jokes, casual banter, movies, games, random internet fun.
   - "Freedom of Speech"      - statements about protecting or threatening free speech.
   - "Other / General"        - anything that doesn't clearly fit into the above (e.g. personal reflections, generic tech talk, random comments).

2. Determine the sentiment of the tweet **within that category**:
   - "positive"
   - "negative"
   - "neutral"

Guidelines:
- Base your decision ONLY on the tweet content provided.
- If the tweet seems to touch multiple areas, pick the **single most central** topic.
- Consider sarcasm or jokes when inferring sentiment, but do not over-interpret beyond what is reasonable from the text.

Output **only** valid JSON in this format:

{{
  "category": "<one of the categories above>",
  "sentiment": "positive" | "negative" | "neutral",
  "reason": "<very short explanation of why you chose this category and sentiment>"
}}
"""


def _get_rapidapi_key() -> str:
    api_key = os.getenv(RAPIDAPI_KEY_ENV)
    if not api_key:
        raise RuntimeError(
            f"RapidAPI key missing. Set {RAPIDAPI_KEY_ENV} in your environment or .env file."
        )
    return api_key


def fetch_tweets(user_id: str, count: int) -> list[str]:
    url = "https://twitter241.p.rapidapi.com/user-tweets"
    headers = {
        "x-rapidapi-key": _get_rapidapi_key(),
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    params = {"user": user_id, "count": str(count)}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    instructions = data.get("result", {}).get("timeline", {}).get("instructions", [])
    entries = []
    for instruction in reversed(instructions):
        entries = instruction.get("entries") or []
        if entries:
            break

    tweets: list[str] = []
    for entry in entries:
        try:
            text = (
                entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["full_text"]
            )
            tweets.append(text)
        except KeyError:
            continue
    return tweets


def categorize_tweets(tweets: Iterable[str]) -> None:
    for content in tweets:
        prompt = gen_prompt(content)
        try:
            result = ask_open_router(prompt)
            print(content)
            print(f"LLM Response: {result}")
            print("-" * 40)
        except Exception as exc:  # pragma: no cover - depends on network/model
            print(f"Error while categorizing tweet: {exc}")

        time.sleep(RATE_LIMIT_DELAY_SECONDS)


def main() -> None:
    try:
        tweets = fetch_tweets(DEFAULT_USER_ID, DEFAULT_TWEET_COUNT)
    except Exception as exc:  # pragma: no cover - depends on external API
        print(f"Error fetching tweets: {exc}")
        return

    if not tweets:
        print("No tweets returned from API.")
        return

    categorize_tweets(tweets)


if __name__ == "__main__":
    main()
