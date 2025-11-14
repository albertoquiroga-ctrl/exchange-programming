"""SQLite helpers for persisting snapshots."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import sqlite3
from pathlib import Path
from typing import Dict, Iterator, List, Optional

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


@dataclass(slots=True)
class WarningRecord:
    level: str
    message: str
    updated_at: datetime


@dataclass(slots=True)
class RainRecord:
    district: str
    intensity: str
    updated_at: datetime


@dataclass(slots=True)
class AqhiRecord:
    station: str
    category: str
    value: float
    updated_at: datetime


@dataclass(slots=True)
class TrafficRecord:
    severity: str
    description: str
    updated_at: datetime


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
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


def save_warning(conn: sqlite3.Connection, record: WarningRecord) -> None:
    conn.execute(
        "INSERT INTO warnings(level, message, updated_at) VALUES (?, ?, ?)",
        (record.level, record.message, record.updated_at.strftime(ISO_FORMAT)),
    )
    conn.commit()


def save_rain(conn: sqlite3.Connection, record: RainRecord) -> None:
    conn.execute(
        "INSERT INTO rain(district, intensity, updated_at) VALUES (?, ?, ?)",
        (record.district, record.intensity, record.updated_at.strftime(ISO_FORMAT)),
    )
    conn.commit()


def save_aqhi(conn: sqlite3.Connection, record: AqhiRecord) -> None:
    conn.execute(
        "INSERT INTO aqhi(station, category, value, updated_at) VALUES (?, ?, ?, ?)",
        (
            record.station,
            record.category,
            record.value,
            record.updated_at.strftime(ISO_FORMAT),
        ),
    )
    conn.commit()


def save_traffic(conn: sqlite3.Connection, record: TrafficRecord) -> None:
    conn.execute(
        "INSERT INTO traffic(severity, description, updated_at) VALUES (?, ?, ?)",
        (record.severity, record.description, record.updated_at.strftime(ISO_FORMAT)),
    )
    conn.commit()


def _fetch_latest_two(conn: sqlite3.Connection, table: str) -> List[sqlite3.Row]:
    cur = conn.execute(
        f"SELECT * FROM {table} ORDER BY id DESC LIMIT 2"
    )
    return list(cur.fetchall())


def get_latest(conn: sqlite3.Connection) -> Dict[str, Optional[sqlite3.Row]]:
    return {
        "warnings": _fetch_latest_row(conn, "warnings"),
        "rain": _fetch_latest_row(conn, "rain"),
        "aqhi": _fetch_latest_row(conn, "aqhi"),
        "traffic": _fetch_latest_row(conn, "traffic"),
    }


def _fetch_latest_row(conn: sqlite3.Connection, table: str) -> Optional[sqlite3.Row]:
    cur = conn.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 1")
    return cur.fetchone()


def get_last_two(conn: sqlite3.Connection, table: str) -> List[sqlite3.Row]:
    return _fetch_latest_two(conn, table)


@contextmanager
def connect(db_path: Path) -> Iterator[sqlite3.Connection]:
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
    "get_last_two",
    "connect",
]
