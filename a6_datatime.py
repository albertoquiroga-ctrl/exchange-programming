from datetime import datetime, timedelta
from typing import Optional, Tuple


def get_last_business_week(reference: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """Return the last full Monday-Friday business week relative to `reference`."""
    if reference is None:
        reference = datetime.now()
    start_of_current_week = reference - timedelta(days=reference.weekday())
    last_monday = start_of_current_week - timedelta(days=7)
    last_friday = last_monday + timedelta(days=4)
    return last_monday, last_friday


def format_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def main() -> None:
    today = datetime.now()
    print(f"Current Time is: {today}")
    print(f"Current Date is: {format_date(today)}")

    yesterday = today - timedelta(days=1)
    print(f"Yesterday's Date is: {format_date(yesterday)}")

    last_week = today - timedelta(days=7)
    print(f"Last Week's Date is: {format_date(last_week)}")

    last_monday, last_friday = get_last_business_week(today)
    print(f"Last Monday: {last_monday}")
    print(f"Last Friday: {last_friday}")

    start_date = format_date(last_monday)
    end_date = format_date(last_friday)
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")
