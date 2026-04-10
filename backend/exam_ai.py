"""Exam Prep AI – quizzes, exams, answer keys, and progress feedback."""

from __future__ import annotations


class ExamAI:
    """Generates quizzes, final exams, answer keys, and feedback reports."""

    def generate(self, prompt: str, exam_type: str = "quiz") -> dict:
        label = "Quiz" if exam_type == "quiz" else "Final Examination"
        title = f"{label}: {prompt[:65]}"
        sections = [
            {
                "heading": "Instructions",
                "content": (
                    f"{'Quiz' if exam_type == 'quiz' else 'Final Exam'} on: {prompt}\n\n"
                    "• Read each question carefully before answering.\n"
                    "• Where applicable, show all working / reasoning.\n"
                    "• Time allowed: "
                    + ("20 minutes" if exam_type == "quiz" else "90 minutes")
                    + "\n"
                    "• Total marks: "
                    + ("20" if exam_type == "quiz" else "100")
                ),
            },
            {
                "heading": "Section A – Multiple Choice",
                "content": (
                    "1. Which of the following best describes the core concept?\n"
                    "   a) Option A   b) Option B   c) Option C   d) Option D\n\n"
                    "2. What is the primary purpose of the foundational principle?\n"
                    "   a) Option A   b) Option B   c) Option C   d) Option D\n\n"
                    "3. Which scenario correctly applies the rule in practice?\n"
                    "   a) Option A   b) Option B   c) Option C   d) Option D"
                ),
            },
            {
                "heading": "Section B – Short Answer",
                "content": (
                    "4. Define the key term in your own words. (3 marks)\n\n"
                    "5. Explain two differences between the main approaches. (4 marks)\n\n"
                    "6. Give one real-world example and explain its significance. (3 marks)"
                ),
            },
            {
                "heading": "Section C – Essay / Extended Response",
                "content": (
                    "7. Critically discuss the topic with reference to at least two "
                    "theoretical perspectives. Support your answer with examples. "
                    + ("(10 marks)" if exam_type == "quiz" else "(30 marks)")
                ),
            },
            {
                "heading": "Answer Key",
                "content": (
                    "Section A: 1-c, 2-b, 3-a (replace with correct answers)\n\n"
                    "Section B:\n"
                    "4. [Definition should include core attributes and context.]\n"
                    "5. [Two clearly contrasted points with supporting evidence.]\n"
                    "6. [Relevant example with clear link to theory.]\n\n"
                    "Section C:\n"
                    "[Model answer: structured argument, two or more perspectives, "
                    "concrete examples, clear conclusion.]"
                ),
            },
            {
                "heading": "Progress Feedback Template",
                "content": (
                    "Student demonstrates:\n"
                    "✓ Strong understanding of foundational concepts\n"
                    "✓ Ability to apply theory to practice\n"
                    "△ Needs improvement: analytical depth in extended responses\n"
                    "△ Review: distinction between related concepts\n\n"
                    "Recommended next steps:\n"
                    "1. Re-read chapters on the core principles.\n"
                    "2. Practice timed essay writing.\n"
                    "3. Attend office hours to discuss feedback."
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}


def _sections_to_text(title: str, sections: list[dict]) -> str:
    lines = [title, "=" * len(title), ""]
    for sec in sections:
        lines.append(sec["heading"])
        lines.append("-" * len(sec["heading"]))
        lines.append(sec["content"])
        lines.append("")
    return "\n".join(lines)
