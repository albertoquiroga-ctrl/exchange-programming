"""Change detection utilities for the HK Conditions Monitor."""

# === Alerting layer ===

# This module is the glue between storage and presentation: it inspects the
# most recent rows, compares them to their predecessors, and emits alert
# messages through messenger implementations.  The comments describe each stage
# so the control flow is easy to follow.
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Protocol, Sequence, TextIO
from pathlib import Path
import logging
import sqlite3
import sys

try:
    from . import db
except ImportError:  # pragma: no cover - allow running as a script
    # Allow `python alerts.py` to work even if the package is not installed.
    PACKAGE_ROOT = Path(__file__).resolve().parents[1]
    if str(PACKAGE_ROOT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_ROOT))
    from hk_monitor import db

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AlertMessage:
    """Structured alert that captures the metric and the before/after states."""

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
        """Push a fully formatted alert to the downstream transport."""
        ...


class ConsoleMessenger:
    """Messenger that prints alerts to stdout for local demos."""

    def __init__(self, stream: Optional[TextIO] = None):
        """Allow dependency injection of the output stream for easier testing."""
        self.stream = stream or sys.stdout

    def send(self, message: AlertMessage) -> None:  # pragma: no cover - console feedback
        """Render the alert on the console and mirror it through logging."""
        text = message.format()
        logger.info("[ALERT] %s", text.replace("\n", " | "))
        print(text, file=self.stream)


class ChangeDetector:
    """Compare the two newest rows per metric and emit alerts when categories change."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        messenger: Optional[Messenger] = None,
    ):
        """Store the database handle and configure table-specific formatters."""
        self.conn = conn
        self.messenger = messenger or ConsoleMessenger()
        # The formatters convert raw sqlite rows into consistent AlertMessages.
        self.table_config: Dict[str, Callable[[sqlite3.Row], AlertMessage]] = {
            "warnings": self._format_warning,
            "rain": self._format_rain,
            "aqhi": self._format_aqhi,
            "traffic": self._format_traffic,
        }

    def run(self) -> int:
        """Compare the newest and previous rows per table and send alerts.

        Returns:
            Number of alerts emitted during this run.
        """

        # Step 1: iterate over each metric table so different feed types can be
        # formatted independently.
        triggered = 0
        for table, formatter in self.table_config.items():
            # Pull the two latest rows so we can compare "current" vs "previous".
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
            triggered += 1
        return triggered

    def _format_warning(self, row: sqlite3.Row) -> AlertMessage:
        """Translate warning rows into a consistent AlertMessage structure."""
        return AlertMessage(
            metric="Warnings",
            previous=row["level"],
            current=row["level"],
            description=row["message"],
        )

    def _format_rain(self, row: sqlite3.Row) -> AlertMessage:
        """Describe rainfall alerts by pairing the district and the intensity."""
        description = f"{row['district']}: {row['intensity']}"
        return AlertMessage(
            metric="Rain",
            previous=row["intensity"],
            current=row["intensity"],
            description=description,
        )

    def _format_aqhi(self, row: sqlite3.Row) -> AlertMessage:
        """Summarise AQHI changes with the numeric value and station name."""
        description = f"{row['station']} AQHI {row['value']:.1f}"
        return AlertMessage(
            metric="AQHI",
            previous=row["category"],
            current=row["category"],
            description=description,
        )

    def _format_traffic(self, row: sqlite3.Row) -> AlertMessage:
        """Surface traffic incidents, highlighting severity and description."""
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
    # Falling back to an empty string avoids crashes while keeping noise low.
    return ""


def _print_snapshot(snapshot: Dict[str, Optional[sqlite3.Row]]) -> None:
    """Print the freshest readings so the CLI is still informative without alerts."""

    # Showing the latest values keeps the terminal output useful even when
    # nothing triggered, so students can confirm the ingestion pipeline works.
    print("\nLatest snapshot:")

    def _print_section(title: str, text: str) -> None:
        underline = "-" * len(title)
        print(f"{title}\n{underline}\n{text}\n")

    _print_section("Warnings", _describe_warning(snapshot.get("warnings")))
    _print_section("Rain", _describe_rain(snapshot.get("rain")))
    _print_section("AQHI", _describe_aqhi(snapshot.get("aqhi")))
    _print_section("Traffic", _describe_traffic(snapshot.get("traffic")))


def _describe_warning(row: Optional[sqlite3.Row]) -> str:
    if not row:
        return "No warning data available."
    # Joining the lines here produces a friendly paragraph for the CLI snapshot.
    return (
        f"Level: {row['level']}\n"
        f"Message: {row['message']}\n"
        f"Updated: {row['updated_at']}"
    )


def _describe_rain(row: Optional[sqlite3.Row]) -> str:
    if not row:
        return "No rain data available."
    # Rain sections emphasize geography because alerts are location specific.
    return (
        f"District: {row['district']}\n"
        f"Intensity: {row['intensity']}\n"
        f"Updated: {row['updated_at']}"
    )


def _describe_aqhi(row: Optional[sqlite3.Row]) -> str:
    if not row:
        return "No AQHI data available."
    # Format numeric AQHI with one decimal place just like the government feed.
    return (
        f"Station: {row['station']}\n"
        f"Category: {row['category']}\n"
        f"Value: {row['value']:.1f}\n"
        f"Updated: {row['updated_at']}"
    )


def _describe_traffic(row: Optional[sqlite3.Row]) -> str:
    if not row:
        return "No traffic data available."
    # Traffic incidents often supply a short paragraph, so we trust the source.
    return (
        f"Severity: {row['severity']}\n"
        f"{row['description']}\n"
        f"Updated: {row['updated_at']}"
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Entry point for running the change detector as a standalone script."""

    # Standard argparse usage so the script can be customised from the CLI.
    parser = argparse.ArgumentParser(description="HK Conditions Monitor alerts")
    parser.add_argument(
        "--config",
        default="config.toml",
        help="Path to the TOML configuration file (default: config.toml)",
    )
    args = parser.parse_args(argv)

    try:
        from .config import Config
    except ImportError:  # pragma: no cover - mirrors the db fallback above
        from hk_monitor.config import Config

    config = Config.load(args.config)
    with db.connect(config.app.database_path) as conn:
        # Pull today's snapshot before running the change detection so the
        # summary can be printed whether or not alerts fire.
        snapshot = db.get_latest(conn)
        count = ChangeDetector(conn).run()
    if count == 0:
        print("No alerts triggered.")
    _print_snapshot(snapshot)


__all__ = ["ChangeDetector", "AlertMessage", "ConsoleMessenger", "Messenger"]


if __name__ == "__main__":
    main()
