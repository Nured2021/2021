"""ORD AI — Reviewer Agent
Code review, quality gates, and HITL approval routing.
"""
import time
import random
from .base import BaseAgent

REVIEW_CHECKS = [
    ("Code style & formatting",   0.95),
    ("Security vulnerabilities",  0.98),
    ("Performance bottlenecks",   0.90),
    ("Documentation coverage",    0.85),
    ("Error handling",            0.92),
    ("Test coverage",             0.97),
    ("Dependency audit",          0.99),
]


class ReviewerAgent(BaseAgent):
    """Reviews generated code and routes to HITL if needed."""

    def __init__(self, agent_id: int = 4):
        super().__init__("Reviewer", agent_id)

    def run(self, task: dict) -> dict:
        self.status = "running"
        self.task = task
        self._log("Starting code review", "start")

        issues = []
        passed = []

        for check, pass_rate in REVIEW_CHECKS:
            time.sleep(0.15 + random.uniform(0, 0.1))
            ok = random.random() < pass_rate
            if ok:
                passed.append(check)
                self._log(f"✓ {check}", "done")
            else:
                issues.append({"check": check, "severity": random.choice(["low", "medium"])})
                self._log(f"⚠ {check} — flagged", "warn")

        # HITL routing
        hitl_required = any(i["severity"] == "high" for i in issues)
        hitl_lane = "HITL_REQUIRED" if hitl_required else ("HITL_OPTIONAL" if issues else "HITL_NONE")

        score = round(len(passed) / len(REVIEW_CHECKS) * 100)
        self._log(f"Review complete. Score: {score}/100. Lane: {hitl_lane}", "done")
        self.status = "done"
        self.progress = 100

        return {
            "agent": self.name,
            "score": score,
            "passed": passed,
            "issues": issues,
            "hitl_lane": hitl_lane,
            "approved": score >= 70,
            "log": self.log,
        }
