"""Senior Professor AI – subject-expert academic content generation."""

from __future__ import annotations

SUPPORTED_SUBJECTS = ["law", "business", "computer science"]


class ProfessorAI:
    """Generates high-level academic content: syllabi, research papers, exams."""

    def generate(self, prompt: str, subject: str = "general") -> dict:
        title = f"Academic Content: {prompt[:70]}"
        sections = [
            {
                "heading": "Course / Topic Overview",
                "content": (
                    f"Subject area: {subject.title()}\n"
                    f"Request: {prompt}\n\n"
                    "This material is prepared at a senior-undergraduate / postgraduate level. "
                    "It integrates current scholarship, case law, industry standards, and "
                    "theoretical frameworks relevant to the discipline."
                ),
            },
            {
                "heading": "Syllabus",
                "content": (
                    "Week 1 – Foundations and Historical Context\n"
                    "Week 2 – Core Principles and Theoretical Frameworks\n"
                    "Week 3 – Applied Analysis and Case Studies\n"
                    "Week 4 – Contemporary Issues and Debates\n"
                    "Week 5 – Research Methods and Academic Writing\n"
                    "Week 6 – Advanced Topics and Emerging Trends\n"
                    "Week 7 – Review, Synthesis, and Final Assessment"
                ),
            },
            {
                "heading": "Academic Explanation",
                "content": (
                    "The topic is examined through multiple analytical lenses. "
                    "Primary sources, landmark decisions (or foundational texts), and "
                    "peer-reviewed literature form the backbone of this treatment. "
                    "Students are expected to engage critically with all assigned readings "
                    "and articulate independent, well-supported arguments."
                ),
            },
            {
                "heading": "High-Level Exam Questions",
                "content": (
                    "1. Critically evaluate the historical development of the core doctrine "
                    "and its contemporary relevance.\n"
                    "2. Compare and contrast competing theoretical frameworks applied to "
                    "this subject area.\n"
                    "3. Using relevant case studies, analyse how practitioners navigate "
                    "key challenges in this field.\n"
                    "4. Essay (2,500 words): Assess the impact of recent developments on "
                    "established principles in this discipline."
                ),
            },
            {
                "heading": "Recommended Reading",
                "content": (
                    "• Core textbook assigned by the institution\n"
                    "• Peer-reviewed journals relevant to the discipline\n"
                    "• Landmark cases / seminal industry reports\n"
                    "• Supplementary lecture notes provided by the professor"
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
