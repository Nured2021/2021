"""
ORD AI — Loop Protection
Prevents infinite reasoning loops via frustration detection and forced mode switching.
"""
import time
import threading
from typing import List, Dict, Optional


class LoopProtection:
    """
    Detects when an agent is spinning in place and forces a strategy change.

    Tracks task history, identifies repeated approach patterns, and injects
    an escape-hatch prompt to break out of the loop.
    """

    _instance: Optional["LoopProtection"] = None
    _cls_lock = threading.Lock()

    def __init__(
        self,
        max_iterations: int = 10,
        max_same_approach: int = 3,
        min_progress_threshold: float = 0.05,
    ):
        self.max_iterations = max_iterations
        self.max_same_approach = max_same_approach
        self.min_progress_threshold = min_progress_threshold
        # Per-task history: task_id -> list of attempt dicts
        self._history: Dict[str, List[Dict]] = {}
        self._lock = threading.Lock()
        self.stuck_count = 0
        self.escape_count = 0

    @classmethod
    def get_instance(cls) -> "LoopProtection":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Record ────────────────────────────────────────────────────────

    def record_attempt(
        self,
        task_id: str,
        approach_type: str,
        score: float,
        result_snippet: str = "",
    ) -> None:
        """Record one attempt for a task. Call after every LLM round."""
        entry = {
            "approach_type": approach_type,
            "score": score,
            "result_snippet": result_snippet[:200],
            "ts": time.time(),
        }
        with self._lock:
            self._history.setdefault(task_id, []).append(entry)

    # ── Detection ─────────────────────────────────────────────────────

    def detect_stuck(self, task_id: str) -> bool:
        """Return True when the agent appears stuck on this task."""
        with self._lock:
            history = list(self._history.get(task_id, []))

        if len(history) < 2:
            return False

        # Exceeded max iteration cap
        if len(history) >= self.max_iterations:
            self.stuck_count += 1
            return True

        recent = history[-min(5, len(history)):]

        # Same approach type repeated too many times
        approaches = [e["approach_type"] for e in recent]
        if len(approaches) >= self.max_same_approach:
            unique = set(approaches[-self.max_same_approach:])
            if len(unique) == 1:
                self.stuck_count += 1
                return True

        # No progress over the last two attempts
        if len(recent) >= 2:
            delta = recent[-1]["score"] - recent[-2]["score"]
            if delta <= self.min_progress_threshold:
                self.stuck_count += 1
                return True

        return False

    # ── Escape hatch ──────────────────────────────────────────────────

    def escape_prompt(self, task_id: str) -> str:
        """Return the escape-hatch prompt to inject when stuck."""
        with self._lock:
            history = list(self._history.get(task_id, []))

        previous = ", ".join(
            {e["approach_type"] for e in history[-5:]} - {""}
        ) or "the same approach repeatedly"

        self.escape_count += 1
        return (
            "⚠ LOOP DETECTED — You have tried variations on the same approach "
            f"({previous}) multiple times without making meaningful progress.\n\n"
            "Before continuing, generate THREE completely different approaches "
            "that share NOTHING in common with what you have already tried.\n"
            "Rank them by likelihood of success, then proceed with the top-ranked approach."
        )

    def force_mode_switch(self, task_id: str) -> str:
        """Alias kept for backward compatibility."""
        return self.escape_prompt(task_id)

    # ── Reset ─────────────────────────────────────────────────────────

    def reset_task(self, task_id: str) -> None:
        """Clear history for a task once it completes or is abandoned."""
        with self._lock:
            self._history.pop(task_id, None)

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        with self._lock:
            active_tasks = len(self._history)
            total_attempts = sum(len(v) for v in self._history.values())
        return {
            "active_tasks": active_tasks,
            "total_attempts": total_attempts,
            "stuck_detections": self.stuck_count,
            "escape_injections": self.escape_count,
            "max_iterations": self.max_iterations,
            "max_same_approach": self.max_same_approach,
        }
