"""Change detection and alert routing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional
import logging
import sqlite3
import requests

from .config import Config
from . import db

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AlertMessage:
    metric: str
    previous: str
    current: str
    description: str

    def format(self) -> str:
        header = f"[{self.metric.upper()}] {self.previous} -> {self.current}"
        return f"{header}\n{self.description}"


class TelegramClient:
    """Minimal Telegram sender wrapping the HTTP Bot API."""

    def __init__(self, token: str, chat_id: str, enabled: bool, test_mode: bool = False):
        self.token = token
        self.chat_id = chat_id
        self.enabled = enabled
        self.test_mode = test_mode

    def send(self, message: AlertMessage) -> None:
        payload = {"chat_id": self.chat_id, "text": message.format()}
        if not self.enabled or self.test_mode:
            logger.info("[DRY RUN] %s", payload["text"])
            print(payload["text"])  # pragma: no cover - CLI feedback
            return
        response = requests.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            timeout=10,
            json=payload,
        )
        response.raise_for_status()


class ChangeDetector:
    def __init__(self, conn: sqlite3.Connection, messenger: TelegramClient):
        self.conn = conn
        self.messenger = messenger
        self.table_config: Dict[str, Callable[[sqlite3.Row], AlertMessage]] = {
            "warnings": self._format_warning,
            "rain": self._format_rain,
            "aqhi": self._format_aqhi,
            "traffic": self._format_traffic,
        }

    def run(self) -> None:
        for table, formatter in self.table_config.items():
            rows = db.get_last_two(self.conn, table)
            if len(rows) < 2:
                continue
            previous, current = rows[1], rows[0]
            if _extract_category(previous) == _extract_category(current):
                continue
            alert = formatter(current)
            alert.previous = _extract_category(previous)
            alert.current = _extract_category(current)
            self.messenger.send(alert)

    def _format_warning(self, row: sqlite3.Row) -> AlertMessage:
        return AlertMessage(
            metric="Warnings",
            previous=row["level"],
            current=row["level"],
            description=row["message"],
        )

    def _format_rain(self, row: sqlite3.Row) -> AlertMessage:
        description = f"{row['district']}: {row['intensity']}"
        return AlertMessage(
            metric="Rain",
            previous=row["intensity"],
            current=row["intensity"],
            description=description,
        )

    def _format_aqhi(self, row: sqlite3.Row) -> AlertMessage:
        description = f"{row['station']} AQHI {row['value']:.1f}"
        return AlertMessage(
            metric="AQHI",
            previous=row["category"],
            current=row["category"],
            description=description,
        )

    def _format_traffic(self, row: sqlite3.Row) -> AlertMessage:
        return AlertMessage(
            metric="Traffic",
            previous=row["severity"],
            current=row["severity"],
            description=row["description"],
        )


def run_alerts(config: Config) -> None:
    from .db import connect

    with connect(config.app.database_path) as conn:
        messenger = TelegramClient(
            token=config.telegram.bot_token,
            chat_id=config.telegram.chat_id,
            enabled=config.telegram.enabled,
            test_mode=config.telegram.test_mode,
        )
        ChangeDetector(conn, messenger).run()


def _extract_category(row: sqlite3.Row) -> str:
    for key in ("category", "level", "intensity", "severity"):
        if key in row.keys():
            return str(row[key])
    return ""


__all__ = ["run_alerts", "ChangeDetector", "TelegramClient", "AlertMessage"]
