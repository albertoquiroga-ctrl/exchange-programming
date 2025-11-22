"""Simple config loader for the HK monitor demo.

Everything returns plain dictionaries so beginners can print and inspect
values easily. We keep defaults short and avoid advanced patterns.
"""

from pathlib import Path

try:  # Python >=3.11
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore[no-redef]


DEFAULTS = {
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
        "warnings": "tests/data/warnings.json",
        "rainfall": "tests/data/rainfall.json",
        "aqhi": "tests/data/aqhi.json",
        "traffic": "tests/data/traffic.json",
    },
}


def load_config(path="config.toml"):
    """Load TOML into a nested dictionary with simple defaults."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"No config found at {config_path}. Copy config.template.toml and edit the values."
        )

    text = config_path.read_text(encoding="utf-8")
    raw = tomllib.loads(text)
    base = config_path.parent

    data = {"app": {}, "api": {}, "mocks": {}}

    app_raw = raw.get("app", {})
    data["app"]["poll_interval"] = int(app_raw.get("poll_interval", DEFAULTS["app"]["poll_interval"]))
    data["app"]["rain_district"] = str(app_raw.get("rain_district", DEFAULTS["app"]["rain_district"]))
    data["app"]["aqhi_station"] = str(app_raw.get("aqhi_station", DEFAULTS["app"]["aqhi_station"]))
    data["app"]["traffic_region"] = str(app_raw.get("traffic_region", DEFAULTS["app"]["traffic_region"]))
    data["app"]["use_mock_data"] = bool(app_raw.get("use_mock_data", DEFAULTS["app"]["use_mock_data"]))

    api_raw = raw.get("api", {})
    data["api"]["warnings_url"] = str(api_raw.get("warnings_url", DEFAULTS["api"]["warnings_url"]))
    data["api"]["rainfall_url"] = str(api_raw.get("rainfall_url", DEFAULTS["api"]["rainfall_url"]))
    data["api"]["aqhi_url"] = str(api_raw.get("aqhi_url", DEFAULTS["api"]["aqhi_url"]))
    data["api"]["traffic_url"] = str(api_raw.get("traffic_url", DEFAULTS["api"]["traffic_url"]))

    mock_raw = raw.get("mocks", {})
    data["mocks"]["warnings"] = str(base / mock_raw.get("warnings", DEFAULTS["mocks"]["warnings"]))
    data["mocks"]["rainfall"] = str(base / mock_raw.get("rainfall", DEFAULTS["mocks"]["rainfall"]))
    data["mocks"]["aqhi"] = str(base / mock_raw.get("aqhi", DEFAULTS["mocks"]["aqhi"]))
    data["mocks"]["traffic"] = str(base / mock_raw.get("traffic", DEFAULTS["mocks"]["traffic"]))

    return data


__all__ = ["load_config", "DEFAULTS"]
