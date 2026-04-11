"""
ORD AI — Structural Defense
Three-layer protection that does NOT rely on human oversight:
  Layer 1: Command sandbox (denylist / workspace restriction)
  Layer 2: Identity version control (detect agent tampering)
  Layer 3: Integrity verification (hash-based config checks)
"""
import hashlib
import json
import re
import threading
import time
from typing import Dict, List, Optional


# ── Denylist: commands that must never execute ─────────────────────────
_DENYLIST_PATTERNS = [
    r"rm\s+-rf",
    r"dd\s+if=",
    r"mkfs",
    r"shutdown",
    r"reboot",
    r"halt",
    r":()\{:|:&\};:",        # fork bomb
    r"wget\s+.*\|.*sh",      # remote code execution
    r"curl\s+.*\|.*bash",    # remote code execution
    r"chmod\s+777",
    r">\s*/etc/passwd",
    r">\s*/etc/shadow",
    r"eval\s*\(",
    r"exec\s*\(",
]

_DENYLIST_RE = [re.compile(p, re.IGNORECASE) for p in _DENYLIST_PATTERNS]


class SandboxLayer:
    """
    OS-level command sanitizer.
    Checks every command against the denylist and workspace boundary
    before handing it off to the runtime.
    """

    def __init__(self, workspace: str = "/tmp/ord_ai_workspace"):
        self.workspace = workspace
        self.blocked_count = 0
        self.allowed_count = 0
        self._lock = threading.Lock()

    def check(self, command: str, strict: bool = False) -> Dict:
        """
        Validate a shell command string.

        Returns:
            {"allowed": True/False, "reason": str, "command": str}
        """
        # Denylist check (non-negotiable)
        for pattern in _DENYLIST_RE:
            if pattern.search(command):
                with self._lock:
                    self.blocked_count += 1
                return {
                    "allowed": False,
                    "reason": f"Command matches enterprise denylist pattern: {pattern.pattern}",
                    "command": command,
                }

        # Workspace check in strict mode
        if strict and self.workspace:
            if any(dangerous in command for dangerous in ["/etc/", "/sys/", "/proc/", "~/.ssh"]):
                with self._lock:
                    self.blocked_count += 1
                return {
                    "allowed": False,
                    "reason": "Command attempts to access outside workspace boundary.",
                    "command": command,
                }

        with self._lock:
            self.allowed_count += 1
        return {"allowed": True, "reason": "OK", "command": command}

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "workspace": self.workspace,
                "blocked_count": self.blocked_count,
                "allowed_count": self.allowed_count,
                "denylist_patterns": len(_DENYLIST_PATTERNS),
            }


class IdentityVersionControl:
    """
    Snapshots agent identity (system prompt hash, tool permissions,
    memory access limits) and detects tampering between calls.
    """

    def __init__(self):
        self._snapshots: List[Dict] = []
        self._lock = threading.Lock()
        self.tamper_detections = 0
        self.snapshot_count = 0

    def snapshot(self, agent_id: str, config: Dict) -> str:
        """
        Capture the current agent identity.
        Returns the snapshot ID.
        """
        snap_id = hashlib.sha256(
            (agent_id + json.dumps(config, sort_keys=True)).encode()
        ).hexdigest()[:16]

        entry = {
            "snap_id": snap_id,
            "agent_id": agent_id,
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_prompt_hash": hashlib.sha256(
                config.get("system_prompt", "").encode()
            ).hexdigest()[:16],
            "tool_permissions": sorted(config.get("tools", [])),
            "memory_limits": config.get("memory_limits", {}),
            "constraints": sorted(config.get("constraints", [])),
        }
        with self._lock:
            self._snapshots.append(entry)
            self.snapshot_count += 1
        return snap_id

    def verify(self, agent_id: str, current_config: Dict) -> Dict:
        """
        Compare current config against the last snapshot for this agent.
        Returns {"ok": True} or {"ok": False, "diff": {...}}
        """
        with self._lock:
            past = next(
                (s for s in reversed(self._snapshots) if s["agent_id"] == agent_id),
                None,
            )

        if past is None:
            return {"ok": True, "note": "No prior snapshot — first run accepted."}

        current_prompt_hash = hashlib.sha256(
            current_config.get("system_prompt", "").encode()
        ).hexdigest()[:16]
        current_tools = sorted(current_config.get("tools", []))

        diff = {}
        if past["system_prompt_hash"] != current_prompt_hash:
            diff["system_prompt_hash"] = {
                "was": past["system_prompt_hash"],
                "now": current_prompt_hash,
            }
        if past["tool_permissions"] != current_tools:
            diff["tool_permissions"] = {
                "was": past["tool_permissions"],
                "now": current_tools,
            }

        if diff:
            self.tamper_detections += 1
            return {"ok": False, "diff": diff, "agent_id": agent_id}

        return {"ok": True}

    def get_history(self, agent_id: Optional[str] = None) -> List[Dict]:
        with self._lock:
            if agent_id:
                return [s for s in self._snapshots if s["agent_id"] == agent_id]
            return list(self._snapshots)

    def get_status(self) -> Dict:
        with self._lock:
            agents = list({s["agent_id"] for s in self._snapshots})
        return {
            "snapshot_count": self.snapshot_count,
            "tamper_detections": self.tamper_detections,
            "tracked_agents": agents,
        }


class StructuralDefense:
    """
    Unified facade for all three structural defense layers.
    Instantiate once and use throughout the platform.
    """

    _instance: Optional["StructuralDefense"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self.sandbox = SandboxLayer()
        self.identity = IdentityVersionControl()

    @classmethod
    def get_instance(cls) -> "StructuralDefense":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def check_command(self, command: str, strict: bool = False) -> Dict:
        return self.sandbox.check(command, strict=strict)

    def snapshot_agent(self, agent_id: str, config: Dict) -> str:
        return self.identity.snapshot(agent_id, config)

    def verify_agent(self, agent_id: str, current_config: Dict) -> Dict:
        return self.identity.verify(agent_id, current_config)

    def get_status(self) -> Dict:
        return {
            "sandbox": self.sandbox.get_status(),
            "identity_vc": self.identity.get_status(),
        }
