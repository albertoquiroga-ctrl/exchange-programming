"""Data collectors for HK public data feeds."""

# === Snapshot collection entry points ===

# The comments in this module walk through the full "collector" leg of the
# pipeline: we start by orchestrating a refresh, then branch into feed-specific
# helpers, and finally drop into utility routines for parsing, caching, and
# HTTP I/O.
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

    # Step 1: decide whether to open a fresh connection so the collector can be
    # reused both by the CLI (which passes its own connection) and tests.
    if conn is None:
        from .db import connect

        # Step 2: open a context-managed connection for one-shot collectors and
        # immediately persist the fetched snapshot.
        with connect(config.app.database_path) as connection:
            _collect(config, connection)
            return db.get_latest_snapshot(connection)
    else:
        # Step 2b: reuse the provided connection to keep the surrounding
        # transaction scope intact.
        _collect(config, conn)
        return db.get_latest_snapshot(conn)


def _collect(config: Config, conn: sqlite3.Connection) -> None:
    """Run each feed collector in turn, writing rows when data is present."""

    # Step 3: pull the weather warning feed first so dashboard users see the
    # high-severity alerts immediately.
    warning_record = fetch_warning(config)
    if warning_record is not None:
        db.save_warning(conn, warning_record)

    # Step 4: hydrate rain, AQHI, then traffic data; every helper returns a
    # domain record or ``None`` so empty feeds simply skip persistence.
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
    """Return the latest weather warning, if any."""

    # Step 1: pull either the live payload or the mock JSON, caching the result
    # keyed by "warnings" so subsequent runs can fall back to disk if needed.
    data = _get_payload(
        config, config.api.warnings_url, config.mocks.warnings, key="warnings"
    )
    # Step 2: the API swaps between "details" and "warning" arrays, so probe
    # both before bailing out.
    details = data.get("details") or data.get("warning") or []
    if not details:
        return None
    chosen = details[0]
    # Step 3: prefer the entry-level timestamp but fall back to the dataset-wide
    # update time so records always receive a concrete ``datetime``.
    timestamp = _parse_time(
        chosen.get("updateTime") or data.get("updateTime")
    )
    return db.WarningRecord(
        level=str(level),
        message=str(message),
        updated_at=_parse_time(str(update_time) if update_time else None),
    )


def fetch_rain(config: Config) -> db.RainRecord | None:
    """Return a rain record for the selected district."""

    # Step 1: download the rainfall feed (or cached mock) under the "rainfall"
    # cache key because some payloads pack multiple data types in one file.
    data = _get_payload(
        config, config.api.rainfall_url, config.mocks.rainfall, key="rainfall"
    )
    # Step 2: normalize the payload, accommodating both "data" and nested
    # "rainfall" -> "data" shapes so the subsequent search is stable.
    if "data" in data:
        rainfall_data = data.get("data", [])
    else:
        rainfall_data = (data.get("rainfall") or {}).get("data", [])
    # Step 3: scan for the configured district so users can swap targets via the
    # CLI without editing this function.
    district_entry = next(
        (row for row in rainfall_data if row.get("place") == config.app.rain_district),
        None,
    )
    if not district_entry:
        return None
    # Step 4: cast to ``float`` because the API often ships strings; forcing a
    # float here keeps comparison logic deterministic.
    value = float(district_entry.get("max", district_entry.get("value", 0)) or 0)
    return db.RainRecord(
        district=district,
        intensity=intensity,
        updated_at=_parse_time(str(record_time) if record_time else None),
    )


def fetch_aqhi(config: Config) -> db.AqhiRecord | None:
    """Return AQHI metrics for the configured station."""

    # Step 1: normalize the AQHI payload into a list of stations.
    data = _get_payload(config, config.api.aqhi_url, config.mocks.aqhi, key="aqhi")
    if isinstance(data, list):
        stations = data
    else:
        stations = data.get("aqhi") or data.get("data") or []
    # Step 2: pick the station requested by the dashboard.
    station_entry = next(
        (row for row in stations if row.get("station") == config.app.aqhi_station),
        None,
    )
    if not station_entry:
        return None
    # Step 3: cast to float so downstream comparisons and pandas aggregations
    # behave consistently even if the API returns strings.
    value = float(station_entry.get("aqhi", station_entry.get("value", 0)) or 0)
    # Step 4: reuse explicit health-risk labels when provided, otherwise derive
    # a text category from the numeric AQHI value.
    category = (
        station_entry.get("health_risk")
        or station_entry.get("category")
        or _categorize_aqhi(value)
    )
    publish_time = station_entry.get("publish_date") or station_entry.get("time")
    dataset_time = None
    if isinstance(data, dict):
        # Having a dataset-level timestamp helps avoid "unknown" update times
        # when the per-station payload omits it.
        dataset_time = data.get("publishDate") or data.get("updateTime")
    return db.AqhiRecord(
        station=station,
        category=str(category),
        value=value,
        updated_at=_parse_time(str(timestamp_source) if timestamp_source else None),
    )


def fetch_traffic(config: Config) -> db.TrafficRecord | None:
    """Return the latest traffic incident that matches the configured region."""

    # Step 1: traffic uses XML upstream, so pass a parser callback that converts
    # it to a list of incident dictionaries before caching.
    data = _get_payload(
        config,
        config.api.traffic_url,
        config.mocks.traffic,
        key="trafficnews",
        parser=_parse_traffic_xml,
    )

    target = config.app.traffic_region.strip().lower()

    def _matches(entry: Dict[str, Any]) -> bool:
        if not target:
            return True
        # Glue all textual fields together and lower-case them so matching
        # behaves like a fuzzy contains query over the user's region string.
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
    if not updated and isinstance(data, dict):
        # Reuse the feed-level timestamp when individual items omit update_time
        # so the dashboard always shows when data was last refreshed.
        updated = data.get("updateTime")
    return db.TrafficRecord(
        severity=str(severity).title(),
        description=normalized_description,
        updated_at=_parse_time(str(updated) if updated else None),
    )


# === Domain-specific helpers ===

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
    """Convert the API timestamps into timezone-aware datetimes."""

    # Step 1: timestamps are optional in almost every feed, so fall back to the
    # current UTC time when nothing is supplied.
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
    """Return either the mock payload or the live HTTP response, caching both."""

    # Step 1: derive a deterministic cache path so live payloads can be reused
    # whenever the network fails or is offline.
    cache_path = _cache_path(mock_path, key)
    if config.app.use_mock_data:
        # Step 2a: load the mock payload from disk and refresh the cache so the
        # most recent "live" data is always available for demos.
        payload = _load_from_disk(mock_path)
        _persist_cache(cache_path, payload)
    else:
        # Step 2b: hit the real API, storing the parsed representation on disk
        # so later runs can fall back gracefully.
        payload = _fetch_live_payload(url, cache_path, parser=parser)
    if key and isinstance(payload, dict):
        # Step 3: many feeds wrap their data in either top-level keys or "data"
        # namespaces; peel those layers automatically when a key is provided.
        if key in payload:
            return payload[key]
        nested = payload.get("data")
        if isinstance(nested, dict) and key in nested:
            return nested[key]
    return payload


def _fetch_live_payload(
    url: str, cache_path: Path, parser: Callable[[str], Any] | None = None
) -> Any:
    """Hit the HTTP endpoint with retries and cache persistence."""

    # Step 1: keep the last error around so we can re-raise it if caching also
    # fails.
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            # Step 2: issue the GET request with an explicit User-Agent and
            # timeout so the public API operators can identify the client.
            response = requests.get(url, timeout=10, headers=HTTP_HEADERS)
            response.raise_for_status()
            if parser:
                # XML feeds need a custom parser before caching; the parser
                # returns a dict/list so downstream code sees JSON-like data.
                payload = parser(response.text)
            else:
                payload = response.json()
            _persist_cache(cache_path, payload)
            return payload
        except (requests.RequestException, ValueError, ET.ParseError) as exc:
            # Step 3: retry a few times, logging warnings so operators can trace
            # transient failures when diagnosing outages.
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
        # Step 4: prefer a stale-but-valid cached payload to raising an error;
        # the CLI already highlights when data is old.
        LOGGER.info("Using cached payload from %s for %s", cache_path, url)
        return cached
    if last_error:
        raise last_error
    raise RuntimeError(f"Unable to fetch payload from {url}")


def _cache_path(mock_path: Path, key: str | None) -> Path:
    """Build a filesystem-friendly cache filename derived from the payload."""

    # Step 1: prefer domain-specific keys so caches remain readable when
    # multiple endpoints share the same mock folder.
    identifier = (key or mock_path.stem or "payload").strip() or "payload"
    safe = "".join(c if c.isalnum() or c in {"-", "_"} else "_" for c in identifier)
    return mock_path.parent / f"last_{safe}.json"


def _persist_cache(path: Path, payload: Any) -> None:
    """Write the latest payload to disk for offline replays."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh)
    except OSError as exc:  # pragma: no cover - cache failures are non-fatal
        LOGGER.debug("Unable to persist payload cache %s: %s", path, exc)


def _load_cached_payload(path: Path) -> Any | None:
    """Load the previously cached payload, if the file is still valid."""
    try:
        return _load_from_disk(path)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        LOGGER.warning("Cached payload at %s is invalid: %s", path, exc)
        return None


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
