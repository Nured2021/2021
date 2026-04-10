"""Main AI Controller – orchestrates the document generation pipeline."""

from __future__ import annotations

from document_ai import DocumentAI
from export_utils import export_pdf, export_docx


class MainAI:
    """Top-level controller that receives a user request and coordinates
    the DocumentAI and export utilities to produce downloadable files."""

    def __init__(self) -> None:
        self._doc_ai = DocumentAI()

    def run(self, prompt: str, doc_type: str = "document") -> dict:
        """Process *prompt* and return generation result with export paths.

        Returns
        -------
        dict with keys:
            title   – document title string
            body    – plain-text preview of the document
            sections – list of {heading, content} dicts
            pdf_path – absolute path to the generated PDF file
            docx_path – absolute path to the generated DOCX file
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        # 1. Generate content
        result = self._doc_ai.generate(prompt.strip(), doc_type=doc_type)

        # 2. Export to PDF and DOCX
        pdf_path = export_pdf(result["title"], result["sections"])
        docx_path = export_docx(result["title"], result["sections"])

        return {
            "title": result["title"],
            "body": result["body"],
            "sections": result["sections"],
            "pdf_path": pdf_path,
            "docx_path": docx_path,
        }
