"""
ORD AI — Cost Governor
Budget governance, per-task cost tracking, and ROI calculation.
Prevents runaway spend before it happens.
"""
import sqlite3
import threading
import time
from typing import Dict, List, Optional

DB_PATH = "/tmp/ord_ai_cost.db"

# Cost per 1k tokens (input / output) per model
_MODEL_RATES: Dict[str, Dict[str, float]] = {
    "gpt-4":           {"in": 0.030, "out": 0.060},
    "gpt-4-turbo":     {"in": 0.010, "out": 0.030},
    "gpt-3.5-turbo":   {"in": 0.001, "out": 0.002},
    "claude-3-opus":   {"in": 0.015, "out": 0.075},
    "claude-3-sonnet": {"in": 0.003, "out": 0.015},
    "ollama":          {"in": 0.000, "out": 0.000},
    "lmstudio":        {"in": 0.000, "out": 0.000},
    "mock":            {"in": 0.000, "out": 0.000},
}

# Routing preference by task type (cheapest adequate model first)
_COST_AWARE_ROUTING: Dict[str, List[str]] = {
    "fast_iteration":     ["lmstudio", "ollama", "gpt-3.5-turbo", "mock"],
    "code_generation":    ["lmstudio", "ollama", "gpt-4-turbo",   "mock"],
    "system_architecture":["gpt-4-turbo", "lmstudio", "ollama",  "mock"],
    "review":             ["gpt-4",       "gpt-4-turbo",          "mock"],
    "sensitive_data":     ["lmstudio",    "ollama",               "mock"],
    "default":            ["lmstudio",    "ollama", "gpt-3.5-turbo", "mock"],
}


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _init_db() -> None:
    con = _db()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS cost_ledger (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            model       TEXT NOT NULL,
            task_type   TEXT DEFAULT 'default',
            tokens_in   INTEGER DEFAULT 0,
            tokens_out  INTEGER DEFAULT 0,
            cost_usd    REAL DEFAULT 0.0,
            workflow_id TEXT DEFAULT '',
            ts          TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS budget_alerts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type  TEXT NOT NULL,
            message     TEXT NOT NULL,
            threshold   REAL,
            actual      REAL,
            ts          TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS cl_ts    ON cost_ledger(ts);
        CREATE INDEX IF NOT EXISTS cl_model ON cost_ledger(model);
    """)
    con.commit()
    con.close()


_init_db()


class CostGovernor:
    """
    Prevents runaway AI costs through:
      • Per-request cost tracking with model rates
      • Daily / workflow budget caps
      • Real-time alerts at configurable thresholds
      • Cost-aware model routing
      • ROI calculation
    """

    _instance: Optional["CostGovernor"] = None
    _cls_lock = threading.Lock()

    def __init__(self, daily_budget_usd: float = 50.0, alert_threshold: float = 0.8):
        self.daily_budget = daily_budget_usd
        self.alert_threshold = alert_threshold
        self._lock = threading.Lock()
        self._blocked_count = 0
        self._allowed_count = 0

    @classmethod
    def get_instance(cls) -> "CostGovernor":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Track ─────────────────────────────────────────────────────────

    def record(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        task_type: str = "default",
        workflow_id: str = "",
    ) -> Dict:
        """Record a completed model call and return cost breakdown."""
        rates = _MODEL_RATES.get(model, _MODEL_RATES["mock"])
        cost = (tokens_in / 1000) * rates["in"] + (tokens_out / 1000) * rates["out"]

        con = _db()
        con.execute(
            "INSERT INTO cost_ledger (model, task_type, tokens_in, tokens_out, cost_usd, workflow_id, ts) VALUES (?,?,?,?,?,?,?)",
            (model, task_type, tokens_in, tokens_out, cost, workflow_id,
             time.strftime("%Y-%m-%d %H:%M:%S")),
        )
        con.commit()
        con.close()

        # Check alert threshold
        daily = self._daily_spent()
        if daily >= self.daily_budget * self.alert_threshold:
            self._alert(
                "threshold_warning",
                f"Daily spend ${daily:.4f} reached {self.alert_threshold*100:.0f}% of ${self.daily_budget:.2f} budget",
                self.daily_budget * self.alert_threshold,
                daily,
            )

        with self._lock:
            self._allowed_count += 1
        return {"model": model, "cost_usd": round(cost, 6), "daily_total_usd": round(daily + cost, 4)}

    # ── Check budget ──────────────────────────────────────────────────

    def check_budget(self, estimated_cost: float) -> Dict:
        """
        Before making a call, check if there is remaining budget.
        Returns {"allowed": True/False, "remaining_usd": float}.
        """
        daily = self._daily_spent()
        remaining = self.daily_budget - daily
        allowed = (daily + estimated_cost) <= self.daily_budget

        if not allowed:
            self._alert(
                "budget_exceeded",
                f"Request blocked — daily budget ${self.daily_budget:.2f} exceeded. "
                f"Spent: ${daily:.4f}, request: ${estimated_cost:.6f}",
                self.daily_budget,
                daily + estimated_cost,
            )
            with self._lock:
                self._blocked_count += 1

        return {
            "allowed": allowed,
            "remaining_usd": round(remaining, 4),
            "daily_spent_usd": round(daily, 4),
            "daily_budget_usd": self.daily_budget,
            "estimated_cost": round(estimated_cost, 6),
        }

    # ── Cost-aware routing ────────────────────────────────────────────

    def route_cost_aware(self, task_type: str) -> List[str]:
        """
        Return the ordered list of models to try for this task type,
        sorted cheapest-first while still meeting capability requirements.
        """
        return _COST_AWARE_ROUTING.get(task_type, _COST_AWARE_ROUTING["default"])

    def estimate_cost(self, model: str, estimated_tokens: int) -> float:
        """Quick cost estimate for a call (assumes 50/50 in/out split)."""
        rates = _MODEL_RATES.get(model, {"in": 0.0, "out": 0.0})
        half = estimated_tokens / 2
        return (half / 1000) * rates["in"] + (half / 1000) * rates["out"]

    # ── ROI ───────────────────────────────────────────────────────────

    def calculate_roi(self, revenue_impact_usd: float, infra_cost_usd: float) -> Dict:
        """
        ROI = (incremental revenue – incremental infra cost) ÷ infra cost
        Returns dict for executive dashboards.
        """
        if infra_cost_usd <= 0:
            roi = float("inf") if revenue_impact_usd > 0 else 0.0
        else:
            roi = (revenue_impact_usd - infra_cost_usd) / infra_cost_usd
        return {
            "revenue_impact_usd": revenue_impact_usd,
            "infra_cost_usd": infra_cost_usd,
            "roi": round(roi, 4),
            "roi_pct": round(roi * 100, 2),
            "profitable": roi > 0,
        }

    # ── Reporting ─────────────────────────────────────────────────────

    def daily_summary(self) -> Dict:
        today = time.strftime("%Y-%m-%d")
        con = _db()
        rows = con.execute(
            """SELECT model, task_type,
               SUM(cost_usd) as total_cost,
               SUM(tokens_in + tokens_out) as total_tokens,
               COUNT(*) as calls
               FROM cost_ledger WHERE ts LIKE ?
               GROUP BY model, task_type
               ORDER BY total_cost DESC""",
            (f"{today}%",),
        ).fetchall()
        total = con.execute(
            "SELECT COALESCE(SUM(cost_usd),0) as t FROM cost_ledger WHERE ts LIKE ?",
            (f"{today}%",),
        ).fetchone()["t"]
        alerts = con.execute(
            "SELECT alert_type, message, ts FROM budget_alerts WHERE ts LIKE ? ORDER BY id DESC LIMIT 5",
            (f"{today}%",),
        ).fetchall()
        con.close()
        return {
            "date": today,
            "daily_budget_usd": self.daily_budget,
            "spent_usd": round(total, 4),
            "remaining_usd": round(max(0.0, self.daily_budget - total), 4),
            "utilization_pct": round(100 * total / max(self.daily_budget, 0.001), 1),
            "by_model_task": [dict(r) for r in rows],
            "alerts": [dict(r) for r in alerts],
        }

    def _daily_spent(self) -> float:
        today = time.strftime("%Y-%m-%d")
        con = _db()
        total = con.execute(
            "SELECT COALESCE(SUM(cost_usd),0) as t FROM cost_ledger WHERE ts LIKE ?",
            (f"{today}%",),
        ).fetchone()["t"]
        con.close()
        return total

    def _alert(self, alert_type: str, message: str, threshold: float, actual: float) -> None:
        con = _db()
        con.execute(
            "INSERT INTO budget_alerts (alert_type, message, threshold, actual, ts) VALUES (?,?,?,?,?)",
            (alert_type, message, threshold, actual, time.strftime("%Y-%m-%d %H:%M:%S")),
        )
        con.commit()
        con.close()

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "daily_budget_usd": self.daily_budget,
                "alert_threshold": self.alert_threshold,
                "allowed_requests": self._allowed_count,
                "blocked_requests": self._blocked_count,
                **self.daily_summary(),
            }
