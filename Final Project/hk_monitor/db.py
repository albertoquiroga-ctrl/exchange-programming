"""SQLite helpers for persisting snapshots."""

# === Persistence layer ===

# This module anchors the "database" leg of the pipeline.  Everything is
# intentionally small and synchronous so the inline comments can describe every
# logical step from connection to query.
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class WarningRecord:
    """Row model for severe weather warnings from the HK Observatory."""

    def __init__(self, level: str, message: str, updated_at: datetime):
        self.level = level
        self.message = message
        self.updated_at = updated_at


class RainRecord:
    """Single reading of rain intensity for the configured district."""

    def __init__(self, district: str, intensity: str, updated_at: datetime):
        self.district = district
        self.intensity = intensity
        self.updated_at = updated_at


class AqhiRecord:
    """Air Quality Health Index measurement with numeric value and category."""

    def __init__(self, station: str, category: str, value: float, updated_at: datetime):
        self.station = station
        self.category = category
        self.value = value
        self.updated_at = updated_at


class TrafficRecord:
    """Description of a traffic incident affecting one of the regions."""

    def __init__(self, severity: str, description: str, updated_at: datetime):
        self.severity = severity
        self.description = description
        self.updated_at = updated_at


def init_db(db_path: Path) -> sqlite3.Connection:
    """Create or open the SQLite database and ensure the schema exists."""

    # Step 1: create the parent folder when running the first time so sqlite3
    # does not fail with a cryptic "unable to open database" error.
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    # Step 2: return rows as ``sqlite3.Row`` objects so the rest of the code can
    # access columns by name, which keeps rendering code readable.
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create all snapshot tables if they do not exist."""

    # Step 1: a single ``executescript`` call keeps schema management simple and
    # ensures every dashboard run uses identical table definitions.
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS rain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district TEXT NOT NULL,
            intensity TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS aqhi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station TEXT NOT NULL,
            category TEXT NOT NULL,
            value REAL NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )
    conn.commit()


def save_warning(conn: sqlite3.Connection, record: Any) -> None:
    """Insert a warning row while normalising timestamps."""

    # ``strftime`` stores ``datetime`` objects in ISO format so ChangeDetector
    # can compare strings lexicographically without re-parsing.
    conn.execute(
        "INSERT INTO warnings(level, message, updated_at) VALUES (?, ?, ?)",
        (
            _record_value(record, "level"),
            _record_value(record, "message"),
            _normalise_timestamp(_record_value(record, "updated_at")).strftime(
                ISO_FORMAT
            ),
        ),
    )
    conn.commit()


def save_rain(conn: sqlite3.Connection, record: Any) -> None:
    """Insert a rain row for the monitored district."""
    conn.execute(
        "INSERT INTO rain(district, intensity, updated_at) VALUES (?, ?, ?)",
        (
            _record_value(record, "district"),
            _record_value(record, "intensity"),
            _normalise_timestamp(_record_value(record, "updated_at")).strftime(
                ISO_FORMAT
            ),
        ),
    )
    conn.commit()


def save_aqhi(conn: sqlite3.Connection, record: Any) -> None:
    """Insert an AQHI row along with the numeric value."""
    conn.execute(
        "INSERT INTO aqhi(station, category, value, updated_at) VALUES (?, ?, ?, ?)",
        (
            _record_value(record, "station"),
            _record_value(record, "category"),
            _record_value(record, "value"),
            _normalise_timestamp(_record_value(record, "updated_at")).strftime(
                ISO_FORMAT
            ),
        ),
    )
    conn.commit()


def save_traffic(conn: sqlite3.Connection, record: Any) -> None:
    """Insert a traffic row describing the latest incident."""
    conn.execute(
        "INSERT INTO traffic(severity, description, updated_at) VALUES (?, ?, ?)",
        (
            _record_value(record, "severity"),
            _record_value(record, "description"),
            _normalise_timestamp(_record_value(record, "updated_at")).strftime(
                ISO_FORMAT
            ),
        ),
    )
    conn.commit()


def _fetch_latest_two(conn: sqlite3.Connection, table: str) -> List[sqlite3.Row]:
    """Return the newest two rows for change detection."""
    # ``table`` is controlled by the caller (warnings/rain/aqhi/traffic), so the
    # simple f-string keeps the query readable for instructional purposes.
    cur = conn.execute(
        f"SELECT * FROM {table} ORDER BY id DESC LIMIT 2"
    )
    return list(cur.fetchall())


def get_latest(conn: sqlite3.Connection) -> Dict[str, Optional[sqlite3.Row]]:
    """Fetch the most recent row for every dashboard tile."""
    return {
        "warnings": _fetch_latest_row(conn, "warnings"),
        "rain": _fetch_latest_row(conn, "rain"),
        "aqhi": _fetch_latest_row(conn, "aqhi"),
        "traffic": _fetch_latest_row(conn, "traffic"),
    }


def get_latest_snapshot(conn: sqlite3.Connection) -> Dict[str, Optional[sqlite3.Row]]:
    """Backward compatible alias used by older modules/tests."""
    return get_latest(conn)


def _fetch_latest_row(conn: sqlite3.Connection, table: str) -> Optional[sqlite3.Row]:
    """Return the newest row for the requested table, if any."""
    cur = conn.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 1")
    return cur.fetchone()


def get_last_two(conn: sqlite3.Connection, table: str) -> List[sqlite3.Row]:
    """Public wrapper used by ChangeDetector to compare consecutive rows."""
    return _fetch_latest_two(conn, table)


def _record_value(record: Any, key: str) -> Any:
    """Support dict-like and object-like records transparently."""

    if isinstance(record, dict):
        return record.get(key)
    return getattr(record, key)


def _normalise_timestamp(value: Any) -> datetime:
    """Accept datetime objects or ISO formatted strings for updated_at."""

    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise TypeError("updated_at must be a datetime or ISO string") from exc
    raise TypeError("updated_at must be a datetime or ISO string")


@contextmanager
def connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Context manager that opens, yields, then closes the SQLite connection."""

    # Reuse ``init_db`` so every caller benefits from auto-migrations.
    conn = init_db(db_path)
    try:
        yield conn
    finally:
        conn.close()


__all__ = [
    "WarningRecord",
    "RainRecord",
    "AqhiRecord",
    "TrafficRecord",
    "init_db",
    "save_warning",
    "save_rain",
    "save_aqhi",
    "save_traffic",
    "get_latest",
    "get_latest_snapshot",
    "get_last_two",
    "connect",
]
