"""Academic Integrity AI – originality review, AI misuse detection, guidance."""

from __future__ import annotations


class IntegrityAI:
    """Generates academic integrity reports and guidance documents."""

    def generate(self, prompt: str) -> dict:
        title = f"Academic Integrity Review: {prompt[:58]}"
        sections = [
            {
                "heading": "Review Request",
                "content": (
                    f"Submission / topic under review: {prompt}\n\n"
                    "This report provides guidance on academic integrity principles "
                    "and flags areas that may require attention before final submission. "
                    "It does not replace a formal institutional plagiarism check."
                ),
            },
            {
                "heading": "Originality Check Guidance",
                "content": (
                    "Checklist for originality:\n"
                    "□ All direct quotations are enclosed in quotation marks and cited.\n"
                    "□ Paraphrased ideas are attributed to the original source.\n"
                    "□ All sources appear in the reference list.\n"
                    "□ The work reflects the student's own analysis and conclusions.\n"
                    "□ No sections have been copied from previous submissions "
                    "(self-plagiarism).\n\n"
                    "Recommendation: Run the submission through your institution's "
                    "approved similarity-detection tool (e.g. Turnitin, iThenticate) "
                    "before submitting."
                ),
            },
            {
                "heading": "AI Misuse Detection Warnings",
                "content": (
                    "Potential indicators of undisclosed AI-generated content:\n"
                    "• Unusually uniform sentence length and structure throughout.\n"
                    "• Generic, non-specific examples that lack personal or contextual "
                    "detail.\n"
                    "• Absence of the student's documented voice or analytical style.\n"
                    "• Content that does not align with class discussions or lecture notes.\n\n"
                    "Policy reminder: Students must disclose any use of AI tools in "
                    "accordance with institutional policy. Undisclosed use may constitute "
                    "academic misconduct."
                ),
            },
            {
                "heading": "Academic Honesty Guidance",
                "content": (
                    "Core principles of academic integrity:\n\n"
                    "1. Honesty – represent your own work accurately.\n"
                    "2. Trust – build a trustworthy academic record.\n"
                    "3. Fairness – respect the effort of other students.\n"
                    "4. Respect – acknowledge the contributions of scholars and authors.\n"
                    "5. Responsibility – take ownership of your academic conduct.\n\n"
                    "If you are uncertain whether a practice is acceptable:\n"
                    "• Consult your course handbook or assessment brief.\n"
                    "• Speak with your instructor or academic integrity officer.\n"
                    "• Use your institution's academic integrity resources."
                ),
            },
            {
                "heading": "Summary & Next Steps",
                "content": (
                    "Overall assessment: [Pending full review]\n\n"
                    "Recommended actions before submission:\n"
                    "1. Complete the originality checklist above.\n"
                    "2. Run through an approved similarity-detection platform.\n"
                    "3. Review and update your citation and reference list.\n"
                    "4. If AI tools were used, add the required disclosure statement.\n"
                    "5. Seek feedback from your instructor if any items remain unclear."
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
