from __future__ import annotations

from datetime import datetime
from pathlib import Path

from hk_monitor import alerts, collector, config, db


class DummyMessenger:
    """Minimal messenger that records alerts instead of printing to stdout."""
    def __init__(self) -> None:
        self.messages: list[alerts.AlertMessage] = []

    def send(self, message: alerts.AlertMessage) -> None:
        self.messages.append(message)


def _load_template_config() -> config.Config:
    template_path = Path(__file__).resolve().parents[1] / "config.template.toml"
    cfg = config.Config.load(template_path)
    cfg.app.use_mock_data = True
    return cfg


def _init_conn(tmp_path: Path):
    """Create an isolated database for each scenario test."""
    return db.init_db(tmp_path / "scenario.db")


def test_warning_upgrade_triggers_alert(tmp_path: Path) -> None:
    # Switching mock payloads simulates the warning level escalating in HK.
    cfg = _load_template_config()
    conn = _init_conn(tmp_path)

    cfg.mocks.warnings = Path(__file__).with_name("data") / "warnings.json"
    warning = collector.fetch_warning(cfg)
    assert warning is not None
    db.save_warning(conn, warning)

    cfg.mocks.warnings = Path(__file__).with_name("data") / "warnings_red.json"
    upgraded = collector.fetch_warning(cfg)
    assert upgraded is not None
    db.save_warning(conn, upgraded)

    messenger = DummyMessenger()
    alerts.ChangeDetector(conn, messenger).run()

    assert messenger.messages, "Expected an alert when warning level changes"
    assert messenger.messages[0].metric == "Warnings"


def test_aqhi_spike_is_detected(tmp_path: Path) -> None:
    # Drive the AQHI collector twice so the change detector sees a big jump.
    cfg = _load_template_config()
    conn = _init_conn(tmp_path)

    aqhi_path = Path(__file__).with_name("data") / "aqhi_spike.json"
    cfg.mocks.aqhi = aqhi_path

    first = collector.fetch_aqhi(cfg)
    assert first is not None
    db.save_aqhi(conn, first)

    # Simulate the next value by taking the second reading manually.
    spike_payload = collector._get_payload(cfg, "", aqhi_path, key=None)
    cfg.mocks.aqhi = aqhi_path
    spike_entry = spike_payload[1]
    db.save_aqhi(
        conn,
        db.AqhiRecord(
            station=cfg.app.aqhi_station,
            category=collector._categorize_aqhi(float(spike_entry["aqhi"])),
            value=float(spike_entry["aqhi"]),
            updated_at=datetime.fromisoformat(spike_entry["time"]),
        ),
    )

    messenger = DummyMessenger()
    alerts.ChangeDetector(conn, messenger).run()

    assert any(msg.metric == "AQHI" for msg in messenger.messages)


def test_traffic_incident_escalation(tmp_path: Path) -> None:
    # Feed two incidents with different severity to exercise the Traffic branch.
    cfg = _load_template_config()
    conn = _init_conn(tmp_path)

    incidents = collector._get_payload(
        cfg,
        "",
        Path(__file__).with_name("data") / "traffic_incident.json",
        key=None,
    )

    first = incidents[0]
    second = incidents[1]

    db.save_traffic(
        conn,
        db.TrafficRecord(
            severity=first["severity"],
            description=first["content"],
            updated_at=datetime.fromisoformat(first["update_time"]),
        ),
    )
    db.save_traffic(
        conn,
        db.TrafficRecord(
            severity=second["severity"],
            description=second["content"],
            updated_at=datetime.fromisoformat(second["update_time"]),
        ),
    )

    messenger = DummyMessenger()
    alerts.ChangeDetector(conn, messenger).run()

    assert any(msg.metric == "Traffic" for msg in messenger.messages)
