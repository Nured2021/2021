"""Document AI – generates structured document content from a prompt."""

from __future__ import annotations

import re
import textwrap


class DocumentAI:
    """Simple rule-based document content generator.

    In production this would call an LLM API; here it produces clean,
    structured content so the app is fully functional without an API key.
    """

    def generate(self, prompt: str, doc_type: str = "document") -> dict:
        """Return a dict with title, sections list, and raw text body."""
        title = self._make_title(prompt)
        sections = self._make_sections(prompt, doc_type)
        body = self._sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _make_title(self, prompt: str) -> str:
        # Capitalise the first sentence / fragment as the title
        clean = prompt.strip().rstrip(".")
        if len(clean) > 80:
            clean = clean[:77] + "..."
        return clean.title()

    def _make_sections(self, prompt: str, doc_type: str) -> list[dict]:
        keywords = [w.lower() for w in re.findall(r"\w+", prompt)]

        if doc_type == "presentation":
            return self._presentation_sections(prompt, keywords)
        if doc_type == "excel":
            return self._spreadsheet_sections(prompt, keywords)
        return self._document_sections(prompt, keywords)

    # --- document ---

    def _document_sections(self, prompt: str, keywords: list[str]) -> list[dict]:
        intro = textwrap.dedent(f"""\
            This document addresses the topic: "{prompt}".
            The following sections provide a comprehensive overview,
            analysis, and actionable recommendations.""")

        overview = textwrap.dedent(f"""\
            The subject matter can be understood through several key dimensions.
            Primary considerations include scope, stakeholders, and expected
            outcomes. Each area is examined in detail within this document.""")

        analysis = textwrap.dedent(f"""\
            A thorough analysis reveals both opportunities and challenges.
            Critical factors to consider:
            • Alignment with strategic objectives
            • Resource requirements and constraints
            • Risk assessment and mitigation strategies
            • Timeline and milestones""")

        recommendations = textwrap.dedent(f"""\
            Based on the analysis above, the following actions are recommended:
            1. Define clear objectives and success metrics.
            2. Allocate appropriate resources and assign ownership.
            3. Establish a monitoring and review cadence.
            4. Communicate progress to relevant stakeholders.""")

        conclusion = textwrap.dedent(f"""\
            In conclusion, addressing "{prompt}" requires a structured approach,
            stakeholder buy-in, and continuous improvement. Implementation of the
            recommendations outlined here will drive measurable results.""")

        return [
            {"heading": "Introduction", "content": intro},
            {"heading": "Overview", "content": overview},
            {"heading": "Analysis", "content": analysis},
            {"heading": "Recommendations", "content": recommendations},
            {"heading": "Conclusion", "content": conclusion},
        ]

    # --- presentation ---

    def _presentation_sections(self, prompt: str, keywords: list[str]) -> list[dict]:
        slides = [
            {"heading": "Slide 1 – Title", "content": f"Topic: {prompt}"},
            {"heading": "Slide 2 – Agenda", "content": "• Introduction\n• Key Points\n• Analysis\n• Next Steps"},
            {"heading": "Slide 3 – Introduction", "content": f"Overview of the topic and why it matters."},
            {"heading": "Slide 4 – Key Points", "content": "• Point 1: Context and background\n• Point 2: Core concepts\n• Point 3: Supporting evidence"},
            {"heading": "Slide 5 – Analysis", "content": "Data-driven insights and observations relevant to the topic."},
            {"heading": "Slide 6 – Next Steps", "content": "1. Immediate actions\n2. Medium-term milestones\n3. Long-term vision"},
            {"heading": "Slide 7 – Conclusion", "content": f"Summary and call to action for: {prompt}"},
        ]
        return slides

    # --- spreadsheet ---

    def _spreadsheet_sections(self, prompt: str, keywords: list[str]) -> list[dict]:
        table = (
            "Category | Description | Value | Notes\n"
            "---------|-------------|-------|------\n"
            "Item A   | First entry | 100   | Review required\n"
            "Item B   | Second entry| 250   | Confirmed\n"
            "Item C   | Third entry | 180   | Pending\n"
            "TOTAL    |             | 530   |\n"
        )
        return [
            {"heading": "Purpose", "content": f"Spreadsheet data for: {prompt}"},
            {"heading": "Data Table", "content": table},
            {"heading": "Notes", "content": "All values are illustrative. Replace with actual data before use."},
        ]

    # ------------------------------------------------------------------

    def _sections_to_text(self, title: str, sections: list[dict]) -> str:
        lines = [title, "=" * len(title), ""]
        for sec in sections:
            lines.append(sec["heading"])
            lines.append("-" * len(sec["heading"]))
            lines.append(sec["content"])
            lines.append("")
        return "\n".join(lines)
