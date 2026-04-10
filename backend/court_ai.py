"""Court AI – mock trials, legal analysis, contracts, and briefs."""

from __future__ import annotations


class CourtAI:
    """Generates mock trial scripts, legal analysis, contracts, and legal briefs."""

    def generate(self, prompt: str) -> dict:
        title = f"Legal Document: {prompt[:68]}"
        sections = [
            {
                "heading": "Case Summary",
                "content": (
                    f"Matter: {prompt}\n\n"
                    "This document is prepared for educational and simulation purposes only. "
                    "It does not constitute legal advice. All parties, facts, and citations "
                    "are fictional unless otherwise stated."
                ),
            },
            {
                "heading": "Mock Trial – Judge's Opening",
                "content": (
                    "The Honourable Judge [Name] presiding.\n\n"
                    "Court is now in session. This matter concerns [brief description]. "
                    "Both parties have agreed to the following procedural rules:\n"
                    "• Opening statements: 5 minutes per side\n"
                    "• Examination of witnesses: direct and cross\n"
                    "• Closing arguments: 10 minutes per side\n"
                    "• Judgment: delivered within 24 hours of proceedings\n\n"
                    "Counsel, you may begin."
                ),
            },
            {
                "heading": "Prosecution / Claimant Arguments",
                "content": (
                    "Opening Statement:\n"
                    "Ladies and gentlemen of the court, the evidence will show that "
                    "[party] acted in direct contravention of [rule/statute/obligation]. "
                    "We will present documentary evidence, witness testimony, and expert "
                    "opinion to establish liability beyond the applicable standard of proof.\n\n"
                    "Key Arguments:\n"
                    "1. Breach of duty: [Details]\n"
                    "2. Causation: [Direct link to harm]\n"
                    "3. Remedy sought: [Damages / Injunction / Specific performance]"
                ),
            },
            {
                "heading": "Defence / Respondent Arguments",
                "content": (
                    "Opening Statement:\n"
                    "The defence will demonstrate that [party] complied with all applicable "
                    "obligations and that the claimant's case is unsupported by the evidence.\n\n"
                    "Key Arguments:\n"
                    "1. No breach: [Factual basis]\n"
                    "2. Intervening cause: [Chain of causation broken]\n"
                    "3. Contributory negligence / comparative fault: [If applicable]"
                ),
            },
            {
                "heading": "Legal Argument Analysis",
                "content": (
                    "Applicable Legal Principles:\n"
                    "• [Statute or common law rule 1]\n"
                    "• [Landmark case authority]\n"
                    "• [Regulatory provision if relevant]\n\n"
                    "Analysis:\n"
                    "Applying the above to the facts, the stronger argument appears to rest "
                    "with [party] on the issue of [X], while [party] has a more compelling "
                    "case on [Y]. The outcome will likely turn on [pivotal issue]."
                ),
            },
            {
                "heading": "Contract / Legal Brief",
                "content": (
                    "CONTRACT TEMPLATE\n\n"
                    "This Agreement is entered into as of [Date] between [Party A] and "
                    "[Party B] (collectively 'the Parties').\n\n"
                    "1. SCOPE OF SERVICES\n"
                    "[Party A] agrees to provide [description of services/goods].\n\n"
                    "2. CONSIDERATION\n"
                    "[Party B] agrees to pay [amount] within [timeframe].\n\n"
                    "3. TERM AND TERMINATION\n"
                    "This Agreement commences on [date] and continues until [end date] "
                    "unless terminated earlier by either party on [notice period] written notice.\n\n"
                    "4. GOVERNING LAW\n"
                    "This Agreement shall be governed by the laws of [Jurisdiction].\n\n"
                    "SIGNED:\n"
                    "__________________   __________________\n"
                    "[Party A]             [Party B]"
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
