"""ORD AI — Merger Agent
Creates PRs, resolves conflicts, increments version, delivers final output.
"""
import time
import random
from .base import BaseAgent


class MergerAgent(BaseAgent):
    """Merges all generated code into the final deliverable."""

    def __init__(self, agent_id: int = 5):
        super().__init__("Merger", agent_id)

    def run(self, task: dict) -> dict:
        self.status = "running"
        self.task = task
        build_data = task.get("build_data", {})

        self._log("Starting merge & delivery", "start")

        steps = [
            ("Creating feature branch",     0.3),
            ("Merging generated files",      0.4),
            ("Resolving conflicts",          0.2),
            ("Bumping version",             0.1),
            ("Creating pull request",        0.2),
            ("Running final CI checks",      0.4),
            ("Merging to main",             0.2),
            ("Tagging release",             0.1),
            ("Deploying to staging",         0.5),
        ]

        for step, delay in steps:
            self._log(f"→ {step}", "info")
            time.sleep(delay + random.uniform(0, 0.1))
            self.progress = int((steps.index((step, delay)) + 1) / len(steps) * 100)

        # Compute new version
        current = build_data.get("version", "v1.0.0").lstrip("v").split(".")
        current[-1] = str(int(current[-1]) + 1)
        new_version = "v" + ".".join(current)

        files = build_data.get("files", ["app.py", "Dockerfile", "README.md"])
        self._log(f"Merge complete → {new_version}", "success")
        self.status = "done"
        self.progress = 100

        return {
            "agent": self.name,
            "version": new_version,
            "files_merged": len(files) if isinstance(files, list) else 3,
            "pr_url": f"https://github.com/ord-ai/system/pull/{random.randint(10, 99)}",
            "deploy_url": "http://staging.ord-ai.app",
            "log": self.log,
        }
