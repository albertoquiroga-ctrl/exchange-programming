from __future__ import annotations

from datetime import datetime, timedelta

from hk_monitor import db
from hk_monitor.app import build_aqhi_history_report


def _insert_aqhi(conn, station: str, start: datetime, values: list[float]) -> None:
    """Populate the database with evenly spaced AQHI readings."""
    ts = start
    for value in values:
        db.save_aqhi(
            conn,
            db.AqhiRecord(
                station=station,
                category="Test",
                value=value,
                updated_at=ts,
            ),
        )
        ts += timedelta(minutes=5)


def test_history_report_shows_stats_and_table(tmp_path):
    conn = db.init_db(tmp_path / "aqhi.db")
    start = datetime(2024, 5, 1, 8, 0)
    _insert_aqhi(conn, "Central", start, [2.0, 3.0, 4.0, 5.0])

    report = build_aqhi_history_report(conn, "Central", limit=5)

    # The ASCII table should contain both headers and summary statistics.
    assert report is not None
    assert "AQHI history for Central" in report
    assert "Range 2.0–5.0" in report
    assert "mean 3.5" in report
    assert "latest change +3.0" in report
    assert "Timestamp" in report and "AQHI" in report and "Category" in report
