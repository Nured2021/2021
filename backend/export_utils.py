"""Export utilities – convert structured content to PDF and DOCX."""

from __future__ import annotations

import os
import tempfile
import uuid

from docx import Document as DocxDocument
from docx.shared import Pt, RGBColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


_EXPORT_DIR = os.path.join(tempfile.gettempdir(), "docgen_exports")
os.makedirs(_EXPORT_DIR, exist_ok=True)


def _unique_path(ext: str) -> str:
    return os.path.join(_EXPORT_DIR, f"{uuid.uuid4().hex}.{ext}")


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

def export_pdf(title: str, sections: list[dict]) -> str:
    path = _unique_path("pdf")
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=18,
        textColor=(0.1, 0.1, 0.5),
    )
    heading_style = ParagraphStyle(
        "DocHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=14,
        spaceAfter=6,
        textColor=(0.15, 0.15, 0.4),
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        spaceAfter=6,
    )

    story = [Paragraph(title, title_style)]

    for sec in sections:
        story.append(Paragraph(sec["heading"], heading_style))
        for line in sec["content"].splitlines():
            line = line.strip()
            if line:
                story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 0.3 * cm))

    doc.build(story)
    return path


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------

def export_docx(title: str, sections: list[dict]) -> str:
    path = _unique_path("docx")
    doc = DocxDocument()

    # Title
    title_para = doc.add_heading(title, level=0)
    title_para.runs[0].font.color.rgb = RGBColor(0x1A, 0x1A, 0x7A)

    for sec in sections:
        h = doc.add_heading(sec["heading"], level=1)
        h.runs[0].font.color.rgb = RGBColor(0x26, 0x26, 0x66)
        for line in sec["content"].splitlines():
            if line.strip():
                p = doc.add_paragraph(line.strip())
                p.runs[0].font.size = Pt(11)

        doc.add_paragraph("")  # spacing

    doc.save(path)
    return path
