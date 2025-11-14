"""Configuration helpers for the HK Conditions Monitor project."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import os

try:  # Python >=3.11
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore[no-redef]


@dataclass(slots=True)
class AppConfig:
    database_path: Path
    poll_interval: int
    rain_district: str
    aqhi_station: str
    traffic_region: str
    use_mock_data: bool = False


@dataclass(slots=True)
class TelegramConfig:
    bot_token: str
    chat_id: str
    test_mode: bool = False

    @property
    def enabled(self) -> bool:
        return bool(self.bot_token and self.chat_id)


@dataclass(slots=True)
class ApiConfig:
    warnings_url: str
    rainfall_url: str
    aqhi_url: str
    traffic_url: str


@dataclass(slots=True)
class MockPaths:
    warnings: Path
    rainfall: Path
    aqhi: Path
    traffic: Path


@dataclass(slots=True)
class Config:
    app: AppConfig
    telegram: TelegramConfig
    api: ApiConfig
    mocks: MockPaths

    @classmethod
    def load(cls, path: Optional[str | os.PathLike[str]] = None) -> "Config":
        """Load TOML configuration.

        Args:
            path: Optional path to a TOML file. Defaults to ``config.toml`` in
                the current working directory.
        """

        config_path = Path(path or "config.toml")
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file '{config_path}' was not found. "
                "Copy config.template.toml to config.toml and adjust the values."
            )

        with config_path.open("rb") as fh:
            data = tomllib.load(fh)

        return cls(
            app=_parse_app_config(data.get("app", {}), config_path.parent),
            telegram=_parse_telegram_config(data.get("telegram", {})),
            api=_parse_api_config(data.get("api", {})),
            mocks=_parse_mock_paths(data.get("mocks", {}), config_path.parent),
        )


def _parse_app_config(data: Dict[str, Any], base: Path) -> AppConfig:
    return AppConfig(
        database_path=(base / data.get("database_path", "final_project.db")).resolve(),
        poll_interval=int(data.get("poll_interval", 300)),
        rain_district=data.get("rain_district", "Central & Western"),
        aqhi_station=data.get("aqhi_station", "Central/Western"),
        traffic_region=data.get("traffic_region", "Hong Kong Island"),
        use_mock_data=bool(data.get("use_mock_data", False)),
    )


def _parse_telegram_config(data: Dict[str, Any]) -> TelegramConfig:
    return TelegramConfig(
        bot_token=str(data.get("bot_token", "")),
        chat_id=str(data.get("chat_id", "")),
        test_mode=bool(data.get("test_mode", False)),
    )


def _parse_api_config(data: Dict[str, Any]) -> ApiConfig:
    return ApiConfig(
        warnings_url=str(data.get("warnings_url", "")),
        rainfall_url=str(data.get("rainfall_url", "")),
        aqhi_url=str(data.get("aqhi_url", "")),
        traffic_url=str(data.get("traffic_url", "")),
    )


def _parse_mock_paths(data: Dict[str, Any], base: Path) -> MockPaths:
    def _resolve(key: str, default: str) -> Path:
        return (base / str(data.get(key, default))).resolve()

    return MockPaths(
        warnings=_resolve("warnings", "tests/data/warnings.json"),
        rainfall=_resolve("rainfall", "tests/data/rainfall.json"),
        aqhi=_resolve("aqhi", "tests/data/aqhi.json"),
        traffic=_resolve("traffic", "tests/data/traffic.json"),
    )


__all__ = [
    "AppConfig",
    "TelegramConfig",
    "ApiConfig",
    "MockPaths",
    "Config",
]
