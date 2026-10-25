from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS xp (
    member_id INTEGER PRIMARY KEY REFERENCES members(member_id) ON DELETE CASCADE,
    xp INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS moderation_cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    actor_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id TEXT PRIMARY KEY,
    guild_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    opener_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TEXT
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: sqlite3.Connection | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.path, timeout=10)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA journal_mode = WAL")
        return self._connection

    def initialize(self) -> None:
        self.connection.executescript(SCHEMA)
        self.connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (1)")
        self.connection.commit()

    def execute(self, sql: str, parameters: Iterable[Any] = ()) -> sqlite3.Cursor:
        cursor = self.connection.execute(sql, tuple(parameters))
        self.connection.commit()
        return cursor

    def fetchone(self, sql: str, parameters: Iterable[Any] = ()) -> sqlite3.Row | None:
        return self.connection.execute(sql, tuple(parameters)).fetchone()

    def fetchall(self, sql: str, parameters: Iterable[Any] = ()) -> list[sqlite3.Row]:
        return self.connection.execute(sql, tuple(parameters)).fetchall()

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
