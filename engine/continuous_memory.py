"""
ORD AI — Continuous Memory
Portable memory that persists across sessions and summarises prior context
for injection into new context windows.
"""
import json
import sqlite3
import threading
import time
from typing import Dict, List, Optional

DB_PATH = "/tmp/ord_ai_continuous_memory.db"


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _init_db() -> None:
    con = _db()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS session_memory (
            session_id  TEXT NOT NULL,
            memory_key  TEXT NOT NULL,
            memory_value TEXT NOT NULL,
            importance  REAL DEFAULT 0.5,
            created_at  TEXT NOT NULL,
            expires_at  TEXT,
            PRIMARY KEY (session_id, memory_key)
        );

        CREATE TABLE IF NOT EXISTS session_meta (
            session_id  TEXT PRIMARY KEY,
            label       TEXT DEFAULT '',
            created_at  TEXT NOT NULL,
            last_active TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS sm_session ON session_memory(session_id);
        CREATE INDEX IF NOT EXISTS sm_importance ON session_memory(importance);
    """)
    con.commit()
    con.close()


_init_db()


class ContinuousMemory:
    """
    Ensures agents can pick up where they left off across session boundaries.

    Key operations:
      • remember()          — store a key-value pair for a session
      • summarize()         — produce a token-budget-aware summary for a new session
      • transfer()          — copy all memories from one session to another
      • list_sessions()     — audit what sessions exist
    """

    _instance: Optional["ContinuousMemory"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self.remember_count = 0
        self.transfer_count = 0

    @classmethod
    def get_instance(cls) -> "ContinuousMemory":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Write ─────────────────────────────────────────────────────────

    def remember(
        self,
        session_id: str,
        key: str,
        value: str,
        importance: float = 0.5,
        ttl_hours: Optional[float] = None,
        label: str = "",
    ) -> None:
        """Store or update a memory entry for a session."""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        expires_at = None
        if ttl_hours is not None:
            expires_ts = time.time() + ttl_hours * 3600
            expires_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_ts))

        con = _db()
        con.execute(
            """INSERT OR REPLACE INTO session_memory
               (session_id, memory_key, memory_value, importance, created_at, expires_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, key, value, importance, now, expires_at),
        )
        # Upsert session meta
        con.execute(
            """INSERT INTO session_meta (session_id, label, created_at, last_active)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(session_id) DO UPDATE SET last_active = excluded.last_active,
               label = CASE WHEN excluded.label != '' THEN excluded.label ELSE label END""",
            (session_id, label, now, now),
        )
        con.commit()
        con.close()
        with self._lock:
            self.remember_count += 1

    # ── Read ──────────────────────────────────────────────────────────

    def recall(self, session_id: str, key: str) -> Optional[str]:
        """Retrieve a single memory entry."""
        con = _db()
        row = con.execute(
            "SELECT memory_value, expires_at FROM session_memory WHERE session_id = ? AND memory_key = ?",
            (session_id, key),
        ).fetchone()
        con.close()
        if row is None:
            return None
        if row["expires_at"] and time.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S") < time.localtime():
            return None  # Expired
        return row["memory_value"]

    def recall_all(self, session_id: str) -> List[Dict]:
        """Return all active (non-expired) memories for a session."""
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        con = _db()
        rows = con.execute(
            """SELECT memory_key, memory_value, importance, created_at, expires_at
               FROM session_memory
               WHERE session_id = ?
               AND (expires_at IS NULL OR expires_at > ?)
               ORDER BY importance DESC""",
            (session_id, now_str),
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    # ── Summarize ─────────────────────────────────────────────────────

    def summarize(self, session_id: str, max_chars: int = 4096) -> str:
        """
        Build a token-budget-aware summary of past session memories for
        injection at the top of a new context window.
        """
        memories = self.recall_all(session_id)
        if not memories:
            return ""

        lines = [f"## Previous session context ({session_id})\n"]
        chars_used = len(lines[0])

        for m in memories:
            entry = f"- **{m['memory_key']}**: {m['memory_value'][:200]}\n"
            if chars_used + len(entry) > max_chars:
                lines.append("- *(additional memories truncated to fit context window)*\n")
                break
            lines.append(entry)
            chars_used += len(entry)

        return "".join(lines)

    # ── Transfer ──────────────────────────────────────────────────────

    def transfer(self, from_session: str, to_session: str) -> int:
        """
        Copy all active memories from one session into another.
        Returns number of entries transferred.
        """
        memories = self.recall_all(from_session)
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        con = _db()
        count = 0
        for m in memories:
            con.execute(
                """INSERT OR REPLACE INTO session_memory
                   (session_id, memory_key, memory_value, importance, created_at, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (to_session, m["memory_key"], m["memory_value"],
                 m["importance"], now, m["expires_at"]),
            )
            count += 1
        # Upsert target session meta
        con.execute(
            """INSERT INTO session_meta (session_id, label, created_at, last_active)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(session_id) DO UPDATE SET last_active = excluded.last_active""",
            (to_session, f"transferred_from_{from_session}", now, now),
        )
        con.commit()
        con.close()
        with self._lock:
            self.transfer_count += 1
        return count

    # ── Housekeeping ──────────────────────────────────────────────────

    def purge_expired(self) -> int:
        """Delete all expired memory entries. Returns count removed."""
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        con = _db()
        cur = con.execute(
            "DELETE FROM session_memory WHERE expires_at IS NOT NULL AND expires_at <= ?",
            (now_str,),
        )
        removed = cur.rowcount
        con.commit()
        con.close()
        return removed

    # ── Audit ─────────────────────────────────────────────────────────

    def list_sessions(self) -> List[Dict]:
        """List all known sessions with metadata."""
        con = _db()
        rows = con.execute(
            "SELECT session_id, label, created_at, last_active FROM session_meta ORDER BY last_active DESC"
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        con = _db()
        total_entries = con.execute("SELECT COUNT(*) FROM session_memory").fetchone()[0]
        total_sessions = con.execute("SELECT COUNT(*) FROM session_meta").fetchone()[0]
        con.close()
        with self._lock:
            return {
                "total_sessions": total_sessions,
                "total_memory_entries": total_entries,
                "remember_count": self.remember_count,
                "transfer_count": self.transfer_count,
            }
