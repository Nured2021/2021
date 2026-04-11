"""
ORD AI — Human Judgment Stabilizer
Detects and flags inconsistent or contradictory human feedback before it
corrupts the HITL loop.
"""
import time
import threading
from typing import Dict, List, Optional


class HumanJudgmentStabilizer:
    """
    Validates incoming human feedback against past decisions in similar contexts.

    When a rating or decision deviates significantly from the historical baseline
    for the same type of task, the system pauses and surfaces the inconsistency
    instead of blindly accepting the feedback.
    """

    _instance: Optional["HumanJudgmentStabilizer"] = None
    _cls_lock = threading.Lock()

    def __init__(self, inconsistency_threshold: float = 0.3, history_window: int = 20):
        self.inconsistency_threshold = inconsistency_threshold
        self.history_window = history_window
        self._feedback_log: List[Dict] = []
        self._lock = threading.Lock()
        self.inconsistency_count = 0
        self.validated_count = 0

    @classmethod
    def get_instance(cls) -> "HumanJudgmentStabilizer":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Validate ─────────────────────────────────────────────────────

    def validate_feedback(
        self,
        rating: float,
        task_type: str,
        context_tags: Optional[List[str]] = None,
        reviewer_id: str = "human",
    ) -> Dict:
        """
        Validate a rating (0-10) against historical baseline for this task_type.

        Returns:
            dict with keys: status ("consistent" | "inconsistent"),
                            message, suggested_action, baseline (if inconsistent)
        """
        context_tags = context_tags or []
        similar = self._find_similar(task_type, context_tags)

        result: Dict = {
            "rating": rating,
            "task_type": task_type,
            "reviewer_id": reviewer_id,
            "status": "consistent",
            "message": "Feedback accepted.",
            "suggested_action": None,
            "baseline": None,
        }

        if similar:
            baseline_ratings = [e["rating"] for e in similar]
            mean_baseline = sum(baseline_ratings) / len(baseline_ratings)
            deviation = abs(rating - mean_baseline)
            normalized_dev = deviation / max(mean_baseline, 1.0)

            if normalized_dev > self.inconsistency_threshold:
                result["status"] = "inconsistent"
                result["baseline"] = round(mean_baseline, 2)
                result["message"] = (
                    f"Your rating ({rating}) differs from the historical baseline "
                    f"({result['baseline']}) for similar '{task_type}' tasks "
                    f"(deviation {deviation:.1f}, threshold {self.inconsistency_threshold})."
                )
                result["suggested_action"] = (
                    "Please reconsider, or confirm the override to proceed."
                )
                self.inconsistency_count += 1
                return result

        # Record accepted feedback
        self._record(rating, task_type, context_tags, reviewer_id)
        self.validated_count += 1
        return result

    def confirm_override(
        self,
        rating: float,
        task_type: str,
        context_tags: Optional[List[str]] = None,
        reviewer_id: str = "human",
    ) -> Dict:
        """
        Human explicitly confirms an inconsistent rating — record it anyway.
        """
        context_tags = context_tags or []
        self._record(rating, task_type, context_tags, reviewer_id)
        self.validated_count += 1
        return {
            "status": "override_accepted",
            "rating": rating,
            "task_type": task_type,
            "message": "Override accepted and recorded.",
        }

    # ── Internal ─────────────────────────────────────────────────────

    def _record(
        self,
        rating: float,
        task_type: str,
        context_tags: List[str],
        reviewer_id: str,
    ) -> None:
        entry = {
            "rating": rating,
            "task_type": task_type,
            "context_tags": context_tags,
            "reviewer_id": reviewer_id,
            "ts": time.time(),
        }
        with self._lock:
            self._feedback_log.append(entry)
            if len(self._feedback_log) > 500:
                self._feedback_log = self._feedback_log[-400:]

    def _find_similar(self, task_type: str, context_tags: List[str]) -> List[Dict]:
        """Find recent feedback entries with the same task_type."""
        with self._lock:
            recent = self._feedback_log[-self.history_window:]
        return [
            e for e in recent
            if e["task_type"] == task_type
        ]

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        with self._lock:
            total = len(self._feedback_log)
            recent = self._feedback_log[-10:]
        return {
            "total_feedback_recorded": total,
            "validated_count": self.validated_count,
            "inconsistency_count": self.inconsistency_count,
            "inconsistency_threshold": self.inconsistency_threshold,
            "history_window": self.history_window,
            "recent_feedback": [
                {"rating": e["rating"], "task_type": e["task_type"]} for e in recent
            ],
        }
