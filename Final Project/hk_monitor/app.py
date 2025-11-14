"""Console demo for the HK Conditions Monitor."""

# === Interactive console front-end ===

# This module is the "face" of the pipeline: we parse CLI flags, drive the
# collectors, persist rows into SQLite, and present a narrated dashboard.  The
# comments below explain the order in which each responsibility executes so the
# file reads like a guided tour.
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")


def parse_args() -> argparse.Namespace:
    """Parse CLI options for the dashboard demo."""

    # Step 1: configure the CLI interface exactly once so both scripts and
    # direct ``python -m`` invocations behave the same.
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

    # Step 1: parse command-line options and load the TOML config referenced by
    # ``--config`` so the CLI mirrors the config-driven pipeline used by tests.
    args = parse_args()
    config = Config.load(args.config)

    # Step 2: keep the SQLite connection open for the whole session so history
    # queries, change detection, and writes share the same handle.
    with db.connect(config.app.database_path) as conn:
        dashboard = DashboardSession(config, conn, enable_alerts=args.alerts)
        if args.collect:
            # Step 3: optionally run an immediate refresh so the user can see a
            # populated dashboard before the prompt appears.
            dashboard.refresh(skip_wait=True)
        dashboard.run(skip_initial_refresh=args.collect)


class MenuController:
    """Handle user selections for the dashboard menu."""

    def __init__(self, config: Config):
        self.config = config
        self._options = _load_menu_options(config)

    def run(self, skip_initial_refresh: bool = False) -> None:
        print("Launching HK Conditions Monitor dashboard. Press Ctrl+C or choose 'q' to exit.")
        # Step 1: alternate between automatic refreshes and user prompts until
        # the user quits or hits Ctrl+C.
        try:
            while True:
                if not skip_initial_refresh:
                    self.refresh()
                else:
                    skip_initial_refresh = False
                if not self._prompt_loop():
                    break
                wait_seconds = max(0, int(self.config.app.poll_interval))
                if wait_seconds:
                    # Poll interval is stored as ``float`` in TOML, so cast to
                    # ``int`` here to avoid fractional sleeps and log spam.
                    print(f"Waiting {wait_seconds}s before the next automatic refresh...\n")
                    time.sleep(wait_seconds)
        except KeyboardInterrupt:
            print("\nExiting dashboard.")

    def refresh(self, skip_wait: bool = False) -> None:
        # Step 1: log the selected district/station/region so terminal output
        # tells readers which choices produced the snapshot.
        logging.info(
            "Refreshing snapshot for %s / %s / %s",
            self.config.app.rain_district,
            self.config.app.aqhi_station,
            self.config.app.traffic_region,
        )
        # Step 2: fetch the latest metrics and persist them via the collector.
        collector.collect_once(self.config, self.conn)
        snapshot = db.get_latest(self.conn)
        if self.enable_alerts:
            # Step 3: route the new rows through change detection and keep track
            # of which tiles emitted alerts so we can highlight them inline.
            messenger = _RecordingMessenger()
            ChangeDetector(self.conn, messenger).run()
            self.alert_metrics = {message.metric for message in messenger.messages}
        else:
            self.alert_metrics = set()

        # Step 4: render the four-tile snapshot along with the selection summary.
        _print_snapshot(
            snapshot,
            highlights=self.alert_metrics,
            selection_info=self._selection_summary(),
        )

    def prompt(self) -> bool:
        menu_text = (
            "Press Enter to refresh now, or choose: [d]istrict, [a]qhi, [t]raffic, [q]uit"
        )
        if history_report:
            # Step 5: display the pandas table so viewers see recent AQHI trends
            # without leaving the console.
            print("\n" + history_report)
        if skip_wait:
            return

    def _selection_summary(self) -> str:
        return (
            "District: {district} | AQHI station: {station} | Traffic region: {region}".format(
                district=self.config.app.rain_district,
                station=self.config.app.aqhi_station,
                region=self.config.app.traffic_region,
            )
        )

    def _prompt_loop(self) -> bool:
        """Handle repeated dashboard menu interactions."""

        menu = "Press Enter to refresh now, or choose: [d]istrict, [a]qhi, [t]raffic, [q]uit"
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
            # Any other keystrokes are invalid; loop to prompt the user again.
            print("Unknown command. Please choose one of the listed options.")

    def _change_selection(
        self,
        option_key: str,
        label: str,
        attribute: str,
    ) -> None:
        options = self._options.get(option_key)
        current_value = getattr(self.config.app, attribute)
        print(f"Current {label}: {current_value}")
        if options:
            # Step 1: show a numbered list based on the values discovered in the
            # mock payloads.
            self._print_options(options)
            selection = input(f"Select a new {label} (number) or press Enter to keep current: ").strip()
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
            # When no curated options exist, accept free-form text but only
            # persist it when the user typed something non-empty.
            manual = input(f"Type a new {label} and press Enter (blank to cancel): ").strip()
            if manual:
                setattr(self.config.app, attribute, manual)
                print(f"Updated {label} to {manual}.")

    @staticmethod
    def _show_menu_options(options: Sequence[str]) -> None:
        index = 1
        for value in options:
            print(f"  {index}. {value}")
            index += 1


class SnapshotPrinter:
    """Format and print the latest snapshot to the console."""

    def display(
        self,
        snapshot: Dict[str, Optional[sqlite3.Row]],
        highlights: Set[str],
        selection_info: Optional[str],
    ) -> None:
        sections = []
        sections.append(("Warnings", self._format_warning(snapshot.get("warnings"))))
        sections.append(("Rain", self._format_rain(snapshot.get("rain"))))
        sections.append(("AQHI", self._format_aqhi(snapshot.get("aqhi"))))
        sections.append(("Traffic", self._format_traffic(snapshot.get("traffic"))))

        separator = "\n" + "=" * 60 + "\n"
        output_lines: List[str] = []
        if selection_info:
            output_lines.append(selection_info)
        for title, body in sections:
            prefix = ""
            suffix = ""
            if title in highlights:
                prefix = "*** "
                suffix = " ***"
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
    data_entries: List[Dict[str, Any]] = []
    if "rainfall" in payload:
        rainfall_section = payload.get("rainfall")
        if isinstance(rainfall_section, dict):
            raw_entries = rainfall_section.get("data")
        else:
            raw_entries = []
    else:
        raw_entries = payload.get("data")
    if isinstance(raw_entries, list):
        for item in raw_entries:
            if isinstance(item, dict):
                data_entries.append(item)
    places: Set[str] = set()
    for item in data_entries:
        place = item.get("place")
        if place:
            places.add(str(place))
    place_list = sorted(list(places))
    return place_list


def _extract_aqhi_stations(path: Path) -> List[str]:
    """Read the mock AQHI payload and surface unique station names."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except OSError:
        return []
    stations: List[Dict[str, Any]] = []
    if isinstance(payload, list):
        for entry in payload:
            if isinstance(entry, dict):
                stations.append(entry)
    else:
        if "aqhi" in payload:
            raw_stations = payload.get("aqhi")
        elif "data" in payload:
            raw_stations = payload.get("data")
        else:
            raw_stations = []
        if isinstance(raw_stations, list):
            for entry in raw_stations:
                if isinstance(entry, dict):
                    stations.append(entry)
    station_names: Set[str] = set()
    for entry in stations:
        station_value = entry.get("station")
        if station_value:
            station_names.add(str(station_value))
    sorted_names = sorted(list(station_names))
    return sorted_names


def _extract_regions(path: Path) -> List[str]:
    """Read the mock traffic payload and surface named regions."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except OSError:
        return []
    incidents: List[Dict[str, Any]] = []
    if isinstance(payload, list):
        for entry in payload:
            if isinstance(entry, dict):
                incidents.append(entry)
    else:
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
    region_names: Set[str] = set()
    for entry in incidents:
        region = entry.get("region") or entry.get("area")
        if region:
            regions.add(str(region))
    return sorted(regions)


def _print_snapshot(
    snapshot: Dict[str, Optional[sqlite3.Row]],
    highlights: Optional[Iterable[str]] = None,
    selection_info: str | None = None,
) -> None:
    """Render the dashboard tiles with optional highlighting."""

    # Each formatter returns a multi-line string summarising the most recent row
    # so the caller can focus on assembling the final view.
    def format_warning(row: Optional[sqlite3.Row]) -> str:
        if not row:
            return "No warning data."
        return f"Level: {row['level']}\nMessage: {row['message']}\nUpdated: {row['updated_at']}"

    def format_rain(row: Optional[sqlite3.Row]) -> str:
        if not row:
            return "No rain data."
        return f"District: {row['district']}\nIntensity: {row['intensity']}\nUpdated: {row['updated_at']}"

    def format_aqhi(row: Optional[sqlite3.Row]) -> str:
        if not row:
            return "No AQHI data."
        return (
            f"Station: {row['station']}\nCategory: {row['category']}\n"
            f"Value: {row['value']:.1f}\nUpdated: {row['updated_at']}"
        )

    def format_traffic(row: Optional[sqlite3.Row]) -> str:
        if not row:
            return "No traffic data."
        return f"Severity: {row['severity']}\n{row['description']}\nUpdated: {row['updated_at']}"

    sections = [
        ("Warnings", format_warning(snapshot.get("warnings"))),
        ("Rain", format_rain(snapshot.get("rain"))),
        ("AQHI", format_aqhi(snapshot.get("aqhi"))),
        ("Traffic", format_traffic(snapshot.get("traffic"))),
    ]

    # ``highlights`` may be ``None``; convert to ``set`` once so we can test
    # membership quickly while building the banner text.
    highlights = set(highlights or [])
    separator = "\n" + "=" * 60 + "\n"
    output_lines = []
    if selection_info:
        output_lines.append(selection_info)
    for title, body in sections:
        prefix = "*** " if title in highlights else ""
        suffix = " ***" if title in highlights else ""
        header = f"{prefix}{title}{suffix}"
        output_lines.append(f"{header}\n{'-' * len(title)}\n{body}")
    print(separator.join(output_lines))


def build_aqhi_history_report(
    conn: sqlite3.Connection, station: str, limit: int = 8
) -> Optional[str]:
    """Return a textual AQHI history table for the selected station."""

    if not station:
        return None

    # Step 1: fetch the most recent ``limit`` readings for the requested
    # station; ``parse_dates`` keeps ``updated_at`` timezone-aware for display.
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

    # Step 2: normalize timestamps to pandas ``datetime64`` so we can format
    # them consistently for presentation.
    df["updated_at"] = pd.to_datetime(df["updated_at"])
    printable = (
        df.copy()
        .assign(updated_at=df["updated_at"].dt.strftime("%Y-%m-%d %H:%M"))
        .rename(columns={"updated_at": "Timestamp", "value": "AQHI", "category": "Category"})
        [["Timestamp", "AQHI", "Category"]]
    )

    # Step 3: crunch simple stats so the console report feels closer to a chart.
    stats = df["value"].agg(["min", "max", "mean"])
    change = df.iloc[0]["value"] - df.iloc[-1]["value"] if len(df) > 1 else 0.0
    stats_line = (
        f"Range {min_value:.1f}–{max_value:.1f}, "
        f"mean {mean_value:.1f}, latest change {latest_change:+.1f}"
    )
    table_text = "\n".join(table_lines)
    return f"{header}\n{table_text}\n{stats_line}"


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
