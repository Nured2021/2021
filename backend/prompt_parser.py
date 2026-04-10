"""Shared prompt parsing utilities – extract topic, intent, and domain from user prompts."""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Topic extraction
# ---------------------------------------------------------------------------

_COMMAND_PREFIXES = re.compile(
    r"^(create|write|generate|build|make|produce|draft|prepare|develop|design|analyse|analyze"
    r"|review|explain|summarize|summarise|describe|outline|plan|provide|give me|i need)\s+"
    r"(a |an |the |my |our )?",
    re.IGNORECASE,
)

_FOR_PHRASES = re.compile(
    r"\s+(for|about|on|regarding|related to|concerning)\s+",
    re.IGNORECASE,
)


def extract_topic(prompt: str) -> str:
    """Return the core topic phrase from a user prompt (Title-Cased, max 100 chars)."""
    cleaned = _COMMAND_PREFIXES.sub("", prompt.strip())
    # Keep only the first meaningful chunk (before 'for', 'about', 'on' or punctuation)
    first_part = re.split(r"[,.\n]", cleaned)[0].strip()
    return first_part[:100].strip().title()


def extract_subject(prompt: str) -> str:
    """Return the subject matter phrase (lower case, max 80 chars)."""
    topic = extract_topic(prompt)
    return topic[:80].strip()


# ---------------------------------------------------------------------------
# Domain detection
# ---------------------------------------------------------------------------

_DOMAINS: dict[str, list[str]] = {
    "legal":    ["law", "legal", "contract", "court", "litigation", "compliance",
                 "statute", "regulation", "attorney", "brief", "lawsuit"],
    "business": ["business", "company", "startup", "market", "revenue", "profit",
                 "sales", "strategy", "brand", "product", "client", "customer",
                 "entrepreneur", "venture", "marketing"],
    "science":  ["science", "biology", "chemistry", "physics", "lab", "experiment",
                 "hypothesis", "molecule", "cell", "research", "data", "formula"],
    "tech":     ["software", "app", "code", "algorithm", "database", "api",
                 "machine learning", "ai", "cloud", "cyber", "programming",
                 "developer", "agile", "sprint"],
    "health":   ["health", "medical", "clinic", "patient", "treatment", "hospital",
                 "nurse", "doctor", "diagnosis", "therapy", "wellness"],
    "education":["education", "course", "student", "teacher", "school", "university",
                 "lecture", "syllabus", "curriculum", "exam", "study"],
    "finance":  ["finance", "budget", "investment", "accounting", "audit", "tax",
                 "portfolio", "asset", "liability", "balance sheet", "cash flow"],
    "hr":       ["human resources", "hiring", "recruitment", "employee", "performance",
                 "onboarding", "payroll", "leave policy", "workforce"],
    "marketing":["marketing", "campaign", "social media", "seo", "content", "brand",
                 "advertising", "audience", "analytics", "funnel", "conversion"],
}


def detect_domain(prompt: str) -> str:
    """Return the most likely domain string for *prompt*, default 'general'."""
    lower = prompt.lower()
    scores: dict[str, int] = {}
    for domain, keywords in _DOMAINS.items():
        scores[domain] = sum(1 for kw in keywords if kw in lower)
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "general"


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "at", "by", "from", "is", "are", "was", "were", "be", "been",
    "has", "have", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "shall", "i", "we", "you", "he", "she", "they", "it",
    "this", "that", "these", "those", "my", "our", "your", "their",
    "me", "us", "him", "her", "them", "as", "if", "so", "up", "out",
    "create", "write", "generate", "build", "make", "produce", "draft",
    "prepare", "develop", "design", "give", "please",
}


def extract_keywords(prompt: str, max_kw: int = 8) -> list[str]:
    """Return up to *max_kw* meaningful keywords from *prompt*."""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", prompt.lower())
    seen: set[str] = set()
    result: list[str] = []
    for w in words:
        if w not in _STOP_WORDS and w not in seen:
            seen.add(w)
            result.append(w)
        if len(result) >= max_kw:
            break
    return result


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

_INTENT_PATTERNS: dict[str, list[str]] = {
    "create":    ["create", "build", "make", "develop", "design", "produce"],
    "write":     ["write", "draft", "compose", "prepare"],
    "analyze":   ["analyze", "analyse", "evaluate", "assess", "review", "examine"],
    "explain":   ["explain", "describe", "define", "clarify", "outline"],
    "summarize": ["summarize", "summarise", "summarize", "condense", "overview"],
    "plan":      ["plan", "schedule", "organize", "organise", "structure"],
    "translate": ["translate", "convert", "localise", "localize"],
}


def detect_intent(prompt: str) -> str:
    """Return the primary intent of the prompt, default 'create'."""
    lower = prompt.lower()
    for intent, patterns in _INTENT_PATTERNS.items():
        if any(p in lower for p in patterns):
            return intent
    return "create"
