"""Education Orchestrator – classifies prompts and routes to the right AI module."""

from __future__ import annotations

import re

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

# ---------------------------------------------------------------------------
# Keyword routing tables
# ---------------------------------------------------------------------------

_PROFESSOR_KEYWORDS = {
    "syllabus", "research paper", "course outline", "lecture", "academic",
    "dissertation", "thesis", "curriculum", "scholarly", "postgraduate",
    "undergraduate", "module", "journal", "professor",
}

_TEACHER_KEYWORDS = {
    "lesson plan", "lesson", "explain", "homework", "activity", "class",
    "teaching", "teacher", "student activity", "worksheet", "study note",
    "tutor", "instruction", "topic",
}

_EXAM_KEYWORDS = {
    "quiz", "exam", "test", "assessment", "answer key", "multiple choice",
    "examination", "questions", "mock exam", "final exam", "midterm",
    "practice test", "feedback", "grading",
}

_SIMULATION_KEYWORDS = {
    "case study", "business case", "interview", "simulation", "project",
    "recommendation letter", "cover letter", "industry", "internship",
    "job", "workplace", "company", "startup", "strategy",
}

_COURT_KEYWORDS = {
    "court", "trial", "legal", "law", "judge", "counsel", "contract",
    "brief", "litigation", "plaintiff", "defendant", "verdict", "statute",
    "regulation", "compliance", "attorney", "mock trial", "argument",
}

_STUDENT_KEYWORDS = {
    "study guide", "summarize", "summary", "summarise", "flashcard",
    "notes", "revision", "explain to me", "help me understand",
    "learning", "student", "pdf", "textbook", "reading",
}

_ADMIN_KEYWORDS = {
    "schedule", "reminder", "deadline", "calendar", "office hours",
    "submission", "tracking", "assignment reminder", "administrative",
    "timetable", "planning", "organize", "organise",
}

_MULTILINGUAL_KEYWORDS = {
    "translate", "translation", "language", "multilingual", "arabic",
    "french", "spanish", "german", "chinese", "portuguese", "localise",
    "localize", "bilingual",
}

_BUSINESS_KEYWORDS = {
    "business plan", "business", "startup", "pitch deck", "investor", "swot",
    "market analysis", "marketing strategy", "financial model", "revenue",
    "competitive analysis", "pestle", "go-to-market", "brand", "entrepreneur",
}

_RESEARCH_KEYWORDS = {
    "literature review", "research paper", "methodology", "hypothesis", "abstract",
    "research proposal", "qualitative", "quantitative", "empirical", "finding",
    "research question", "academic paper",
}

_ANALYTICS_KEYWORDS = {
    "analytics", "data analysis", "kpi", "metrics", "dashboard", "insights",
    "trend analysis", "forecast", "correlation", "statistical", "performance report",
    "data insights",
}

_CONTENT_KEYWORDS = {
    "blog", "blog post", "article", "social media", "linkedin", "twitter",
    "instagram", "email campaign", "newsletter", "copywriting", "ad copy",
    "press release", "seo", "caption", "content strategy",
}

_COURSE_KEYWORDS = {
    "course outline", "curriculum", "syllabus", "module outline", "learning objectives",
    "course builder", "lesson sequence", "bootcamp", "training programme",
    "assessment plan", "reading list", "e-learning",
}


MODULE_INFO = [
    {"id": "professor",   "label": "Senior Professor", "icon": "🎓",
     "description": "Syllabi, research papers, academic explanations, high-level exams"},
    {"id": "teacher",     "label": "Teacher",          "icon": "📚",
     "description": "Lesson plans, topic explanations, homework help, class activities"},
    {"id": "exam",        "label": "Exam Prep",        "icon": "📝",
     "description": "Quizzes, final exams, answer keys, progress feedback"},
    {"id": "simulation",  "label": "Simulations",      "icon": "💼",
     "description": "Business cases, interview simulations, industry projects"},
    {"id": "court",       "label": "Court",            "icon": "⚖️",
     "description": "Mock trials, legal arguments, contracts, briefs"},
    {"id": "student",     "label": "Student Assistant","icon": "🙋",
     "description": "Study guides, textbook summaries, learning support"},
    {"id": "admin",       "label": "Admin",            "icon": "🗂️",
     "description": "Scheduling, reminders, submission tracking"},
    {"id": "multilingual","label": "Languages",        "icon": "🌐",
     "description": "Translation, localisation, multilingual content"},
    {"id": "integrity",   "label": "Integrity",        "icon": "🛡️",
     "description": "Originality checks, AI misuse detection, honesty guidance"},
    {"id": "business",    "label": "Business AI",      "icon": "💼",
     "description": "Business plans, pitch decks, SWOT, marketing strategy, financial models"},
    {"id": "research",    "label": "Research AI",      "icon": "🔬",
     "description": "Literature reviews, research papers, methodology, abstracts"},
    {"id": "analytics",   "label": "Analytics AI",     "icon": "📊",
     "description": "Data insights, KPI dashboards, trend analysis, forecasts"},
    {"id": "content",     "label": "Content AI",       "icon": "✍️",
     "description": "Blog posts, social media, email campaigns, press releases"},
    {"id": "course",      "label": "Course Builder AI","icon": "🏫",
     "description": "Full course outlines, syllabi, assessment plans, reading lists"},
]


class EducationOrchestrator:
    """Routes education prompts to the appropriate AI module."""

    def __init__(self) -> None:
        self._professor  = ProfessorAI()
        self._teacher    = TeacherAI()
        self._exam       = ExamAI()
        self._simulation = SimulationAI()
        self._court      = CourtAI()
        self._student    = StudentAI()
        self._admin      = AdminAI()
        self._multilingual = MultilingualAI()
        self._integrity  = IntegrityAI()
        self._business   = BusinessAI()
        self._research   = ResearchAI()
        self._analytics  = AnalyticsAI()
        self._content    = ContentAI()
        self._course     = CourseBuilderAI()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, prompt: str) -> str:
        """Return the module id that best matches the prompt."""
        lower = prompt.lower()
        tokens = set(re.findall(r"\b\w[\w\s]*\b", lower))

        scores: dict[str, int] = {
            "professor":    _score(lower, _PROFESSOR_KEYWORDS),
            "teacher":      _score(lower, _TEACHER_KEYWORDS),
            "exam":         _score(lower, _EXAM_KEYWORDS),
            "simulation":   _score(lower, _SIMULATION_KEYWORDS),
            "court":        _score(lower, _COURT_KEYWORDS),
            "student":      _score(lower, _STUDENT_KEYWORDS),
            "admin":        _score(lower, _ADMIN_KEYWORDS),
            "multilingual": _score(lower, _MULTILINGUAL_KEYWORDS),
            "integrity":    _score(lower, _INTEGRITY_KEYWORDS),
            "business":     _score(lower, _BUSINESS_KEYWORDS),
            "research":     _score(lower, _RESEARCH_KEYWORDS),
            "analytics":    _score(lower, _ANALYTICS_KEYWORDS),
            "content":      _score(lower, _CONTENT_KEYWORDS),
            "course":       _score(lower, _COURSE_KEYWORDS),
        }

        best = max(scores, key=lambda k: scores[k])
        return best if scores[best] > 0 else "professor"

    def generate(self, prompt: str, module: str | None = None) -> dict:
        """Generate content for *prompt*, routing to *module* (auto-detect if None)."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        module = module or self.classify(prompt.strip())
        result = self._dispatch(prompt.strip(), module)
        result["module"] = module
        return result

    def chat(self, message: str, module: str | None = None) -> dict:
        """Return a conversational response from the appropriate module."""
        module = module or self.classify(message.strip())
        response = (
            f"[{_module_label(module)}] Understood. Here is my response to your query:\n\n"
            f"'{message}'\n\n"
            "In a production system, this would stream a contextual AI response. "
            "For now, please use the /education/generate endpoint to produce a full "
            "structured document based on your query."
        )
        return {"module": module, "reply": response}

    # ------------------------------------------------------------------
    # Private dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, prompt: str, module: str) -> dict:
        dispatch_map = {
            "professor":    lambda p: self._professor.generate(p),
            "teacher":      lambda p: self._teacher.generate(p),
            "exam":         lambda p: self._exam.generate(p),
            "simulation":   lambda p: self._simulation.generate(p),
            "court":        lambda p: self._court.generate(p),
            "student":      lambda p: self._student.generate(p),
            "admin":        lambda p: self._admin.generate(p),
            "multilingual": lambda p: self._multilingual.generate(p),
            "integrity":    lambda p: self._integrity.generate(p),
            "business":     lambda p: self._business.generate(p),
            "research":     lambda p: self._research.generate(p),
            "analytics":    lambda p: self._analytics.generate(p),
            "content":      lambda p: self._content.generate(p),
            "course":       lambda p: self._course.generate(p),
        }
        handler = dispatch_map.get(module)
        if handler is None:
            raise ValueError(f"Unknown education module: '{module}'")
        return handler(prompt)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score(text: str, keywords: set[str]) -> int:
    return sum(1 for kw in keywords if kw in text)


def _module_label(module_id: str) -> str:
    for m in MODULE_INFO:
        if m["id"] == module_id:
            return m["label"]
    return module_id.title()
