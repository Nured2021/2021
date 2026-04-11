"""
ORD AI — Post-Mortem & Incident Learning
Capture incidents, categorise root causes, and generate concrete improvements.
Transforms every failure into training data and process improvements.
"""
import json
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional

DB_PATH = "/tmp/ord_ai_incidents.db"

ROOT_CAUSE_CATEGORIES = ["model", "data", "integration", "human", "infrastructure", "unknown"]


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _init_db() -> None:
    con = _db()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS incidents (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id     TEXT UNIQUE NOT NULL,
            title           TEXT NOT NULL,
            severity        TEXT DEFAULT 'medium',  -- critical | high | medium | low
            root_cause      TEXT DEFAULT 'unknown',
            description     TEXT DEFAULT '',
            trace_snapshot  TEXT DEFAULT '{}',
            cascade_effects TEXT DEFAULT '[]',
            improvements    TEXT DEFAULT '[]',
            status          TEXT DEFAULT 'open',    -- open | resolved | wont_fix
            created_at      TEXT NOT NULL,
            resolved_at     TEXT
        );
        CREATE TABLE IF NOT EXISTS improvement_tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT NOT NULL,
            task        TEXT NOT NULL,
            owner       TEXT DEFAULT 'team',
            priority    TEXT DEFAULT 'medium',
            status      TEXT DEFAULT 'open',
            created_at  TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS inc_status   ON incidents(status);
        CREATE INDEX IF NOT EXISTS inc_severity ON incidents(severity);
        CREATE INDEX IF NOT EXISTS imp_incident ON improvement_tasks(incident_id);
    """)
    con.commit()
    con.close()


_init_db()


class PostMortemSystem:
    """
    Continuous post-mortem and incident learning loop.

    Usage:
        pm = PostMortemSystem.get_instance()
        inc_id = pm.record_incident("LLM hallucination spike", severity="high", ...)
        pm.resolve_incident(inc_id, improvements=[...])
    """

    _instance: Optional["PostMortemSystem"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self._open_count = 0
        self._resolved_count = 0

    @classmethod
    def get_instance(cls) -> "PostMortemSystem":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Record ────────────────────────────────────────────────────────

    def record_incident(
        self,
        title: str,
        severity: str = "medium",
        description: str = "",
        root_cause: str = "unknown",
        trace_snapshot: Optional[Dict] = None,
        cascade_effects: Optional[List[str]] = None,
    ) -> str:
        """
        Open a new incident and return its ID.

        root_cause must be one of: model | data | integration | human | infrastructure | unknown
        """
        if root_cause not in ROOT_CAUSE_CATEGORIES:
            root_cause = "unknown"

        import hashlib
        incident_id = hashlib.md5(
            f"{title}{time.time()}".encode()
        ).hexdigest()[:12]
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        # Auto-generate improvement suggestions based on root cause
        auto_improvements = self._suggest_improvements(root_cause, description)

        con = _db()
        con.execute(
            """INSERT INTO incidents
               (incident_id, title, severity, root_cause, description,
                trace_snapshot, cascade_effects, improvements, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                incident_id, title, severity, root_cause, description,
                json.dumps(trace_snapshot or {}),
                json.dumps(cascade_effects or []),
                json.dumps(auto_improvements),
                "open", now,
            ),
        )
        # Create improvement tasks
        for task_text in auto_improvements:
            con.execute(
                "INSERT INTO improvement_tasks (incident_id, task, priority, created_at) VALUES (?,?,?,?)",
                (incident_id, task_text, severity, now),
            )
        con.commit()
        con.close()

        with self._lock:
            self._open_count += 1
        return incident_id

    # ── Resolve ───────────────────────────────────────────────────────

    def resolve_incident(
        self,
        incident_id: str,
        resolution_notes: str = "",
        additional_improvements: Optional[List[str]] = None,
    ) -> Dict:
        """Mark an incident as resolved and add any extra improvements."""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        con = _db()
        row = con.execute(
            "SELECT id FROM incidents WHERE incident_id = ?", (incident_id,)
        ).fetchone()
        if row is None:
            con.close()
            return {"error": f"Incident {incident_id} not found."}

        con.execute(
            "UPDATE incidents SET status='resolved', resolved_at=?, description=description||? WHERE incident_id=?",
            (now, f"\n\nResolution: {resolution_notes}", incident_id),
        )
        for task_text in (additional_improvements or []):
            con.execute(
                "INSERT INTO improvement_tasks (incident_id, task, priority, created_at) VALUES (?,?,'high',?)",
                (incident_id, task_text, now),
            )
        con.commit()
        con.close()

        with self._lock:
            self._open_count = max(0, self._open_count - 1)
            self._resolved_count += 1
        return {"status": "resolved", "incident_id": incident_id}

    # ── Query ─────────────────────────────────────────────────────────

    def list_incidents(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        con = _db()
        filters, params = [], []
        if status:
            filters.append("status = ?")
            params.append(status)
        if severity:
            filters.append("severity = ?")
            params.append(severity)
        where = ("WHERE " + " AND ".join(filters)) if filters else ""
        rows = con.execute(
            f"SELECT incident_id, title, severity, root_cause, status, created_at, resolved_at "
            f"FROM incidents {where} ORDER BY id DESC LIMIT ?",
            params + [limit],
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    def get_incident(self, incident_id: str) -> Optional[Dict]:
        con = _db()
        row = con.execute(
            "SELECT * FROM incidents WHERE incident_id = ?", (incident_id,)
        ).fetchone()
        if row is None:
            con.close()
            return None
        result = dict(row)
        result["trace_snapshot"]  = json.loads(result["trace_snapshot"])
        result["cascade_effects"] = json.loads(result["cascade_effects"])
        result["improvements"]    = json.loads(result["improvements"])
        tasks = con.execute(
            "SELECT task, owner, priority, status FROM improvement_tasks WHERE incident_id = ?",
            (incident_id,),
        ).fetchall()
        result["improvement_tasks"] = [dict(t) for t in tasks]
        con.close()
        return result

    def improvement_tasks(self, status: str = "open") -> List[Dict]:
        con = _db()
        rows = con.execute(
            "SELECT it.*, i.title as incident_title, i.severity FROM improvement_tasks it "
            "JOIN incidents i ON i.incident_id = it.incident_id "
            "WHERE it.status = ? ORDER BY it.id DESC",
            (status,),
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    # ── Internal helpers ──────────────────────────────────────────────

    def _suggest_improvements(self, root_cause: str, description: str) -> List[str]:
        base = {
            "model": [
                "Add output validation and hallucination detection before sending to user.",
                "Implement response grounding check against source documents.",
                "Add model fallback chain for degraded quality detection.",
            ],
            "data": [
                "Add input validation and schema enforcement at ingestion.",
                "Implement data quality scoring before adding to RAG knowledge base.",
                "Add poisoning detection to all memory write paths.",
            ],
            "integration": [
                "Add circuit breaker pattern for all external API calls.",
                "Implement retry with exponential backoff for transient errors.",
                "Add timeout and error budget tracking per integration.",
            ],
            "human": [
                "Add inconsistency detection to HITL feedback loop.",
                "Implement structured approval forms instead of free-text.",
                "Add audit trail for all human decisions.",
            ],
            "infrastructure": [
                "Add health checks and auto-restart for all services.",
                "Implement graceful degradation when backends are unavailable.",
                "Add resource usage alerts before hitting limits.",
            ],
            "unknown": [
                "Capture full execution trace for root cause analysis.",
                "Add structured logging to all agent decision points.",
                "Schedule post-mortem review within 24 hours.",
            ],
        }
        return base.get(root_cause, base["unknown"])

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        con = _db()
        total = con.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
        by_severity = {
            row["severity"]: row["cnt"]
            for row in con.execute(
                "SELECT severity, COUNT(*) as cnt FROM incidents GROUP BY severity"
            ).fetchall()
        }
        by_cause = {
            row["root_cause"]: row["cnt"]
            for row in con.execute(
                "SELECT root_cause, COUNT(*) as cnt FROM incidents GROUP BY root_cause"
            ).fetchall()
        }
        open_tasks = con.execute(
            "SELECT COUNT(*) FROM improvement_tasks WHERE status='open'"
        ).fetchone()[0]
        con.close()
        with self._lock:
            return {
                "total_incidents": total,
                "open_incidents": self._open_count,
                "resolved_incidents": self._resolved_count,
                "by_severity": by_severity,
                "by_root_cause": by_cause,
                "open_improvement_tasks": open_tasks,
            }
