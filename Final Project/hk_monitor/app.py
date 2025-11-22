"""HK Conditions Monitor (simple console, live data only).

Single file. Fetches live data from Hong Kong open-data APIs.
No TOML config, no database, no mocks.
"""

import argparse
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Iterable

import requests

DEFAULTS = {
    "rain_district": "Central & Western",
    "aqhi_station": "Central/Western",
    "traffic_region": "Hong Kong Island",
    "poll_interval": 60,
}

RAIN_CHOICES = [
    "Central & Western",
    "Eastern",
    "Southern",
    "Wan Chai",
    "Kowloon City",
    "Kwun Tong",
    "Wong Tai Sin",
    "Yau Tsim Mong",
    "Sha Tin",
    "Tai Po",
    "Tsuen Wan",
    "Tuen Mun",
    "Yuen Long",
]

AQHI_CHOICES = [
    "Central/Western",
    "Eastern",
    "Kwun Tong",
    "Sham Shui Po",
    "Sha Tin",
    "Tsuen Wan",
    "Tuen Mun",
    "Yuen Long",
]

TRAFFIC_CHOICES = [
    "Hong Kong Island",
    "Kowloon",
    "New Territories",
    "Lantau Island",
    "Islands District",
]

URLS = {
    "warnings": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=en",
    "rain": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en",
    "aqhi": "https://dashboard.data.gov.hk/api/aqhi-individual?format=json",
    "traffic": "https://www.td.gov.hk/en/special_news/trafficnews.xml",
}

HTTP_HEADERS = {"User-Agent": "HKConditionsMonitor/1.0 (+https://data.gov.hk)"}


def main():
    _parse_args()  # kept for future flags
    config = DEFAULTS.copy()

    print("HK Conditions Monitor (live data)")
    print("Commands: Enter=refresh, c=change locations, q=quit")
    print("Current choices are shown when changing locations.\n")

    while True:
        snapshot = _collect_snapshot(config)
        _print_snapshot(snapshot, config)

        choice = input("\nEnter=refresh | c=change locations | q=quit: ").strip().lower()
        if choice == "q":
            break
        if choice == "c":
            _change_locations(config)
            continue
        wait_seconds = max(0, int(config.get("poll_interval", 0)))
        if wait_seconds:
            print(f"Waiting {wait_seconds} seconds...\n")
            time.sleep(wait_seconds)


def _parse_args():
    parser = argparse.ArgumentParser(description="Simple HK monitor console")
    return parser.parse_args()


def _collect_snapshot(config):
    return {
        "warnings": _fetch_warning(config),
        "rain": _fetch_rain(config),
        "aqhi": _fetch_aqhi(config),
        "traffic": _fetch_traffic(config),
    }


def _fetch_warning(config):
    payload: Any = _get_payload("warnings")
    if not isinstance(payload, dict):
        return _empty_warning()

    feed_time = payload.get("updateTime") or payload.get("issueTime")
    details = payload.get("details") or payload.get("warning") or payload.get("data")
    if not isinstance(details, list) or not details:
        return _empty_warning(feed_time)

    entry = details[0]
    level = (
        entry.get("warningStatementCode")
        or entry.get("warningMessageCode")
        or entry.get("warningSignal")
        or entry.get("warningType")
        or entry.get("level")
        or "Unknown"
    )
    message = (
        entry.get("warningMessage")
        or entry.get("message")
        or entry.get("description")
        or "Weather warning in effect."
    )
    updated = entry.get("updateTime") or entry.get("issueTime") or feed_time
    return {
        "level": str(level),
        "message": str(message),
        "updated_at": _ts(updated),
    }


def _fetch_rain(config):
    payload: Any = _get_payload("rain")
    entries = []
    if isinstance(payload, dict):
        data = payload.get("data") or (payload.get("rainfall") or {}).get("data")
        if isinstance(data, list):
            entries = [row for row in data if isinstance(row, dict)]
    elif isinstance(payload, list):
        entries = [row for row in payload if isinstance(row, dict)]

    district = config["rain_district"]
    entry = next((row for row in entries if row.get("place") == district), None)
    if not entry:
        entry = next((row for row in entries if _norm(row.get("place")) == _norm(district)), None)
    if not entry:
        return {"district": district, "intensity": "No data", "updated_at": _ts()}

    value = _to_float(entry.get("max") or entry.get("value") or entry.get("mm"))
    category = _categorize_rain(value)
    updated = entry.get("recordTime") or entry.get("time") or payload.get("updateTime")
    return {
        "district": str(entry.get("place") or district),
        "intensity": f"{value:.1f} mm ({category})",
        "updated_at": _ts(updated),
    }


def _fetch_aqhi(config):
    payload: Any = _get_payload("aqhi")
    if isinstance(payload, list):
        stations = [row for row in payload if isinstance(row, dict)]
    elif isinstance(payload, dict):
        raw = payload.get("aqhi") or payload.get("data")
        stations = [row for row in raw if isinstance(row, dict)] if isinstance(raw, list) else []
    else:
        stations = []

    entry = next((row for row in stations if row.get("station") == config["aqhi_station"]), None)
    if not entry:
        return {
            "station": config["aqhi_station"],
            "category": "Unknown",
            "value": "No data",
            "updated_at": _ts(),
        }

    value = _to_float(entry.get("aqhi") or entry.get("value") or entry.get("index"))
    category = entry.get("health_risk") or entry.get("category") or _categorize_aqhi(value)
    timestamp = entry.get("time") or entry.get("publish_date") or entry.get("updateTime")
    if not timestamp and isinstance(payload, dict):
        timestamp = payload.get("publishDate") or payload.get("updateTime")

    return {
        "station": str(entry.get("station") or config["aqhi_station"]),
        "category": str(category),
        "value": value,
        "updated_at": _ts(timestamp),
    }


def _fetch_traffic(config):
    payload: Any = _get_payload("traffic", parser=_parse_traffic_xml)
    incidents = _extract_traffic_entries(payload)
    entry = _pick_traffic_entry(incidents, config["traffic_region"])
    if not entry:
        return {"severity": "Info", "description": "No traffic data.", "updated_at": _ts()}

    severity = entry.get("severity") or entry.get("category") or entry.get("status") or "Info"
    description = (
        entry.get("content") or entry.get("description") or entry.get("summary") or "Traffic update"
    )
    updated = entry.get("update_time") or entry.get("updateTime") or (
        payload.get("updateTime") if isinstance(payload, dict) else None
    )

    return {
        "severity": str(severity).title(),
        "description": str(description).strip(),
        "updated_at": _ts(updated),
    }


def _get_payload(kind: str, parser=None) -> Any:
    url = URLS[kind]
    response = requests.get(url, timeout=10, headers=HTTP_HEADERS)
    response.raise_for_status()
    return parser(response.text) if parser else response.json()


def _parse_traffic_xml(text):
    root = ET.fromstring(text)
    incidents = []
    for message in root.findall(".//message"):
        payload = {}
        for child in message:
            key = child.tag.lower()
            payload[key] = (child.text or "").strip()
        incidents.append(
            {
                "region": payload.get("district_en") or payload.get("region"),
                "severity": payload.get("incident_heading_en") or payload.get("severity"),
                "content": payload.get("content_en") or payload.get("incident_detail_en"),
                "update_time": payload.get("announcement_date"),
                "location": payload.get("location_en"),
                "direction": payload.get("direction_en"),
                "description": payload.get("incident_detail_en"),
                "status": payload.get("incident_status_en"),
            }
        )
    return {"trafficnews": incidents}


def _extract_traffic_entries(payload):
    if isinstance(payload, list):
        return [entry for entry in payload if isinstance(entry, dict)]
    if isinstance(payload, dict):
        for key in ("trafficnews", "incidents", "messages", "data"):
            raw = payload.get(key)
            if isinstance(raw, list):
                return [entry for entry in raw if isinstance(entry, dict)]
    return []


def _pick_traffic_entry(incidents, target_region):
    if not incidents:
        return None
    needle = target_region.strip().lower()
    if not needle:
        return incidents[0]
    for entry in incidents:
        parts = [
            entry.get("region"),
            entry.get("location"),
            entry.get("direction"),
            entry.get("content"),
            entry.get("description"),
        ]
        joined = " ".join(str(part) for part in parts if part).lower()
        if needle in joined:
            return entry
    return incidents[0]


def _print_snapshot(snapshot, config):
    header = (
        f"District: {config['rain_district']} | "
        f"AQHI: {config['aqhi_station']} | "
        f"Traffic: {config['traffic_region']}"
    )
    print("\n" + "=" * 60)
    print(header)
    print("-" * len(header))
    print("\nWarnings\n--------")
    print(_format_warning(snapshot["warnings"]))
    print("\nRain\n----")
    print(_format_rain(snapshot["rain"]))
    print("\nAQHI\n----")
    print(_format_aqhi(snapshot["aqhi"]))
    print("\nTraffic\n-------")
    print(_format_traffic(snapshot["traffic"]))
    print("=" * 60)


def _change_locations(config):
    print("\nChange locations (press Enter to keep current)")
    config["rain_district"] = _select_from_list(
        "Rain districts", RAIN_CHOICES, config["rain_district"]
    )
    config["aqhi_station"] = _select_from_list(
        "AQHI stations", AQHI_CHOICES, config["aqhi_station"]
    )
    config["traffic_region"] = _select_from_list(
        "Traffic regions", TRAFFIC_CHOICES, config["traffic_region"]
    )


def _print_choices(title: str, options: Iterable[str]):
    print(f"\n{title}:")
    for idx, option in enumerate(options, start=1):
        print(f"  {idx}. {option}")


def _select_from_list(title: str, options: list[str], current: str) -> str:
    _print_choices(title, options)
    raw = input(f"{title[:-1]} (current: {current}): ").strip()
    if not raw:
        return current
    try:
        index = int(raw) - 1
    except ValueError:
        # If not a number, keep current so students don't get errors.
        return current
    if 0 <= index < len(options):
        return options[index]
    return current


def _format_warning(row):
    return f"Level: {row['level']}\nMessage: {row['message']}\nUpdated: {row['updated_at']}"


def _format_rain(row):
    return (
        f"District: {row['district']}\n"
        f"Intensity: {row['intensity']}\n"
        f"Updated: {row['updated_at']}"
    )


def _format_aqhi(row):
    return (
        f"Station: {row['station']}\n"
        f"Category: {row['category']}\n"
        f"Value: {row['value']}\n"
        f"Updated: {row['updated_at']}"
    )


def _format_traffic(row):
    return (
        f"Severity: {row['severity']}\n"
        f"{row['description']}\n"
        f"Updated: {row['updated_at']}"
    )


def _ts(raw=None):
    if not raw:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        dt = datetime.fromisoformat(str(raw))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return str(raw)


def _norm(text):
    if not isinstance(text, str):
        return ""
    t = text.strip().lower()
    if t.endswith(" district"):
        t = t[: -len(" district")]
    return t


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _categorize_rain(value):
    if value >= 30:
        return "Black Rain"
    if value >= 15:
        return "Red Rain"
    if value >= 5:
        return "Amber Rain"
    if value >= 1:
        return "Showers"
    return "Dry"


def _categorize_aqhi(value):
    if value >= 10:
        return "Serious"
    if value >= 7:
        return "Very High"
    if value >= 4:
        return "High"
    if value >= 3:
        return "Moderate"
    return "Low"


def _empty_warning(feed_time=None):
    return {
        "level": "None",
        "message": "No weather warnings in force.",
        "updated_at": _ts(feed_time),
    }


if __name__ == "__main__":
    main()
