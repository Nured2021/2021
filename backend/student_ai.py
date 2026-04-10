"""Student Assistant AI – 24/7 learning companion, summaries, study guides."""

from __future__ import annotations


class StudentAI:
    """Generates study guides, summaries, and answers questions from content."""

    def generate(self, prompt: str) -> dict:
        title = f"Study Guide: {prompt[:70]}"
        sections = [
            {
                "heading": "Overview",
                "content": (
                    f"Learning request: {prompt}\n\n"
                    "This study guide is designed to help you master the material "
                    "efficiently. Work through each section in order, testing yourself "
                    "at each stage before moving on."
                ),
            },
            {
                "heading": "Key Concepts Summary",
                "content": (
                    "Concept 1: [Name]\n"
                    "  Definition: [Clear, plain-language explanation]\n"
                    "  Why it matters: [Practical significance]\n\n"
                    "Concept 2: [Name]\n"
                    "  Definition: [Clear, plain-language explanation]\n"
                    "  Why it matters: [Practical significance]\n\n"
                    "Concept 3: [Name]\n"
                    "  Definition: [Clear, plain-language explanation]\n"
                    "  Why it matters: [Practical significance]"
                ),
            },
            {
                "heading": "Textbook / PDF Summary",
                "content": (
                    "Main thesis / argument: [Core claim of the source material]\n\n"
                    "Supporting points:\n"
                    "• [Point 1 with brief evidence]\n"
                    "• [Point 2 with brief evidence]\n"
                    "• [Point 3 with brief evidence]\n\n"
                    "Critical evaluation: [Strengths and limitations of the argument]\n\n"
                    "Connection to course themes: [How this fits the broader subject]"
                ),
            },
            {
                "heading": "Self-Test Questions",
                "content": (
                    "1. What is the central idea of this topic?\n"
                    "2. How does Concept 1 relate to Concept 2?\n"
                    "3. Give one example that illustrates the main principle.\n"
                    "4. What are two counter-arguments or exceptions?\n"
                    "5. How would you explain this to someone with no background in the subject?"
                ),
            },
            {
                "heading": "Study Tips & Schedule",
                "content": (
                    "Recommended study schedule:\n"
                    "Day 1: Read and annotate the core material (45 min)\n"
                    "Day 2: Create your own notes from memory (30 min)\n"
                    "Day 3: Answer the self-test questions without looking at notes (20 min)\n"
                    "Day 4: Review gaps and re-read weak areas (25 min)\n"
                    "Day 5: Practice with past exam questions (40 min)\n\n"
                    "Tips:\n"
                    "• Use spaced repetition – review material at increasing intervals.\n"
                    "• Teach the concept to a classmate to deepen understanding.\n"
                    "• Take regular breaks using the Pomodoro technique (25 min on, 5 min off)."
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
