"""ORD AI — Planner Agent
Breaks user prompts into executable task DAGs.
"""
import time
import random
from .base import BaseAgent


TASK_TEMPLATES = {
    "chatbot":     ["Design conversation flow", "Build NLP engine", "Create response generator",
                    "Add memory/context", "Build chat UI", "Write tests", "Deploy"],
    "ecommerce":   ["Design data models", "Build product catalog", "Implement cart & checkout",
                    "Integrate payments", "Build admin panel", "Write tests", "Deploy"],
    "api":         ["Design API schema", "Build authentication", "Implement endpoints",
                    "Add rate limiting", "Generate documentation", "Write tests", "Deploy"],
    "ai_agent":    ["Define agent goals", "Build reasoning engine", "Implement tools",
                    "Add memory layer", "Create evaluation loop", "Write tests", "Deploy"],
    "dashboard":   ["Design layout", "Build data pipeline", "Create visualizations",
                    "Add real-time updates", "Implement filters", "Write tests", "Deploy"],
    "default":     ["Analyze requirements", "Design architecture", "Implement core features",
                    "Build UI/UX", "Add integrations", "Write tests", "Deploy & monitor"],
}


class PlannerAgent(BaseAgent):
    """Decomposes prompts into executable task lists."""

    def __init__(self, agent_id: int = 1):
        super().__init__("Planner", agent_id)

    def run(self, task: dict) -> dict:
        self.status = "running"
        self.task = task
        prompt = task.get("prompt", "").lower()

        self._log(f"Analyzing prompt: '{task.get('prompt', '')}'", "start")

        # Determine task type
        task_type = "default"
        for key in TASK_TEMPLATES:
            if key in prompt:
                task_type = key
                break

        self._log(f"Detected task type: {task_type}", "info")
        self._simulate_work(steps=3, base_delay=0.2)

        tasks = TASK_TEMPLATES[task_type]
        plan = [{"id": i + 1, "name": t, "status": "pending", "agent": "implementer"}
                for i, t in enumerate(tasks)]

        self._log(f"Plan created: {len(plan)} tasks", "done")
        self.status = "done"
        self.progress = 100

        return {
            "agent": self.name,
            "task_type": task_type,
            "plan": plan,
            "total_tasks": len(plan),
            "log": self.log,
        }
