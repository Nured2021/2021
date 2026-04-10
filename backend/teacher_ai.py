"""Teacher AI – lesson planning, topic explanations, homework help."""

from __future__ import annotations


class TeacherAI:
    """Generates lesson plans, explanations, class activities, and study notes."""

    def generate(self, prompt: str) -> dict:
        title = f"Lesson Material: {prompt[:70]}"
        sections = [
            {
                "heading": "Lesson Objectives",
                "content": (
                    f"Topic: {prompt}\n\n"
                    "By the end of this lesson, students will be able to:\n"
                    "• Explain the core concepts in their own words.\n"
                    "• Apply the concepts to real-world examples.\n"
                    "• Identify connections to prior learning."
                ),
            },
            {
                "heading": "Lesson Plan (60 minutes)",
                "content": (
                    "0–5 min   : Warm-up / hook question\n"
                    "5–15 min  : Direct instruction – introduce key terms and concepts\n"
                    "15–30 min : Guided practice – worked examples with class discussion\n"
                    "30–45 min : Independent or group activity\n"
                    "45–55 min : Review and Q&A\n"
                    "55–60 min : Exit ticket / formative check"
                ),
            },
            {
                "heading": "Topic Explanation",
                "content": (
                    "The topic is introduced through concrete, relatable examples before "
                    "moving to abstract theory. Key vocabulary is highlighted and defined "
                    "in accessible language. Visual aids, analogies, and real-world "
                    "connections are used throughout to maximise understanding."
                ),
            },
            {
                "heading": "Homework Assignment",
                "content": (
                    "1. Read the assigned section and take margin notes on the three most "
                    "important ideas.\n"
                    "2. Complete the five practice questions at the end of the chapter.\n"
                    "3. Bring one real-world example related to today's topic to share "
                    "with the class next session."
                ),
            },
            {
                "heading": "Class Activity / Study Notes",
                "content": (
                    "Activity: Think-Pair-Share\n"
                    "Students individually reflect on the prompt question, then discuss "
                    "with a partner, and finally share key insights with the full class.\n\n"
                    "Study Notes:\n"
                    "• Concept map template provided (attach or distribute separately)\n"
                    "• Summary sheet with key definitions and formulas\n"
                    "• Review checklist for self-assessment"
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
