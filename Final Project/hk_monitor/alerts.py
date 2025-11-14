"""Change detection utilities for the HK Conditions Monitor."""

# === Alerting layer ===

# This module is the glue between storage and presentation: it inspects the
# most recent rows, compares them to their predecessors, and emits alert
# messages through messenger implementations.  The comments describe each stage
# so the control flow is easy to follow.
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Protocol, TextIO
import logging
import sqlite3
import sys

from . import db

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AlertMessage:
    metric: str
    previous: str
    current: str
    description: str

    def format(self) -> str:
        """Return a printable, two-line alert message."""

        # Keep the first line compact so console output stays readable; the
        # second line contains the detailed description from the record.
        header = f"[{self.metric.upper()}] {self.previous} -> {self.current}"
        return f"{header}\n{self.description}"


class Messenger(Protocol):
    """Simple protocol describing objects that can receive alert messages."""

    def send(self, message: AlertMessage) -> None:
        ...


class ConsoleMessenger:
    """Messenger that prints alerts to stdout for local demos."""

    def __init__(self, stream: Optional[TextIO] = None):
        self.stream = stream or sys.stdout

    def send(self, message: AlertMessage) -> None:  # pragma: no cover - console feedback
        text = message.format()
        logger.info("[ALERT] %s", text.replace("\n", " | "))
        print(text, file=self.stream)


class ChangeDetector:
    def __init__(
        self,
        conn: sqlite3.Connection,
        messenger: Optional[Messenger] = None,
    ):
        self.conn = conn
        self.messenger = messenger or ConsoleMessenger()
        self.table_config: Dict[str, Callable[[sqlite3.Row], AlertMessage]] = {
            "warnings": self._format_warning,
            "rain": self._format_rain,
            "aqhi": self._format_aqhi,
            "traffic": self._format_traffic,
        }

    def run(self) -> None:
        """Compare the newest and previous rows per table and send alerts."""

        # Step 1: iterate over each metric table so different feed types can be
        # formatted independently.
        for table, formatter in self.table_config.items():
            rows = db.get_last_two(self.conn, table)
            if len(rows) < 2:
                continue
            previous, current = rows[1], rows[0]
            if _extract_category(previous) == _extract_category(current):
                continue
            # Step 2: lazily format the alert so expensive rendering only occurs
            # when a real change has been detected.
            alert = formatter(current)
            alert.previous = _extract_category(previous)
            alert.current = _extract_category(current)
            self.messenger.send(alert)

    def _format_warning(self, row: sqlite3.Row) -> AlertMessage:
        return AlertMessage(
            metric="Warnings",
            previous=row["level"],
            current=row["level"],
            description=row["message"],
        )

    def _format_rain(self, row: sqlite3.Row) -> AlertMessage:
        description = f"{row['district']}: {row['intensity']}"
        return AlertMessage(
            metric="Rain",
            previous=row["intensity"],
            current=row["intensity"],
            description=description,
        )

    def _format_aqhi(self, row: sqlite3.Row) -> AlertMessage:
        description = f"{row['station']} AQHI {row['value']:.1f}"
        return AlertMessage(
            metric="AQHI",
            previous=row["category"],
            current=row["category"],
            description=description,
        )

    def _format_traffic(self, row: sqlite3.Row) -> AlertMessage:
        return AlertMessage(
            metric="Traffic",
            previous=row["severity"],
            current=row["severity"],
            description=row["description"],
        )


def _extract_category(row: sqlite3.Row) -> str:
    """Return a string that represents the severity/category for the row."""

    # Step 1: prioritise semantic fields so warnings/rain/AQHI/traffic produce
    # consistent alert headers regardless of table.
    for key in ("category", "level", "intensity", "severity"):
        if key in row.keys():
            return str(row[key])
    return ""


__all__ = ["ChangeDetector", "AlertMessage", "ConsoleMessenger", "Messenger"]
