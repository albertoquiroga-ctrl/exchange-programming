"""Configuration helpers for the HK Conditions Monitor project."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import os
import re

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
    api: ApiConfig
    mocks: MockPaths

    @classmethod
    def load(cls, path: Optional[str | os.PathLike[str]] = None) -> "Config":
        """Load TOML configuration.

        Args:
            path: Optional path to a TOML file. Defaults to ``config.toml`` in
                the current working directory.
        """

        requested_path = Path(path or "config.toml")
        config_path = _resolve_config_path(requested_path)
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file '{requested_path}' was not found. "
                "Copy config.template.toml to config.toml and adjust the values."
            )

        text = config_path.read_text(encoding="utf-8")
        data = _parse_toml(text)

        return cls(
            app=_parse_app_config(data.get("app", {}), config_path.parent),
            api=_parse_api_config(data.get("api", {})),
            mocks=_parse_mock_paths(data.get("mocks", {}), config_path.parent),
        )


def _parse_app_config(data: Dict[str, Any], base: Path) -> AppConfig:
    database_raw = _require_str(data.get("database_path", "final_project.db"), "app.database_path")
    poll_interval = int(data.get("poll_interval", 300))
    if poll_interval <= 0:
        raise ValueError("app.poll_interval must be a positive integer")
    return AppConfig(
        database_path=(base / database_raw).resolve(),
        poll_interval=poll_interval,
        rain_district=_require_str(data.get("rain_district", "Central & Western"), "app.rain_district"),
        aqhi_station=_require_str(data.get("aqhi_station", "Central/Western"), "app.aqhi_station"),
        traffic_region=_require_str(data.get("traffic_region", "Hong Kong Island"), "app.traffic_region"),
        use_mock_data=bool(data.get("use_mock_data", False)),
    )


def _parse_api_config(data: Dict[str, Any]) -> ApiConfig:
    defaults = {
        "warnings_url": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=en",
        "rainfall_url": "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en",
        "aqhi_url": "https://dashboard.data.gov.hk/api/aqhi-individual?format=json",
        "traffic_url": "https://www.td.gov.hk/en/special_news/trafficnews.xml",
    }
    return ApiConfig(
        warnings_url=_require_str(data.get("warnings_url", defaults["warnings_url"]), "api.warnings_url"),
        rainfall_url=_require_str(data.get("rainfall_url", defaults["rainfall_url"]), "api.rainfall_url"),
        aqhi_url=_require_str(data.get("aqhi_url", defaults["aqhi_url"]), "api.aqhi_url"),
        traffic_url=_require_str(data.get("traffic_url", defaults["traffic_url"]), "api.traffic_url"),
    )


def _parse_mock_paths(data: Dict[str, Any], base: Path) -> MockPaths:
    def _resolve(key: str, default: str) -> Path:
        resolved = (base / str(data.get(key, default))).resolve()
        if not resolved.exists():
            raise ValueError(f"Mock payload '{resolved}' was not found")
        return resolved

    return MockPaths(
        warnings=_resolve("warnings", "tests/data/warnings.json"),
        rainfall=_resolve("rainfall", "tests/data/rainfall.json"),
        aqhi=_resolve("aqhi", "tests/data/aqhi.json"),
        traffic=_resolve("traffic", "tests/data/traffic.json"),
    )


def _require_str(value: Any, field_name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"Configuration field '{field_name}' is required")
    return text


_WINDOWS_PATH_KEYS = ("database_path", "warnings", "rainfall", "aqhi", "traffic")
_WINDOWS_PATH_PATTERN = re.compile(
    r'^(\s*(?:' + "|".join(_WINDOWS_PATH_KEYS) + r")\s*=\s*)\"([^\"\n]*)\"",
    re.MULTILINE,
)


def _parse_toml(text: str) -> Dict[str, Any]:
    """Load TOML text, tolerating Windows-style paths without escaping."""
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        sanitised = _normalise_windows_paths(text)
        if sanitised != text:
            try:
                return tomllib.loads(sanitised)
            except tomllib.TOMLDecodeError:
                pass
        raise exc


def _normalise_windows_paths(text: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        prefix, value = match.groups()
        if "\\" not in value:
            return match.group(0)
        return f'{prefix}"{value.replace("\\", "/")}"'

    return _WINDOWS_PATH_PATTERN.sub(_replace, text)


def _resolve_config_path(path: Path) -> Path:
    """Return the first existing config path when searching common locations."""
    candidates: List[Path] = []
    if path.is_absolute():
        candidates.append(path)
    else:
        cwd = Path.cwd()
        module_dir = Path(__file__).resolve().parent
        search_roots = [cwd, module_dir, module_dir.parent]
        # Include additional parents of the module directory for robustness.
        search_roots.extend(module_dir.parents[1:])
        seen: Set[Path] = set()
        for root in search_roots:
            candidate = (root / path).resolve()
            if candidate in seen:
                continue
            seen.add(candidate)
            candidates.append(candidate)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Fall back to the first candidate so callers can surface a sensible error.
    return candidates[0] if candidates else path


__all__ = [
    "AppConfig",
    "ApiConfig",
    "MockPaths",
    "Config",
]
