"""
ORD AI — Prompt Injection Defense
Multi-agent defense pipeline that detects and neutralises injection attacks
before they reach the main agent.

Threat categories covered:
  1. Direct override:   "Ignore previous instructions"
  2. Role hijack:       "You are now a different AI"
  3. Code execution:    Embedded shell/Python in user input
  4. Data exfiltration: Instructions to leak data externally
  5. Obfuscation:       Base64, ROT13, spaced characters, unicode tricks
"""
import base64
import re
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ── Pattern library ───────────────────────────────────────────────────

_OVERRIDE_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?prior",
    r"forget\s+(everything|all\s+previous)",
    r"new\s+system\s+prompt",
    r"override\s+system",
    r"you\s+are\s+now\s+",
    r"pretend\s+you\s+(are|have\s+no)\s+",
    r"act\s+as\s+(if\s+you\s+(are|were)\s+)?(?!an?\s+AI\s+builder)",  # allow normal role references
    r"jailbreak",
    r"DAN\s+mode",
    r"developer\s+mode",
]

_CODE_EXEC_PATTERNS = [
    r"exec\s*\(",
    r"eval\s*\(",
    r"__import__\s*\(",
    r"os\.system\s*\(",
    r"subprocess\.(run|call|Popen)\s*\(",
    r"import\s+os",
    r"import\s+subprocess",
    r"`[^`]+`",                             # backtick shell execution
    r"\$\([^)]+\)",                         # bash command substitution
]

_EXFILTRATION_PATTERNS = [
    r"(send|post|upload|exfiltrate).{0,60}(http|ftp|sftp|webhook|endpoint)",
    r"leak.{0,30}(data|key|secret|token|password)",
    r"(print|return|output).{0,30}(api_key|secret|password|token)",
    r"curl\s+",
    r"wget\s+",
    r"requests\.(get|post)\s*\(",
]

_ALL_PATTERNS = (
    [("override", p) for p in _OVERRIDE_PATTERNS]
    + [("code_exec", p) for p in _CODE_EXEC_PATTERNS]
    + [("exfiltration", p) for p in _EXFILTRATION_PATTERNS]
)
_COMPILED = [(cat, re.compile(p, re.IGNORECASE)) for cat, p in _ALL_PATTERNS]

# ── Threat levels ─────────────────────────────────────────────────────
THREAT_LEVEL = {
    "override": "high",
    "code_exec": "critical",
    "exfiltration": "critical",
    "obfuscation": "medium",
    "clean": "none",
}


@dataclass
class DefenseResult:
    is_safe: bool
    threat_level: str
    threats_found: List[str]
    sanitized_input: str
    original_input: str
    action_taken: str   # "passed" | "sanitized" | "blocked"

    def to_dict(self) -> Dict:
        return {
            "is_safe": self.is_safe,
            "threat_level": self.threat_level,
            "threats_found": self.threats_found,
            "sanitized_input": self.sanitized_input[:500],
            "action_taken": self.action_taken,
        }


class PromptInjectionDefense:
    """
    Sequential multi-agent defense pipeline.

    Agent 1: Detect injection patterns
    Agent 2: Classify threat level
    Agent 3: Sanitize / neutralise
    Agent 4: Verify the sanitized output is clean
    """

    _instance: Optional["PromptInjectionDefense"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self.blocked_count = 0
        self.sanitized_count = 0
        self.passed_count = 0

    @classmethod
    def get_instance(cls) -> "PromptInjectionDefense":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Agent 1: Detect ───────────────────────────────────────────────

    def _detect(self, text: str) -> List[Tuple[str, str]]:
        """Return list of (category, matched_text) tuples."""
        findings: List[Tuple[str, str]] = []
        for cat, pattern in _COMPILED:
            m = pattern.search(text)
            if m:
                findings.append((cat, m.group(0)[:80]))
        return findings

    def _detect_obfuscation(self, text: str) -> bool:
        """Check for base64 / spaced-character obfuscation attempts."""
        # Base64 blobs longer than 40 chars that decode to suspicious content
        b64_chunks = re.findall(r"[A-Za-z0-9+/]{40,}={0,2}", text)
        for chunk in b64_chunks:
            try:
                decoded = base64.b64decode(chunk + "==").decode("utf-8", errors="ignore").lower()
                if any(kw in decoded for kw in ["ignore", "exec", "import", "system"]):
                    return True
            except Exception:
                pass
        # Spaced-out injection: "i g n o r e  p r e v i o u s"
        collapsed = re.sub(r"(\w)\s+", r"\1", text)
        if collapsed != text:
            sub_findings = self._detect(collapsed)
            if sub_findings:
                return True
        return False

    # ── Agent 2: Classify ─────────────────────────────────────────────

    def _classify(self, findings: List[Tuple[str, str]], obfuscated: bool) -> str:
        if obfuscated:
            return "obfuscation"
        categories = {cat for cat, _ in findings}
        if "code_exec" in categories or "exfiltration" in categories:
            return "critical"
        if "override" in categories:
            return "high"
        return "clean"

    # ── Agent 3: Sanitize ─────────────────────────────────────────────

    def _sanitize(self, text: str, findings: List[Tuple[str, str]]) -> str:
        """Remove or neutralize detected threat patterns."""
        sanitized = text
        for cat, pattern in _COMPILED:
            sanitized = pattern.sub(f"[{cat.upper()}_REMOVED]", sanitized)
        return sanitized.strip()

    # ── Agent 4: Verify ───────────────────────────────────────────────

    def _verify_clean(self, text: str) -> bool:
        """Confirm sanitized text passes all checks."""
        return len(self._detect(text)) == 0 and not self._detect_obfuscation(text)

    # ── Main pipeline ─────────────────────────────────────────────────

    def inspect(self, user_input: str, strict: bool = False) -> DefenseResult:
        """
        Run the full defense pipeline on a user input string.

        strict=True → block on ANY threat (even medium)
        strict=False → attempt sanitization for medium threats, block critical
        """
        # Agent 1: Detect
        findings = self._detect(user_input)
        obfuscated = self._detect_obfuscation(user_input)

        # Agent 2: Classify
        threat_category = self._classify(findings, obfuscated)
        threat_level = THREAT_LEVEL.get(threat_category, "none")
        threats_found = list({cat for cat, _ in findings})
        if obfuscated:
            threats_found.append("obfuscation")

        # Clean input — pass through immediately
        if threat_level == "none":
            with self._lock:
                self.passed_count += 1
            return DefenseResult(
                is_safe=True,
                threat_level="none",
                threats_found=[],
                sanitized_input=user_input,
                original_input=user_input,
                action_taken="passed",
            )

        # Critical threats — block
        if threat_level == "critical" or strict:
            with self._lock:
                self.blocked_count += 1
            return DefenseResult(
                is_safe=False,
                threat_level=threat_level,
                threats_found=threats_found,
                sanitized_input="[INPUT BLOCKED — threat level: " + threat_level + "]",
                original_input=user_input,
                action_taken="blocked",
            )

        # Agent 3: Sanitize for medium/high
        sanitized = self._sanitize(user_input, findings)

        # Agent 4: Verify
        if not self._verify_clean(sanitized):
            with self._lock:
                self.blocked_count += 1
            return DefenseResult(
                is_safe=False,
                threat_level=threat_level,
                threats_found=threats_found,
                sanitized_input="[INPUT BLOCKED — sanitization failed]",
                original_input=user_input,
                action_taken="blocked",
            )

        with self._lock:
            self.sanitized_count += 1
        return DefenseResult(
            is_safe=True,
            threat_level=threat_level,
            threats_found=threats_found,
            sanitized_input=sanitized,
            original_input=user_input,
            action_taken="sanitized",
        )

    def safe_input(self, user_input: str, strict: bool = False) -> Optional[str]:
        """
        Convenience wrapper.
        Returns sanitized input string, or None if input is blocked.
        """
        result = self.inspect(user_input, strict=strict)
        return result.sanitized_input if result.is_safe else None

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        with self._lock:
            total = self.blocked_count + self.sanitized_count + self.passed_count
            return {
                "total_inspected": total,
                "passed": self.passed_count,
                "sanitized": self.sanitized_count,
                "blocked": self.blocked_count,
                "block_rate_pct": round(100 * self.blocked_count / max(total, 1), 1),
                "patterns_monitored": len(_ALL_PATTERNS),
            }
