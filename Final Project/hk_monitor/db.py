"""Tiny in-memory placeholder now that SQLite is gone.

Use save_snapshot/get_latest to share the most recent data inside this
process. Nothing is written to disk.
"""

LAST_SNAPSHOT = {
    "warnings": None,
    "rain": None,
    "aqhi": None,
    "traffic": None,
}


def save_snapshot(snapshot):
    LAST_SNAPSHOT.update(snapshot)


def get_latest():
    return dict(LAST_SNAPSHOT)


__all__ = ["save_snapshot", "get_latest", "LAST_SNAPSHOT"]
