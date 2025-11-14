from __future__ import annotations

from pathlib import Path

import pytest

from hk_monitor.config import Config


def _write_config(tmp_path: Path, content: str) -> Path:
    # Helper used throughout the suite to persist ad-hoc TOML payloads.
    config_path = tmp_path / "config.toml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


def _base_config(tmp_path: Path) -> str:
    db_path = tmp_path / "test.db"
    project_root = Path(__file__).resolve().parents[1]
    mocks_root = project_root / "tests" / "data"
    # Build a fully functional config so each test can tweak a single field.
    return f"""
[app]
database_path = "{db_path}"
poll_interval = 300
rain_district = "Central & Western"
aqhi_station = "Central/Western"
traffic_region = "Hong Kong Island"
use_mock_data = true

[api]
warnings_url = "https://example.com/warnings"
rainfall_url = "https://example.com/rain"
aqhi_url = "https://example.com/aqhi"
traffic_url = "https://example.com/traffic"

[mocks]
warnings = "{mocks_root / 'warnings.json'}"
rainfall = "{mocks_root / 'rainfall.json'}"
aqhi = "{mocks_root / 'aqhi.json'}"
traffic = "{mocks_root / 'traffic.json'}"
"""


def test_invalid_poll_interval_raises(tmp_path: Path) -> None:
    # Poll interval must stay positive so the CLI loop never divides by zero.
    config_text = _base_config(tmp_path).replace("poll_interval = 300", "poll_interval = 0")
    config_path = _write_config(tmp_path, config_text)
    with pytest.raises(ValueError, match="poll_interval"):
        Config.load(config_path)


def test_missing_api_url_is_invalid(tmp_path: Path) -> None:
    # API URLs are validated through _require_str; blank values should explode.
    config_text = _base_config(tmp_path).replace("warnings_url = \"https://example.com/warnings\"", "warnings_url = \"\"")
    config_path = _write_config(tmp_path, config_text)
    with pytest.raises(ValueError, match="api.warnings_url"):
        Config.load(config_path)


def test_missing_mock_payload_file_fails(tmp_path: Path) -> None:
    base = _base_config(tmp_path)
    project_root = Path(__file__).resolve().parents[1]
    mocks_root = project_root / "tests" / "data"
    placeholder = f"warnings = \"{mocks_root / 'warnings.json'}\""
    config_text = base.replace(placeholder, "warnings = \"/tmp/does-not-exist.json\"")
    config_path = _write_config(tmp_path, config_text)
    # Loading should raise immediately because collectors rely on those files.
    with pytest.raises(ValueError, match="Mock payload"):
        Config.load(config_path)
