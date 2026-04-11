"""ORD AI — Base Agent"""
import time
import random


class BaseAgent:
    """Base class for all ORD AI agents."""

    def __init__(self, name: str, agent_id: int = 0):
        self.name = name
        self.agent_id = agent_id
        self.status = "idle"
        self.task = None
        self.progress = 0
        self.log = []

    def _log(self, msg: str, kind: str = "info"):
        entry = {"time": time.strftime("%H:%M:%S"), "agent": self.name, "msg": msg, "kind": kind}
        self.log.append(entry)
        return entry

    def _simulate_work(self, steps: int = 5, base_delay: float = 0.3):
        """Simulate work with progress updates."""
        for i in range(steps):
            self.progress = int((i + 1) / steps * 100)
            time.sleep(base_delay + random.uniform(0, 0.2))

    def run(self, task: dict) -> dict:
        raise NotImplementedError
