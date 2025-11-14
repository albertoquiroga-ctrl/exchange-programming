"""Data collectors for HK public data feeds."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict
import sqlite3

import requests

from . import db
from .config import Config

ISO_VARIANTS = ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ")


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
    return db.AqhiRecord(
        station=config.app.aqhi_station,
        category=_categorize_aqhi(value),
        value=value,
        updated_at=_parse_time(station_entry.get("time") or data.get("updateTime")),
    )


def fetch_traffic(config: Config) -> db.TrafficRecord | None:
    data = _get_payload(
        config, config.api.traffic_url, config.mocks.traffic, key="trafficnews"
    )
    if isinstance(data, list):
        incidents = data
    else:
        incidents = data.get("trafficnews") or data.get("incidents") or []
    entry = next(
        (row for row in incidents if config.app.traffic_region in row.get("region", "")),
        None,
    )
    if not entry:
        return None
    severity = entry.get("severity", entry.get("category", "info"))
    description = entry.get("content") or entry.get("summary") or "Traffic update"
    return db.TrafficRecord(
        severity=severity.title(),
        description=description.strip(),
        updated_at=_parse_time(entry.get("update_time") or data.get("updateTime")),
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
    config: Config, url: str, mock_path: Path, key: str | None = None
) -> Dict[str, Any]:
    if config.app.use_mock_data:
        with mock_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    else:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()
    if key and isinstance(payload, dict):
        if key in payload:
            return payload[key]
        nested = payload.get("data")
        if isinstance(nested, dict) and key in nested:
            return nested[key]
    return payload


__all__ = [
    "collect_once",
    "fetch_warning",
    "fetch_rain",
    "fetch_aqhi",
    "fetch_traffic",
]
