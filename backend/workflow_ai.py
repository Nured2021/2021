"""Workflow AI — one-click cross-module automations (slides from doc, excel from doc, etc.)."""

from __future__ import annotations

from main_ai import MainAI

_brain = MainAI()


WORKFLOWS = {
    "to_slides": {
        "label": "Generate Slides",
        "icon":  "📽️",
        "description": "Convert this document into a professional slide presentation",
    },
    "to_excel": {
        "label": "Extract to Excel",
        "icon":  "📊",
        "description": "Extract all data and tables into a structured spreadsheet",
    },
    "translate": {
        "label": "Translate Document",
        "icon":  "🌐",
        "description": "Translate this document into another language",
    },
    "check_integrity": {
        "label": "Check Integrity",
        "icon":  "🛡️",
        "description": "Review this document for originality and citation issues",
    },
    "study_guide": {
        "label": "Create Study Guide",
        "icon":  "📚",
        "description": "Convert this content into a student study guide with flashcards",
    },
    "to_business_plan": {
        "label": "Build Business Plan",
        "icon":  "🏢",
        "description": "Expand this content into a full business plan",
    },
    "check_legal": {
        "label": "Legal Review",
        "icon":  "⚖️",
        "description": "Review this document for legal issues and suggest improvements",
    },
    "to_course": {
        "label": "Build Course",
        "icon":  "🏫",
        "description": "Convert this content into a structured course curriculum",
    },
}


def run_workflow(action: str, source_content: str, source_title: str,
                 extra_params: dict | None = None) -> dict:
    """Execute a cross-module workflow on source content.

    Parameters
    ----------
    action         : workflow key from WORKFLOWS dict
    source_content : the body text of the source document
    source_title   : title of the source document
    extra_params   : optional extra parameters (e.g. target_language for translate)
    """
    params = extra_params or {}
    short  = source_content[:3000]  # Truncate for prompt

    if action == "to_slides":
        prompt = (
            f"Convert the following document into a compelling professional slide presentation. "
            f"Create 6–8 slides with clear headings, concise bullet points, and speaker notes.\n\n"
            f"Document title: {source_title}\n\n{short}"
        )
        return _brain.run(prompt, module_hint="slides")

    elif action == "to_excel":
        prompt = (
            f"Extract all data, tables, numbers, metrics, timelines, and structured information "
            f"from the following document and organise them into a spreadsheet with multiple sheets, "
            f"appropriate column headers, and SUM/AVERAGE formulas where relevant.\n\n"
            f"Document title: {source_title}\n\n{short}"
        )
        return _brain.run(prompt, module_hint="excel")

    elif action == "translate":
        lang = params.get("language", "Spanish")
        prompt = (
            f"Translate the following document into {lang}. "
            f"Preserve all headings, bullet points, and formatting. "
            f"Also provide a bilingual glossary of key terms.\n\n"
            f"Document title: {source_title}\n\n{short}"
        )
        return _brain.run(prompt, module_hint="multilingual")

    elif action == "check_integrity":
        prompt = (
            f"Perform a comprehensive academic integrity review of the following document. "
            f"Check for citation completeness, potential plagiarism indicators, bias, "
            f"factual inconsistencies, and provide a corrected version with proper citations.\n\n"
            f"Document title: {source_title}\n\n{short}"
        )
        return _brain.run(prompt, module_hint="integrity")

    elif action == "study_guide":
        prompt = (
            f"Convert the following content into a comprehensive student study guide. "
            f"Include: summary, key terms and definitions, flashcard questions and answers, "
            f"practice questions, and a revision checklist.\n\n"
            f"Document title: {source_title}\n\n{short}"
        )
        return _brain.run(prompt, module_hint="student")

    elif action == "to_business_plan":
        prompt = (
            f"Expand the following content into a comprehensive business plan with "
            f"executive summary, market analysis, financial projections, and SWOT analysis.\n\n"
            f"Based on: {source_title}\n\n{short}"
        )
        return _brain.run(prompt, module_hint="business")

    elif action == "check_legal":
        prompt = (
            f"Review the following document for legal issues, contractual risks, compliance gaps, "
            f"and suggest improvements with proper legal language.\n\n"
            f"Document title: {source_title}\n\n{short}"
        )
        return _brain.run(prompt, module_hint="court")

    elif action == "to_course":
        prompt = (
            f"Convert the following content into a structured educational course curriculum "
            f"with modules, learning objectives, weekly schedule, assessments, and reading list.\n\n"
            f"Based on: {source_title}\n\n{short}"
        )
        return _brain.run(prompt, module_hint="course")

    else:
        raise ValueError(f"Unknown workflow action: '{action}'")
