"""
ORD AI — MultiModelRouter
Routes tasks to the best available LLM backend.
Supports: LMStudio, Ollama, OpenAI-compatible, Mock (always works).
"""
import json
import os
import time
import random
import threading
from typing import Optional

try:
    import urllib.request
    import urllib.error
    _urllib_ok = True
except ImportError:
    _urllib_ok = False

# ── Task type → preferred backend routing ────────────────────────────
ROUTING_TABLE = {
    "code_generation":    ["lmstudio", "ollama", "openai", "mock"],
    "system_architecture":["ollama",   "lmstudio","openai", "mock"],
    "fast_iteration":     ["ollama",   "lmstudio","openai", "mock"],
    "sensitive_data":     ["lmstudio", "ollama",  "mock"],
    "validation":         ["lmstudio", "ollama",  "openai", "mock"],
    "review":             ["openai",   "lmstudio","ollama", "mock"],
    "merge":              ["lmstudio", "ollama",  "openai", "mock"],
    "default":            ["lmstudio", "ollama",  "openai", "mock"],
}

# ── Mock responses for offline operation ─────────────────────────────
MOCK_RESPONSES = {
    "code_generation": [
        "```python\ndef solution(input_data):\n    # AI-generated implementation\n    result = process(input_data)\n    return result\n```",
        "```javascript\nconst handler = async (req, res) => {\n  const data = await processRequest(req.body);\n  res.json({ success: true, data });\n};\n```",
    ],
    "system_architecture": [
        "Architecture plan: 3-tier microservices with API gateway, Redis cache, PostgreSQL primary + read replicas, deployed on Kubernetes.",
        "Recommended: Event-driven architecture using Kafka for async processing, CQRS pattern for read/write separation, gRPC for service communication.",
    ],
    "validation": [
        "Validation complete: Code quality 94/100. No critical issues. 2 style warnings. Security scan passed.",
        "Tests passing: 147/150. Coverage: 94%. Performance: within SLA thresholds.",
    ],
    "review": [
        "Code review complete: Logic is sound. Suggest adding error handling in lines 34-45. Documentation is good.",
        "Review passed. Consider extracting the validation logic into a separate utility. Overall implementation is clean.",
    ],
    "default": [
        "Task analyzed and completed successfully. Output meets quality standards.",
        "Processing complete. All requirements addressed. Ready for next stage.",
    ],
}


class ModelRouter:
    """Routes prompts to the best available LLM backend."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self, config_path: str = "autopilot/config.json"):
        self.config = self._load_config(config_path)
        self.backends = self.config.get("llm_backends", {})
        self._availability: dict[str, bool] = {}
        self._last_check: dict[str, float] = {}
        self._check_interval = 30  # seconds
        self.stats = {b: {"calls": 0, "tokens": 0, "errors": 0, "latency_ms": []} for b in self.backends}
        self.stats["mock"] = {"calls": 0, "tokens": 0, "errors": 0, "latency_ms": []}
        self._probe_all()

    @classmethod
    def get_instance(cls, config_path: str = "autopilot/config.json") -> "ModelRouter":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(config_path)
        return cls._instance

    def _load_config(self, path: str) -> dict:
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return {"llm_backends": {}, "agents": {}}

    def _probe_backend(self, name: str) -> bool:
        """Check if a backend is reachable."""
        cfg = self.backends.get(name, {})
        base_url = cfg.get("base_url", "")
        if not base_url or not _urllib_ok:
            return False
        try:
            url = base_url.rstrip("/") + "/models"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {cfg.get('api_key','')}"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _probe_all(self):
        for name in self.backends:
            self._availability[name] = self._probe_backend(name)
            self._last_check[name] = time.time()
        self._availability["mock"] = True

    def _is_available(self, backend: str) -> bool:
        if backend == "mock":
            return True
        now = time.time()
        last = self._last_check.get(backend, 0)
        if now - last > self._check_interval:
            self._availability[backend] = self._probe_backend(backend)
            self._last_check[backend] = now
        return self._availability.get(backend, False)

    def _call_openai_compatible(self, backend: str, prompt: str, task_type: str) -> str:
        cfg = self.backends[backend]
        base_url = cfg["base_url"].rstrip("/")
        model = cfg.get("model", "gpt-3.5-turbo")
        api_key = cfg.get("api_key", "")
        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": "You are ORD AI, an expert AI builder. Be concise and precise."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1024,
            "temperature": 0.1,
        }).encode()
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]

    def _call_mock(self, task_type: str) -> str:
        pool = MOCK_RESPONSES.get(task_type, MOCK_RESPONSES["default"])
        return random.choice(pool)

    def ask(self, prompt: str, task_type: str = "default") -> dict:
        """Route prompt to best available backend. Returns response + metadata."""
        route = ROUTING_TABLE.get(task_type, ROUTING_TABLE["default"])
        for backend in route:
            if not self._is_available(backend):
                continue
            t0 = time.time()
            try:
                if backend == "mock":
                    response = self._call_mock(task_type)
                    latency = int((time.time() - t0) * 1000) + random.randint(80, 300)
                else:
                    response = self._call_openai_compatible(backend, prompt, task_type)
                    latency = int((time.time() - t0) * 1000)
                tokens = len(response.split()) * 4 // 3  # rough estimate
                self.stats[backend]["calls"] += 1
                self.stats[backend]["tokens"] += tokens
                self.stats[backend]["latency_ms"].append(latency)
                if len(self.stats[backend]["latency_ms"]) > 100:
                    self.stats[backend]["latency_ms"] = self.stats[backend]["latency_ms"][-50:]
                return {
                    "response": response,
                    "backend": backend,
                    "model": self.backends.get(backend, {}).get("model", "mock"),
                    "task_type": task_type,
                    "latency_ms": latency,
                    "tokens": tokens,
                    "success": True,
                }
            except Exception as e:
                self.stats.setdefault(backend, {}).setdefault("errors", 0)
                self.stats[backend]["errors"] = self.stats[backend].get("errors", 0) + 1
                self._availability[backend] = False
                continue
        # Should never reach here since mock always works
        return {"response": "No backend available.", "backend": "none", "success": False}

    def get_status(self) -> dict:
        """Return full router status for the dashboard."""
        result = {}
        for name in list(self.backends.keys()) + ["mock"]:
            s = self.stats.get(name, {})
            lats = s.get("latency_ms", [])
            avg_lat = int(sum(lats) / len(lats)) if lats else 0
            avail = self._is_available(name)
            cfg = self.backends.get(name, {})
            result[name] = {
                "available": avail,
                "model": cfg.get("model", "built-in mock") if name != "mock" else "ORD-Mock-v1",
                "calls": s.get("calls", 0),
                "tokens": s.get("tokens", 0),
                "errors": s.get("errors", 0),
                "avg_latency_ms": avg_lat,
                "base_url": cfg.get("base_url", "internal") if name != "mock" else "internal",
            }
        return result

    def active_backend(self) -> str:
        """Return name of currently active (preferred available) backend."""
        for name in ["lmstudio", "ollama", "openai", "mock"]:
            if self._is_available(name):
                return name
        return "mock"
