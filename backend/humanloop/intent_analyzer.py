"""Deep Intent Analyzer – understands user requests like AI Doc Maker."""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class WritingStyle(Enum):
    PROFESSIONAL = "professional"
    CASUAL       = "casual"
    ACADEMIC     = "academic"
    LEGAL        = "legal"
    CREATIVE     = "creative"
    PERSUASIVE   = "persuasive"


class DocumentFormat(Enum):
    STANDARD          = "standard"
    PITCH_DECK        = "pitch_deck"
    EXECUTIVE_SUMMARY = "executive_summary"
    FULL_DOCUMENT     = "full_document"
    LETTER            = "letter"
    EMAIL             = "email"
    BLOG              = "blog"
    SOCIAL_MEDIA      = "social_media"


class Tone(Enum):
    FORMAL      = "formal"
    FRIENDLY    = "friendly"
    PERSUASIVE  = "persuasive"
    INFORMATIVE = "informative"
    HUMOROUS    = "humorous"


@dataclass
class IntentAnalysis:
    document_type:    str
    industry:         Optional[str]
    target_audience:  Optional[str]
    estimated_length: str
    complexity:       str
    key_topics:       List[str]
    suggested_style:  WritingStyle
    suggested_format: DocumentFormat
    suggested_tone:   Tone
    confidence:       float = 0.85


class IntentAnalyzer:
    """Deeply analyzes user prompts to understand exactly what they want."""

    DOCUMENT_TYPES: Dict[str, List[str]] = {
        "business_plan":     ["business plan", "business proposal", "company plan", "startup plan"],
        "marketing_plan":    ["marketing plan", "marketing strategy", "campaign plan"],
        "financial_report":  ["financial report", "financial statement", "balance sheet", "income statement"],
        "legal_contract":    ["contract", "agreement", "nda", "non-disclosure", "terms of service", "service agreement"],
        "resume":            ["resume", "cv", "curriculum vitae", "cover letter"],
        "essay":             ["essay", "paper", "article", "blog post", "research paper"],
        "legal_brief":       ["legal brief", "memorandum of law", "closing argument", "court brief"],
        "lesson_plan":       ["lesson plan", "teaching plan", "class plan", "lecture plan"],
        "syllabus":          ["syllabus", "course outline", "curriculum"],
        "study_guide":       ["study guide", "revision guide", "cheat sheet", "study notes"],
        "presentation":      ["presentation", "slide deck", "pitch deck", "powerpoint", "slides"],
        "email":             ["email", "e-mail", "email draft", "message"],
        "report":            ["report", "analysis report", "summary report", "progress report"],
        "proposal":          ["proposal", "project proposal", "rfp", "bid"],
    }

    INDUSTRIES: Dict[str, List[str]] = {
        "coffee_shop":   ["coffee shop", "cafe", "coffee house", "barista"],
        "restaurant":    ["restaurant", "food", "dining", "catering"],
        "tech_startup":  ["tech startup", "software", "app", "saas", "technology", "fintech"],
        "retail":        ["retail", "store", "ecommerce", "shop", "e-commerce"],
        "healthcare":    ["healthcare", "medical", "clinic", "hospital", "pharma"],
        "legal":         ["law firm", "legal", "attorney", "lawyer", "law"],
        "education":     ["school", "university", "college", "education", "academic", "edtech"],
        "finance":       ["finance", "bank", "investment", "trading", "fintech", "accounting"],
        "marketing":     ["marketing", "advertising", "brand", "agency", "pr"],
        "real_estate":   ["real estate", "property", "housing", "construction"],
        "nonprofit":     ["nonprofit", "charity", "ngo", "foundation"],
    }

    AUDIENCE_MAP: Dict[str, List[str]] = {
        "investors":           ["investor", "bank", "venture capital", "vc", "funder", "shareholder"],
        "customers":           ["customer", "client", "consumer", "buyer"],
        "students":            ["student", "learner", "pupil"],
        "educators":           ["teacher", "professor", "instructor", "educator"],
        "legal_professionals": ["lawyer", "judge", "court", "attorney", "legal"],
        "executives":          ["ceo", "cto", "management", "board", "executive"],
        "general_public":      ["public", "reader", "audience"],
    }

    def analyze(self, prompt: str) -> IntentAnalysis:
        """Deeply analyze the user's prompt and return a structured IntentAnalysis."""
        doc_type  = self._detect_document_type(prompt)
        industry  = self._detect_industry(prompt)
        audience  = self._detect_audience(prompt)
        topics    = self._extract_topics(prompt)
        length    = self._estimate_length(prompt, doc_type)
        complexity = self._determine_complexity(prompt, doc_type)

        return IntentAnalysis(
            document_type    = doc_type,
            industry         = industry,
            target_audience  = audience,
            estimated_length = length,
            complexity       = complexity,
            key_topics       = topics,
            suggested_style  = self._suggest_style(doc_type),
            suggested_format = self._suggest_format(doc_type),
            suggested_tone   = self._suggest_tone(doc_type, industry),
        )

    # ── private helpers ──────────────────────────────────────────────────────

    def _detect_document_type(self, prompt: str) -> str:
        lower = prompt.lower()
        for doc_type, keywords in self.DOCUMENT_TYPES.items():
            if any(kw in lower for kw in keywords):
                return doc_type
        return "general_document"

    def _detect_industry(self, prompt: str) -> Optional[str]:
        lower = prompt.lower()
        for industry, keywords in self.INDUSTRIES.items():
            if any(kw in lower for kw in keywords):
                return industry
        return None

    def _detect_audience(self, prompt: str) -> Optional[str]:
        lower = prompt.lower()
        for audience, keywords in self.AUDIENCE_MAP.items():
            if any(kw in lower for kw in keywords):
                return audience
        return "general"

    def _extract_topics(self, prompt: str) -> List[str]:
        stop = {"write", "create", "generate", "make", "a", "an", "the", "for",
                "about", "on", "with", "and", "or", "of", "to", "in", "my", "our"}
        words = re.findall(r"\b[a-zA-Z]{4,}\b", prompt.lower())
        seen: list[str] = []
        for w in words:
            if w not in stop and w not in seen:
                seen.append(w)
            if len(seen) == 6:
                break
        return seen

    def _estimate_length(self, prompt: str, doc_type: str) -> str:
        lower = prompt.lower()
        if any(w in lower for w in ("short", "brief", "quick", "simple", "one-page")):
            return "1–2 pages"
        if any(w in lower for w in ("detailed", "comprehensive", "full", "complete", "extensive")):
            return "10+ pages"
        # defaults by doc type
        long_types = {"business_plan", "financial_report", "legal_contract", "legal_brief", "syllabus"}
        if doc_type in long_types:
            return "8–10 pages"
        return "3–5 pages"

    def _determine_complexity(self, prompt: str, doc_type: str) -> str:
        high_types = {"legal_contract", "legal_brief", "financial_report", "syllabus"}
        if doc_type in high_types:
            return "High"
        lower = prompt.lower()
        if any(w in lower for w in ("detailed", "comprehensive", "advanced", "complex")):
            return "High"
        if any(w in lower for w in ("simple", "basic", "easy", "beginner")):
            return "Low"
        return "Medium"

    def _suggest_style(self, doc_type: str) -> WritingStyle:
        mapping = {
            "legal_contract":  WritingStyle.LEGAL,
            "legal_brief":     WritingStyle.LEGAL,
            "business_plan":   WritingStyle.PROFESSIONAL,
            "marketing_plan":  WritingStyle.PERSUASIVE,
            "financial_report":WritingStyle.PROFESSIONAL,
            "resume":          WritingStyle.PROFESSIONAL,
            "essay":           WritingStyle.ACADEMIC,
            "report":          WritingStyle.PROFESSIONAL,
            "proposal":        WritingStyle.PERSUASIVE,
            "lesson_plan":     WritingStyle.PROFESSIONAL,
            "syllabus":        WritingStyle.ACADEMIC,
            "study_guide":     WritingStyle.ACADEMIC,
            "presentation":    WritingStyle.PERSUASIVE,
            "email":           WritingStyle.CASUAL,
        }
        return mapping.get(doc_type, WritingStyle.PROFESSIONAL)

    def _suggest_format(self, doc_type: str) -> DocumentFormat:
        mapping = {
            "business_plan":   DocumentFormat.FULL_DOCUMENT,
            "marketing_plan":  DocumentFormat.STANDARD,
            "financial_report":DocumentFormat.STANDARD,
            "legal_contract":  DocumentFormat.LETTER,
            "legal_brief":     DocumentFormat.STANDARD,
            "essay":           DocumentFormat.STANDARD,
            "presentation":    DocumentFormat.PITCH_DECK,
            "email":           DocumentFormat.EMAIL,
            "proposal":        DocumentFormat.EXECUTIVE_SUMMARY,
        }
        return mapping.get(doc_type, DocumentFormat.STANDARD)

    def _suggest_tone(self, doc_type: str, industry: Optional[str]) -> Tone:
        if doc_type in ("legal_contract", "legal_brief", "financial_report"):
            return Tone.FORMAL
        if doc_type in ("marketing_plan", "proposal", "presentation"):
            return Tone.PERSUASIVE
        if doc_type in ("essay", "report", "syllabus", "study_guide", "lesson_plan"):
            return Tone.INFORMATIVE
        if industry in ("coffee_shop", "restaurant", "retail"):
            return Tone.FRIENDLY
        return Tone.FORMAL
