"""Disposable SQLite-backed proposal and artifact cache."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class ProjectCache:
    def __init__(self, state_dir: Path) -> None:
        state_dir.mkdir(parents=True, exist_ok=True)
        self.path = state_dir / "cache.sqlite3"
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS proposals (
                    proposal_id TEXT PRIMARY KEY,
                    base_revision TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    revision TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def put_proposal(self, proposal_id: str, base_revision: str, payload: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO proposals(proposal_id, base_revision, payload) VALUES (?, ?, ?)",
                (proposal_id, base_revision, json.dumps(payload, sort_keys=True)),
            )

    def get_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM proposals WHERE proposal_id = ?", (proposal_id,)
            ).fetchone()
        return None if row is None else json.loads(row[0])

    def put_artifact(self, artifact_id: str, revision: str, payload: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO artifacts(artifact_id, revision, payload) VALUES (?, ?, ?)",
                (artifact_id, revision, json.dumps(payload, sort_keys=True)),
            )

    def list_artifacts(self, *, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM artifacts ORDER BY created_at DESC, artifact_id DESC LIMIT ?",
                (max(1, min(limit, 1000)),),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]
