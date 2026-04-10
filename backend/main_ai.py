"""Main AI Controller – orchestrates the document generation pipeline."""

from __future__ import annotations

from document_ai import DocumentAI
from export_utils import export_pdf, export_docx, export_pptx, export_xlsx


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
            title     – document title string
            body      – plain-text preview of the document
            sections  – list of {heading, content} dicts
            pdf_path  – absolute path to the generated PDF file (always present)
            docx_path – absolute path to the generated DOCX file (doc/pdf)
            pptx_path – absolute path to the generated PPTX file (slides only)
            xlsx_path – absolute path to the generated XLSX file (excel only)
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        # 1. Generate content
        result = self._doc_ai.generate(prompt.strip(), doc_type=doc_type)

        title    = result["title"]
        sections = result["sections"]
        output   = {
            "title":    title,
            "body":     result["body"],
            "sections": sections,
        }

        # 2. Export based on requested format
        normalized = doc_type.lower()

        if normalized == "slides":
            output["pptx_path"] = export_pptx(title, sections)
            output["pdf_path"]  = export_pdf(title, sections)
        elif normalized == "excel":
            output["xlsx_path"] = export_xlsx(title, sections)
            output["pdf_path"]  = export_pdf(title, sections)
        else:
            # "doc", "pdf", "document" – always produce both DOCX and PDF
            output["pdf_path"]  = export_pdf(title, sections)
            output["docx_path"] = export_docx(title, sections)

        return output
