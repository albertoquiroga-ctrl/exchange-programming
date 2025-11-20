from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import io

import requests

from hk_monitor import collector, db, alerts
from hk_monitor.config import Config


def _load_config() -> Config:
    # Reuse the provided template so tests run with realistic defaults.
    config_path = Path(__file__).resolve().parents[1] / "config.template.toml"
    return Config.load(config_path)


def test_fetch_warning_from_mock():
    config = _load_config()
    record = collector.fetch_warning(config)
    assert record is not None
    assert record.level == "TC8"


def test_collect_once_persists(tmp_path):
    # Smoke test that verifies every feed saves at least one row into SQLite.
    config = _load_config()
    config.app.database_path = tmp_path / "test.db"
    with db.connect(config.app.database_path) as conn:
        snapshot = collector.collect_once(config, conn)
        assert snapshot["warnings"] is not None
        assert snapshot["rain"] is not None


def test_change_detector_emits_alert_on_category_change(tmp_path):
    # Simulate a warning upgrade and ensure the messenger captures it.
    config = _load_config()
    config.app.database_path = tmp_path / "test.db"
    with db.connect(config.app.database_path) as conn:
        older = {
            "level": "TC3",
            "message": "Strong wind expected",
            "updated_at": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        newer = db.WarningRecord(
            level="TC8",
            message="Typhoon signal 8",
            updated_at=datetime.now(timezone.utc),
        )
        db.save_warning(conn, older)
        db.save_warning(conn, newer)
        buffer = io.StringIO()
        messenger = alerts.ConsoleMessenger(stream=buffer)
        detector = alerts.ChangeDetector(conn, messenger)
        detector.run()
        captured = buffer.getvalue()
        assert "TC3" in captured
        assert "TC8" in captured


def test_fetch_warning_uses_cached_payload_on_http_failure(monkeypatch):
    # Prime the cache using mock data so a fallback snapshot exists.
    config = _load_config()
    baseline = collector.fetch_warning(config)
    assert baseline is not None

    failing_config = _load_config()
    failing_config.app.use_mock_data = False

    load_calls: dict[str, Path] = {}
    original_loader = collector._load_cached_payload

    def spy_loader(path: Path):
        load_calls["path"] = path
        return original_loader(path)

    monkeypatch.setattr(collector, "_load_cached_payload", spy_loader)

    def failing_get(*args, **kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr(collector.requests, "get", failing_get)

    record = collector.fetch_warning(failing_config)
    assert record is not None
    assert load_calls["path"].name.startswith("last_warnings")
