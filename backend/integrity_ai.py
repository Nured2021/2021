"""Academic Integrity AI – originality review, AI misuse detection, guidance."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class IntegrityAI:
    """Generates academic integrity reports, originality guides, and ethics checks."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=5)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_rewrite   = any(w in lower for w in ["rewrite", "paraphrase", "rephrase", "improve"])
        is_citation  = any(w in lower for w in ["citation", "reference", "cite", "bibliography"])
        is_ai_check  = any(w in lower for w in ["ai detection", "ai-generated", "chatgpt", "generated"])

        title = f"Integrity Review: {topic}"
        sections = [
            {
                "heading": "Review Summary",
                "content": (
                    f"Submission reviewed: {topic}\n"
                    f"Subject domain: {domain.title()}\n"
                    f"Key areas: {kw_str}\n\n"
                    f"This integrity review assesses your submission for {topic.lower()} against "
                    f"academic honesty standards. It covers originality, citation practices, "
                    f"AI-content indicators, and ethical compliance. This report is for "
                    f"guidance only and does not replace an institutional plagiarism check."
                ),
            },
            {
                "heading": "Originality Checklist",
                "content": (
                    f"Originality Review for {topic}:\n\n"
                    f"  □ All direct quotations from sources on {kw_str} are in quotation marks\n"
                    f"  □ Every quote is followed by an in-text citation (Author, Year, p. X)\n"
                    f"  □ Paraphrased ideas are rewritten in your own words AND cited\n"
                    f"  □ No text has been copied verbatim without quotation marks\n"
                    f"  □ The reference list at the end matches every in-text citation\n"
                    f"  □ You have not recycled sections from previous submissions (self-plagiarism)\n"
                    f"  □ Data, statistics, and diagrams are attributed to their source\n"
                    f"  □ Common knowledge about {topic.lower()} does not require citation, "
                    f"    but specific claims and theories do\n\n"
                    f"Score your checklist: ___/8 boxes ticked\n"
                    f"  8/8 = Ready to submit  |  6–7/8 = Minor revision  |  <6/8 = Review required"
                ),
            },
            {
                "heading": "AI-Generated Content Indicators",
                "content": (
                    f"Scan results for potential AI-generated content in {topic}:\n\n"
                    f"Indicators to review:\n"
                    f"  ⚠ Overly uniform sentence length and structure throughout the document\n"
                    f"  ⚠ Very general or non-specific examples that lack personal or contextual detail\n"
                    f"  ⚠ Absence of your documented voice, analytical style, or course-specific examples\n"
                    f"  ⚠ Content that does not reference class discussions, lectures, or assigned readings\n"
                    f"  ⚠ Perfect grammar and zero stylistic variation (unusual for human writing)\n"
                    f"  ⚠ Phrases like 'As an AI language model...' or similar disclosures\n\n"
                    f"Policy reminder for {domain.title()} assignments:\n"
                    f"  Undisclosed use of AI tools to generate or substantially complete academic work "
                    f"  may constitute academic misconduct. Check your institution's AI use policy. "
                    f"  If you used AI tools for {topic.lower()}, disclose this clearly in your submission "
                    f"  in accordance with your course guidelines."
                ),
            },
            {
                "heading": "Citation & Reference Guidance",
                "content": (
                    f"Citation guide for {topic} (select your required style):\n\n"
                    f"APA (7th Edition):\n"
                    f"  In-text: (Author, Year) or (Author, Year, p. X) for direct quotes\n"
                    f"  Reference list: Author, A. A. (Year). Title of work. Publisher.\n"
                    f"  Example: Smith, J. (2022). {topic}: Principles and practice. Oxford Press.\n\n"
                    f"Harvard:\n"
                    f"  In-text: (Smith, 2022) or (Smith, 2022: 45) for page numbers\n"
                    f"  Reference: Smith, J. (2022) {topic}: Principles and practice. Oxford: Oxford Press.\n\n"
                    f"OSCOLA (Legal):\n"
                    f"  Case: Party A v Party B [Year] Court Reference\n"
                    f"  Statute: Name of Act Year, s X\n"
                    f"  Article: Author, 'Title' (Year) Volume Journal StartPage\n\n"
                    f"For {kw_str}: Ensure all sources related to these concepts are cited using "
                    f"the style required by your institution. Consistency is mandatory."
                ),
            },
            {
                "heading": "Ethical Compliance & Recommendations",
                "content": (
                    f"Ethical standards check for {topic}:\n\n"
                    f"Academic honesty principles applied:\n"
                    f"  1. Honesty: Does the work accurately represent your own understanding "
                    f"     of {topic.lower()}?\n"
                    f"  2. Fairness: Have you given proper credit to all scholars whose ideas "
                    f"     on {kw_str} appear in your work?\n"
                    f"  3. Responsibility: Have you complied with all assessment guidelines?\n"
                    f"  4. Integrity: Is there any section that might be misrepresented as your "
                    f"     own work when it is not?\n\n"
                    f"Recommended actions before submitting {topic}:\n"
                    f"  1. Complete the originality checklist above and address any unchecked items\n"
                    f"  2. Run through your institution's approved similarity tool (Turnitin / iThenticate)\n"
                    f"  3. Review and update your reference list for completeness\n"
                    f"  4. Add an AI disclosure statement if applicable\n"
                    f"  5. Book a meeting with your instructor if any items are unclear\n\n"
                    f"If your similarity score is >15%: Review flagged sections and paraphrase / cite properly.\n"
                    f"If your similarity score is >30%: Major revision required before submission."
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
