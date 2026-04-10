"""Main AI Controller – Central Brain that routes every prompt to the correct specialist AI."""

from __future__ import annotations

# ── Specialist AI imports ──────────────────────────────────────────────────
from document_ai       import DocumentAI
from professor_ai      import ProfessorAI
from teacher_ai        import TeacherAI
from exam_ai           import ExamAI
from simulation_ai     import SimulationAI
from court_ai          import CourtAI
from student_ai        import StudentAI
from admin_ai          import AdminAI
from multilingual_ai   import MultilingualAI
from integrity_ai      import IntegrityAI
from business_ai       import BusinessAI
from research_ai       import ResearchAI
from analytics_ai      import AnalyticsAI
from content_ai        import ContentAI
from course_builder_ai import CourseBuilderAI
from upload_ai         import UploadAI
from export_utils      import export_pdf, export_docx, export_pptx, export_xlsx


# ── Routing table (keyword → module_key) ─────────────────────────────────

_ROUTING: dict[str, list[str]] = {
    # Office / document types
    "slides":        ["slide", "slides", "presentation", "powerpoint", "pptx", "pitch deck", "keynote", "deck"],
    "excel":         ["spreadsheet", "excel", "xlsx", "budget", "table", "tracker", "invoice",
                      "expense", "salary", "financial model", "inventory", "stock", "data sheet"],
    # Legal / Court
    "court":         ["court", "legal", "law", "contract", "agreement", "litigation", "brief",
                      "clause", "statute", "regulation", "hearing", "tribunal", "arbitration",
                      "opening statement", "closing argument", "cross-examination", "deposition",
                      "motion", "injunction", "plaintiff", "defendant", "counsel", "attorney",
                      "witness", "verdict", "judgment"],
    # Education
    "professor":     ["professor", "academic", "scholarly", "peer review", "journal", "cite",
                      "literature", "dissertation", "thesis", "university", "graduate",
                      "postgraduate", "scholarly", "syllabus", "lecture notes", "academic paper",
                      "academic writing", "undergraduate", "doctoral"],
    "teacher":       ["teacher", "lesson plan", "lesson", "classroom", "pedagogy", "tutor",
                      "instruct", "teach", "activity", "homework"],
    "exam":          ["exam", "quiz", "test", "assessment", "multiple choice", "question paper",
                      "midterm", "final exam", "answer key", "marking", "grade"],
    "simulation":    ["simulation", "role play", "roleplay", "mock", "scenario", "case study",
                      "interview", "cover letter", "recommendation letter", "project"],
    "student":       ["student", "study", "study guide", "flashcard", "revision", "notes",
                      "homework help", "explain to me", "explain this", "help me understand"],
    "admin":         ["admin", "schedule", "timetable", "calendar", "reminder", "deadline",
                      "organise", "organize", "manage", "task", "tracker", "file", "folder"],
    "multilingual":  ["translate", "translation", "multilingual", "language", "french", "spanish",
                      "arabic", "german", "chinese", "portuguese", "italian", "japanese",
                      "localise", "localize", "glossary", "bilingual"],
    "integrity":     ["plagiarism", "integrity", "originality", "citation check", "rewrite",
                      "paraphrase", "ai detection", "turnitin", "similarity", "ethics check"],
    # Business / Professional
    "business":      ["business plan", "business", "startup", "pitch", "investor", "swot",
                      "market analysis", "strategy", "revenue", "profit", "marketing strategy",
                      "competitive analysis", "pestle", "financial projection", "go-to-market",
                      "entrepreneur", "venture", "brand", "product roadmap"],
    "research":      ["research", "literature review", "methodology", "hypothesis", "abstract",
                      "research paper", "research proposal", "finding", "empirical", "survey",
                      "qualitative", "quantitative", "case study research", "academic paper"],
    "analytics":     ["analytics", "data analysis", "kpi", "metrics", "dashboard", "insights",
                      "trend", "forecast", "correlation", "statistical", "performance report",
                      "data insights", "data report", "chart description"],
    "content":       ["blog", "blog post", "article", "social media", "linkedin", "twitter",
                      "instagram", "facebook", "email campaign", "newsletter", "copywriting",
                      "ad copy", "press release", "announcement", "content strategy", "seo",
                      "caption", "tagline", "headline"],
    "course":        ["course", "curriculum", "syllabus", "module", "learning objectives",
                      "course outline", "lesson sequence", "bootcamp", "training programme",
                      "e-learning", "assessment plan", "reading list", "rubric"],
}

# Module key → display name
_MODULE_NAMES: dict[str, str] = {
    "slides":       "Slides AI",
    "excel":        "Excel AI",
    "document":     "Documents AI",
    "professor":    "Senior Professors AI",
    "teacher":      "Teachers AI",
    "exam":         "Exam Prep AI",
    "simulation":   "Simulations AI",
    "court":        "Court AI",
    "student":      "Student Assistant AI",
    "admin":        "Admin AI",
    "multilingual": "Languages AI",
    "integrity":    "Integrity AI",
    "business":     "Business AI",
    "research":     "Research AI",
    "analytics":    "Analytics AI",
    "content":      "Content AI",
    "course":       "Course Builder AI",
    "upload":       "Upload AI",
}


def detect_module(prompt: str, hint: str = "") -> str:
    """Detect the best module for *prompt*, with optional *hint* from the UI.

    Priority:
        1. Explicit non-generic hint (user clicked a specific module tab)
        2. Longest keyword match in prompt text
        3. Fall back to "document"

    "auto", "document", and "" are treated as NO hint — keyword detection runs.
    """
    # Generic / empty hints — skip and do keyword detection
    _GENERIC = {"", "auto", "document", "doc", "pdf", "docx"}

    normalised = hint.strip().lower()

    # Map common aliases from front-end pill/tab names
    _ALIAS = {
        "ppt":          "slides",
        "pptx":         "slides",
        "presentation": "slides",
        "xls":          "excel",
        "xlsx":         "excel",
        "spreadsheet":  "excel",
        "lang":         "multilingual",
        "language":     "multilingual",
        "translate":    "multilingual",
        "coursebuilder":"course",
        "course_builder":"course",
        "edu_professor":    "professor",
        "edu_teacher":      "teacher",
        "edu_exam":         "exam",
        "edu_simulation":   "simulation",
        "edu_court":        "court",
        "edu_student":      "student",
        "edu_admin":        "admin",
        "edu_multilingual": "multilingual",
        "edu_integrity":    "integrity",
    }

    if normalised in _ALIAS:
        normalised = _ALIAS[normalised]

    # Accept explicit non-generic hint
    if normalised and normalised not in _GENERIC and normalised in _MODULE_NAMES:
        return normalised

    # Score all modules by keyword matches
    text = prompt.lower()
    scores: dict[str, int] = {}
    for module, keywords in _ROUTING.items():
        score = sum(
            (len(kw.split()) + 1) for kw in keywords if kw in text
        )
        if score:
            scores[module] = score

    if scores:
        return max(scores, key=lambda k: scores[k])

    # Default
    return "document"


class MainAI:
    """Central Brain – receives any prompt, detects the correct specialist AI,
    runs generation, and returns a normalised output dict with export paths."""

    def __init__(self) -> None:
        # Instantiate all specialist AIs (lightweight — no model loading)
        self._agents: dict = {
            "document":    DocumentAI(),
            "slides":      DocumentAI(),   # slides mode
            "excel":       DocumentAI(),   # excel mode
            "professor":   ProfessorAI(),
            "teacher":     TeacherAI(),
            "exam":        ExamAI(),
            "simulation":  SimulationAI(),
            "court":       CourtAI(),
            "student":     StudentAI(),
            "admin":       AdminAI(),
            "multilingual":MultilingualAI(),
            "integrity":   IntegrityAI(),
            "business":    BusinessAI(),
            "research":    ResearchAI(),
            "analytics":   AnalyticsAI(),
            "content":     ContentAI(),
            "course":      CourseBuilderAI(),
            "upload":      UploadAI(),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, prompt: str, doc_type: str = "auto", module_hint: str = "") -> dict:
        """Route *prompt* to the right AI and return a normalised result dict.

        Parameters
        ----------
        prompt      : User's natural-language request.
        doc_type    : Legacy hint from older API (kept for back-compat). "document"/"auto" → keyword detect.
        module_hint : Explicit module key hint from UI (e.g. 'court', 'business').
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        # module_hint takes priority over doc_type
        effective_hint = module_hint or doc_type
        module = detect_module(prompt.strip(), hint=effective_hint)

        # Run the correct specialist
        result = self._dispatch(prompt.strip(), module)

        # Ensure module is stamped in result
        result.setdefault("module", module)
        result.setdefault("module_name", _MODULE_NAMES.get(module, "Easy AI"))

        # Export files
        title    = result["title"]
        sections = result["sections"]
        self._attach_exports(result, module, title, sections)

        return result

    def detect(self, prompt: str, hint: str = "") -> str:
        """Return the module key that would be selected for this prompt (for UI preview)."""
        return detect_module(prompt, hint=hint)

    # ------------------------------------------------------------------
    # Internal dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, prompt: str, module: str) -> dict:
        agents = self._agents

        if module == "slides":
            return agents["document"].generate(prompt, doc_type="slides")
        if module == "excel":
            return agents["document"].generate(prompt, doc_type="excel")
        if module == "document":
            return agents["document"].generate(prompt, doc_type="document")
        if module == "professor":
            return agents["professor"].generate(prompt)
        if module == "teacher":
            return agents["teacher"].generate(prompt)
        if module == "exam":
            return agents["exam"].generate(prompt)
        if module == "simulation":
            return agents["simulation"].generate(prompt)
        if module == "court":
            return agents["court"].generate(prompt)
        if module == "student":
            return agents["student"].generate(prompt)
        if module == "admin":
            return agents["admin"].generate(prompt)
        if module == "multilingual":
            return agents["multilingual"].generate(prompt)
        if module == "integrity":
            return agents["integrity"].generate(prompt)
        if module == "business":
            return agents["business"].generate(prompt)
        if module == "research":
            return agents["research"].generate(prompt)
        if module == "analytics":
            return agents["analytics"].generate(prompt)
        if module == "content":
            return agents["content"].generate(prompt)
        if module == "course":
            return agents["course"].generate(prompt)
        # Fallback
        return agents["document"].generate(prompt, doc_type="document")

    def _attach_exports(self, result: dict, module: str, title: str, sections: list[dict]) -> None:
        """Generate and attach export file paths based on module type."""
        if module == "slides":
            result["pptx_path"] = export_pptx(title, sections)
            result["pdf_path"]  = export_pdf(title, sections)
        elif module == "excel":
            result["xlsx_path"] = export_xlsx(title, sections)
            result["pdf_path"]  = export_pdf(title, sections)
        else:
            result["pdf_path"]  = export_pdf(title, sections)
            result["docx_path"] = export_docx(title, sections)
