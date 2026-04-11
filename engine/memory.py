"""
ORD AI — MemoryBank
Three-tier memory architecture:
  • Short-term  — in-process TTL cache (current session context)
  • Long-term   — SQLite FTS (past builds, learned patterns)
  • Episodic    — SQLite events (specific events, bugs fixed, decisions)
"""
import sqlite3
import threading
import time
import json
import hashlib
from typing import Any, Optional

DB_PATH = "/tmp/ord_ai_memory.db"


def _db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _init_db():
    con = _db()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS long_term (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            key      TEXT NOT NULL,
            content  TEXT NOT NULL,
            tags     TEXT DEFAULT '',
            ts       REAL NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS long_term_fts
            USING fts5(key, content, tags, content=long_term, content_rowid=id);

        CREATE TABLE IF NOT EXISTS episodic (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            event    TEXT NOT NULL,
            kind     TEXT NOT NULL DEFAULT 'info',
            payload  TEXT DEFAULT '{}',
            ts       REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS episodic_kind ON episodic(kind);
        CREATE INDEX IF NOT EXISTS episodic_ts   ON episodic(ts);
    """)
    con.commit()
    con.close()


_init_db()


class MemoryBank:
    """Short + Long + Episodic memory for the ORD AI platform."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self, short_term_ttl: int = 3600):
        self._short: dict[str, dict] = {}   # {key: {value, expires}}
        self._short_lock = threading.Lock()
        self._short_ttl = short_term_ttl
        self._gc_thread = threading.Thread(target=self._gc_loop, daemon=True)
        self._gc_thread.start()

    @classmethod
    def get_instance(cls) -> "MemoryBank":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Short-term ────────────────────────────────────────────────────

    def st_set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires = time.time() + (ttl or self._short_ttl)
        with self._short_lock:
            self._short[key] = {"value": value, "expires": expires}

    def st_get(self, key: str) -> Optional[Any]:
        with self._short_lock:
            entry = self._short.get(key)
            if entry and entry["expires"] > time.time():
                return entry["value"]
            if entry:
                del self._short[key]
        return None

    def st_all(self) -> list[dict]:
        now = time.time()
        with self._short_lock:
            return [
                {"key": k, "value": v["value"], "ttl_remaining": int(v["expires"] - now)}
                for k, v in self._short.items()
                if v["expires"] > now
            ]

    def _gc_loop(self):
        while True:
            time.sleep(60)
            now = time.time()
            with self._short_lock:
                expired = [k for k, v in self._short.items() if v["expires"] <= now]
                for k in expired:
                    del self._short[k]

    # ── Long-term ─────────────────────────────────────────────────────

    def lt_save(self, key: str, content: Any, tags: str = "") -> int:
        text = content if isinstance(content, str) else json.dumps(content)
        con = _db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO long_term (key, content, tags, ts) VALUES (?, ?, ?, ?)",
            (key, text, tags, time.time()),
        )
        row_id = cur.lastrowid
        cur.execute(
            "INSERT INTO long_term_fts(rowid, key, content, tags) VALUES (?, ?, ?, ?)",
            (row_id, key, text, tags),
        )
        con.commit()
        con.close()
        return row_id

    def lt_search(self, query: str, limit: int = 5) -> list[dict]:
        con = _db()
        cur = con.cursor()
        try:
            cur.execute(
                """SELECT lt.id, lt.key, lt.content, lt.tags, lt.ts
                   FROM long_term_fts fts
                   JOIN long_term lt ON lt.id = fts.rowid
                   WHERE long_term_fts MATCH ?
                   ORDER BY rank LIMIT ?""",
                (query, limit),
            )
        except sqlite3.OperationalError:
            # FTS query syntax issue — fall back to LIKE
            cur.execute(
                "SELECT id, key, content, tags, ts FROM long_term WHERE content LIKE ? LIMIT ?",
                (f"%{query}%", limit),
            )
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        return rows

    def lt_stats(self) -> dict:
        con = _db()
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) as cnt, MAX(ts) as latest FROM long_term")
        row = dict(cur.fetchone())
        con.close()
        return {"count": row["cnt"], "latest_ts": row["latest"]}

    # ── Episodic ──────────────────────────────────────────────────────

    def ep_record(self, event: str, kind: str = "info", payload: Any = None) -> None:
        con = _db()
        con.execute(
            "INSERT INTO episodic (event, kind, payload, ts) VALUES (?, ?, ?, ?)",
            (event, kind, json.dumps(payload or {}), time.time()),
        )
        con.commit()
        con.close()

    def ep_recent(self, limit: int = 20, kind: Optional[str] = None) -> list[dict]:
        con = _db()
        cur = con.cursor()
        if kind:
            cur.execute(
                "SELECT * FROM episodic WHERE kind=? ORDER BY ts DESC LIMIT ?", (kind, limit)
            )
        else:
            cur.execute("SELECT * FROM episodic ORDER BY ts DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        return rows

    def ep_stats(self) -> dict:
        con = _db()
        cur = con.cursor()
        cur.execute("SELECT kind, COUNT(*) as cnt FROM episodic GROUP BY kind")
        by_kind = {r["kind"]: r["cnt"] for r in cur.fetchall()}
        cur.execute("SELECT COUNT(*) as total FROM episodic")
        total = cur.fetchone()["total"]
        con.close()
        return {"total": total, "by_kind": by_kind}

    # ── Dashboard summary ─────────────────────────────────────────────

    def summary(self) -> dict:
        with self._short_lock:
            st_count = sum(1 for v in self._short.values() if v["expires"] > time.time())
        lt = self.lt_stats()
        ep = self.ep_stats()
        return {
            "short_term":  {"active_keys": st_count, "ttl_seconds": self._short_ttl},
            "long_term":   lt,
            "episodic":    ep,
        }
