"""Console demo for the HK Conditions Monitor."""

# === Interactive console front-end ===

# This module is the "face" of the pipeline: we parse CLI flags, drive the
# collectors, persist rows into SQLite, and present a narrated dashboard.  The
# comments explain the order in which each responsibility executes so the file
# reads like a guided tour.
from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

try:
    from . import alerts, collector, db
    from .alerts import ChangeDetector, ConsoleMessenger
    from .config import Config
except ImportError:  # pragma: no cover - allows running as a script
    PACKAGE_ROOT = Path(__file__).resolve().parents[1]
    if str(PACKAGE_ROOT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_ROOT))
    from hk_monitor import alerts, collector, db
    from hk_monitor.alerts import ChangeDetector, ConsoleMessenger
    from hk_monitor.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)


def parse_args() -> argparse.Namespace:
    """Parse CLI options for the dashboard demo."""

    parser = argparse.ArgumentParser(description="HK Conditions Monitor CLI")
    parser.add_argument(
        "--config",
        default="config.toml",
        help="Path to the TOML configuration file (default: config.toml)",
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="Fetch metrics once before showing the dashboard.",
    )
    parser.add_argument(
        "--alerts",
        action="store_true",
        help="Run change detection and print alerts after refreshing data.",
    )
    return parser.parse_args()


def main() -> None:
    """Launch the console dashboard according to the supplied arguments."""

    args = parse_args()
    config = Config.load(args.config)

    with db.connect(config.app.database_path) as conn:
        dashboard = DashboardSession(config, conn, enable_alerts=args.alerts)
        if args.collect:
            dashboard.refresh()
        dashboard.run(skip_initial_refresh=args.collect)


class DashboardSession:
    """Coordinate refreshes, prompts, and optional alerting."""

    def __init__(
        self, config: Config, conn: sqlite3.Connection, enable_alerts: bool = False
    ) -> None:
        self.config = config
        self.conn = conn
        self.enable_alerts = enable_alerts
        self.menu = MenuController(config)
        self.printer = SnapshotPrinter()
        self.history = HistoryReporter(conn)
        self._alert_metrics: Set[str] = set()

    def run(self, skip_initial_refresh: bool = False) -> None:
        print("Launching HK Conditions Monitor dashboard. Press Ctrl+C or choose 'q' to exit.")
        skip_refresh = skip_initial_refresh
        try:
            while True:
                if not skip_refresh:
                    self.refresh()
                else:
                    skip_refresh = False
                if not self.menu.prompt():
                    break
                wait_seconds = max(0, int(self.config.app.poll_interval))
                if wait_seconds:
                    print(f"Waiting {wait_seconds}s before the next automatic refresh...\n")
                    time.sleep(wait_seconds)
        except KeyboardInterrupt:
            print("\nExiting dashboard.")

    def refresh(self) -> None:
        logging.info(
            "Refreshing snapshot for %s / %s / %s",
            self.config.app.rain_district,
            self.config.app.aqhi_station,
            self.config.app.traffic_region,
        )
        collector.collect_once(self.config, self.conn)
        snapshot = db.get_latest(self.conn)
        highlights = self._detect_alerts()
        selection_summary = self.menu.selection_summary()
        self.printer.display(
            snapshot,
            highlights=highlights,
            selection_info=selection_summary,
        )
        self.history.print_report(self.config.app.aqhi_station)

    def _detect_alerts(self) -> Set[str]:
        if not self.enable_alerts:
            self._alert_metrics = set()
            return self._alert_metrics
        messenger = _RecordingMessenger()
        ChangeDetector(self.conn, messenger).run()
        self._alert_metrics = {message.metric for message in messenger.messages}
        return self._alert_metrics


class MenuController:
    """Handle user selections for the dashboard menu."""

    def __init__(self, config: Config):
        self.config = config
        self._options = _load_menu_options(config)

    def prompt(self) -> bool:
        """Return True when a refresh should occur, False to exit."""

        menu_text = "Press Enter to refresh now, or choose: [d]istrict, [a]qhi, [t]raffic, [q]uit"
        while True:
            try:
                choice = input(f"{menu_text}\n> ").strip().lower()
            except EOFError:
                return False
            if choice in ("", "r"):
                return True
            if choice == "q":
                return False
            if choice == "d":
                self._change_selection("rain", "rain district", "rain_district")
                continue
            if choice == "a":
                self._change_selection("aqhi", "AQHI station", "aqhi_station")
                continue
            if choice == "t":
                self._change_selection("traffic", "traffic region", "traffic_region")
                continue
            print("Unknown command. Please choose one of the listed options.")

    def selection_summary(self) -> str:
        return (
            "District: {district} | AQHI station: {station} | Traffic region: {region}".format(
                district=self.config.app.rain_district,
                station=self.config.app.aqhi_station,
                region=self.config.app.traffic_region,
            )
        )

    def _change_selection(
        self,
        option_key: str,
        label: str,
        attribute: str,
    ) -> None:
        options = self._options.get(option_key, [])
        current_value = getattr(self.config.app, attribute)
        print(f"Current {label}: {current_value}")
        if options:
            self._print_options(options)
            selection = input(
                f"Select a new {label} (number) or press Enter to keep current: "
            ).strip()
            if not selection:
                return
            try:
                index = int(selection) - 1
            except ValueError:
                print("Invalid selection, keeping current value.")
                return
            if 0 <= index < len(options):
                new_value = options[index]
                setattr(self.config.app, attribute, new_value)
                print(f"Updated {label} to {new_value}.")
            else:
                print("Selection out of range, keeping current value.")
        else:
            manual = input(f"Type a new {label} and press Enter (blank to cancel): ").strip()
            if manual:
                setattr(self.config.app, attribute, manual)
                print(f"Updated {label} to {manual}.")

    @staticmethod
    def _print_options(options: Sequence[str]) -> None:
        for index, value in enumerate(options, start=1):
            print(f"  {index}. {value}")


class SnapshotPrinter:
    """Format and print the latest snapshot to the console."""

    def display(
        self,
        snapshot: Dict[str, Optional[sqlite3.Row]],
        highlights: Set[str],
        selection_info: Optional[str],
    ) -> None:
        sections = [
            ("Warnings", self._format_warning(snapshot.get("warnings"))),
            ("Rain", self._format_rain(snapshot.get("rain"))),
            ("AQHI", self._format_aqhi(snapshot.get("aqhi"))),
            ("Traffic", self._format_traffic(snapshot.get("traffic"))),
        ]

        separator = "\n" + "=" * 60 + "\n"
        output_lines: List[str] = []
        if selection_info:
            output_lines.append(selection_info)
        for title, body in sections:
            prefix = "*** " if title in highlights else ""
            suffix = " ***" if title in highlights else ""
            header = f"{prefix}{title}{suffix}"
            underline = "-" * len(title)
            section_text = f"{header}\n{underline}\n{body}"
            output_lines.append(section_text)
        print(separator.join(output_lines))

    @staticmethod
    def _format_warning(row: Optional[sqlite3.Row]) -> str:
        if not row:
            return "No warning data."
        return (
            f"Level: {row['level']}\n"
            f"Message: {row['message']}\n"
            f"Updated: {row['updated_at']}"
        )

    @staticmethod
    def _format_rain(row: Optional[sqlite3.Row]) -> str:
        if not row:
            return "No rain data."
        return (
            f"District: {row['district']}\n"
            f"Intensity: {row['intensity']}\n"
            f"Updated: {row['updated_at']}"
        )

    @staticmethod
    def _format_aqhi(row: Optional[sqlite3.Row]) -> str:
        if not row:
            return "No AQHI data."
        value = row["value"]
        value_text = f"{value:.1f}"
        return (
            f"Station: {row['station']}\n"
            f"Category: {row['category']}\n"
            f"Value: {value_text}\n"
            f"Updated: {row['updated_at']}"
        )

    @staticmethod
    def _format_traffic(row: Optional[sqlite3.Row]) -> str:
        if not row:
            return "No traffic data."
        return (
            f"Severity: {row['severity']}\n"
            f"{row['description']}\n"
            f"Updated: {row['updated_at']}"
        )


class HistoryReporter:
    """Generate AQHI history tables for the selected station."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def print_report(self, station: str) -> None:
        report = build_aqhi_history_report(self.conn, station)
        if report:
            print("\n" + report)


class _RecordingMessenger(ConsoleMessenger):
    """Console messenger that keeps the alert list for highlighting."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: List[alerts.AlertMessage] = []

    def send(self, message: alerts.AlertMessage) -> None:  # type: ignore[override]
        super().send(message)
        self.messages.append(message)


# === Menu discovery helpers ===

def _load_menu_options(config: Config) -> Dict[str, List[str]]:
    """Build lookup tables for every dashboard selection type."""

    return {
        "rain": _extract_places(config.mocks.rainfall),
        "aqhi": _extract_aqhi_stations(config.mocks.aqhi),
        "traffic": _extract_regions(config.mocks.traffic),
    }


def _extract_places(path: Path) -> List[str]:
    """Read the mock rainfall payload and list the available districts."""

    try:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except OSError:
        return []
    entries: List[Dict[str, Any]] = []
    if "rainfall" in payload:
        rainfall_section = payload.get("rainfall")
        if isinstance(rainfall_section, dict):
            entries = rainfall_section.get("data", [])
    else:
        entries = payload.get("data", [])
    places: Set[str] = set()
    if isinstance(entries, list):
        for item in entries:
            if isinstance(item, dict) and item.get("place"):
                places.add(str(item["place"]))
    return sorted(places)


def _extract_aqhi_stations(path: Path) -> List[str]:
    """Read the mock AQHI payload and surface unique station names."""

    try:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except OSError:
        return []
    stations: List[Dict[str, Any]] = []
    if isinstance(payload, list):
        stations = [entry for entry in payload if isinstance(entry, dict)]
    else:
        raw = payload.get("aqhi") or payload.get("data")
        if isinstance(raw, list):
            stations = [entry for entry in raw if isinstance(entry, dict)]
    names = sorted({str(entry["station"]) for entry in stations if entry.get("station")})
    return names


def _extract_regions(path: Path) -> List[str]:
    """Read the mock traffic payload and surface named regions."""

    try:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except OSError:
        return []
    incidents: List[Dict[str, Any]] = []
    if isinstance(payload, list):
        incidents = [entry for entry in payload if isinstance(entry, dict)]
    else:
        raw = None
        for key in ("trafficnews", "incidents", "data"):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                raw = candidate
                break
        if isinstance(raw, list):
            incidents = [entry for entry in raw if isinstance(entry, dict)]
    regions: Set[str] = set()
    for entry in incidents:
        region = entry.get("region") or entry.get("area")
        if region:
            regions.add(str(region))
    return sorted(regions)


def build_aqhi_history_report(
    conn: sqlite3.Connection, station: str, limit: int = 8
) -> Optional[str]:
    """Return a textual AQHI history table for the selected station."""

    if not station:
        return None
    query = """
        SELECT station, category, value, updated_at
        FROM aqhi
        WHERE station = ?
        ORDER BY datetime(updated_at) DESC
        LIMIT ?
    """
    cursor = conn.execute(query, (station, limit))
    rows = cursor.fetchall()
    if not rows:
        return None

    table_rows: List[List[str]] = []
    values: List[float] = []
    for row in rows:
        timestamp = _format_timestamp(row["updated_at"])
        value = float(row["value"])
        values.append(value)
        table_rows.append(
            [
                timestamp,
                f"{value:.1f}",
                str(row["category"]),
            ]
        )

    headers = ["Timestamp", "AQHI", "Category"]
    widths = [len(header) for header in headers]
    for row in table_rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def _format_row(cells: List[str]) -> str:
        return " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))

    lines = [
        f"AQHI history for {station}",
        _format_row(headers),
        "-+-".join("-" * width for width in widths),
    ]
    lines.extend(_format_row(row) for row in table_rows)

    min_value = min(values)
    max_value = max(values)
    mean_value = sum(values) / len(values)
    latest_change = values[0] - values[-1]
    stats_line = (
        f"Range {min_value:.1f}–{max_value:.1f}, "
        f"mean {mean_value:.1f}, latest change {latest_change:+.1f}"
    )
    lines.append(stats_line)
    return "\n".join(lines)


def _format_timestamp(timestamp: str) -> str:
    """Normalize timestamps stored via db.ISO_FORMAT into readable text."""

    try:
        dt = datetime.strptime(timestamp, db.ISO_FORMAT)
    except ValueError:
        try:
            dt = datetime.fromisoformat(timestamp)
        except ValueError:
            return timestamp
    return dt.strftime("%Y-%m-%d %H:%M")


if __name__ == "__main__":
    main()
