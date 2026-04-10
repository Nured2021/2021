"""Multilingual AI – translation, localisation, multilingual academic content."""

from __future__ import annotations

SUPPORTED_LANGUAGES = [
    "English", "Arabic", "French", "Spanish", "German",
    "Mandarin Chinese", "Portuguese", "Swahili",
]


class MultilingualAI:
    """Generates multilingual academic content and translation guidance."""

    def generate(self, prompt: str, target_language: str = "English") -> dict:
        title = f"Multilingual Content: {prompt[:60]}"
        sections = [
            {
                "heading": "Source Content",
                "content": (
                    f"Original request: {prompt}\n"
                    f"Target language: {target_language}\n\n"
                    "The following content has been prepared with multilingual delivery "
                    "in mind. Full machine or human translation should be applied before "
                    "distribution to target audiences."
                ),
            },
            {
                "heading": "Translated / Localised Content",
                "content": (
                    f"[Content in {target_language} would appear here after translation.]\n\n"
                    "Note: This stub provides the structural template. Connect a translation "
                    "API (e.g. DeepL, Google Translate) or a professional translator to "
                    "populate this section with accurate target-language text."
                ),
            },
            {
                "heading": "Localisation Notes",
                "content": (
                    f"Key localisation considerations for {target_language}:\n"
                    "• Date and number formats may differ from the source locale.\n"
                    "• Idiomatic expressions should be culturally adapted, not literally "
                    "translated.\n"
                    "• Formal register is recommended for all academic content.\n"
                    "• Right-to-left layout required for Arabic and similar scripts.\n"
                    "• Legal and regulatory terminology should be verified by a qualified "
                    "local expert."
                ),
            },
            {
                "heading": "Multilingual Glossary",
                "content": (
                    "Term (English)         | Translation Placeholder\n"
                    "-----------------------|------------------------\n"
                    "Academic integrity     | [Target language term]\n"
                    "Assessment criteria    | [Target language term]\n"
                    "Learning outcomes      | [Target language term]\n"
                    "Peer review            | [Target language term]\n"
                    "Plagiarism             | [Target language term]"
                ),
            },
            {
                "heading": "Supported Languages",
                "content": (
                    "Currently supported language list:\n"
                    + "\n".join(f"• {lang}" for lang in SUPPORTED_LANGUAGES)
                    + "\n\nAdditional languages can be added by extending the translation "
                    "integration layer."
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
