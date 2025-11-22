"""Simple in-memory change checker.

This module compares two snapshots (dictionaries) and prints friendly
messages when the main categories change.
"""

import argparse
from pathlib import Path
import sys

try:
    from .collector import collect_once
    from .config import load_config
except ImportError:  # pragma: no cover - allow running as a script
    PACKAGE_ROOT = Path(__file__).resolve().parents[1]
    if str(PACKAGE_ROOT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_ROOT))
    from hk_monitor.collector import collect_once
    from hk_monitor.config import load_config


def detect_changes(previous, current):
    """Return a list of change messages between two snapshots."""
    if previous is None:
        return []

    changes = []
    for key in ("warnings", "rain", "aqhi", "traffic"):
        old_value = _pick_category(previous.get(key))
        new_value = _pick_category(current.get(key))
        if not new_value:
            continue
        if old_value and old_value != new_value:
            changes.append(_format_change(key, old_value, new_value, current.get(key)))
    return changes


def _pick_category(section):
    if not section or not isinstance(section, dict):
        return ""
    for key in ("category", "level", "intensity", "severity"):
        if key in section:
            return str(section[key])
    return ""


def _format_change(section_name, old, new, section):
    detail = ""
    if section:
        if section_name == "rain" and "district" in section:
            detail = f" for {section['district']}"
        if section_name == "aqhi" and "station" in section:
            detail = f" at {section['station']}"
    return f"{section_name.title()} changed from {old} to {new}{detail}"


def print_alerts(messages):
    if not messages:
        print("No alerts triggered.")
        return
    print("Alerts:")
    for message in messages:
        print(f"- {message}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check snapshot changes without a database.")
    parser.add_argument(
        "--config",
        default="config.toml",
        help="Path to the TOML configuration file (default: config.toml)",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    print("Collecting first snapshot...")
    first = collect_once(config)
    input("Press Enter to collect again and check for changes.")
    second = collect_once(config)
    print_alerts(detect_changes(first, second))


__all__ = ["detect_changes", "print_alerts"]


if __name__ == "__main__":
    main()
