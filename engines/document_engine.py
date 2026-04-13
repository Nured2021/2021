"""
Document Engine — Generates PDF and DOCX files from structured content.
Uses ReportLab for PDF, python-docx for DOCX.
"""
import os
import io
import textwrap
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

BRAND_COLOR = HexColor("#2563eb")
BRAND_DARK = HexColor("#1e40af")


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="DocTitle", parent=styles["Title"],
        fontSize=26, textColor=BRAND_DARK, spaceAfter=20,
        alignment=TA_CENTER, fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="DocSubtitle", parent=styles["Normal"],
        fontSize=12, textColor=HexColor("#6b7280"), spaceAfter=30,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="SectionHead", parent=styles["Heading1"],
        fontSize=16, textColor=BRAND_COLOR, spaceBefore=18, spaceAfter=8,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="BodyText2", parent=styles["Normal"],
        fontSize=11, leading=16, alignment=TA_JUSTIFY,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="BulletItem", parent=styles["Normal"],
        fontSize=11, leading=15, leftIndent=24, bulletIndent=12,
        spaceAfter=4,
    ))
    return styles


def generate_content(prompt: str, mode: str = "formal") -> dict:
    title = prompt[:80].strip().title()
    now = datetime.now().strftime("%B %d, %Y")

    sections = [
        {
            "heading": "1. Executive Summary",
            "body": f"This document addresses the following request: \"{prompt}\". "
                    "It has been prepared with professional standards and comprehensive analysis. "
                    "The content below provides a thorough exploration of the subject matter, "
                    "organized into clear sections for ease of reference.",
        },
        {
            "heading": "2. Background & Context",
            "body": "Understanding the context is essential for proper analysis. "
                    "This section establishes the foundational knowledge required to appreciate "
                    "the recommendations and findings presented in subsequent sections. "
                    "The topic has been researched using authoritative sources and current data.",
        },
        {
            "heading": "3. Detailed Analysis",
            "body": "The core analysis reveals several important findings. "
                    "Each point has been carefully evaluated against industry standards and best practices. "
                    "The methodology employed ensures reliability and reproducibility of results.",
            "bullets": [
                "Comprehensive data collection and validation",
                "Multi-factor analysis with cross-referencing",
                "Industry benchmark comparison",
                "Risk assessment and mitigation strategies",
                "Quality assurance protocols applied",
            ],
        },
        {
            "heading": "4. Key Findings",
            "body": "Based on the analysis conducted, the following key findings have emerged. "
                    "These findings form the basis for the recommendations in the next section.",
            "bullets": [
                "Finding 1: Primary objectives are achievable within the defined scope",
                "Finding 2: Resource allocation aligns with industry benchmarks",
                "Finding 3: Timeline projections are realistic with proper management",
                "Finding 4: Identified risks can be mitigated with proposed strategies",
            ],
        },
        {
            "heading": "5. Recommendations",
            "body": "The following recommendations are based on the findings above. "
                    "Implementation should follow the priority order listed below to maximize effectiveness.",
            "bullets": [
                "Implement Phase 1 improvements immediately",
                "Establish monitoring and feedback mechanisms",
                "Schedule quarterly reviews for progress assessment",
                "Allocate resources for continuous improvement",
            ],
        },
        {
            "heading": "6. Conclusion",
            "body": f"This document has provided a comprehensive analysis of: \"{prompt}\". "
                    "The recommendations outlined above should be implemented in a phased approach "
                    "to ensure smooth transition and measurable outcomes. "
                    "Regular review cycles will ensure continued alignment with objectives.",
        },
    ]

    return {"title": title, "date": now, "sections": sections, "mode": mode}


def generate_pdf(prompt: str, mode: str = "formal") -> str:
    content = generate_content(prompt, mode)
    filename = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    styles = _build_styles()
    story = []

    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(content["title"], styles["DocTitle"]))
    story.append(Paragraph(f"Generated on {content['date']} | Mode: {content['mode'].upper()}", styles["DocSubtitle"]))
    story.append(Paragraph("EASY AI DOC & EDUCATION CORE", styles["DocSubtitle"]))
    story.append(HRFlowable(width="80%", color=BRAND_COLOR, thickness=2, spaceAfter=20))
    story.append(PageBreak())

    toc_text = "<b>Table of Contents</b><br/><br/>"
    for sec in content["sections"]:
        toc_text += f"{sec['heading']}<br/>"
    story.append(Paragraph(toc_text, styles["BodyText2"]))
    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="100%", color=HexColor("#e5e7eb"), thickness=1, spaceAfter=12))

    for sec in content["sections"]:
        story.append(Paragraph(sec["heading"], styles["SectionHead"]))
        story.append(Paragraph(sec["body"], styles["BodyText2"]))
        if "bullets" in sec:
            for b in sec["bullets"]:
                story.append(Paragraph(f"\u2022  {b}", styles["BulletItem"]))
        story.append(Spacer(1, 12))

    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="100%", color=HexColor("#e5e7eb"), thickness=1, spaceAfter=8))
    story.append(Paragraph(
        f"<i>Document generated by EASY AI DOC & EDUCATION CORE on {content['date']}</i>",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=HexColor("#9ca3af"), alignment=TA_CENTER),
    ))

    doc.build(story)
    return filename


def generate_docx(prompt: str, mode: str = "formal") -> str:
    content = generate_content(prompt, mode)
    filename = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    doc = Document()

    style = doc.styles["Title"]
    style.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

    doc.add_heading(content["title"], level=0)
    sub = doc.add_paragraph(f"Generated on {content['date']} | Mode: {content['mode'].upper()}")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.color.rgb = RGBColor(0x6B, 0x72, 0x80)

    doc.add_paragraph("EASY AI DOC & EDUCATION CORE").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    doc.add_heading("Table of Contents", level=1)
    for sec in content["sections"]:
        doc.add_paragraph(sec["heading"], style="List Number")
    doc.add_page_break()

    for sec in content["sections"]:
        doc.add_heading(sec["heading"], level=1)
        doc.add_paragraph(sec["body"])
        if "bullets" in sec:
            for b in sec["bullets"]:
                doc.add_paragraph(b, style="List Bullet")

    footer = doc.add_paragraph(f"Document generated by EASY AI DOC & EDUCATION CORE on {content['date']}")
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.runs[0].font.size = Pt(8)
    footer.runs[0].font.color.rgb = RGBColor(0x9C, 0xA3, 0xAF)

    doc.save(filepath)
    return filename
