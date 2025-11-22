"""Configuration helpers for the HK Conditions Monitor project.

This module keeps configuration loading small and predictable: it reads a
single TOML file (either the provided path or ``config.toml`` in the current
directory) and returns lightweight objects with the fields the rest of the
application expects.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional

try:  # Python >=3.11
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore[no-redef]


class Config:
    """Top-level container for application, API, and mock settings."""

    def __init__(self, app: SimpleNamespace, api: SimpleNamespace, mocks: SimpleNamespace) -> None:
        self.app = app
        self.api = api
        self.mocks = mocks

    @classmethod
    def load(cls, path: Optional[str | Path] = None) -> "Config":
        """Load TOML configuration from the given path or ``config.toml``."""

        primary = Path(path) if path else Path("config.toml")
        search_paths = [primary]
        if not path:
            packaged_default = Path(__file__).resolve().parent / "config.toml"
            if packaged_default not in search_paths:
                search_paths.append(packaged_default)

        config_path: Optional[Path] = None
        for candidate in search_paths:
            if candidate.exists():
                config_path = candidate
                break

        if config_path is None:
            tried = ", ".join(str(p) for p in search_paths)
            raise FileNotFoundError(
                f"Configuration file was not found. Tried: {tried}. "
                "Copy config.template.toml to config.toml and adjust the values."
            )

        data = _parse_toml(config_path.read_text(encoding="utf-8"))
        base = config_path.parent

        app = _parse_app_config(data.get("app", {}), base)
        api = _parse_api_config(data.get("api", {}))
        mocks = _parse_mock_paths(data.get("mocks", {}), base)

        return cls(app=app, api=api, mocks=mocks)


def _parse_app_config(data: Dict[str, Any], base: Path) -> SimpleNamespace:
    """Coerce and validate the [app] section from the TOML payload."""

    database_raw = str(data.get("database_path", "final_project.db"))
    database_path = (base / database_raw).resolve()

    try:
        poll_interval = int(data.get("poll_interval", 300))
    except (TypeError, ValueError):
        raise ValueError("app.poll_interval must be a positive integer") from None
    if poll_interval <= 0:
        raise ValueError("app.poll_interval must be a positive integer")

    rain_district = _require_string(data.get("rain_district", "Central & Western"), "app.rain_district")
    aqhi_station = _require_string(data.get("aqhi_station", "Central/Western"), "app.aqhi_station")
    traffic_region = _require_string(data.get("traffic_region", "Hong Kong Island"), "app.traffic_region")
    use_mock_data = bool(data.get("use_mock_data", False))

    return SimpleNamespace(
        database_path=database_path,
        poll_interval=poll_interval,
        rain_district=rain_district,
        aqhi_station=aqhi_station,
        traffic_region=traffic_region,
        use_mock_data=use_mock_data,
    )


def _parse_api_config(data: Dict[str, Any]) -> SimpleNamespace:
    """Fill in API defaults while still allowing overrides in config.toml."""

    defaults = {
        "warnings_url": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=en",
        "rainfall_url": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en",
        "aqhi_url": "https://dashboard.data.gov.hk/api/aqhi-individual?format=json",
        "traffic_url": "https://www.td.gov.hk/en/special_news/trafficnews.xml",
    }

    return SimpleNamespace(
        warnings_url=_require_string(data.get("warnings_url", defaults["warnings_url"]), "api.warnings_url"),
        rainfall_url=_require_string(data.get("rainfall_url", defaults["rainfall_url"]), "api.rainfall_url"),
        aqhi_url=_require_string(data.get("aqhi_url", defaults["aqhi_url"]), "api.aqhi_url"),
        traffic_url=_require_string(data.get("traffic_url", defaults["traffic_url"]), "api.traffic_url"),
    )


def _parse_mock_paths(data: Dict[str, Any], base: Path) -> SimpleNamespace:
    """Resolve mock payload paths relative to the config file location."""

    def _resolve(key: str, default: str) -> Path:
        path = (base / str(data.get(key, default))).resolve()
        if not path.exists():
            raise ValueError(f"Mock payload '{path}' was not found")
        return path

    return SimpleNamespace(
        warnings=_resolve("warnings", "tests/data/warnings.json"),
        rainfall=_resolve("rainfall", "tests/data/rainfall.json"),
        aqhi=_resolve("aqhi", "tests/data/aqhi.json"),
        traffic=_resolve("traffic", "tests/data/traffic.json"),
    )


def _require_string(value: Any, field_name: str) -> str:
    """Validate string-like configuration entries and strip whitespace."""

    text = str(value).strip()
    if not text:
        raise ValueError(f"Configuration field '{field_name}' is required")
    return text


def _parse_toml(text: str) -> Dict[str, Any]:
    """Load TOML text using the available parser."""

    return tomllib.loads(text)


__all__ = ["Config"]
