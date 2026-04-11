"""
ORD AI — Observability
Three-perspective monitoring: Engineering traces, Executive cost metrics,
Customer experience quality scoring.
"""
import hashlib
import json
import sqlite3
import threading
import time
from typing import Dict, List, Optional

DB_PATH = "/tmp/ord_ai_observability.db"

# Cost per 1k tokens (input/output) per model family
_COST_TABLE: Dict[str, Dict[str, float]] = {
    "gpt-4":          {"in": 0.030, "out": 0.060},
    "gpt-4-turbo":    {"in": 0.010, "out": 0.030},
    "gpt-3.5-turbo":  {"in": 0.001, "out": 0.002},
    "claude-3-sonnet":{"in": 0.003, "out": 0.015},
    "claude-3-opus":  {"in": 0.015, "out": 0.075},
    "ollama":         {"in": 0.000, "out": 0.000},
    "lmstudio":       {"in": 0.000, "out": 0.000},
    "mock":           {"in": 0.000, "out": 0.000},
}

# Simple hallucination / quality heuristics (no external model needed)
_GROUNDING_NEGATIVE_SIGNALS = [
    "i'm not sure", "i cannot confirm", "as an ai",
    "i don't have access", "made up", "fictional",
]


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _init_db() -> None:
    con = _db()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS traces (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id     TEXT NOT NULL,
            agent_id     TEXT NOT NULL,
            prompt_hash  TEXT,
            tool_call    TEXT DEFAULT '',
            response_preview TEXT DEFAULT '',
            latency_ms   INTEGER DEFAULT 0,
            backend      TEXT DEFAULT '',
            ts           TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cost_events (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            model     TEXT NOT NULL,
            tokens_in INTEGER DEFAULT 0,
            tokens_out INTEGER DEFAULT 0,
            cost_usd  REAL DEFAULT 0,
            task_type TEXT DEFAULT '',
            ts        TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS quality_scores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id    TEXT NOT NULL,
            agent_id    TEXT NOT NULL,
            score       REAL NOT NULL,
            flags       TEXT DEFAULT '[]',
            ts          TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS tr_agent ON traces(agent_id);
        CREATE INDEX IF NOT EXISTS tr_ts    ON traces(ts);
        CREATE INDEX IF NOT EXISTS ce_model ON cost_events(model);
        CREATE INDEX IF NOT EXISTS qs_agent ON quality_scores(agent_id);
    """)
    con.commit()
    con.close()


_init_db()


class AgentObservability:
    """
    Three-perspective observability for the ORD AI ∞-Loop.

    Engineering  → trace_decision()    (every prompt / tool call / response)
    Executive    → track_cost()        (token spend, cost per model, daily totals)
    Customer     → evaluate_quality()  (groundedness, relevance, policy checks)
    """

    _instance: Optional["AgentObservability"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self._trace_count = 0
        self._cost_total_usd = 0.0
        self._quality_total = 0.0
        self._quality_samples = 0

    @classmethod
    def get_instance(cls) -> "AgentObservability":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Engineering view ──────────────────────────────────────────────

    def trace_decision(
        self,
        agent_id: str,
        prompt: str,
        response: str,
        tool_call: str = "",
        backend: str = "mock",
        latency_ms: int = 0,
        trace_id: Optional[str] = None,
    ) -> str:
        """Record a complete agent decision. Returns the trace_id."""
        tid = trace_id or hashlib.md5(
            f"{agent_id}{time.time()}".encode()
        ).hexdigest()[:12]
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        con = _db()
        con.execute(
            """INSERT INTO traces (trace_id, agent_id, prompt_hash, tool_call,
               response_preview, latency_ms, backend, ts)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (tid, agent_id, prompt_hash, tool_call,
             response[:500], latency_ms, backend, now),
        )
        con.commit()
        con.close()

        with self._lock:
            self._trace_count += 1
        return tid

    def get_traces(self, agent_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Retrieve recent traces, optionally filtered by agent."""
        con = _db()
        if agent_id:
            rows = con.execute(
                "SELECT * FROM traces WHERE agent_id = ? ORDER BY id DESC LIMIT ?",
                (agent_id, limit),
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT * FROM traces ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        con.close()
        return [dict(r) for r in rows]

    # ── Executive view ────────────────────────────────────────────────

    def track_cost(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        task_type: str = "default",
    ) -> float:
        """Calculate and record cost for a model call. Returns cost_usd."""
        rates = _COST_TABLE.get(model, _COST_TABLE["mock"])
        cost = (tokens_in / 1000) * rates["in"] + (tokens_out / 1000) * rates["out"]

        con = _db()
        con.execute(
            "INSERT INTO cost_events (model, tokens_in, tokens_out, cost_usd, task_type, ts) VALUES (?,?,?,?,?,?)",
            (model, tokens_in, tokens_out, cost, task_type, time.strftime("%Y-%m-%d %H:%M:%S")),
        )
        con.commit()
        con.close()

        with self._lock:
            self._cost_total_usd += cost
        return cost

    def cost_summary(self, since_hours: float = 24.0) -> Dict:
        """Aggregate spend breakdown for the last N hours."""
        cutoff = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(time.time() - since_hours * 3600),
        )
        con = _db()
        rows = con.execute(
            """SELECT model, SUM(cost_usd) as total_cost,
               SUM(tokens_in) as total_in, SUM(tokens_out) as total_out,
               COUNT(*) as calls
               FROM cost_events WHERE ts >= ?
               GROUP BY model""",
            (cutoff,),
        ).fetchall()
        total = con.execute(
            "SELECT SUM(cost_usd) as t FROM cost_events WHERE ts >= ?", (cutoff,)
        ).fetchone()["t"] or 0.0
        con.close()
        return {
            "period_hours": since_hours,
            "total_usd": round(total, 6),
            "by_model": [dict(r) for r in rows],
        }

    # ── Customer / quality view ───────────────────────────────────────

    def evaluate_quality(
        self,
        response: str,
        grounding_context: str = "",
        agent_id: str = "system",
        trace_id: Optional[str] = None,
    ) -> Dict:
        """
        Score response quality (0-1) using heuristic signals.
        Flags hallucination indicators and policy violations.
        """
        flags: List[str] = []
        score = 1.0

        # Hallucination signals
        lower = response.lower()
        for signal in _GROUNDING_NEGATIVE_SIGNALS:
            if signal in lower:
                flags.append(f"hallucination_signal: '{signal}'")
                score -= 0.15

        # Grounding check: does key context appear in response?
        if grounding_context:
            context_words = set(grounding_context.lower().split())
            response_words = set(lower.split())
            overlap = len(context_words & response_words) / max(len(context_words), 1)
            if overlap < 0.1:
                flags.append("low_grounding_overlap")
                score -= 0.2

        # Length / completeness signal
        if len(response.strip()) < 10:
            flags.append("response_too_short")
            score -= 0.3

        score = max(0.0, min(1.0, score))
        tid = trace_id or hashlib.md5(f"{agent_id}{time.time()}".encode()).hexdigest()[:12]

        con = _db()
        con.execute(
            "INSERT INTO quality_scores (trace_id, agent_id, score, flags, ts) VALUES (?,?,?,?,?)",
            (tid, agent_id, score, json.dumps(flags), time.strftime("%Y-%m-%d %H:%M:%S")),
        )
        con.commit()
        con.close()

        with self._lock:
            self._quality_total += score
            self._quality_samples += 1

        return {"trace_id": tid, "score": round(score, 3), "flags": flags}

    def quality_summary(self) -> Dict:
        """Average quality score and flag frequency."""
        con = _db()
        rows = con.execute(
            "SELECT agent_id, AVG(score) as avg_score, COUNT(*) as samples FROM quality_scores GROUP BY agent_id"
        ).fetchall()
        con.close()
        with self._lock:
            overall = self._quality_total / max(self._quality_samples, 1)
        return {
            "overall_avg_score": round(overall, 3),
            "by_agent": [dict(r) for r in rows],
            "total_evaluated": self._quality_samples,
        }

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        con = _db()
        total_traces = con.execute("SELECT COUNT(*) FROM traces").fetchone()[0]
        total_cost_events = con.execute("SELECT COUNT(*) FROM cost_events").fetchone()[0]
        total_quality = con.execute("SELECT COUNT(*) FROM quality_scores").fetchone()[0]
        con.close()
        with self._lock:
            avg_q = self._quality_total / max(self._quality_samples, 1)
        return {
            "total_traces": total_traces,
            "total_cost_events": total_cost_events,
            "total_quality_evals": total_quality,
            "session_cost_usd": round(self._cost_total_usd, 6),
            "session_avg_quality": round(avg_q, 3),
        }
