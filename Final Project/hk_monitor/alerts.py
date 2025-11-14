"""Change detection utilities for the HK Conditions Monitor."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, TextIO
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

    def run(self) -> None:
        self._check_warnings()
        self._check_rain()
        self._check_aqhi()
        self._check_traffic()

    def _check_warnings(self) -> None:
        rows = db.get_last_two_warnings(self.conn)
        if len(rows) < 2:
            return
        previous = rows[1]
        current = rows[0]
        if compare_warning_rows(previous, current):
            print_warning_alert(self.messenger, previous, current)

    def _check_rain(self) -> None:
        rows = db.get_last_two_rain(self.conn)
        if len(rows) < 2:
            return
        previous = rows[1]
        current = rows[0]
        if compare_rain_rows(previous, current):
            print_rain_alert(self.messenger, previous, current)

    def _check_aqhi(self) -> None:
        rows = db.get_last_two_aqhi(self.conn)
        if len(rows) < 2:
            return
        previous = rows[1]
        current = rows[0]
        if compare_aqhi_rows(previous, current):
            print_aqhi_alert(self.messenger, previous, current)

    def _check_traffic(self) -> None:
        rows = db.get_last_two_traffic(self.conn)
        if len(rows) < 2:
            return
        previous = rows[1]
        current = rows[0]
        if compare_traffic_rows(previous, current):
            print_traffic_alert(self.messenger, previous, current)


def compare_warning_rows(previous: sqlite3.Row, current: sqlite3.Row) -> bool:
    previous_level = previous["level"]
    current_level = current["level"]
    return str(previous_level) != str(current_level)


def print_warning_alert(
    messenger: Messenger, previous: sqlite3.Row, current: sqlite3.Row
) -> None:
    message = AlertMessage(
        metric="Warnings",
        previous=str(previous["level"]),
        current=str(current["level"]),
        description=str(current["message"]),
    )
    messenger.send(message)


def compare_rain_rows(previous: sqlite3.Row, current: sqlite3.Row) -> bool:
    previous_value = previous["intensity"]
    current_value = current["intensity"]
    return str(previous_value) != str(current_value)


def print_rain_alert(
    messenger: Messenger, previous: sqlite3.Row, current: sqlite3.Row
) -> None:
    description = f"{current['district']}: {current['intensity']}"
    message = AlertMessage(
        metric="Rain",
        previous=str(previous["intensity"]),
        current=str(current["intensity"]),
        description=description,
    )
    messenger.send(message)


def compare_aqhi_rows(previous: sqlite3.Row, current: sqlite3.Row) -> bool:
    previous_value = previous["category"]
    current_value = current["category"]
    return str(previous_value) != str(current_value)


def print_aqhi_alert(
    messenger: Messenger, previous: sqlite3.Row, current: sqlite3.Row
) -> None:
    value_text = f"{current['value']:.1f}"
    description = f"{current['station']} AQHI {value_text}"
    message = AlertMessage(
        metric="AQHI",
        previous=str(previous["category"]),
        current=str(current["category"]),
        description=description,
    )
    messenger.send(message)


def compare_traffic_rows(previous: sqlite3.Row, current: sqlite3.Row) -> bool:
    previous_value = previous["severity"]
    current_value = current["severity"]
    return str(previous_value) != str(current_value)


def print_traffic_alert(
    messenger: Messenger, previous: sqlite3.Row, current: sqlite3.Row
) -> None:
    message = AlertMessage(
        metric="Traffic",
        previous=str(previous["severity"]),
        current=str(current["severity"]),
        description=str(current["description"]),
    )
    messenger.send(message)


__all__ = ["ChangeDetector", "AlertMessage", "ConsoleMessenger", "Messenger"]
