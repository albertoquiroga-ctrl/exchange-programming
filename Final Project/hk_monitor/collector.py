"""Data collectors for HK public data feeds."""

# === Snapshot collection entry points ===

# This module walks through the "collector" leg of the pipeline: first we drive
# a refresh, then branch into feed-specific helpers, and finally fall back to
# caching/HTTP utilities.  Everything here favors clarity over micro-
# optimizations so students can trace how data flows from HTTP into SQLite.
from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence
import sqlite3
import xml.etree.ElementTree as ET

import requests

from . import db
from .config import Config

LOGGER = logging.getLogger(__name__)
ISO_VARIANTS = ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ")
# Sending a descriptive UA helps data.gov.hk trace demo traffic if needed.
HTTP_HEADERS = {"User-Agent": "HKConditionsMonitor/1.0 (+https://data.gov.hk)"}


def collect_once(
    config: Config, conn: sqlite3.Connection | None = None
) -> Dict[str, sqlite3.Row | None]:
    """Fetch all metrics once and persist them into SQLite."""

    if conn is None:
        # Tests call this helper without a connection, so lazily create one that
        # mirrors ``hk_monitor.app``.
        from .db import connect

        # Treat the `collect_once` helper as a one-shot pipeline: open a
        # connection, scrape data, and immediately return a fresh snapshot.
        with connect(config.app.database_path) as connection:
            _collect(config, connection)
            return db.get_latest_snapshot(connection)
    _collect(config, conn)
    return db.get_latest_snapshot(conn)


def _collect(config: Config, conn: sqlite3.Connection) -> None:
    """Run each feed collector in turn, writing rows when data is present."""

    # Capture and persist each metric independently so one flaky endpoint does
    # not block the remaining feeds.
    warning_record = fetch_warning(config)
    if warning_record is not None:
        db.save_warning(conn, warning_record)

    rain_record = fetch_rain(config)
    if rain_record is not None:
        db.save_rain(conn, rain_record)

    aqhi_record = fetch_aqhi(config)
    if aqhi_record is not None:
        db.save_aqhi(conn, aqhi_record)

    traffic_record = fetch_traffic(config)
    if traffic_record is not None:
        db.save_traffic(conn, traffic_record)


def fetch_warning(config: Config) -> db.WarningRecord | None:
    """Return the latest weather warning, if any."""

    # Step 1: fetch the payload once from either the bundled mock file or HTTP.
    payload = _get_payload(
        config, config.api.warnings_url, config.mocks.warnings, key=None
    )
    # Step 2: locate the most recent warning entry and normalize timestamps.
    feed_timestamp = None
    if isinstance(payload, dict):
        feed_timestamp = payload.get("updateTime") or payload.get("issueTime")
    details: Sequence[Dict[str, Any]] = []
    if isinstance(payload, dict):
        raw = payload.get("details") or payload.get("warning") or payload.get("data")
        if isinstance(raw, list):
            details = [entry for entry in raw if isinstance(entry, dict)]
    if not details:
        return db.WarningRecord(
            level="None",
            message="No weather warnings in force.",
            updated_at=_parse_time(str(feed_timestamp) if feed_timestamp else None),
        )
    # Step 3: build a normalized record so downstream storage stays stable.
    # The feed lists warnings in reverse chronological order, so take the first
    # structured entry and normalise keys coming from different HK APIs.
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
    updated = (
        entry.get("updateTime")
        or entry.get("issueTime")
        or payload.get("updateTime")
        or payload.get("issueTime")
    )
    return db.WarningRecord(
        level=str(level),
        message=str(message),
        updated_at=_parse_time(str(updated) if updated else None),
    )


def fetch_rain(config: Config) -> db.RainRecord | None:
    """Return a rain record for the selected district."""

    # Step 1: fetch the payload once from the configured source.
    payload = _get_payload(
        config, config.api.rainfall_url, config.mocks.rainfall, key=None
    )
    entries: List[Dict[str, Any]] = []
    if isinstance(payload, dict):
        if "data" in payload:
            data = payload.get("data")
        else:
            data = (payload.get("rainfall") or {}).get("data")
        if isinstance(data, list):
            entries = [row for row in data if isinstance(row, dict)]
    elif isinstance(payload, list):
        entries = [row for row in payload if isinstance(row, dict)]
    # Step 2: pick the configured district reading instead of averaging.
    district = config.app.rain_district
    entry = next((row for row in entries if row.get("place") == district), None)
    if not entry:
        target = _normalise_district(district)
        entry = next(
            (
                row
                for row in entries
                if _normalise_district(row.get("place")) == target
            ),
            None,
        )
    if not entry:
        return None
    # Step 3: build the stored record while normalizing numeric fields.
    raw_value = entry.get("max") or entry.get("value") or entry.get("mm") or 0
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        value = 0.0
    category = _categorize_rain(value)
    intensity = f"{value:.1f} mm ({category})"
    updated = entry.get("recordTime") or entry.get("time")
    if not updated and isinstance(payload, dict):
        updated = payload.get("updateTime")
    return db.RainRecord(
        district=str(entry.get("place") or district),
        intensity=intensity,
        updated_at=_parse_time(str(updated) if updated else None),
    )


def fetch_aqhi(config: Config) -> db.AqhiRecord | None:
    """Return AQHI metrics for the configured station."""

    # Step 1: fetch once from the mock or live endpoint.
    payload = _get_payload(config, config.api.aqhi_url, config.mocks.aqhi, key=None)
    if isinstance(payload, list):
        stations = [row for row in payload if isinstance(row, dict)]
    else:
        raw = None
        if isinstance(payload, dict):
            raw = payload.get("aqhi") or payload.get("data")
        if isinstance(raw, list):
            stations = [row for row in raw if isinstance(row, dict)]
        else:
            stations = []
    # Step 2: iterate through the payload to find the selected station.
    entry = next(
        (row for row in stations if row.get("station") == config.app.aqhi_station),
        None,
    )
    if not entry:
        return None
    # Step 3: build a normalized record matching the expected DB schema.
    try:
        value = float(entry.get("aqhi") or entry.get("value") or entry.get("index") or 0)
    except (TypeError, ValueError):
        value = 0.0
    category = (
        entry.get("health_risk")
        or entry.get("category")
        or _categorize_aqhi(value)
    )
    timestamp = (
        entry.get("time")
        or entry.get("publish_date")
        or entry.get("updateTime")
    )
    if not timestamp and isinstance(payload, dict):
        timestamp = payload.get("publishDate") or payload.get("updateTime")
    return db.AqhiRecord(
        station=str(entry.get("station") or config.app.aqhi_station),
        category=str(category),
        value=value,
        updated_at=_parse_time(str(timestamp) if timestamp else None),
    )


def fetch_traffic(config: Config) -> db.TrafficRecord | None:
    """Return the latest traffic incident that matches the configured region."""

    # Step 1: fetch the payload and parse XML when necessary.
    payload = _get_payload(
        config,
        config.api.traffic_url,
        config.mocks.traffic,
        key=None,
        parser=_parse_traffic_xml,
    )
    # Step 2: narrow to the learner's focus region.
    incidents = _extract_traffic_entries(payload)
    entry = _pick_traffic_entry(incidents, config.app.traffic_region)
    if not entry:
        return None
    # Step 3: normalize fields so database rows remain consistent.
    severity = (
        entry.get("severity")
        or entry.get("category")
        or entry.get("status")
        or "Info"
    )
    description = (
        entry.get("content")
        or entry.get("description")
        or entry.get("summary")
        or "Traffic update"
    )
    updated = entry.get("update_time") or entry.get("updateTime")
    if not updated and isinstance(payload, dict):
        updated = payload.get("updateTime")
    return db.TrafficRecord(
        severity=str(severity).title(),
        description=str(description).strip(),
        updated_at=_parse_time(str(updated) if updated else None),
    )


def _extract_traffic_entries(payload: Any) -> List[Dict[str, Any]]:
    """Return a flat list of incident dictionaries from varied payload shapes."""

    if isinstance(payload, list):
        return [entry for entry in payload if isinstance(entry, dict)]
    if isinstance(payload, dict):
        for key in ("trafficnews", "incidents", "messages", "data"):
            raw = payload.get(key)
            if isinstance(raw, list):
                return [entry for entry in raw if isinstance(entry, dict)]
    return []


def _pick_traffic_entry(
    incidents: Sequence[Dict[str, Any]], target_region: str
) -> Dict[str, Any] | None:
    """Return the first incident whose text contains the requested region."""

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


# === Domain-specific helpers ===

def _categorize_rain(value: float) -> str:
    """Map millimetres of rainfall to the HK Observatory warning levels."""
    if value >= 30:
        return "Black Rain"
    if value >= 15:
        return "Red Rain"
    if value >= 5:
        return "Amber Rain"
    if value >= 1:
        return "Showers"
    return "Dry"


def _normalise_district(name: Any) -> str:
    """Normalise different spellings like 'Central & Western District'."""

    if not isinstance(name, str):
        return ""
    text = name.strip().lower()
    suffix = " district"
    if text.endswith(suffix):
        text = text[: -len(suffix)].strip()
    return text


def _categorize_aqhi(value: float) -> str:
    """Translate AQHI numbers into the textual bands used by HK authorities."""
    if value >= 10:
        return "Serious"
    if value >= 7:
        return "Very High"
    if value >= 4:
        return "High"
    if value >= 3:
        return "Moderate"
    return "Low"


def _parse_time(raw: str | None) -> datetime:
    """Convert the API timestamps into timezone-aware datetimes."""

    if not raw:
        return datetime.now(timezone.utc)
    for fmt in ISO_VARIANTS:
        try:
            return datetime.strptime(raw, fmt)
        except (TypeError, ValueError):
            continue
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return datetime.now(timezone.utc)


def _get_payload(
    config: Config,
    url: str,
    mock_path: Path,
    key: str | None = None,
    parser: Callable[[str], Any] | None = None,
) -> Any:
    """Return either the mock payload or the live HTTP response once."""

    if config.app.use_mock_data:
        try:
            payload = _load_from_disk(mock_path)
        except (OSError, json.JSONDecodeError) as exc:
            LOGGER.warning("Unable to load mock payload %s: %s", mock_path, exc)
            payload = {}
    else:
        try:
            response = requests.get(url, timeout=10, headers=HTTP_HEADERS)
            response.raise_for_status()
            payload = parser(response.text) if parser else response.json()
        except (requests.RequestException, ValueError, ET.ParseError) as exc:
            LOGGER.warning("Failed to fetch payload from %s: %s", url, exc)
            payload = {}
    if key and isinstance(payload, dict):
        if key in payload:
            return payload[key]
        nested = payload.get("data")
        if isinstance(nested, dict) and key in nested:
            return nested[key]
    return payload


def _load_from_disk(path: Path) -> Any:
    """Convenience helper for reading JSON mock files."""

    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _parse_traffic_xml(text: str) -> Dict[str, Any]:
    """Convert the Transport Department XML into JSON-like dictionaries."""

    root = ET.fromstring(text)
    incidents = []
    for message in root.findall(".//message"):
        payload: Dict[str, Any] = {}
        for child in message:
            # Lowercase tags to keep dictionary lookups consistent.
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
    "_categorize_aqhi",
]
