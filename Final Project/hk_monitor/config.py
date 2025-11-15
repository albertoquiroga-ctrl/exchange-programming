"""Configuration helpers for the HK Conditions Monitor project.

Beyond simply reading ``config.toml``, this module offers the glue that keeps
the console dashboard configurable in teaching labs where students launch the
tool from unpredictable directories and operating systems.  Centralising all
I/O, parsing, and validation logic here keeps the rest of the codebase focused
on the monitoring experience itself (polling APIs, persisting readings, and
rendering the dashboard panels).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import os
import re

try:  # Python >=3.11
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    # Keep compatibility with Python 3.9/3.10 environments commonly found in
    # teaching labs by falling back to ``tomli``.
    import tomli as tomllib  # type: ignore[no-redef]


@dataclass(slots=True)
class AppConfig:
    """Runtime options that influence how the console dashboard behaves.

    The dashboard session learns which sensors, districts, and mock switches
    to use through this object, so every loop iteration depends on these
    values being clean and well-typed.
    """

    database_path: Path
    poll_interval: int
    rain_district: str
    aqhi_station: str
    traffic_region: str
    use_mock_data: bool = False


@dataclass(slots=True)
class ApiConfig:
    """Endpoints for the upstream data providers.

    Keeping endpoints configurable allows instructors to swap in mirrors or
    captive portals without touching the networking or parsing code.
    """

    warnings_url: str
    rainfall_url: str
    aqhi_url: str
    traffic_url: str


@dataclass(slots=True)
class MockPaths:
    """Filesystem locations for offline payloads used while developing.

    Running the CLI with ``--use-mock-data`` depends on these files existing,
    so resolving them early avoids confusing crashes deep inside collectors.
    """

    warnings: Path
    rainfall: Path
    aqhi: Path
    traffic: Path


@dataclass(slots=True)
class Config:
    """Top-level container that groups application, API, and mock settings.

    The rest of the HK monitor imports this single object so that the way a
    course deploys the project (real data vs. mocks, on-disk DB locations, etc)
    never leaks into other modules.
    """

    app: AppConfig
    api: ApiConfig
    mocks: MockPaths

    @classmethod
    def load(cls, path: Optional[str | os.PathLike[str]] = None) -> "Config":
        """Load TOML configuration.

        Args:
            path: Optional path to a TOML file. Defaults to ``config.toml`` in
                the current working directory.

        The loader is intentionally defensive: it searches multiple directories,
        auto-fixes common Windows path mistakes, and raises descriptive errors.
        That way the CLI always starts with a sensible explanation instead of
        exploding somewhere in the networking stack.
        """

        requested_path = Path(path or "config.toml")
        # Students often launch the CLI from various folders, so resolve the
        # config by searching cwd, the package directory, and a few parents.
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
    """Coerce and validate the [app] section from the TOML payload."""
    database_raw = _require_str(data.get("database_path", "final_project.db"), "app.database_path")
    # Paths inside config.toml are interpreted relative to the file itself so
    # that teams can copy the entire folder elsewhere without editing values.
    poll_interval = int(data.get("poll_interval", 300))
    # Reject zero/negative refresh intervals early rather than creating a tight
    # while loop in ``app.DashboardSession``.
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
    """Fill in API defaults while still allowing overrides in config.toml."""
    # The defaults dictionary mirrors the URLs published by HK data sources so
    # students can boot the project without editing config while still letting
    # instructors redirect traffic through offline mirrors when needed.
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
    """Resolve mock payload paths relative to the config file location."""
    def _resolve(key: str, default: str) -> Path:
        """Ensure every mock file exists so --collect never crashes mid-run."""
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
    """Validate string-like configuration entries and strip whitespace."""
    text = str(value).strip()
    if not text:
        # Provide a descriptive error so students know which key to fix.
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
        # Configs edited on Windows often contain ``C:\`` style paths; attempt
        # to normalise them before surfacing the parse error.
        sanitised = _normalise_windows_paths(text)
        if sanitised != text:
            try:
                # Re-run parsing with the sanitised version. If it still fails
                # we intentionally bubble up the original error afterwards so
                # students can see their exact typo.
                return tomllib.loads(sanitised)
            except tomllib.TOMLDecodeError:
                pass
        raise exc


def _normalise_windows_paths(text: str) -> str:
    """Replace backslashes with forward slashes for TOML-friendly parsing."""
    def _replace(match: re.Match[str]) -> str:
        """Perform the actual substitution while keeping the key untouched."""
        prefix, value = match.groups()
        if "\\" not in value:
            return match.group(0)
        cleaned_value = value.replace("\\", "/")
        return f'{prefix}"{cleaned_value}"'

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
