"""
ORD AI — Secure Memory Bank
Memory poisoning protection: provenance tracking, audit trail, and rollback.

Every read and write is logged. Suspicious content is flagged for review.
Rollback restores a memory entry to its last known-good state.
"""
import hashlib
import json
import sqlite3
import threading
import time
import uuid
from typing import Dict, List, Optional

DB_PATH = "/tmp/ord_ai_secure_memory.db"

# Patterns that suggest a memory poisoning attempt
_POISON_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard all prior",
    "you are now",
    "forget everything",
    "new system prompt",
    "jailbreak",
    "bypass safety",
    "<script",
    "exec(",
    "__import__",
    "os.system",
    "subprocess.run",
]


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _init_db() -> None:
    con = _db()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS secure_memories (
            id          TEXT PRIMARY KEY,
            content     TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            source      TEXT NOT NULL,
            tags        TEXT DEFAULT '',
            is_flagged  INTEGER DEFAULT 0,
            version     INTEGER DEFAULT 1,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS memory_versions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id   TEXT NOT NULL,
            version     INTEGER NOT NULL,
            content     TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            created_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS memory_audit (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id   TEXT NOT NULL,
            action      TEXT NOT NULL,
            agent_id    TEXT NOT NULL,
            details     TEXT DEFAULT '',
            ts          TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS audit_memory_id ON memory_audit(memory_id);
        CREATE INDEX IF NOT EXISTS audit_agent_id  ON memory_audit(agent_id);
        CREATE INDEX IF NOT EXISTS ver_memory_id   ON memory_versions(memory_id);
    """)
    con.commit()
    con.close()


_init_db()


class SecureMemoryBank:
    """
    Drop-in extension of the main MemoryBank that adds:
      • Provenance tracking (which agent wrote this?)
      • Full audit trail (every read/write logged)
      • Poison pattern detection
      • Per-entry versioned history
      • Rollback to any previous version
    """

    _instance: Optional["SecureMemoryBank"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self.write_count = 0
        self.read_count = 0
        self.flag_count = 0
        self.rollback_count = 0

    @classmethod
    def get_instance(cls) -> "SecureMemoryBank":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Write ─────────────────────────────────────────────────────────

    def add_memory(
        self,
        content: str,
        source: str = "system",
        tags: str = "",
    ) -> Dict:
        """
        Store a memory entry with provenance.
        Returns dict with id, flagged, and message.
        """
        memory_id = str(uuid.uuid4())
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        flagged = self._detect_poison(content)

        con = _db()
        con.execute(
            """INSERT INTO secure_memories
               (id, content, content_hash, source, tags, is_flagged, version, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)""",
            (memory_id, content, content_hash, source, tags, int(flagged), now, now),
        )
        con.execute(
            """INSERT INTO memory_versions (memory_id, version, content, content_hash, created_at)
               VALUES (?, 1, ?, ?, ?)""",
            (memory_id, content, content_hash, now),
        )
        self._audit(con, memory_id, "WRITE", source, f"flagged={flagged}")
        con.commit()
        con.close()

        with self._lock:
            self.write_count += 1
            if flagged:
                self.flag_count += 1

        return {
            "id": memory_id,
            "flagged": flagged,
            "message": (
                "⚠ Memory flagged for review — possible poisoning pattern detected."
                if flagged
                else "Memory stored."
            ),
        }

    # ── Read ──────────────────────────────────────────────────────────

    def read_memory(self, memory_id: str, agent_id: str = "system") -> Optional[str]:
        """Retrieve memory content and log the access."""
        con = _db()
        self._audit(con, memory_id, "READ", agent_id)
        row = con.execute(
            "SELECT content, is_flagged FROM secure_memories WHERE id = ?",
            (memory_id,),
        ).fetchone()
        con.commit()
        con.close()

        if row is None:
            return None

        with self._lock:
            self.read_count += 1

        if row["is_flagged"]:
            return f"[FLAGGED — review required] {row['content']}"
        return row["content"]

    # ── Rollback ──────────────────────────────────────────────────────

    def rollback(self, memory_id: str, to_version: int = 1) -> Dict:
        """Restore a memory entry to a specific version."""
        con = _db()
        row = con.execute(
            "SELECT content, content_hash FROM memory_versions WHERE memory_id = ? AND version = ?",
            (memory_id, to_version),
        ).fetchone()
        if row is None:
            con.close()
            return {"error": f"Version {to_version} not found for memory {memory_id}"}

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        con.execute(
            """UPDATE secure_memories
               SET content = ?, content_hash = ?, is_flagged = 0,
                   version = ?, updated_at = ?
               WHERE id = ?""",
            (row["content"], row["content_hash"], to_version, now, memory_id),
        )
        self._audit(con, memory_id, "ROLLBACK", "system", f"restored_to_version={to_version}")
        con.commit()
        con.close()

        with self._lock:
            self.rollback_count += 1

        return {"status": "rolled_back", "memory_id": memory_id, "version": to_version}

    # ── Query ─────────────────────────────────────────────────────────

    def list_flagged(self) -> List[Dict]:
        """Return all flagged memory entries for human review."""
        con = _db()
        rows = con.execute(
            "SELECT id, content, source, tags, created_at FROM secure_memories WHERE is_flagged = 1"
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    def get_audit_trail(self, memory_id: str) -> List[Dict]:
        """Return full audit history for a memory entry."""
        con = _db()
        rows = con.execute(
            "SELECT action, agent_id, details, ts FROM memory_audit WHERE memory_id = ? ORDER BY id",
            (memory_id,),
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    def get_versions(self, memory_id: str) -> List[Dict]:
        """List all versions of a memory entry."""
        con = _db()
        rows = con.execute(
            "SELECT version, content_hash, created_at FROM memory_versions WHERE memory_id = ? ORDER BY version",
            (memory_id,),
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    # ── Helpers ───────────────────────────────────────────────────────

    def _detect_poison(self, content: str) -> bool:
        lower = content.lower()
        return any(p in lower for p in _POISON_PATTERNS)

    def _audit(
        self,
        con: sqlite3.Connection,
        memory_id: str,
        action: str,
        agent_id: str,
        details: str = "",
    ) -> None:
        con.execute(
            "INSERT INTO memory_audit (memory_id, action, agent_id, details, ts) VALUES (?, ?, ?, ?, ?)",
            (memory_id, action, agent_id, details, time.strftime("%Y-%m-%d %H:%M:%S")),
        )

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        con = _db()
        total = con.execute("SELECT COUNT(*) FROM secure_memories").fetchone()[0]
        flagged = con.execute(
            "SELECT COUNT(*) FROM secure_memories WHERE is_flagged = 1"
        ).fetchone()[0]
        audit_total = con.execute("SELECT COUNT(*) FROM memory_audit").fetchone()[0]
        con.close()
        with self._lock:
            return {
                "total_memories": total,
                "flagged_memories": flagged,
                "audit_log_entries": audit_total,
                "write_count": self.write_count,
                "read_count": self.read_count,
                "flag_count": self.flag_count,
                "rollback_count": self.rollback_count,
                "poison_patterns_monitored": len(_POISON_PATTERNS),
            }
