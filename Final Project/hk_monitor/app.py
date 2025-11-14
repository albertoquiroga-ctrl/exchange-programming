"""Console demo for the HK Conditions Monitor."""
from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

import pandas as pd

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
    args = parse_args()
    config = Config.load(args.config)

    with db.connect(config.app.database_path) as conn:
        run_dashboard(
            config,
            conn,
            enable_alerts=args.alerts,
            collect_before=args.collect,
        )


def run_dashboard(
    config: Config,
    conn: sqlite3.Connection,
    enable_alerts: bool,
    collect_before: bool,
) -> None:
    menu_controller = MenuController(config)
    snapshot_printer = SnapshotPrinter()
    history_reporter = HistoryReporter(conn)
    skip_initial_refresh = False

    print("Launching HK Conditions Monitor dashboard. Press Ctrl+C or choose 'q' to exit.")
    if collect_before:
        refresh_and_display(
            config,
            conn,
            enable_alerts,
            menu_controller,
            snapshot_printer,
            history_reporter,
        )
        skip_initial_refresh = True

    try:
        while True:
            if not skip_initial_refresh:
                refresh_and_display(
                    config,
                    conn,
                    enable_alerts,
                    menu_controller,
                    snapshot_printer,
                    history_reporter,
                )
            else:
                skip_initial_refresh = False
            if not menu_controller.prompt():
                break
            wait_seconds = int(config.app.poll_interval)
            if wait_seconds < 0:
                wait_seconds = 0
            if wait_seconds:
                print(f"Waiting {wait_seconds}s before the next automatic refresh...\n")
                time.sleep(wait_seconds)
    except KeyboardInterrupt:
        print("\nExiting dashboard.")


def refresh_and_display(
    config: Config,
    conn: sqlite3.Connection,
    enable_alerts: bool,
    menu_controller: "MenuController",
    snapshot_printer: "SnapshotPrinter",
    history_reporter: "HistoryReporter",
) -> None:
    snapshot, highlights = refresh_snapshot(config, conn, enable_alerts)
    selection_info = menu_controller.selection_summary()
    snapshot_printer.display(snapshot, highlights, selection_info)
    history_reporter.print_report(menu_controller.current_station())


def refresh_snapshot(
    config: Config, conn: sqlite3.Connection, enable_alerts: bool
) -> tuple[Dict[str, Optional[sqlite3.Row]], Set[str]]:
    logging.info(
        "Refreshing snapshot for %s / %s / %s",
        config.app.rain_district,
        config.app.aqhi_station,
        config.app.traffic_region,
    )
    collector.collect_once(config, conn)
    snapshot = db.get_latest_snapshot(conn)
    highlights: Set[str] = set()
    if enable_alerts:
        messenger = _RecordingMessenger()
        ChangeDetector(conn, messenger).run()
        for message in messenger.messages:
            highlights.add(message.metric)
    return snapshot, highlights


class MenuController:
    """Handle user selections for the dashboard menu."""

    def __init__(self, config: Config):
        self.config = config
        self._options = _load_menu_options(config)

    def selection_summary(self) -> str:
        district = self.config.app.rain_district
        station = self.config.app.aqhi_station
        region = self.config.app.traffic_region
        summary = (
            "District: {district} | AQHI station: {station} | Traffic region: {region}"
        )
        return summary.format(district=district, station=station, region=region)

    def current_station(self) -> str:
        return self.config.app.aqhi_station

    def prompt(self) -> bool:
        menu_text = (
            "Press Enter to refresh now, or choose: [d]istrict, [a]qhi, [t]raffic, [q]uit"
        )
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
            self._show_menu_options(options)
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


def _load_menu_options(config: Config) -> Dict[str, List[str]]:
    return {
        "rain": _extract_places(config.mocks.rainfall),
        "aqhi": _extract_aqhi_stations(config.mocks.aqhi),
        "traffic": _extract_regions(config.mocks.traffic),
    }


def _extract_places(path: Path) -> List[str]:
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
        region_value = entry.get("region")
        if not region_value:
            region_value = entry.get("area")
        if region_value:
            region_names.add(str(region_value))
    sorted_regions = sorted(list(region_names))
    return sorted_regions


def build_aqhi_history_report(
    conn: sqlite3.Connection, station: str, limit: int = 8
) -> Optional[str]:
    """Return a pandas-powered AQHI history table for the selected station."""

    if not station:
        return None

    query = """
        SELECT station, category, value, updated_at
        FROM aqhi
        WHERE station = ?
        ORDER BY datetime(updated_at) DESC
        LIMIT ?
    """
    dataframe = pd.read_sql_query(
        query,
        conn,
        params=(station, limit),
        parse_dates=["updated_at"],
    )

    if dataframe.empty:
        return None

    dataframe["updated_at"] = pd.to_datetime(dataframe["updated_at"])
    printable_df = dataframe.copy()
    printable_df["updated_at"] = printable_df["updated_at"].dt.strftime("%Y-%m-%d %H:%M")
    printable_df = printable_df.rename(
        columns={"updated_at": "Timestamp", "value": "AQHI", "category": "Category"}
    )
    printable_df = printable_df[["Timestamp", "AQHI", "Category"]]

    stats = dataframe["value"].agg(["min", "max", "mean"])
    latest_change = 0.0
    if len(dataframe) > 1:
        latest_change = dataframe.iloc[0]["value"] - dataframe.iloc[-1]["value"]
    stats_line = (
        f"Range {stats['min']:.1f}–{stats['max']:.1f}, "
        f"mean {stats['mean']:.1f}, latest change {latest_change:+.1f}"
    )

    header = f"AQHI history for {station} (last {len(dataframe)} readings)"
    table_text = printable_df.to_string(index=False, float_format=lambda v: f"{v:0.1f}")
    return f"{header}\n{table_text}\n{stats_line}"


if __name__ == "__main__":
    main()
