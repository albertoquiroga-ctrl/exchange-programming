"""Console demo for the HK Conditions Monitor."""
from __future__ import annotations

import argparse
import logging
import sqlite3
from typing import Dict, Optional

from . import collector, alerts, db
from .config import Config

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
        help="Run change detection and emit alerts after refreshing data.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = Config.load(args.config)

    with db.connect(config.app.database_path) as conn:
        if args.collect:
            logging.info("Collecting new data snapshot...")
            collector.collect_once(config, conn)
        snapshot = db.get_latest(conn)
        _print_snapshot(snapshot)

    if args.alerts:
        logging.info("Running change detection after snapshot update...")
        alerts.run_alerts(config)


def _print_snapshot(snapshot: Dict[str, Optional[sqlite3.Row]]) -> None:
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

    separator = "\n" + "=" * 60 + "\n"
    output_lines = []
    for title, body in sections:
        output_lines.append(f"{title}\n{'-' * len(title)}\n{body}")
    print(separator.join(output_lines))


if __name__ == "__main__":
    main()
