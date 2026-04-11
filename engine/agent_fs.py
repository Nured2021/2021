"""
ORD AI — Agent Filesystem (AgentFS)
Unified SQLite-backed storage: filesystem, key-value store, and audit trail
in one portable file.  Queryable with SQL, portable across environments.
"""
import hashlib
import json
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional

DB_PATH = "/tmp/ord_ai_agentfs.db"


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _init_db() -> None:
    con = _db()
    con.executescript("""
        -- Filesystem table: blobs stored by virtual path
        CREATE TABLE IF NOT EXISTS fs_files (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            path        TEXT UNIQUE NOT NULL,
            content     BLOB NOT NULL,
            content_type TEXT DEFAULT 'text/plain',
            size_bytes  INTEGER DEFAULT 0,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        -- Key-value store: agent state, configs, counters
        CREATE TABLE IF NOT EXISTS kv_store (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL,
            namespace   TEXT DEFAULT 'default',
            updated_at  TEXT NOT NULL
        );

        -- Immutable audit / tool-call log
        CREATE TABLE IF NOT EXISTS tool_calls (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tool        TEXT NOT NULL,
            agent_id    TEXT DEFAULT 'system',
            input_json  TEXT DEFAULT '{}',
            output_json TEXT DEFAULT '{}',
            duration_ms INTEGER DEFAULT 0,
            ts          TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS fs_path   ON fs_files(path);
        CREATE INDEX IF NOT EXISTS kv_ns     ON kv_store(namespace);
        CREATE INDEX IF NOT EXISTS tc_tool   ON tool_calls(tool);
        CREATE INDEX IF NOT EXISTS tc_agent  ON tool_calls(agent_id);
        CREATE INDEX IF NOT EXISTS tc_ts     ON tool_calls(ts);
    """)
    con.commit()
    con.close()


_init_db()


class AgentFS:
    """
    Unified agent filesystem.

    fs.*    — file-system operations (write, read, list, delete)
    kv.*    — key-value operations (set, get, delete, list)
    tools.* — immutable audit log (record, query)
    sql.*   — raw SQL for power users / debugging
    """

    _instance: Optional["AgentFS"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self._write_count = 0
        self._read_count = 0
        self._tool_call_count = 0

    @classmethod
    def get_instance(cls) -> "AgentFS":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Filesystem ────────────────────────────────────────────────────

    def fs_write(
        self,
        path: str,
        content: str,
        content_type: str = "text/plain",
    ) -> Dict:
        """Write (or overwrite) a file at the given virtual path."""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        data = content.encode("utf-8") if isinstance(content, str) else content
        con = _db()
        con.execute(
            """INSERT INTO fs_files (path, content, content_type, size_bytes, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(path) DO UPDATE SET
                   content = excluded.content,
                   content_type = excluded.content_type,
                   size_bytes = excluded.size_bytes,
                   updated_at = excluded.updated_at""",
            (path, data, content_type, len(data), now, now),
        )
        con.commit()
        con.close()
        with self._lock:
            self._write_count += 1
        return {"path": path, "size_bytes": len(data), "status": "written"}

    def fs_read(self, path: str) -> Optional[str]:
        """Read a file. Returns None if not found."""
        con = _db()
        row = con.execute("SELECT content FROM fs_files WHERE path = ?", (path,)).fetchone()
        con.close()
        if row is None:
            return None
        with self._lock:
            self._read_count += 1
        data = row["content"]
        return data.decode("utf-8") if isinstance(data, (bytes, bytearray)) else data

    def fs_list(self, prefix: str = "/") -> List[Dict]:
        """List files under a path prefix."""
        con = _db()
        rows = con.execute(
            "SELECT path, content_type, size_bytes, updated_at FROM fs_files WHERE path LIKE ? ORDER BY path",
            (f"{prefix}%",),
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    def fs_delete(self, path: str) -> bool:
        con = _db()
        cur = con.execute("DELETE FROM fs_files WHERE path = ?", (path,))
        con.commit()
        con.close()
        return cur.rowcount > 0

    # ── Key-value ─────────────────────────────────────────────────────

    def kv_set(self, key: str, value: Any, namespace: str = "default") -> None:
        """Store any JSON-serialisable value."""
        con = _db()
        con.execute(
            """INSERT INTO kv_store (key, value, namespace, updated_at) VALUES (?, ?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value,
               namespace = excluded.namespace, updated_at = excluded.updated_at""",
            (key, json.dumps(value), namespace, time.strftime("%Y-%m-%d %H:%M:%S")),
        )
        con.commit()
        con.close()

    def kv_get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value by key."""
        con = _db()
        row = con.execute("SELECT value FROM kv_store WHERE key = ?", (key,)).fetchone()
        con.close()
        if row is None:
            return default
        return json.loads(row["value"])

    def kv_delete(self, key: str) -> bool:
        con = _db()
        cur = con.execute("DELETE FROM kv_store WHERE key = ?", (key,))
        con.commit()
        con.close()
        return cur.rowcount > 0

    def kv_list(self, namespace: str = "default") -> List[Dict]:
        """List all keys in a namespace."""
        con = _db()
        rows = con.execute(
            "SELECT key, updated_at FROM kv_store WHERE namespace = ? ORDER BY key",
            (namespace,),
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    # ── Tool-call audit log ───────────────────────────────────────────

    def tools_record(
        self,
        tool: str,
        input_data: Any,
        output_data: Any,
        agent_id: str = "system",
        duration_ms: int = 0,
    ) -> int:
        """Append an immutable tool-call record. Returns the record ID."""
        con = _db()
        cur = con.execute(
            """INSERT INTO tool_calls (tool, agent_id, input_json, output_json, duration_ms, ts)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                tool,
                agent_id,
                json.dumps(input_data, default=str)[:2000],
                json.dumps(output_data, default=str)[:2000],
                duration_ms,
                time.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        record_id = cur.lastrowid
        con.commit()
        con.close()
        with self._lock:
            self._tool_call_count += 1
        return record_id

    def tools_query(
        self,
        tool: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """Query the tool-call log."""
        con = _db()
        if tool and agent_id:
            rows = con.execute(
                "SELECT * FROM tool_calls WHERE tool = ? AND agent_id = ? ORDER BY id DESC LIMIT ?",
                (tool, agent_id, limit),
            ).fetchall()
        elif tool:
            rows = con.execute(
                "SELECT * FROM tool_calls WHERE tool = ? ORDER BY id DESC LIMIT ?",
                (tool, limit),
            ).fetchall()
        elif agent_id:
            rows = con.execute(
                "SELECT * FROM tool_calls WHERE agent_id = ? ORDER BY id DESC LIMIT ?",
                (agent_id, limit),
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT * FROM tool_calls ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    # ── Raw SQL ───────────────────────────────────────────────────────

    def sql_query(self, query: str) -> List[Dict]:
        """
        Execute a read-only SQL query for debugging and analysis.
        Only SELECT statements are allowed.
        """
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT statements are permitted.")
        con = _db()
        rows = con.execute(query).fetchall()
        con.close()
        return [dict(r) for r in rows]

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        con = _db()
        file_count = con.execute("SELECT COUNT(*) FROM fs_files").fetchone()[0]
        kv_count   = con.execute("SELECT COUNT(*) FROM kv_store").fetchone()[0]
        tc_count   = con.execute("SELECT COUNT(*) FROM tool_calls").fetchone()[0]
        total_size = con.execute("SELECT COALESCE(SUM(size_bytes),0) FROM fs_files").fetchone()[0]
        con.close()
        with self._lock:
            return {
                "db_path": DB_PATH,
                "files": file_count,
                "kv_entries": kv_count,
                "tool_calls": tc_count,
                "total_file_bytes": total_size,
                "write_count": self._write_count,
                "read_count": self._read_count,
                "tool_call_count": self._tool_call_count,
            }
