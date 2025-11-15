from __future__ import annotations

import json
import os
import time
from pathlib import Path
from textwrap import dedent

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

from open_router_client import ask_open_router

DEFAULT_RAPIDAPI_URL = "https://twitter241.p.rapidapi.com/user-tweets"
DEFAULT_RAPIDAPI_HOST = "twitter241.p.rapidapi.com"
RAPIDAPI_URL = os.getenv("RAPIDAPI_URL", DEFAULT_RAPIDAPI_URL)
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", DEFAULT_RAPIDAPI_HOST)
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
DEFAULT_SLEEP_SECONDS = 10
DEFAULT_USER_ID = "44196397"
DEFAULT_TWEET_COUNT = 20


def _require_rapidapi_key() -> str:
    if not RAPIDAPI_KEY:
        raise RuntimeError(
            "Missing RAPIDAPI_KEY. Update your .env file with RapidAPI credentials."
        )
    return RAPIDAPI_KEY


def gen_prompt(content: str) -> str:
    """Create the categorisation prompt for a single tweet."""
    prompt = f"""
        You are an expert annotator analyzing individual tweets by Elon Musk.

        Tweet:
        {content}

        Your tasks:

        1. Assign the tweet to exactly one of the following categories:
           - "Tesla": Tesla products, stock, management, factories, etc.
           - "SpaceX": rockets, Starship, Starlink, launches, satellites, etc.
           - "X": X (formerly Twitter) features, policies, moderation, or company issues.
           - "xAI / Grok": xAI, Grok, AI capabilities, AI safety tied to xAI.
           - "Other Elon Musk Company": Neuralink, The Boring Company, SolarCity, etc.
           - "US Politics": US government, elections, politicians, political parties, policies.
           - "Global Politics": non-US governments, geopolitics, wars, diplomacy, policy issues.
           - "Cryptocurrency": Bitcoin, Dogecoin, other coins, crypto markets, blockchain talk.
           - "Fun or Entertainment": memes, jokes, casual banter, movies, games, random fun.
           - "Freedom of Speech": defending or debating freedom of speech.
           - "Other / General": anything that does not clearly fit the categories above.

        2. Determine the sentiment of the tweet within that category:
           - "positive"
           - "negative"
           - "neutral"

        Guidelines:
        - Base your decision ONLY on the tweet content provided.
        - If the tweet touches multiple areas, pick the single most central topic.
        - Consider sarcasm or jokes, but do not over-interpret beyond the text.

        Output only valid JSON in this exact format:
        {{
          "category": "<one of the categories above>",
          "sentiment": "positive" | "negative" | "neutral",
          "reason": "<very short explanation of why you chose this category and sentiment>"
        }}
    """
    return dedent(prompt).strip()


def fetch_elon_tweets(
    user_id: str = DEFAULT_USER_ID,
    count: int = DEFAULT_TWEET_COUNT,
) -> list[str]:
    """Fetch the latest tweets for the provided user via RapidAPI."""
    headers = {
        "x-rapidapi-key": _require_rapidapi_key(),
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    params = {"user": user_id, "count": str(count)}
    try:
        response = requests.get(
            RAPIDAPI_URL,
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:  # noqa: PERF203 - clarity first
        raise RuntimeError(f"Failed to fetch tweets from RapidAPI: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("RapidAPI returned an invalid JSON payload.") from exc

    instructions = data.get("result", {}).get("timeline", {}).get("instructions", [])
    tweets: list[str] = []
    for instruction in instructions:
        entries = instruction.get("entries") or []
        for entry in entries:
            tweet_text = (
                entry.get("content", {})
                .get("itemContent", {})
                .get("tweet_results", {})
                .get("result", {})
                .get("legacy", {})
                .get("full_text")
            )
            if tweet_text:
                tweets.append(tweet_text)

    if not tweets:
        raise RuntimeError("RapidAPI response did not include any tweet text.")

    return tweets


def categorize_tweet(content: str) -> dict:
    """Send a single tweet to the LLM and parse the JSON result."""
    prompt = gen_prompt(content)
    return ask_open_router(prompt)


def main() -> None:
    tweets = fetch_elon_tweets()
    for idx, tweet in enumerate(tweets, start=1):
        print(f"Tweet #{idx}:")
        print(tweet)
        try:
            result = categorize_tweet(tweet)
            print("LLM Response:")
            print(json.dumps(result, indent=2))
        except Exception as exc:  # noqa: BLE001 - keep the script running
            print(f"Error while categorizing tweet: {exc}")
        print("-" * 40)
        if idx < len(tweets):
            time.sleep(DEFAULT_SLEEP_SECONDS)


if __name__ == "__main__":
    main()
