from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

import numpy as np


def _now() -> float:
    return time.time()


class Store:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # The store is shared across threads (the MCP server warms up the engine
        # in a background thread and runs tool calls in a threadpool), so the
        # connection must not be bound to a single thread.
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._init()

    def _init(self) -> None:
        with self._lock:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS repos (
                    owner_repo TEXT PRIMARY KEY,
                    fetched_at REAL NOT NULL,
                    meta TEXT NOT NULL,
                    readme TEXT
                );
                CREATE TABLE IF NOT EXISTS embeddings (
                    owner_repo TEXT NOT NULL,
                    model TEXT NOT NULL,
                    dimension INTEGER NOT NULL,
                    vector BLOB NOT NULL,
                    PRIMARY KEY (owner_repo, model)
                );
                CREATE TABLE IF NOT EXISTS query_cache (
                    key TEXT PRIMARY KEY,
                    created_at REAL NOT NULL,
                    payload TEXT NOT NULL
                );
                """
            )
            self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def get_repo(self, owner_repo: str, ttl_hours: float) -> dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT fetched_at, meta, readme FROM repos WHERE owner_repo = ?",
                (owner_repo,),
            ).fetchone()
        if row is None:
            return None
        if _now() - row["fetched_at"] > ttl_hours * 3600:
            return None
        meta = json.loads(row["meta"])
        meta["readme"] = row["readme"]
        return meta

    def put_repo(self, meta: dict[str, Any], readme: str | None) -> None:
        owner_repo = meta["full_name"]
        payload = {k: v for k, v in meta.items() if k != "readme"}
        with self._lock:
            self._conn.execute(
                "INSERT INTO repos (owner_repo, fetched_at, meta, readme) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(owner_repo) DO UPDATE SET fetched_at = excluded.fetched_at, "
                "meta = excluded.meta, readme = excluded.readme",
                (owner_repo, _now(), json.dumps(payload), readme),
            )
            self._conn.commit()

    def get_embedding(self, owner_repo: str, model: str) -> np.ndarray | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT dimension, vector FROM embeddings WHERE owner_repo = ? AND model = ?",
                (owner_repo, model),
            ).fetchone()
        if row is None:
            return None
        return np.frombuffer(row["vector"], dtype=np.float32)

    def put_embedding(self, owner_repo: str, model: str, vector: np.ndarray) -> None:
        vec = np.asarray(vector, dtype=np.float32)
        with self._lock:
            self._conn.execute(
                "INSERT INTO embeddings (owner_repo, model, dimension, vector) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(owner_repo, model) DO UPDATE SET vector = excluded.vector, dimension = excluded.dimension",
                (owner_repo, model, int(vec.size), vec.tobytes()),
            )
            self._conn.commit()

    def get_query(self, key: str, ttl_hours: float) -> list[dict[str, Any]] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT created_at, payload FROM query_cache WHERE key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return None
        if _now() - row["created_at"] > ttl_hours * 3600:
            return None
        return json.loads(row["payload"])

    def put_query(self, key: str, results: list[dict[str, Any]]) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO query_cache (key, created_at, payload) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET created_at = excluded.created_at, payload = excluded.payload",
                (key, _now(), json.dumps(results)),
            )
            self._conn.commit()

    def stats(self) -> dict[str, int]:
        with self._lock:
            repos = self._conn.execute("SELECT COUNT(*) AS n FROM repos").fetchone()["n"]
            embeddings = self._conn.execute("SELECT COUNT(*) AS n FROM embeddings").fetchone()["n"]
            queries = self._conn.execute("SELECT COUNT(*) AS n FROM query_cache").fetchone()["n"]
        return {"repos": repos, "embeddings": embeddings, "cached_queries": queries}
