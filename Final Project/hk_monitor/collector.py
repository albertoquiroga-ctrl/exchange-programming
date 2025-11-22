"""Collect data for the HK public feeds without using a database.

Each helper returns a simple dictionary that can be printed straight to
the console. This keeps the code close to the exercises used in class.
"""

from datetime import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import requests

HTTP_HEADERS = {"User-Agent": "HKConditionsMonitor/1.0 (+https://data.gov.hk)"}


def collect_once(config):
    """Grab one snapshot of every metric and return it."""

    return {
        "warnings": fetch_warning(config),
        "rain": fetch_rain(config),
        "aqhi": fetch_aqhi(config),
        "traffic": fetch_traffic(config),
    }


def fetch_warning(config):
    payload = _get_payload(
        config,
        config["api"]["warnings_url"],
        config["mocks"]["warnings"],
    )
    if not isinstance(payload, dict):
        return None

    feed_time = payload.get("updateTime") or payload.get("issueTime")
    details = payload.get("details") or payload.get("warning") or payload.get("data")
    if not isinstance(details, list):
        details = []

    entries = [item for item in details if isinstance(item, dict)]
    if not entries:
        return {
            "level": "None",
            "message": "No weather warnings in force.",
            "updated_at": _timestamp(feed_time),
        }

    entry = entries[0]
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
        "updated_at": _timestamp(updated),
    }


def fetch_rain(config):
    payload = _get_payload(
        config,
        config["api"]["rainfall_url"],
        config["mocks"]["rainfall"],
    )
    entries = []
    if isinstance(payload, dict):
        data = payload.get("data") or (payload.get("rainfall") or {}).get("data")
        if isinstance(data, list):
            entries = [row for row in data if isinstance(row, dict)]
    elif isinstance(payload, list):
        entries = [row for row in payload if isinstance(row, dict)]

    district = config["app"]["rain_district"]
    entry = next((row for row in entries if row.get("place") == district), None)
    if not entry:
        target = _normalise_district(district)
        entry = next(
            (row for row in entries if _normalise_district(row.get("place")) == target),
            None,
        )
    if not entry:
        return None

    raw_value = entry.get("max") or entry.get("value") or entry.get("mm") or 0
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        value = 0.0
    intensity = f"{value:.1f} mm ({_categorize_rain(value)})"
    updated = entry.get("recordTime") or entry.get("time") or payload.get("updateTime")

    return {
        "district": str(entry.get("place") or district),
        "intensity": intensity,
        "updated_at": _timestamp(updated),
    }


def fetch_aqhi(config):
    payload = _get_payload(
        config,
        config["api"]["aqhi_url"],
        config["mocks"]["aqhi"],
    )
    if isinstance(payload, list):
        stations = [row for row in payload if isinstance(row, dict)]
    elif isinstance(payload, dict):
        raw = payload.get("aqhi") or payload.get("data")
        stations = [row for row in raw if isinstance(row, dict)] if isinstance(raw, list) else []
    else:
        stations = []

    entry = next((row for row in stations if row.get("station") == config["app"]["aqhi_station"]), None)
    if not entry:
        return None

    try:
        value = float(entry.get("aqhi") or entry.get("value") or entry.get("index") or 0)
    except (TypeError, ValueError):
        value = 0.0

    category = entry.get("health_risk") or entry.get("category") or _categorize_aqhi(value)
    timestamp = entry.get("time") or entry.get("publish_date") or entry.get("updateTime")
    if not timestamp and isinstance(payload, dict):
        timestamp = payload.get("publishDate") or payload.get("updateTime")

    return {
        "station": str(entry.get("station") or config["app"]["aqhi_station"]),
        "category": str(category),
        "value": value,
        "updated_at": _timestamp(timestamp),
    }


def fetch_traffic(config):
    payload = _get_payload(
        config,
        config["api"]["traffic_url"],
        config["mocks"]["traffic"],
        parser=_parse_traffic_xml,
    )
    incidents = _extract_traffic_entries(payload)
    entry = _pick_traffic_entry(incidents, config["app"]["traffic_region"])
    if not entry:
        return None

    severity = entry.get("severity") or entry.get("category") or entry.get("status") or "Info"
    description = (
        entry.get("content")
        or entry.get("description")
        or entry.get("summary")
        or "Traffic update"
    )
    updated = entry.get("update_time") or entry.get("updateTime") or payload.get("updateTime") if isinstance(payload, dict) else None

    return {
        "severity": str(severity).title(),
        "description": str(description).strip(),
        "updated_at": _timestamp(updated),
    }


def _get_payload(config, url, mock_path, parser=None):
    """Return mock data when use_mock_data is true; otherwise call the API once."""
    if config["app"].get("use_mock_data", False):
        try:
            return _load_from_disk(mock_path)
        except (OSError, json.JSONDecodeError):
            return {}

    try:
        response = requests.get(url, timeout=10, headers=HTTP_HEADERS)
        response.raise_for_status()
        return parser(response.text) if parser else response.json()
    except Exception:
        return {}


def _load_from_disk(path: str):
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _timestamp(raw):
    """Turn different timestamp shapes into a short, readable string."""
    if not raw:
        return _now_text()
    try:
        dt = datetime.fromisoformat(str(raw))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return str(raw)


def _now_text():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M")


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


def _normalise_district(name):
    if not isinstance(name, str):
        return ""
    text = name.strip().lower()
    suffix = " district"
    if text.endswith(suffix):
        text = text[: -len(suffix)].strip()
    return text


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


def _parse_traffic_xml(text):
    root = ET.fromstring(text)
    incidents = []
    for message in root.findall(".//message"):
        payload = {}
        for child in message:
            key = child.tag.lower()
            value = (child.text or "").strip()
            payload[key] = value
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


__all__ = [
    "collect_once",
    "fetch_warning",
    "fetch_rain",
    "fetch_aqhi",
    "fetch_traffic",
]
