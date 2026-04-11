"""
ORD AI — Composable Agent Primitives
Build agents from small, reusable natural-language building blocks instead
of large monolithic prompts.  Fixing one capability no longer risks breaking
another.
"""
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── Primitive types ───────────────────────────────────────────────────

@dataclass
class RoleComponent:
    """A single, focused capability (50–150 chars recommended)."""
    name: str
    description: str
    tags: List[str] = field(default_factory=list)


@dataclass
class DesiredOutcome:
    """What a successful response must contain."""
    name: str
    description: str
    tags: List[str] = field(default_factory=list)


@dataclass
class TradeoffRule:
    """How to resolve conflicts between competing values."""
    name: str
    rule: str
    tags: List[str] = field(default_factory=list)


# ── Primitive registry ────────────────────────────────────────────────

# Pre-built primitives that ship with ORD AI
_BUILTIN_ROLES: List[RoleComponent] = [
    RoleComponent("code_writer",     "Write clean, production-ready code that passes linting and tests.", ["code", "implement"]),
    RoleComponent("code_reviewer",   "Identify bugs, security issues, and style violations in provided code.", ["review", "quality"]),
    RoleComponent("system_designer", "Design scalable system architectures with clear component boundaries.", ["architecture", "design"]),
    RoleComponent("test_generator",  "Generate comprehensive test suites covering happy paths, edge cases, and failure modes.", ["test", "validation"]),
    RoleComponent("bug_fixer",       "Diagnose root causes and produce minimal, targeted fixes without side-effects.", ["fix", "debug"]),
    RoleComponent("doc_writer",      "Write concise, accurate technical documentation and inline comments.", ["docs", "readme"]),
    RoleComponent("security_auditor","Evaluate code and configurations for OWASP vulnerabilities and supply-chain risks.", ["security", "audit"]),
    RoleComponent("deploy_engineer", "Produce Docker, Kubernetes, and CI/CD configurations for production deployment.", ["deploy", "devops"]),
]

_BUILTIN_OUTCOMES: List[DesiredOutcome] = [
    DesiredOutcome("structured_output",  "Return a JSON object with clearly labeled fields.", ["format"]),
    DesiredOutcome("inline_explanation", "Include a brief reasoning note alongside each output item.", ["explain"]),
    DesiredOutcome("actionable_items",   "End with a numbered list of concrete next steps.", ["action"]),
    DesiredOutcome("code_with_tests",    "Always pair code with corresponding unit tests.", ["code", "test"]),
    DesiredOutcome("diff_only",          "Return only the changed lines in unified-diff format.", ["code", "review"]),
    DesiredOutcome("risk_score",         "Assign a 0-10 risk score and justify it.", ["security", "review"]),
]

_BUILTIN_TRADEOFFS: List[TradeoffRule] = [
    TradeoffRule("thoroughness_vs_speed",  "When thoroughness and speed conflict: prefer thoroughness.", ["general"]),
    TradeoffRule("safety_vs_feature",      "When safety and new features conflict: always choose safety.", ["security"]),
    TradeoffRule("simplicity_vs_power",    "When simplicity and power conflict: prefer simplicity unless explicitly asked for power.", ["code"]),
    TradeoffRule("latency_vs_accuracy",    "When latency and accuracy conflict: default to accuracy; mention the trade-off.", ["performance"]),
]


class ComposableAgent:
    """
    An agent whose behaviour is assembled at runtime from primitive building
    blocks.  Adding or swapping one primitive does not affect the others.
    """

    def __init__(self, agent_id: str = "agent"):
        self.agent_id = agent_id
        self.roles: List[RoleComponent] = []
        self.outcomes: List[DesiredOutcome] = []
        self.tradeoffs: List[TradeoffRule] = []

    # ── Builder methods ───────────────────────────────────────────────

    def add_role(self, primitive: RoleComponent) -> "ComposableAgent":
        self.roles.append(primitive)
        return self

    def add_outcome(self, primitive: DesiredOutcome) -> "ComposableAgent":
        self.outcomes.append(primitive)
        return self

    def add_tradeoff(self, primitive: TradeoffRule) -> "ComposableAgent":
        self.tradeoffs.append(primitive)
        return self

    def remove_primitive(self, name: str) -> "ComposableAgent":
        """Remove a primitive by name from any category."""
        self.roles      = [r for r in self.roles      if r.name != name]
        self.outcomes   = [o for o in self.outcomes   if o.name != name]
        self.tradeoffs  = [t for t in self.tradeoffs  if t.name != name]
        return self

    # ── Compose ───────────────────────────────────────────────────────

    def compose_system_prompt(self) -> str:
        """
        Assemble a system prompt from the selected primitives.
        Produces a clean, readable, modular prompt.
        """
        parts: List[str] = ["You are ORD AI, an expert AI builder.\n"]

        if self.roles:
            parts.append("## Your Capabilities")
            for r in self.roles:
                parts.append(f"- {r.description}")
            parts.append("")

        if self.outcomes:
            parts.append("## Output Requirements")
            for o in self.outcomes:
                parts.append(f"- {o.description}")
            parts.append("")

        if self.tradeoffs:
            parts.append("## Decision Rules")
            for t in self.tradeoffs:
                parts.append(f"- {t.rule}")
            parts.append("")

        return "\n".join(parts)

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "roles":     [{"name": r.name, "description": r.description, "tags": r.tags} for r in self.roles],
            "outcomes":  [{"name": o.name, "description": o.description, "tags": o.tags} for o in self.outcomes],
            "tradeoffs": [{"name": t.name, "rule": t.rule, "tags": t.tags} for t in self.tradeoffs],
            "system_prompt_preview": self.compose_system_prompt()[:400],
        }


# ── Agent factory ─────────────────────────────────────────────────────

class AgentFactory:
    """
    Central registry that builds composable agents from named primitives.
    Supports the standard ORD AI agent pipeline + custom agent creation.
    """

    _instance: Optional["AgentFactory"] = None
    _cls_lock = threading.Lock()

    def __init__(self):
        self._roles     = {r.name: r for r in _BUILTIN_ROLES}
        self._outcomes  = {o.name: o for o in _BUILTIN_OUTCOMES}
        self._tradeoffs = {t.name: t for t in _BUILTIN_TRADEOFFS}
        self._agents: Dict[str, ComposableAgent] = {}
        self._lock = threading.Lock()
        self._build_standard_agents()

    @classmethod
    def get_instance(cls) -> "AgentFactory":
        with cls._cls_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Standard pipeline agents ──────────────────────────────────────

    def _build_standard_agents(self):
        planner = (
            ComposableAgent("planner")
            .add_role(self._roles["system_designer"])
            .add_outcome(self._outcomes["actionable_items"])
            .add_tradeoff(self._tradeoffs["thoroughness_vs_speed"])
        )
        implementer = (
            ComposableAgent("implementer")
            .add_role(self._roles["code_writer"])
            .add_outcome(self._outcomes["code_with_tests"])
            .add_tradeoff(self._tradeoffs["simplicity_vs_power"])
        )
        validator = (
            ComposableAgent("validator")
            .add_role(self._roles["test_generator"])
            .add_outcome(self._outcomes["structured_output"])
            .add_tradeoff(self._tradeoffs["thoroughness_vs_speed"])
        )
        reviewer = (
            ComposableAgent("reviewer")
            .add_role(self._roles["code_reviewer"])
            .add_role(self._roles["security_auditor"])
            .add_outcome(self._outcomes["risk_score"])
            .add_outcome(self._outcomes["diff_only"])
            .add_tradeoff(self._tradeoffs["safety_vs_feature"])
        )
        merger = (
            ComposableAgent("merger")
            .add_role(self._roles["deploy_engineer"])
            .add_outcome(self._outcomes["structured_output"])
            .add_tradeoff(self._tradeoffs["safety_vs_feature"])
        )
        for agent in (planner, implementer, validator, reviewer, merger):
            self._agents[agent.agent_id] = agent

    # ── Public API ────────────────────────────────────────────────────

    def get_agent(self, agent_id: str) -> Optional[ComposableAgent]:
        with self._lock:
            return self._agents.get(agent_id)

    def create_agent(
        self,
        agent_id: str,
        role_names: Optional[List[str]] = None,
        outcome_names: Optional[List[str]] = None,
        tradeoff_names: Optional[List[str]] = None,
    ) -> ComposableAgent:
        """Compose a new agent from named primitives and register it."""
        agent = ComposableAgent(agent_id)
        for name in (role_names or []):
            if name in self._roles:
                agent.add_role(self._roles[name])
        for name in (outcome_names or []):
            if name in self._outcomes:
                agent.add_outcome(self._outcomes[name])
        for name in (tradeoff_names or []):
            if name in self._tradeoffs:
                agent.add_tradeoff(self._tradeoffs[name])
        with self._lock:
            self._agents[agent_id] = agent
        return agent

    def register_role(self, primitive: RoleComponent) -> None:
        with self._lock:
            self._roles[primitive.name] = primitive

    def register_outcome(self, primitive: DesiredOutcome) -> None:
        with self._lock:
            self._outcomes[primitive.name] = primitive

    def register_tradeoff(self, primitive: TradeoffRule) -> None:
        with self._lock:
            self._tradeoffs[primitive.name] = primitive

    def list_primitives(self) -> Dict:
        with self._lock:
            return {
                "roles":     [{"name": r.name, "description": r.description, "tags": r.tags} for r in self._roles.values()],
                "outcomes":  [{"name": o.name, "description": o.description, "tags": o.tags} for o in self._outcomes.values()],
                "tradeoffs": [{"name": t.name, "rule": t.rule, "tags": t.tags} for t in self._tradeoffs.values()],
            }

    def list_agents(self) -> List[Dict]:
        with self._lock:
            return [a.to_dict() for a in self._agents.values()]

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "registered_roles":     len(self._roles),
                "registered_outcomes":  len(self._outcomes),
                "registered_tradeoffs": len(self._tradeoffs),
                "composed_agents":      len(self._agents),
            }
