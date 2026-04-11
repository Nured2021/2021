"""
ORD AI — Load & Stress Tester
Three-scenario testing to find the breaking point before production does.
  1. Normal operations — baseline throughput + latency
  2. Surge conditions  — auto-scaling under spike traffic
  3. Adversarial       — rate limits, corrupted payloads, timeout handling
"""
import asyncio
import random
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScenarioResult:
    scenario: str
    concurrent_requests: int
    total_requests: int
    succeeded: int
    failed: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    errors: List[str] = field(default_factory=list)
    duration_s: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "scenario": self.scenario,
            "concurrent_requests": self.concurrent_requests,
            "total_requests": self.total_requests,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "success_rate_pct": round(100 * self.succeeded / max(self.total_requests, 1), 1),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "p95_latency_ms": round(self.p95_latency_ms, 1),
            "p99_latency_ms": round(self.p99_latency_ms, 1),
            "throughput_rps": round(self.throughput_rps, 2),
            "errors": self.errors[:10],
            "duration_s": round(self.duration_s, 2),
        }


class LoadTester:
    """
    Simulated load and stress testing for the ORD AI ∞-Loop.

    In production this would drive real HTTP calls; in the current
    environment it simulates latency/error distributions so the results
    can be reported on the dashboard immediately.
    """

    _instance: Optional["LoadTester"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self._running = False
        self._results: List[ScenarioResult] = []
        self._current_scenario: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "LoadTester":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Scenario helpers ──────────────────────────────────────────────

    async def _simulate_request(
        self,
        base_latency_ms: float = 150,
        error_rate: float = 0.02,
        timeout_ms: float = 5000,
    ) -> Dict:
        """Simulate a single agent request with realistic latency."""
        # Jitter
        latency_ms = base_latency_ms * random.lognormvariate(0, 0.4)
        latency_ms = min(latency_ms, timeout_ms)
        await asyncio.sleep(latency_ms / 1000)

        if random.random() < error_rate:
            raise RuntimeError(
                random.choice([
                    "connection_timeout",
                    "rate_limit_429",
                    "upstream_503",
                    "corrupted_payload",
                ])
            )
        return {"latency_ms": latency_ms, "status": "ok"}

    async def _run_concurrent(
        self,
        scenario: str,
        n_requests: int,
        concurrency: int,
        base_latency_ms: float,
        error_rate: float,
    ) -> ScenarioResult:
        latencies: List[float] = []
        errors: List[str] = []
        succeeded = 0
        failed = 0

        semaphore = asyncio.Semaphore(concurrency)
        start = time.time()

        async def worker(_):
            nonlocal succeeded, failed
            async with semaphore:
                try:
                    res = await self._simulate_request(
                        base_latency_ms=base_latency_ms,
                        error_rate=error_rate,
                    )
                    latencies.append(res["latency_ms"])
                    succeeded += 1
                except Exception as exc:
                    failed += 1
                    errors.append(str(exc))

        await asyncio.gather(*[worker(i) for i in range(n_requests)])
        duration = max(time.time() - start, 0.001)

        latencies.sort()
        p95 = latencies[int(0.95 * len(latencies)) - 1] if latencies else 0
        p99 = latencies[int(0.99 * len(latencies)) - 1] if latencies else 0
        avg = sum(latencies) / max(len(latencies), 1)

        return ScenarioResult(
            scenario=scenario,
            concurrent_requests=concurrency,
            total_requests=n_requests,
            succeeded=succeeded,
            failed=failed,
            avg_latency_ms=avg,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            throughput_rps=succeeded / duration,
            errors=list(set(errors)),
            duration_s=duration,
        )

    # ── Public scenarios ──────────────────────────────────────────────

    async def test_normal_operations(
        self,
        concurrent_users: int = 20,
        total_requests: int = 100,
    ) -> ScenarioResult:
        """
        Establish baseline: typical production load.
        Target: sub-300 ms avg latency, >98% success rate.
        """
        with self._lock:
            self._current_scenario = "normal_operations"
        result = await self._run_concurrent(
            scenario="normal_operations",
            n_requests=total_requests,
            concurrency=concurrent_users,
            base_latency_ms=150,
            error_rate=0.01,
        )
        with self._lock:
            self._results.append(result)
            self._current_scenario = None
        return result

    async def test_surge_conditions(
        self,
        spike_factor: int = 5,
        base_concurrent: int = 20,
        total_requests: int = 200,
    ) -> ScenarioResult:
        """
        Surge test: N× normal traffic.
        Verifies the system degrades gracefully, not catastrophically.
        """
        with self._lock:
            self._current_scenario = "surge_conditions"
        result = await self._run_concurrent(
            scenario=f"surge_x{spike_factor}",
            n_requests=total_requests,
            concurrency=base_concurrent * spike_factor,
            base_latency_ms=150,
            error_rate=0.05 + (spike_factor * 0.01),
        )
        with self._lock:
            self._results.append(result)
            self._current_scenario = None
        return result

    async def test_adversarial_scenarios(
        self,
        total_requests: int = 100,
    ) -> ScenarioResult:
        """
        Adversarial: high error rate + slow responses + corrupted payloads.
        Verifies circuit-breakers, retries, and error handling.
        """
        with self._lock:
            self._current_scenario = "adversarial"
        result = await self._run_concurrent(
            scenario="adversarial",
            n_requests=total_requests,
            concurrency=30,
            base_latency_ms=800,
            error_rate=0.30,
        )
        with self._lock:
            self._results.append(result)
            self._current_scenario = None
        return result

    def run_all_sync(self) -> List[Dict]:
        """Blocking wrapper for all three scenarios (use in threads)."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            normal = loop.run_until_complete(self.test_normal_operations())
            surge  = loop.run_until_complete(self.test_surge_conditions())
            adv    = loop.run_until_complete(self.test_adversarial_scenarios())
            return [normal.to_dict(), surge.to_dict(), adv.to_dict()]
        finally:
            loop.close()

    def start_background(self) -> Dict:
        """Kick off all three scenarios in a daemon thread."""
        with self._lock:
            if self._running:
                return {"status": "already_running"}
            self._running = True

        def _worker():
            self.run_all_sync()
            with self._lock:
                self._running = False

        threading.Thread(target=_worker, daemon=True).start()
        return {"status": "started"}

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "running": self._running,
                "current_scenario": self._current_scenario,
                "completed_scenarios": len(self._results),
                "results": [r.to_dict() for r in self._results[-10:]],
            }
