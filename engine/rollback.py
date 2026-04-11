"""
ORD AI — Rollback & Recovery System
Versioned bundle snapshots for one-command rollback of the entire agent state.

Every artifact that defines agent behaviour is captured together:
  • System prompts / identity config
  • Model routing config
  • Memory snapshots (long-term)
  • Fine-tuning checkpoint paths
  • HITL policy version

Automated threshold-based triggers shift traffic to the previous stable bundle
when quality drops below a configurable level.
"""
import hashlib
import json
import sqlite3
import threading
import time
from typing import Dict, List, Optional

DB_PATH = "/tmp/ord_ai_rollback.db"


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _init_db() -> None:
    con = _db()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS bundles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            bundle_id    TEXT UNIQUE NOT NULL,
            label        TEXT NOT NULL,
            created_at   TEXT NOT NULL,
            is_active    INTEGER DEFAULT 0,
            quality_score REAL DEFAULT 1.0,
            manifest     TEXT NOT NULL       -- JSON
        );
        CREATE TABLE IF NOT EXISTS rollback_events (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            from_bundle  TEXT NOT NULL,
            to_bundle    TEXT NOT NULL,
            trigger      TEXT NOT NULL,      -- manual | auto_threshold | emergency
            reason       TEXT DEFAULT '',
            ts           TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS b_active ON bundles(is_active);
        CREATE INDEX IF NOT EXISTS b_ts     ON bundles(created_at);
    """)
    con.commit()
    con.close()


_init_db()


class RollbackSystem:
    """
    One-command rollback for the complete ORD AI agent state.

    Usage:
        rb = RollbackSystem.get_instance()
        bundle_id = rb.snapshot_bundle("v2.1-stable", manifest)
        rb.rollback(bundle_id)
    """

    _instance: Optional["RollbackSystem"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self._auto_threshold: Optional[float] = None
        self._auto_metric: Optional[str] = None
        self._snapshot_count = 0
        self._rollback_count = 0
        # Create an initial "baseline" bundle on first run
        self._ensure_baseline()

    @classmethod
    def get_instance(cls) -> "RollbackSystem":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Snapshot ──────────────────────────────────────────────────────

    def snapshot_bundle(
        self,
        label: str,
        manifest: Dict,
        set_active: bool = True,
    ) -> str:
        """
        Capture a versioned bundle.

        manifest keys (all optional):
          system_prompt, routing_config, memory_snapshot_path,
          finetune_checkpoint, hitl_policy_version, extra
        """
        content = json.dumps(manifest, sort_keys=True)
        bundle_id = hashlib.sha256(
            f"{label}{content}{time.time()}".encode()
        ).hexdigest()[:16]
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        con = _db()
        if set_active:
            con.execute("UPDATE bundles SET is_active = 0")
        con.execute(
            """INSERT INTO bundles (bundle_id, label, created_at, is_active, quality_score, manifest)
               VALUES (?, ?, ?, ?, 1.0, ?)""",
            (bundle_id, label, now, int(set_active), content),
        )
        con.commit()
        con.close()

        with self._lock:
            self._snapshot_count += 1
        return bundle_id

    # ── Rollback ──────────────────────────────────────────────────────

    def rollback(
        self,
        bundle_id: str,
        trigger: str = "manual",
        reason: str = "",
    ) -> Dict:
        """Restore a specific bundle as the active version."""
        con = _db()
        row = con.execute(
            "SELECT bundle_id, label, manifest FROM bundles WHERE bundle_id = ?",
            (bundle_id,),
        ).fetchone()
        if row is None:
            con.close()
            return {"error": f"Bundle {bundle_id} not found."}

        # Find current active bundle for the event log
        active_row = con.execute(
            "SELECT bundle_id FROM bundles WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
        ).fetchone()
        from_bundle = active_row["bundle_id"] if active_row else "none"

        # Swap active
        con.execute("UPDATE bundles SET is_active = 0")
        con.execute("UPDATE bundles SET is_active = 1 WHERE bundle_id = ?", (bundle_id,))
        con.execute(
            """INSERT INTO rollback_events (from_bundle, to_bundle, trigger, reason, ts)
               VALUES (?, ?, ?, ?, ?)""",
            (from_bundle, bundle_id, trigger, reason, time.strftime("%Y-%m-%d %H:%M:%S")),
        )
        con.commit()
        con.close()

        with self._lock:
            self._rollback_count += 1

        return {
            "status": "rolled_back",
            "bundle_id": bundle_id,
            "label": row["label"],
            "trigger": trigger,
            "manifest": json.loads(row["manifest"]),
        }

    def rollback_to_previous(self, reason: str = "manual") -> Dict:
        """Rollback to the second-most-recent bundle."""
        con = _db()
        rows = con.execute(
            "SELECT bundle_id FROM bundles ORDER BY id DESC LIMIT 2"
        ).fetchall()
        con.close()
        if len(rows) < 2:
            return {"error": "No previous bundle to roll back to."}
        return self.rollback(rows[1]["bundle_id"], trigger="manual", reason=reason)

    # ── Auto-threshold ────────────────────────────────────────────────

    def set_auto_rollback(self, metric: str, threshold: float) -> None:
        """
        Configure automated rollback.
        Example: metric="hallucination_rate", threshold=0.05
        """
        with self._lock:
            self._auto_metric = metric
            self._auto_threshold = threshold

    def check_auto_rollback(self, metric: str, current_value: float) -> Dict:
        """
        Call after each quality evaluation.
        If the metric exceeds the threshold, rollback is triggered automatically.
        """
        with self._lock:
            configured_metric = self._auto_metric
            threshold = self._auto_threshold

        if configured_metric != metric or threshold is None:
            return {"triggered": False}

        if current_value > threshold:
            result = self.rollback_to_previous(
                reason=f"auto: {metric}={current_value:.3f} > threshold {threshold}"
            )
            result["triggered"] = True
            result["metric"] = metric
            result["value"] = current_value
            return result

        return {"triggered": False, "metric": metric, "value": current_value}

    # ── Update quality ────────────────────────────────────────────────

    def update_bundle_quality(self, bundle_id: str, quality_score: float) -> None:
        con = _db()
        con.execute(
            "UPDATE bundles SET quality_score = ? WHERE bundle_id = ?",
            (quality_score, bundle_id),
        )
        con.commit()
        con.close()

    # ── Query ─────────────────────────────────────────────────────────

    def list_bundles(self) -> List[Dict]:
        con = _db()
        rows = con.execute(
            "SELECT bundle_id, label, created_at, is_active, quality_score FROM bundles ORDER BY id DESC"
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    def get_active_bundle(self) -> Optional[Dict]:
        con = _db()
        row = con.execute(
            "SELECT bundle_id, label, created_at, quality_score, manifest FROM bundles WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
        ).fetchone()
        con.close()
        if row is None:
            return None
        d = dict(row)
        d["manifest"] = json.loads(d["manifest"])
        return d

    def rollback_history(self, limit: int = 20) -> List[Dict]:
        con = _db()
        rows = con.execute(
            "SELECT * FROM rollback_events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    # ── Status ────────────────────────────────────────────────────────

    def _ensure_baseline(self) -> None:
        con = _db()
        count = con.execute("SELECT COUNT(*) FROM bundles").fetchone()[0]
        con.close()
        if count == 0:
            self.snapshot_bundle(
                "baseline-v1.0.0",
                {
                    "system_prompt": "ORD AI initial baseline",
                    "routing_config": "default",
                    "hitl_policy_version": "1.0",
                },
                set_active=True,
            )

    def get_status(self) -> Dict:
        con = _db()
        total_bundles = con.execute("SELECT COUNT(*) FROM bundles").fetchone()[0]
        total_rollbacks = con.execute("SELECT COUNT(*) FROM rollback_events").fetchone()[0]
        con.close()
        with self._lock:
            return {
                "total_bundles": total_bundles,
                "total_rollback_events": total_rollbacks,
                "snapshot_count": self._snapshot_count,
                "rollback_count": self._rollback_count,
                "auto_rollback_metric": self._auto_metric,
                "auto_rollback_threshold": self._auto_threshold,
                "active_bundle": self.get_active_bundle(),
            }
