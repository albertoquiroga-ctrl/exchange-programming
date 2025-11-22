"""Hardcoded defaults so beginners don't need TOML files."""

from copy import deepcopy
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_CONFIG = {
    "app": {
        "poll_interval": 300,
        "rain_district": "Central & Western",
        "aqhi_station": "Central/Western",
        "traffic_region": "Hong Kong Island",
        "use_mock_data": False,
    },
    "api": {
        "warnings_url": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=en",
        "rainfall_url": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en",
        "aqhi_url": "https://dashboard.data.gov.hk/api/aqhi-individual?format=json",
        "traffic_url": "https://www.td.gov.hk/en/special_news/trafficnews.xml",
    },
    "mocks": {
        "warnings": str(BASE_DIR / "tests/data/warnings.json"),
        "rainfall": str(BASE_DIR / "tests/data/rainfall.json"),
        "aqhi": str(BASE_DIR / "tests/data/aqhi.json"),
        "traffic": str(BASE_DIR / "tests/data/traffic.json"),
    },
}


def load_config(_ignored_path=None):
    """Return a fresh copy of the defaults."""
    return deepcopy(DEFAULT_CONFIG)


__all__ = ["load_config", "DEFAULT_CONFIG"]
