from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone, timedelta
from pathlib import Path
from hk_monitor import collector, db, alerts
from hk_monitor.config import Config


def _load_config() -> Config:
    config_path = Path(__file__).resolve().parents[1] / "config.template.toml"
    return Config.load(config_path)


def test_fetch_warning_from_mock():
    config = _load_config()
    record = collector.fetch_warning(config)
    assert record is not None
    assert record.level == "TC8"


def test_collect_once_persists(tmp_path):
    config = _load_config()
    config.app = replace(config.app, database_path=tmp_path / "test.db")
    with db.connect(config.app.database_path) as conn:
        snapshot = collector.collect_once(config, conn)
        assert snapshot["warnings"] is not None
        assert snapshot["rain"] is not None


def test_change_detector_emits_alert_on_category_change(tmp_path, capsys):
    config = _load_config()
    config.app = replace(config.app, database_path=tmp_path / "test.db")
    with db.connect(config.app.database_path) as conn:
        older = db.WarningRecord(
            level="TC3",
            message="Strong wind expected",
            updated_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        newer = db.WarningRecord(
            level="TC8",
            message="Typhoon signal 8",
            updated_at=datetime.now(timezone.utc),
        )
        db.save_warning(conn, older)
        db.save_warning(conn, newer)
        messenger = alerts.TelegramClient(token="", chat_id="", enabled=False, test_mode=True)
        detector = alerts.ChangeDetector(conn, messenger)
        detector.run()
        captured = capsys.readouterr().out
        assert "TC3" in captured
        assert "TC8" in captured
