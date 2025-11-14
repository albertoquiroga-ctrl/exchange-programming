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
            return db.get_latest(connection)
    else:
        _collect(config, conn)
        return db.get_latest(conn)


def _collect(config: Config, conn: sqlite3.Connection) -> None:
    warning_record = fetch_warning(config)
    if warning_record:
        db.save_warning(conn, warning_record)

    rain_record = fetch_rain(config)
    if rain_record:
        db.save_rain(conn, rain_record)

    aqhi_record = fetch_aqhi(config)
    if aqhi_record:
        db.save_aqhi(conn, aqhi_record)

    traffic_record = fetch_traffic(config)
    if traffic_record:
        db.save_traffic(conn, traffic_record)


def fetch_warning(config: Config) -> db.WarningRecord | None:
    data = _get_payload(
        config, config.api.warnings_url, config.mocks.warnings, key="warnings"
    )
    details = data.get("details") or data.get("warning") or []
    if not details:
        return None
    chosen = details[0]
    timestamp = _parse_time(
        chosen.get("updateTime") or data.get("updateTime")
    )
    return db.WarningRecord(
        level=chosen.get("warningStatementCode", "UNKNOWN"),
        message=chosen.get("warningMessage", "No warning message supplied."),
        updated_at=timestamp,
    )


def fetch_rain(config: Config) -> db.RainRecord | None:
    data = _get_payload(
        config, config.api.rainfall_url, config.mocks.rainfall, key="rainfall"
    )
    if "data" in data:
        rainfall_data = data.get("data", [])
    else:
        rainfall_data = (data.get("rainfall") or {}).get("data", [])
    district_entry = next(
        (row for row in rainfall_data if row.get("place") == config.app.rain_district),
        None,
    )
    if not district_entry:
        return None
    value = float(district_entry.get("max", district_entry.get("value", 0)) or 0)
    return db.RainRecord(
        district=config.app.rain_district,
        intensity=_categorize_rain(value),
        updated_at=_parse_time(district_entry.get("recordTime") or data.get("updateTime")),
    )


def fetch_aqhi(config: Config) -> db.AqhiRecord | None:
    data = _get_payload(config, config.api.aqhi_url, config.mocks.aqhi, key="aqhi")
    if isinstance(data, list):
        stations = data
    else:
        stations = data.get("aqhi") or data.get("data") or []
    station_entry = next(
        (row for row in stations if row.get("station") == config.app.aqhi_station),
        None,
    )
    if not station_entry:
        return None
    value = float(station_entry.get("aqhi", station_entry.get("value", 0)) or 0)
    category = (
        station_entry.get("health_risk")
        or station_entry.get("category")
        or _categorize_aqhi(value)
    )
    publish_time = station_entry.get("publish_date") or station_entry.get("time")
    dataset_time = None
    if isinstance(data, dict):
        dataset_time = data.get("publishDate") or data.get("updateTime")
    return db.AqhiRecord(
        station=config.app.aqhi_station,
        category=str(category),
        value=value,
        updated_at=_parse_time(publish_time or dataset_time),
    )


def fetch_traffic(config: Config) -> db.TrafficRecord | None:
    data = _get_payload(
        config,
        config.api.traffic_url,
        config.mocks.traffic,
        key="trafficnews",
        parser=_parse_traffic_xml,
    )
    if isinstance(data, list):
        incidents = data
    else:
        incidents = data.get("trafficnews") or data.get("incidents") or []
    if not incidents:
        return None

    target = config.app.traffic_region.strip().lower()

    def _matches(entry: Dict[str, Any]) -> bool:
        if not target:
            return True
        haystack = " ".join(
            filter(
                None,
                [
                    entry.get("region"),
                    entry.get("location"),
                    entry.get("direction"),
                    entry.get("content"),
                ],
            )
        ).lower()
        return target in haystack

    entry = next((row for row in incidents if _matches(row)), None) or incidents[0]
    severity = entry.get("severity", entry.get("category", "info"))
    description = entry.get("content") or entry.get("summary") or "Traffic update"
    updated = entry.get("update_time")
    if not updated and isinstance(data, dict):
        updated = data.get("updateTime")
    return db.TrafficRecord(
        severity=severity.title(),
        description=description.strip(),
        updated_at=_parse_time(updated),
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
        payload = {child.tag.lower(): (child.text or "").strip() for child in message}
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
