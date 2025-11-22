"""Ultra-simple HK Conditions Monitor demo.

Single file, no database, no config files. Each refresh shows randomised
mock data so students can focus on the printout and the input loop.
"""

import argparse
import random
import time
from datetime import datetime


DEFAULTS = {
    "rain_district": "Central & Western",
    "aqhi_station": "Central/Western",
    "traffic_region": "Hong Kong Island",
    "poll_interval": 5,
}

SAMPLE_WARNINGS = [
    ("None", "No weather warnings in force."),
    ("Amber Rain", "Showers in parts of the city."),
    ("Thunderstorm", "Thunderstorms expected, stay indoors."),
]

SAMPLE_TRAFFIC = [
    ("Info", "Light traffic reported."),
    ("Minor", "Slow traffic near the harbour tunnel."),
    ("Major", "Accident on main highway, expect delays."),
]


def main():
    args = _parse_args()
    config = DEFAULTS.copy()

    print("HK Conditions Monitor (super simple)")
    print("Data lives only on screen. Refresh to see new random values.\n")

    while True:
        snapshot = _make_snapshot(config)
        _print_snapshot(snapshot, config)

        choice = input("\nEnter=refresh | c=change locations | q=quit: ").strip().lower()
        if choice == "q":
            break
        if choice == "c":
            _change_locations(config)
            continue
        wait_seconds = max(0, int(config.get("poll_interval", 0)))
        if wait_seconds:
            print(f"Waiting {wait_seconds} seconds...\n")
            time.sleep(wait_seconds)


def _parse_args():
    parser = argparse.ArgumentParser(description="Simple HK monitor console")
    # Kept for compatibility; currently does nothing fancy.
    parser.add_argument("--use-mock", action="store_true", help="Mock data is always used.")
    return parser.parse_args()


def _make_snapshot(config):
    now = _ts()
    warning_level, warning_msg = random.choice(SAMPLE_WARNINGS)
    rain_value = round(random.uniform(0, 20), 1)
    rain_category = _categorize_rain(rain_value)
    aqhi_value = round(random.uniform(1, 10), 1)
    aqhi_category = _categorize_aqhi(aqhi_value)
    traffic_level, traffic_msg = random.choice(SAMPLE_TRAFFIC)

    return {
        "warnings": {
            "level": warning_level,
            "message": warning_msg,
            "updated_at": now,
        },
        "rain": {
            "district": config["rain_district"],
            "intensity": f"{rain_value} mm ({rain_category})",
            "updated_at": now,
        },
        "aqhi": {
            "station": config["aqhi_station"],
            "category": aqhi_category,
            "value": aqhi_value,
            "updated_at": now,
        },
        "traffic": {
            "severity": traffic_level,
            "description": traffic_msg,
            "updated_at": now,
        },
    }


def _print_snapshot(snapshot, config):
    header = (
        f"District: {config['rain_district']} | "
        f"AQHI: {config['aqhi_station']} | "
        f"Traffic: {config['traffic_region']}"
    )
    print("\n" + "=" * 60)
    print(header)
    print("-" * len(header))
    print("\nWarnings\n--------")
    print(_format_warning(snapshot["warnings"]))
    print("\nRain\n----")
    print(_format_rain(snapshot["rain"]))
    print("\nAQHI\n----")
    print(_format_aqhi(snapshot["aqhi"]))
    print("\nTraffic\n-------")
    print(_format_traffic(snapshot["traffic"]))
    print("=" * 60)


def _change_locations(config):
    new_rain = input(f"Rain district (current: {config['rain_district']}): ").strip()
    if new_rain:
        config["rain_district"] = new_rain
    new_aqhi = input(f"AQHI station (current: {config['aqhi_station']}): ").strip()
    if new_aqhi:
        config["aqhi_station"] = new_aqhi
    new_traffic = input(f"Traffic region (current: {config['traffic_region']}): ").strip()
    if new_traffic:
        config["traffic_region"] = new_traffic


def _format_warning(row):
    return f"Level: {row['level']}\nMessage: {row['message']}\nUpdated: {row['updated_at']}"


def _format_rain(row):
    return (
        f"District: {row['district']}\n"
        f"Intensity: {row['intensity']}\n"
        f"Updated: {row['updated_at']}"
    )


def _format_aqhi(row):
    return (
        f"Station: {row['station']}\n"
        f"Category: {row['category']}\n"
        f"Value: {row['value']}\n"
        f"Updated: {row['updated_at']}"
    )


def _format_traffic(row):
    return (
        f"Severity: {row['severity']}\n"
        f"{row['description']}\n"
        f"Updated: {row['updated_at']}"
    )


def _ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _categorize_rain(value):
    if value >= 15:
        return "Red Rain"
    if value >= 5:
        return "Amber Rain"
    if value >= 1:
        return "Showers"
    return "Dry"


def _categorize_aqhi(value):
    if value >= 10:
        return "Serious"
    if value >= 7:
        return "Very High"
    if value >= 4:
        return "High"
    if value >= 3:
        return "Moderate"
    return "Low"


if __name__ == "__main__":
    main()
