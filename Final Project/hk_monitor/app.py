"""Beginner-friendly console for the HK Conditions Monitor.

All data lives in memory. Refresh the dashboard and type new locations
whenever you like. No database or advanced patterns.
"""

import argparse
import time
from pathlib import Path
import sys

try:
    from .collector import collect_once
    from .config import load_config
    from .alerts import detect_changes, print_alerts
except ImportError:  # pragma: no cover - allow running as a script
    PACKAGE_ROOT = Path(__file__).resolve().parents[1]
    if str(PACKAGE_ROOT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_ROOT))
    from hk_monitor.collector import collect_once
    from hk_monitor.config import load_config
    from hk_monitor.alerts import detect_changes, print_alerts


def parse_args():
    parser = argparse.ArgumentParser(description="HK Conditions Monitor (simple console)")
    parser.add_argument(
        "--config",
        default="config.toml",
        help="Path to the TOML configuration file (default: config.toml)",
    )
    parser.add_argument(
        "--use-mock",
        action="store_true",
        help="Force mock data even if the config says otherwise.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    if args.use_mock:
        config["app"]["use_mock_data"] = True

    print("HK Conditions Monitor (beginner version)")
    print("Data is not stored anywhere. Refresh to see fresh values.\n")

    last_snapshot = None
    while True:
        snapshot = collect_once(config)
        _show_snapshot(snapshot, config)
        alerts = detect_changes(last_snapshot, snapshot)
        if alerts:
            print_alerts(alerts)
        last_snapshot = snapshot

        choice = input("\nPress Enter to refresh, c to change locations, q to quit: ").strip().lower()
        if choice == "q":
            break
        if choice == "c":
            _ask_for_locations(config)
            continue
        wait_seconds = max(0, int(config["app"].get("poll_interval", 0)))
        if wait_seconds:
            print(f"Waiting {wait_seconds} seconds...\n")
            time.sleep(wait_seconds)


def _ask_for_locations(config):
    app = config["app"]
    new_rain = input(f"Rain district (current: {app['rain_district']}): ").strip()
    if new_rain:
        app["rain_district"] = new_rain

    new_aqhi = input(f"AQHI station (current: {app['aqhi_station']}): ").strip()
    if new_aqhi:
        app["aqhi_station"] = new_aqhi

    new_traffic = input(f"Traffic region (current: {app['traffic_region']}): ").strip()
    if new_traffic:
        app["traffic_region"] = new_traffic


def _show_snapshot(snapshot, config):
    selection_line = (
        f"District: {config['app']['rain_district']} | "
        f"AQHI: {config['app']['aqhi_station']} | "
        f"Traffic: {config['app']['traffic_region']}"
    )
    print("\n" + "=" * 60)
    print(selection_line)
    print("-" * len(selection_line))
    print("\nWarnings\n--------")
    print(_format_warning(snapshot.get("warnings")))
    print("\nRain\n----")
    print(_format_rain(snapshot.get("rain")))
    print("\nAQHI\n----")
    print(_format_aqhi(snapshot.get("aqhi")))
    print("\nTraffic\n-------")
    print(_format_traffic(snapshot.get("traffic")))
    print("=" * 60)


def _format_warning(row):
    if not row:
        return "No warning data."
    return (
        f"Level: {row['level']}\n"
        f"Message: {row['message']}\n"
        f"Updated: {row['updated_at']}"
    )


def _format_rain(row):
    if not row:
        return "No rain data."
    return (
        f"District: {row['district']}\n"
        f"Intensity: {row['intensity']}\n"
        f"Updated: {row['updated_at']}"
    )


def _format_aqhi(row):
    if not row:
        return "No AQHI data."
    try:
        value_text = f"{float(row['value']):.1f}"
    except (TypeError, ValueError):
        value_text = str(row["value"])
    return (
        f"Station: {row['station']}\n"
        f"Category: {row['category']}\n"
        f"Value: {value_text}\n"
        f"Updated: {row['updated_at']}"
    )


def _format_traffic(row):
    if not row:
        return "No traffic data."
    return (
        f"Severity: {row['severity']}\n"
        f"{row['description']}\n"
        f"Updated: {row['updated_at']}"
    )


if __name__ == "__main__":
    main()
