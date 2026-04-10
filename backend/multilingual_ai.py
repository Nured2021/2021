"""Multilingual AI – translation, localisation, multilingual academic content."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords

SUPPORTED_LANGUAGES = [
    "English", "Arabic", "French", "Spanish", "German",
    "Mandarin Chinese", "Portuguese", "Italian", "Japanese", "Swahili",
]

# Sample phrase library for common academic/legal/business terms (illustrative)
_PHRASE_BANK: dict[str, dict[str, str]] = {
    "French": {
        "introduction": "Introduction",
        "conclusion": "Conclusion",
        "academic integrity": "intégrité académique",
        "legal analysis": "analyse juridique",
        "business proposal": "proposition commerciale",
        "executive summary": "résumé exécutif",
        "recommendations": "recommandations",
        "lesson plan": "plan de cours",
        "study guide": "guide d'étude",
        "examination": "examen",
    },
    "Spanish": {
        "introduction": "Introducción",
        "conclusion": "Conclusión",
        "academic integrity": "integridad académica",
        "legal analysis": "análisis jurídico",
        "business proposal": "propuesta comercial",
        "executive summary": "resumen ejecutivo",
        "recommendations": "recomendaciones",
        "lesson plan": "plan de clase",
        "study guide": "guía de estudio",
        "examination": "examen",
    },
    "Arabic": {
        "introduction": "مقدمة",
        "conclusion": "خاتمة",
        "academic integrity": "النزاهة الأكاديمية",
        "legal analysis": "التحليل القانوني",
        "business proposal": "مقترح تجاري",
        "executive summary": "الملخص التنفيذي",
        "recommendations": "التوصيات",
        "lesson plan": "خطة الدرس",
        "study guide": "دليل الدراسة",
        "examination": "امتحان",
    },
    "German": {
        "introduction": "Einleitung",
        "conclusion": "Schlussfolgerung",
        "academic integrity": "akademische Integrität",
        "legal analysis": "Rechtsanalyse",
        "business proposal": "Geschäftsvorschlag",
        "executive summary": "Zusammenfassung",
        "recommendations": "Empfehlungen",
        "lesson plan": "Unterrichtsplan",
        "study guide": "Lernleitfaden",
        "examination": "Prüfung",
    },
}


def _detect_target_language(prompt: str) -> str:
    lower = prompt.lower()
    if any(w in lower for w in ["french", "français", "en français"]):
        return "French"
    if any(w in lower for w in ["spanish", "español", "en español"]):
        return "Spanish"
    if any(w in lower for w in ["arabic", "عربي", "into arabic"]):
        return "Arabic"
    if any(w in lower for w in ["german", "deutsch", "auf deutsch"]):
        return "German"
    if any(w in lower for w in ["chinese", "mandarin", "普通话"]):
        return "Mandarin Chinese"
    if any(w in lower for w in ["portuguese", "português"]):
        return "Portuguese"
    if any(w in lower for w in ["italian", "italiano"]):
        return "Italian"
    if any(w in lower for w in ["japanese", "日本語"]):
        return "Japanese"
    if any(w in lower for w in ["swahili", "kiswahili"]):
        return "Swahili"
    return "French"  # default when no language specified but translate requested


class MultilingualAI:
    """Generates multilingual content, translation guides, and localisation packages."""

    def generate(self, prompt: str, target_language: str = "") -> dict:
        topic = extract_topic(prompt)
        keywords = extract_keywords(prompt, max_kw=5)
        kw_str = ", ".join(keywords) if keywords else topic.lower()

        if not target_language:
            target_language = _detect_target_language(prompt)

        # Look up any known translations for the keywords
        lang_phrases = _PHRASE_BANK.get(target_language, {})
        translated_terms = []
        for kw in keywords[:5]:
            translation = lang_phrases.get(kw.lower(), f"[{kw} in {target_language}]")
            translated_terms.append((kw.title(), translation))

        is_rtl = target_language in ("Arabic",)
        rtl_note = "⚠ Right-to-left layout required. Use RTL text direction in your document." if is_rtl else ""

        title = f"Translation & Localisation: {topic} → {target_language}"
        sections = [
            {
                "heading": "Translation Request",
                "content": (
                    f"Source content: {topic}\n"
                    f"Key concepts: {kw_str}\n"
                    f"Target language: {target_language}\n"
                    f"Document type: {self._detect_doc_type(prompt)}\n\n"
                    f"This document provides a structured translation framework for {topic.lower()} "
                    f"into {target_language}. Professional translation of the full content is "
                    f"recommended before distribution to ensure accuracy of specialised terminology.\n"
                    f"{rtl_note}"
                ),
            },
            {
                "heading": f"Translated Content ({target_language})",
                "content": (
                    f"TRANSLATED VERSION — {topic} — {target_language.upper()}\n\n"
                    f"{'مهم: هذا النص يُقرأ من اليمين إلى اليسار' if is_rtl else ''}\n\n"
                    f"[Section 1 — Introduction]\n"
                    f"  {lang_phrases.get('introduction', 'Introduction')}: "
                    f"  [Full translation of your introduction text about {topic.lower()} here]\n\n"
                    f"[Section 2 — Main Content]\n"
                    f"  [Full translation of core content covering {kw_str}]\n\n"
                    f"[Section 3 — {lang_phrases.get('recommendations', 'Recommendations')}]\n"
                    f"  [Full translation of recommendations]\n\n"
                    f"[Section 4 — {lang_phrases.get('conclusion', 'Conclusion')}]\n"
                    f"  [Full translation of conclusion]\n\n"
                    f"To generate a complete translation, connect a translation API (DeepL, "
                    f"Google Translate, or OpenAI) and pass the source text through this pipeline."
                ),
            },
            {
                "heading": "Bilingual Glossary",
                "content": (
                    f"Key Terms: English → {target_language}\n\n"
                    f"{'Term (English)':<30} | {'Translation ({})'.format(target_language)}\n"
                    f"{'-'*30}-+-{'-'*30}\n"
                    + "\n".join(
                        f"{eng:<30} | {trans}"
                        for eng, trans in translated_terms
                    )
                    + "\n\n"
                    + "\n".join(
                        f"{eng:<30} | {trans}"
                        for eng, trans in lang_phrases.items()
                        if eng not in [t[0].lower() for t in translated_terms]
                    )[:500]
                ),
            },
            {
                "heading": "Localisation Notes",
                "content": (
                    f"Localisation checklist for {target_language}:\n\n"
                    f"  □ Date format: {self._date_format(target_language)}\n"
                    f"  □ Number format: {self._number_format(target_language)}\n"
                    f"  □ Currency: {self._currency(target_language)}\n"
                    f"  □ Text direction: {'Right-to-Left (RTL)' if is_rtl else 'Left-to-Right (LTR)'}\n"
                    f"  □ Formal register: Use formal/polite form (e.g., 'vous' not 'tu' in French)\n"
                    f"  □ Specialised terms in {topic.lower()} must be verified by a subject-matter expert\n"
                    f"  □ Legal / regulatory terminology requires qualified local review\n"
                    f"  □ Cultural references adapted (not literally translated)\n"
                    f"  □ Fonts support {target_language} character set"
                ),
            },
            {
                "heading": "Supported Languages",
                "content": (
                    f"Easy AI Language Module supports:\n\n"
                    + "\n".join(f"  • {lang}" for lang in SUPPORTED_LANGUAGES)
                    + f"\n\nCurrently translating: {target_language}\n\n"
                    f"To translate into a different language, include the target language name "
                    f"in your prompt. Example: 'Translate this document about {topic.lower()} into Spanish'"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    @staticmethod
    def _detect_doc_type(prompt: str) -> str:
        lower = prompt.lower()
        if any(w in lower for w in ["legal", "court", "contract"]): return "Legal Document"
        if any(w in lower for w in ["academic", "essay", "paper"]): return "Academic Paper"
        if any(w in lower for w in ["business", "proposal"]): return "Business Document"
        return "General Document"

    @staticmethod
    def _date_format(lang: str) -> str:
        fmts = {"French": "DD/MM/YYYY", "Spanish": "DD/MM/AAAA", "German": "DD.MM.YYYY",
                "Arabic": "DD/MM/YYYY (Hijri calendar may also apply)", "Mandarin Chinese": "YYYY年MM月DD日"}
        return fmts.get(lang, "DD/MM/YYYY")

    @staticmethod
    def _number_format(lang: str) -> str:
        fmts = {"French": "1 000,00 (space thousands, comma decimal)",
                "Spanish": "1.000,00 (period thousands, comma decimal)",
                "German": "1.000,00 (period thousands, comma decimal)"}
        return fmts.get(lang, "1,000.00 (comma thousands, period decimal)")

    @staticmethod
    def _currency(lang: str) -> str:
        curr = {"French": "EUR (€)", "Spanish": "EUR (€) or local currency", "German": "EUR (€)",
                "Arabic": "Local currency (SAR, AED, etc.)", "Mandarin Chinese": "CNY (¥)",
                "Portuguese": "EUR (€) or BRL (R$)", "Japanese": "JPY (¥)"}
        return curr.get(lang, "Confirm with local team")


def _sections_to_text(title: str, sections: list[dict]) -> str:
    lines = [title, "=" * len(title), ""]
    for sec in sections:
        lines.append(sec["heading"])
        lines.append("-" * len(sec["heading"]))
        lines.append(sec["content"])
        lines.append("")
    return "\n".join(lines)
