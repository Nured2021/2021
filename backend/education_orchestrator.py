"""Education Orchestrator – classifies prompts and routes to the right AI module."""

from __future__ import annotations

import re

from professor_ai import ProfessorAI
from teacher_ai import TeacherAI
from exam_ai import ExamAI
from simulation_ai import SimulationAI
from court_ai import CourtAI
from student_ai import StudentAI
from admin_ai import AdminAI
from multilingual_ai import MultilingualAI
from integrity_ai import IntegrityAI

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

_INTEGRITY_KEYWORDS = {
    "plagiarism", "originality", "integrity", "academic honesty",
    "ai detection", "similarity", "citation", "reference", "misconduct",
    "turnitin", "ithenticate",
}

# Module labels returned to the client for display purposes
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
]


class EducationOrchestrator:
    """Routes education prompts to the appropriate AI module."""

    def __init__(self) -> None:
        self._professor = ProfessorAI()
        self._teacher = TeacherAI()
        self._exam = ExamAI()
        self._simulation = SimulationAI()
        self._court = CourtAI()
        self._student = StudentAI()
        self._admin = AdminAI()
        self._multilingual = MultilingualAI()
        self._integrity = IntegrityAI()

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
        return {"module": module, "response": response}

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
