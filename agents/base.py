"""ORD AI — Base Agent"""
import time
import random

try:
    from engine.model_router import ModelRouter
    from engine.memory import MemoryBank
    from engine.rag import HybridRAG
    _ENGINE_OK = True
except ImportError:
    _ENGINE_OK = False


class BaseAgent:
    """Base class for all ORD AI agents."""

    def __init__(self, name: str, agent_id: int = 0):
        self.name = name
        self.agent_id = agent_id
        self.status = "idle"
        self.task = None
        self.progress = 0
        self.log = []
        # Wire up engine components if available
        if _ENGINE_OK:
            self.router = ModelRouter.get_instance()
            self.memory = MemoryBank.get_instance()
            self.rag = HybridRAG.get_instance()
        else:
            self.router = None
            self.memory = None
            self.rag = None

    def _log(self, msg: str, kind: str = "info"):
        entry = {"time": time.strftime("%H:%M:%S"), "agent": self.name, "msg": msg, "kind": kind}
        self.log.append(entry)
        return entry

    def _ask_llm(self, prompt: str, task_type: str = "default") -> str:
        """Ask the LLM via ModelRouter. Falls back to mock if unavailable."""
        if self.router:
            result = self.router.ask(prompt, task_type=task_type)
            return result["response"]
        return f"[{self.name}] Task completed: {prompt[:60]}..."

    def _fetch_context(self, query: str) -> str:
        """Fetch relevant context from RAG."""
        if self.rag:
            result = self.rag.query(query, top_k=3)
            return result["context"]
        return ""

    def _remember(self, key: str, value):
        """Store a value in short-term memory."""
        if self.memory:
            self.memory.st_set(f"{self.name}:{key}", value)

    def _recall(self, key: str):
        """Recall a value from short-term memory."""
        if self.memory:
            return self.memory.st_get(f"{self.name}:{key}")
        return None

    def _simulate_work(self, steps: int = 5, base_delay: float = 0.3):
        """Simulate work with progress updates."""
        for i in range(steps):
            self.progress = int((i + 1) / steps * 100)
            time.sleep(base_delay + random.uniform(0, 0.2))

    def run(self, task: dict) -> dict:
        raise NotImplementedError
