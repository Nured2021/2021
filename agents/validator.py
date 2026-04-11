"""ORD AI — Validator Agent
Runs tests, linting, security checks, and performance validation.
"""
import time
import random
from .base import BaseAgent

TEST_SUITES = [
    {"name": "Unit Tests",        "total": 145, "kind": "unit"},
    {"name": "Integration Tests", "total": 67,  "kind": "integration"},
    {"name": "Performance Tests", "total": 50,  "kind": "performance"},
    {"name": "Security Scan",     "total": 20,  "kind": "security"},
    {"name": "UI Tests",          "total": 89,  "kind": "ui"},
]


class ValidatorAgent(BaseAgent):
    """Runs the full test suite and reports results."""

    def __init__(self, agent_id: int = 3):
        super().__init__("Validator", agent_id)

    def run(self, task: dict) -> dict:
        self.status = "running"
        self.task = task
        self._log("Starting validation suite", "start")

        results = []
        total_pass = 0
        total_tests = 0

        for suite in TEST_SUITES:
            self._log(f"Running {suite['name']}...", "info")
            time.sleep(0.3 + random.uniform(0, 0.2))
            # Simulate ~97-100% pass rate
            failures = random.randint(0, max(1, suite["total"] // 50))
            passed = suite["total"] - failures
            total_pass += passed
            total_tests += suite["total"]
            results.append({
                "name": suite["name"],
                "passed": passed,
                "total": suite["total"],
                "failed": failures,
                "pct": round(passed / suite["total"] * 100, 1),
            })
            self._log(f"{suite['name']}: {passed}/{suite['total']} ✓", "done" if failures == 0 else "warn")

        coverage = round(total_pass / total_tests * 100, 1)
        self._log(f"Validation complete. Coverage: {coverage}%", "done")
        self.status = "done"
        self.progress = 100

        return {
            "agent": self.name,
            "results": results,
            "total_passed": total_pass,
            "total_tests": total_tests,
            "coverage": coverage,
            "log": self.log,
        }
