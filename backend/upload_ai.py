"""Upload AI – reads, extracts, and summarises uploaded file content."""

from __future__ import annotations

import re

from prompt_parser import extract_keywords, detect_domain


class UploadAI:
    """Reads text extracted from uploaded files and generates structured summaries."""

    def summarise(self, text: str, filename: str = "uploaded file") -> dict:
        """Generate a structured 3-section summary from raw extracted text.

        Parameters
        ----------
        text:     Raw text content extracted from the file.
        filename: Original filename (used for context labelling).
        """
        if not text or not text.strip():
            return self._empty_summary(filename)

        cleaned = self._clean_text(text)
        keywords = extract_keywords(cleaned, max_kw=8)
        domain = detect_domain(cleaned)
        kw_str = ", ".join(keywords) if keywords else "general content"

        # Sentence-level analysis
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', cleaned) if len(s.strip()) > 30]
        total_sentences = len(sentences)
        total_words = len(cleaned.split())
        total_chars = len(cleaned)

        # Extract likely key points (sentences with keywords)
        key_sentences = [s for s in sentences if any(kw in s.lower() for kw in keywords)][:5]
        if not key_sentences:
            key_sentences = sentences[:5]

        title = f"File Summary: {filename}"
        sections = [
            {
                "heading": "Document Overview",
                "content": (
                    f"File: {filename}\n"
                    f"Domain: {domain.title()}\n"
                    f"Content length: ~{total_words:,} words / {total_sentences} sentences\n"
                    f"Core topics: {kw_str}\n\n"
                    f"PARAGRAPH 1 — WHAT THIS DOCUMENT IS ABOUT:\n"
                    f"This document covers topics related to {kw_str}. "
                    f"{'The content is structured and detailed, indicating a formal document.' if total_words > 500 else 'The content is brief and focused.'} "
                    f"The primary domain appears to be {domain.title()}, based on the terminology and context used throughout the text. "
                    f"{'Key sections address multiple aspects of the topic in depth.' if total_sentences > 20 else 'The document focuses on a specific, targeted subject.'}"
                ),
            },
            {
                "heading": "Key Points Extracted",
                "content": (
                    f"PARAGRAPH 2 — MAIN CONTENT EXTRACTED:\n"
                    f"The most significant points from this document are:\n\n"
                    + "\n".join(
                        f"  • {sent.strip()[:200]}{'...' if len(sent.strip()) > 200 else '.'}"
                        for sent in key_sentences
                    )
                    + f"\n\nKey terms and concepts identified: {kw_str}\n\n"
                    f"These points represent the core substance of '{filename}' as determined by "
                    f"semantic density and keyword frequency analysis."
                ),
            },
            {
                "heading": "Summary & Suggested Next Steps",
                "content": (
                    f"PARAGRAPH 3 — SUMMARY & ACTIONS:\n"
                    f"In summary, '{filename}' addresses {kw_str}. "
                    f"The document {'provides detailed guidance' if total_words > 1000 else 'offers a concise overview'} "
                    f"on {domain.title()} topics.\n\n"
                    f"Based on the content of this file, suggested next steps:\n\n"
                    f"  1. Generate a document — Use the Document AI to expand on {kw_str.split(',')[0].strip() if keywords else 'this topic'}\n"
                    f"  2. Create a presentation — Have Slides AI turn these key points into a deck\n"
                    f"  3. Build a study guide — Student AI can create flashcards and self-test questions\n"
                    f"  4. Draft a report — Business AI or Research AI can build on these findings\n"
                    f"  5. Translate — Multilingual AI can convert this summary to another language\n\n"
                    f"Click any tool in the sidebar and say "
                    f"'Use the uploaded file about {kw_str.split(',')[0].strip() if keywords else 'this topic'}' "
                    f"to continue working with this content."
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {
            "title": title,
            "sections": sections,
            "body": body,
            "keywords": keywords,
            "domain": domain,
            "word_count": total_words,
            "module": "upload",
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove excessive whitespace and non-printable characters."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
        return text.strip()[:8000]  # cap at 8k chars for processing

    @staticmethod
    def _empty_summary(filename: str) -> dict:
        title = f"Upload Notice: {filename}"
        sections = [
            {
                "heading": "No Content Extracted",
                "content": (
                    f"The file '{filename}' was uploaded but no readable text content could be extracted.\n\n"
                    f"This may occur if:\n"
                    f"  • The file is a scanned image (no OCR layer)\n"
                    f"  • The file is password-protected or encrypted\n"
                    f"  • The file format is not supported for text extraction\n\n"
                    f"Supported formats for automatic extraction: .txt, .md, .csv, .json\n"
                    f"For PDF/DOCX: Text-based (not scanned) documents work best.\n\n"
                    f"What to do:\n"
                    f"  1. Try copying the text from the file and pasting it into the prompt box\n"
                    f"  2. Use a PDF-to-text converter before uploading\n"
                    f"  3. Type a description of the file content directly in the prompt"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body, "keywords": [], "domain": "general", "word_count": 0, "module": "upload"}


def _sections_to_text(title: str, sections: list[dict]) -> str:
    lines = [title, "=" * len(title), ""]
    for sec in sections:
        lines.append(sec["heading"])
        lines.append("-" * len(sec["heading"]))
        lines.append(sec["content"])
        lines.append("")
    return "\n".join(lines)
