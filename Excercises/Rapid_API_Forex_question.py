# Instructions. Implement the following functions with the help of API in RapidAPI.com
#
# Hints: use this API https://rapidapi.com/exchangerateapi/api/exchangerate-api

from __future__ import annotations

import os
from typing import Dict

import requests

# Constants keep configuration in a single place for easy reuse and readability.
RAPIDAPI_HOST = "exchangerate-api.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}/rapid/latest"
RAPIDAPI_KEY_ENV = "RAPIDAPI_KEY"
DEFAULT_RAPIDAPI_KEY = "e1d928f3e2mshdd455565a50becap165279jsn6ad22dcbee6d"


def _load_api_key() -> str:
    """Fetch the RapidAPI key from environment variables with a friendly error."""
    # Prefer an environment variable so secrets are not committed, but fall back to the provided key.
    api_key = os.getenv(RAPIDAPI_KEY_ENV, DEFAULT_RAPIDAPI_KEY)
    if not api_key:
        raise RuntimeError(
            "Missing RapidAPI credentials. Either set the RAPIDAPI_KEY environment variable "
            "or populate DEFAULT_RAPIDAPI_KEY with a valid token."
        )
    return api_key


def _fetch_conversion_rates(base_currency: str) -> Dict[str, float]:
    """Call the RapidAPI endpoint and return the conversion rate map for the base currency."""
    api_key = _load_api_key()
    # We ensure the base currency is upper case because the API expects ISO currency codes.
    normalized_base = base_currency.upper()
    url = f"{RAPIDAPI_BASE_URL}/{normalized_base}"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"RapidAPI request failed for {normalized_base}: {exc}") from exc

    payload = response.json()

    # The API returns either "conversion_rates" or "rates" depending on the chosen endpoint.
    conversion_rates: Dict[str, float] | None = payload.get("conversion_rates") or payload.get("rates")
    if not conversion_rates:
        raise RuntimeError(
            f"Unexpected response structure when requesting rates for {normalized_base}: {payload}"
        )

    return conversion_rates


# Return the amount with real time rate
def get_exchange_rate(amount, from_currency, to_currency):
    """Convert the provided amount between currencies using RapidAPI's ExchangeRate API."""
    if not isinstance(from_currency, str) or not isinstance(to_currency, str):
        raise TypeError("Currency codes must be provided as strings.")

    # Turn the raw amount into a float so downstream math works consistently.
    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError) as exc:
        raise TypeError("Amount must be a number.") from exc

    if numeric_amount < 0:
        raise ValueError("Amount must be non-negative.")

    rates = _fetch_conversion_rates(from_currency)
    target_currency = to_currency.upper()

    if target_currency not in rates:
        raise ValueError(
            f"Could not find conversion rate from {from_currency.upper()} to {target_currency}."
        )

    # Perform the currency conversion with the retrieved rate.
    rate = rates[target_currency]
    # Multiply after retrieving the rate to perform the actual currency conversion.
    return numeric_amount * rate


print(get_exchange_rate(10_000,"HKD","USD"))  # should give roughly 1278
print(get_exchange_rate(1_000_000,"JPY","HKD"))  # should give roughly 52000
