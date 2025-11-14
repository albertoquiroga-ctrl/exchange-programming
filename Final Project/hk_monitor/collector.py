"""Data collectors for HK public data feeds."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict
import sqlite3
import xml.etree.ElementTree as ET

import requests

from . import db
from .config import Config

ISO_VARIANTS = ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ")
LOGGER = logging.getLogger(__name__)
MAX_ATTEMPTS = 3
HTTP_HEADERS = {"User-Agent": "HKConditionsMonitor/1.0 (+https://data.gov.hk)"}


def collect_once(
    config: Config, conn: sqlite3.Connection | None = None
) -> Dict[str, sqlite3.Row | None]:
    """Fetch all metrics once and persist them into SQLite."""
    if conn is None:
        from .db import connect

        with connect(config.app.database_path) as connection:
            _collect(config, connection)
            return db.get_latest_snapshot(connection)
    else:
        _collect(config, conn)
        return db.get_latest_snapshot(conn)


def _collect(config: Config, conn: sqlite3.Connection) -> None:
    # Warnings: load -> filter -> normalize -> persist
    warning_record = fetch_warning(config)
    if warning_record is not None:
        db.save_warning(conn, warning_record)

    # Rain: load -> filter -> normalize -> persist
    rain_record = fetch_rain(config)
    if rain_record is not None:
        db.save_rain(conn, rain_record)

    # AQHI: load -> filter -> normalize -> persist
    aqhi_record = fetch_aqhi(config)
    if aqhi_record is not None:
        db.save_aqhi(conn, aqhi_record)

    # Traffic: load -> filter -> normalize -> persist
    traffic_record = fetch_traffic(config)
    if traffic_record is not None:
        db.save_traffic(conn, traffic_record)


def fetch_warning(config: Config) -> db.WarningRecord | None:
    # Load phase
    payload = load_warning_payload(config)
    if not payload:
        return None

    # Filter phase
    detail = choose_warning_detail(payload)
    if detail is None:
        return None

    # Normalize phase
    return normalize_warning_detail(detail, payload)


def fetch_rain(config: Config) -> db.RainRecord | None:
    # Load phase
    payload = load_rain_payload(config)
    if payload is None:
        return None

    # Filter phase
    entries = extract_rain_entries(payload)
    district_entry = select_rain_entry(entries, config.app.rain_district)
    if district_entry is None:
        return None

    # Normalize phase
    return normalize_rain_entry(district_entry, payload, config.app.rain_district)


def fetch_aqhi(config: Config) -> db.AqhiRecord | None:
    # Load phase
    payload = load_aqhi_payload(config)
    if payload is None:
        return None

    # Filter phase
    stations = extract_aqhi_entries(payload)
    station_entry = select_aqhi_station(stations, config.app.aqhi_station)
    if station_entry is None:
        return None

    # Normalize phase
    return normalize_aqhi_entry(station_entry, payload, config.app.aqhi_station)


def fetch_traffic(config: Config) -> db.TrafficRecord | None:
    # Load phase
    payload = load_traffic_payload(config)
    if payload is None:
        return None

    # Filter phase
    incidents = extract_traffic_entries(payload)
    chosen = select_traffic_entry(incidents, config.app.traffic_region)
    if chosen is None:
        return None

    # Normalize phase
    return normalize_traffic_entry(chosen, payload)


def load_warning_payload(config: Config) -> Dict[str, Any]:
    return _get_payload(
        config, config.api.warnings_url, config.mocks.warnings, key="warnings"
    )


def choose_warning_detail(payload: Dict[str, Any]) -> Dict[str, Any] | None:
    details: list[Dict[str, Any]] = []
    if "details" in payload:
        raw_details = payload.get("details")
        if isinstance(raw_details, list):
            details = raw_details
    elif "warning" in payload:
        raw_warning = payload.get("warning")
        if isinstance(raw_warning, list):
            details = raw_warning
    if not details:
        return None
    return details[0]


def normalize_warning_detail(
    detail: Dict[str, Any], payload: Dict[str, Any]
) -> db.WarningRecord:
    update_time = detail.get("updateTime")
    if not update_time:
        update_time = payload.get("updateTime")
    level = detail.get("warningStatementCode")
    if not level:
        level = "UNKNOWN"
    message = detail.get("warningMessage")
    if not message:
        message = "No warning message supplied."
    return db.WarningRecord(
        level=str(level),
        message=str(message),
        updated_at=_parse_time(str(update_time) if update_time else None),
    )


def load_rain_payload(config: Config) -> Dict[str, Any] | None:
    payload = _get_payload(
        config, config.api.rainfall_url, config.mocks.rainfall, key="rainfall"
    )
    if isinstance(payload, dict):
        return payload
    return None


def extract_rain_entries(payload: Dict[str, Any]) -> list[Dict[str, Any]]:
    entries: list[Dict[str, Any]] = []
    if "data" in payload:
        raw_entries = payload.get("data")
    else:
        rainfall_section = payload.get("rainfall")
        if isinstance(rainfall_section, dict):
            raw_entries = rainfall_section.get("data")
        else:
            raw_entries = []
    if not isinstance(raw_entries, list):
        raw_entries = []
    for entry in raw_entries:
        if isinstance(entry, dict):
            entries.append(entry)
    return entries


def select_rain_entry(
    entries: list[Dict[str, Any]], district: str
) -> Dict[str, Any] | None:
    for entry in entries:
        place = entry.get("place")
        if place == district:
            return entry
    return None


def normalize_rain_entry(
    entry: Dict[str, Any], payload: Dict[str, Any], district: str
) -> db.RainRecord:
    value_field = entry.get("max")
    if value_field is None:
        value_field = entry.get("value")
    value_text = 0.0
    if value_field is not None:
        value_text = float(value_field)
    intensity = _categorize_rain(value_text)
    record_time = entry.get("recordTime")
    if not record_time:
        record_time = payload.get("updateTime")
    return db.RainRecord(
        district=district,
        intensity=intensity,
        updated_at=_parse_time(str(record_time) if record_time else None),
    )


def load_aqhi_payload(config: Config) -> Any:
    return _get_payload(config, config.api.aqhi_url, config.mocks.aqhi, key="aqhi")


def extract_aqhi_entries(payload: Any) -> list[Dict[str, Any]]:
    entries: list[Dict[str, Any]] = []
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                entries.append(item)
    elif isinstance(payload, dict):
        if "aqhi" in payload:
            raw_entries = payload.get("aqhi")
        elif "data" in payload:
            raw_entries = payload.get("data")
        else:
            raw_entries = []
        if isinstance(raw_entries, list):
            for item in raw_entries:
                if isinstance(item, dict):
                    entries.append(item)
    return entries


def select_aqhi_station(
    entries: list[Dict[str, Any]], station: str
) -> Dict[str, Any] | None:
    for entry in entries:
        current_station = entry.get("station")
        if current_station == station:
            return entry
    return None


def normalize_aqhi_entry(
    entry: Dict[str, Any], payload: Any, station: str
) -> db.AqhiRecord:
    value_field = entry.get("aqhi")
    if value_field is None:
        value_field = entry.get("value")
    value = 0.0
    if value_field is not None:
        value = float(value_field)
    category = entry.get("health_risk")
    if not category:
        category = entry.get("category")
    if not category:
        category = _categorize_aqhi(value)
    publish_time = entry.get("publish_date")
    if not publish_time:
        publish_time = entry.get("time")
    dataset_time = None
    if isinstance(payload, dict):
        dataset_time = payload.get("publishDate")
        if not dataset_time:
            dataset_time = payload.get("updateTime")
    timestamp_source = publish_time if publish_time else dataset_time
    return db.AqhiRecord(
        station=station,
        category=str(category),
        value=value,
        updated_at=_parse_time(str(timestamp_source) if timestamp_source else None),
    )


def load_traffic_payload(config: Config) -> Any:
    return _get_payload(
        config,
        config.api.traffic_url,
        config.mocks.traffic,
        key="trafficnews",
        parser=_parse_traffic_xml,
    )


def extract_traffic_entries(payload: Any) -> list[Dict[str, Any]]:
    incidents: list[Dict[str, Any]] = []
    if isinstance(payload, list):
        for entry in payload:
            if isinstance(entry, dict):
                incidents.append(entry)
    elif isinstance(payload, dict):
        if "trafficnews" in payload:
            raw_incidents = payload.get("trafficnews")
        elif "incidents" in payload:
            raw_incidents = payload.get("incidents")
        else:
            raw_incidents = []
        if isinstance(raw_incidents, list):
            for entry in raw_incidents:
                if isinstance(entry, dict):
                    incidents.append(entry)
    return incidents


def select_traffic_entry(
    incidents: list[Dict[str, Any]], target_region: str
) -> Dict[str, Any] | None:
    if not incidents:
        return None
    search_text = target_region.strip().lower()
    if not search_text:
        return incidents[0]
    for entry in incidents:
        words: list[str] = []
        region_text = entry.get("region")
        if region_text:
            words.append(str(region_text))
        location_text = entry.get("location")
        if location_text:
            words.append(str(location_text))
        direction_text = entry.get("direction")
        if direction_text:
            words.append(str(direction_text))
        content_text = entry.get("content")
        if content_text:
            words.append(str(content_text))
        haystack = " ".join(words).lower()
        if search_text in haystack:
            return entry
    return incidents[0]


def normalize_traffic_entry(
    entry: Dict[str, Any], payload: Any
) -> db.TrafficRecord:
    severity = entry.get("severity")
    if not severity:
        severity = entry.get("category")
    if not severity:
        severity = "info"
    description = entry.get("content")
    if not description:
        description = entry.get("summary")
    if not description:
        description = "Traffic update"
    updated = entry.get("update_time")
    if not updated and isinstance(payload, dict):
        updated = payload.get("updateTime")
    normalized_description = str(description).strip()
    return db.TrafficRecord(
        severity=str(severity).title(),
        description=normalized_description,
        updated_at=_parse_time(str(updated) if updated else None),
    )


def _categorize_rain(value: float) -> str:
    if value >= 30:
        return "Black Rain"
    if value >= 15:
        return "Red Rain"
    if value >= 5:
        return "Amber Rain"
    if value >= 1:
        return "Showers"
    return "Dry"


def _categorize_aqhi(value: float) -> str:
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
    if not raw:
        return datetime.now(timezone.utc)
    for fmt in ISO_VARIANTS:
        try:
            return datetime.strptime(raw, fmt)
        except (ValueError, TypeError):
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
    cache_path = _cache_path(mock_path, key)
    if config.app.use_mock_data:
        payload = _load_from_disk(mock_path)
        _persist_cache(cache_path, payload)
    else:
        payload = _fetch_live_payload(url, cache_path, parser=parser)
    if key and isinstance(payload, dict):
        if key in payload:
            return payload[key]
        nested = payload.get("data")
        if isinstance(nested, dict) and key in nested:
            return nested[key]
    return payload


def _fetch_live_payload(
    url: str, cache_path: Path, parser: Callable[[str], Any] | None = None
) -> Any:
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(url, timeout=10, headers=HTTP_HEADERS)
            response.raise_for_status()
            if parser:
                payload = parser(response.text)
            else:
                payload = response.json()
            _persist_cache(cache_path, payload)
            return payload
        except (requests.RequestException, ValueError, ET.ParseError) as exc:
            last_error = exc
            LOGGER.warning(
                "Attempt %s/%s to fetch %s failed: %s",
                attempt,
                MAX_ATTEMPTS,
                url,
                exc,
            )
    cached = _load_cached_payload(cache_path)
    if cached is not None:
        LOGGER.info("Using cached payload from %s for %s", cache_path, url)
        return cached
    if last_error:
        raise last_error
    raise RuntimeError(f"Unable to fetch payload from {url}")


def _cache_path(mock_path: Path, key: str | None) -> Path:
    identifier = (key or mock_path.stem or "payload").strip() or "payload"
    safe = "".join(c if c.isalnum() or c in {"-", "_"} else "_" for c in identifier)
    return mock_path.parent / f"last_{safe}.json"


def _persist_cache(path: Path, payload: Any) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh)
    except OSError as exc:  # pragma: no cover - cache failures are non-fatal
        LOGGER.debug("Unable to persist payload cache %s: %s", path, exc)


def _load_cached_payload(path: Path) -> Any | None:
    try:
        return _load_from_disk(path)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        LOGGER.warning("Cached payload at %s is invalid: %s", path, exc)
        return None


def _load_from_disk(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _parse_traffic_xml(text: str) -> Dict[str, Any]:
    root = ET.fromstring(text)
    incidents = []
    for message in root.findall(".//message"):
        payload: Dict[str, Any] = {}
        for child in message:
            key = child.tag.lower()
            value = child.text or ""
            payload[key] = value.strip()
        region = (
            payload.get("district_en")
            or payload.get("direction_en")
            or payload.get("location_en")
            or payload.get("incident_heading_en")
            or ""
        )
        severity = (
            payload.get("incident_heading_en")
            or payload.get("incident_detail_en")
            or payload.get("incident_status_en")
            or "Info"
        )
        description = (
            payload.get("content_en")
            or payload.get("incident_detail_en")
            or payload.get("incident_heading_en")
            or "Traffic update"
        )
        incidents.append(
            {
                "region": region,
                "severity": severity,
                "content": description,
                "description": description,
                "update_time": payload.get("announcement_date"),
                "location": payload.get("location_en"),
                "direction": payload.get("direction_en"),
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
