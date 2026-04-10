"""Export utilities – convert structured content to PDF, DOCX, PPTX and XLSX."""

from __future__ import annotations

import os
import re
import tempfile
import uuid

from docx import Document as DocxDocument
from docx.shared import Pt, RGBColor, Cm, Inches
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


_EXPORT_DIR = os.path.join(tempfile.gettempdir(), "docgen_exports")
os.makedirs(_EXPORT_DIR, exist_ok=True)

# Accent colours (RGB tuples for ReportLab, RGB ints for python-docx)
_BRAND_BLUE   = (0x1A / 255, 0x1A / 255, 0x7A / 255)
_BRAND_TEAL   = (0x00 / 255, 0x7B / 255, 0x8A / 255)
_DOCX_BLUE    = RGBColor(0x1A, 0x1A, 0x7A)
_DOCX_TEAL    = RGBColor(0x00, 0x7B, 0x8A)


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

    title_style = ParagraphStyle("DocTitle",    parent=styles["Title"],   fontSize=20, spaceAfter=18, textColor=_BRAND_BLUE)
    head_style  = ParagraphStyle("DocHeading",  parent=styles["Heading2"],fontSize=13, spaceBefore=14, spaceAfter=6, textColor=_BRAND_TEAL)
    body_style  = ParagraphStyle("DocBody",     parent=styles["Normal"],  fontSize=10, leading=15, spaceAfter=6)
    bullet_style= ParagraphStyle("DocBullet",   parent=styles["Normal"],  fontSize=10, leading=15, spaceAfter=4, leftIndent=16)

    story = [Paragraph(title.replace("<","&lt;").replace(">","&gt;"), title_style)]

    for sec in sections:
        story.append(Paragraph(sec["heading"].replace("<","&lt;"), head_style))
        for line in sec["content"].splitlines():
            line = line.strip()
            if not line:
                continue
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if line.startswith(("•", "-", "✓", "✗", "△", "□", "✅", "❌", "⚠")):
                story.append(Paragraph(safe, bullet_style))
            else:
                story.append(Paragraph(safe, body_style))
        story.append(Spacer(1, 0.3 * cm))

    doc.build(story)
    return path


# ---------------------------------------------------------------------------
# DOCX (professional layout with heading styles and table support)
# ---------------------------------------------------------------------------

def export_docx(title: str, sections: list[dict]) -> str:
    path = _unique_path("docx")
    doc = DocxDocument()

    # Page margins
    for section in doc.sections:
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

    # Title
    title_para = doc.add_heading(title, level=0)
    if title_para.runs:
        title_para.runs[0].font.color.rgb = _DOCX_BLUE
        title_para.runs[0].font.size = Pt(22)

    for sec in sections:
        h = doc.add_heading(sec["heading"], level=1)
        if h.runs:
            h.runs[0].font.color.rgb = _DOCX_TEAL
            h.runs[0].font.size = Pt(13)

        # Detect pipe-table rows and render as a DOCX table
        table_rows = _extract_table_rows(sec["content"])
        if table_rows:
            _add_docx_table(doc, table_rows)
        else:
            for line in sec["content"].splitlines():
                line_s = line.strip()
                if not line_s:
                    continue
                p = doc.add_paragraph()
                if line_s.startswith(("•", "-", "✓", "✗", "△", "□")):
                    p.style = doc.styles["List Bullet"]
                    p.add_run(line_s.lstrip("•- "))
                else:
                    run = p.add_run(line_s)
                    run.font.size = Pt(11)

        doc.add_paragraph("")

    doc.save(path)
    return path


def _extract_table_rows(content: str) -> list[list[str]]:
    """Parse pipe-delimited table rows from content text, return list of row lists."""
    rows = []
    for line in content.splitlines():
        stripped = line.strip()
        if "|" in stripped and not re.match(r"^[-| ]+$", stripped):
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if cells:
                rows.append(cells)
    return rows if len(rows) >= 2 else []


def _add_docx_table(doc: DocxDocument, rows: list[list[str]]) -> None:
    """Add a formatted DOCX table from a list of row lists."""
    if not rows:
        return
    max_cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=max_cols)
    table.style = "Table Grid"
    for r_idx, row in enumerate(rows):
        for c_idx, cell_text in enumerate(row):
            if c_idx < max_cols:
                cell = table.cell(r_idx, c_idx)
                cell.text = cell_text
                if r_idx == 0:
                    cell.paragraphs[0].runs[0].bold = True


# ---------------------------------------------------------------------------
# PPTX (professional multi-layout presentation with speaker notes)
# ---------------------------------------------------------------------------

_PPTX_COLORS = {
    "title_bg":   "1A1A7A",  # deep navy
    "accent":     "007B8A",  # teal
    "white":      "FFFFFF",
    "light_gray": "F5F5F5",
    "dark_text":  "1A1A2E",
}


def export_pptx(title: str, sections: list[dict]) -> str:
    from pptx import Presentation
    from pptx.util import Inches, Pt as PPt, Emu
    from pptx.dml.color import RGBColor as PPTRgb
    from pptx.enum.text import PP_ALIGN

    path = _unique_path("pptx")
    prs = Presentation()

    # Use widescreen 16:9
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)

    def hex_to_rgb(h: str) -> PPTRgb:
        return PPTRgb(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def set_tf_color(tf, hex_color: str) -> None:
        for para in tf.paragraphs:
            for run in para.runs:
                run.font.color.rgb = hex_to_rgb(hex_color)

    # --- Title slide (layout 0) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = hex_to_rgb(_PPTX_COLORS["title_bg"])

    # Title text box
    txb = slide.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.5), Inches(1.8))
    tf  = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text      = title
    p.alignment = PP_ALIGN.CENTER
    p.runs[0].font.size  = PPt(40)
    p.runs[0].font.bold  = True
    p.runs[0].font.color.rgb = hex_to_rgb(_PPTX_COLORS["white"])

    # Subtitle
    sub = slide.shapes.add_textbox(Inches(0.8), Inches(4.1), Inches(11.5), Inches(0.8))
    stf = sub.text_frame
    sp  = stf.paragraphs[0]
    sp.text      = "Generated by Easy AI  ·  " + "─" * 20
    sp.alignment = PP_ALIGN.CENTER
    sp.runs[0].font.size  = PPt(16)
    sp.runs[0].font.color.rgb = hex_to_rgb(_PPTX_COLORS["accent"])

    # --- Content slides ---
    for idx, sec in enumerate(sections):
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
        bg2 = slide.background.fill
        bg2.solid()
        bg2.fore_color.rgb = hex_to_rgb(_PPTX_COLORS["light_gray"])

        # Heading bar
        bar = slide.shapes.add_shape(
            1,  # MSO_SHAPE_TYPE.RECTANGLE
            Inches(0), Inches(0), Inches(13.33), Inches(1.2)
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_to_rgb(_PPTX_COLORS["title_bg"])
        bar.line.fill.background()

        # Heading text
        htb = slide.shapes.add_textbox(Inches(0.4), Inches(0.1), Inches(12.5), Inches(1.0))
        htf = htb.text_frame
        hp  = htf.paragraphs[0]
        hp.text = sec["heading"]
        if hp.runs:
            hp.runs[0].font.size  = PPt(24)
            hp.runs[0].font.bold  = True
            hp.runs[0].font.color.rgb = hex_to_rgb(_PPTX_COLORS["white"])

        # Slide number chip
        num_box = slide.shapes.add_textbox(Inches(12.4), Inches(0.1), Inches(0.9), Inches(0.5))
        ntf = num_box.text_frame
        np_ = ntf.paragraphs[0]
        np_.text = f"{idx + 1}"
        if np_.runs:
            np_.runs[0].font.size  = PPt(12)
            np_.runs[0].font.color.rgb = hex_to_rgb(_PPTX_COLORS["accent"])

        # Content text box
        ctb = slide.shapes.add_textbox(Inches(0.5), Inches(1.4), Inches(12.3), Inches(5.7))
        ctf = ctb.text_frame
        ctf.word_wrap = True

        first_line = True
        for line in sec["content"].splitlines():
            line_s = line.strip()
            if not line_s:
                continue
            if first_line:
                para = ctf.paragraphs[0]
                first_line = False
            else:
                para = ctf.add_paragraph()

            is_bullet = line_s.startswith(("•", "-", "✓", "✗", "△", "□", "✅", "❌", "⚠", "*"))
            if is_bullet:
                para.level = 1
                clean = line_s.lstrip("•-*✓✗△□✅❌⚠ ")
            else:
                para.level = 0
                clean = line_s

            run = para.add_run()
            run.text = clean
            run.font.size = PPt(13 if is_bullet else 14)
            run.font.color.rgb = hex_to_rgb(_PPTX_COLORS["dark_text"])
            if not is_bullet and (":" in clean or clean.isupper()):
                run.font.bold = True

        # Speaker notes
        notes_slide = slide.notes_slide
        notes_tf    = notes_slide.notes_text_frame
        notes_tf.text = f"Slide {idx + 1}: {sec['heading']}\n\n" + sec["content"][:600]

    prs.save(path)
    return path


# ---------------------------------------------------------------------------
# XLSX (real spreadsheet with formulas, multiple sheets, auto charts)
# ---------------------------------------------------------------------------

def export_xlsx(title: str, sections: list[dict]) -> str:
    from openpyxl import Workbook
    from openpyxl.styles import (
        Font, PatternFill, Alignment, Border, Side, numbers
    )
    from openpyxl.chart import BarChart, Reference
    from openpyxl.utils import get_column_letter

    path = _unique_path("xlsx")
    wb   = Workbook()

    # Colour palette
    NAVY  = "1A1A7A"
    TEAL  = "007B8A"
    WHITE = "FFFFFF"
    LIGHT = "EAF4F4"

    hdr_font  = Font(bold=True, color=WHITE, size=12)
    hdr_fill  = PatternFill("solid", fgColor=NAVY)
    sub_fill  = PatternFill("solid", fgColor=TEAL)
    alt_fill  = PatternFill("solid", fgColor=LIGHT)
    centered  = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_al   = Alignment(horizontal="left",   vertical="center", wrap_text=True)

    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ── Summary sheet ─────────────────────────────────────────────────────
    ws_sum = wb.active
    ws_sum.title = "Summary"

    ws_sum.row_dimensions[1].height = 30
    ws_sum["A1"] = title
    ws_sum["A1"].font = Font(bold=True, color=WHITE, size=14)
    ws_sum["A1"].fill = hdr_fill
    ws_sum["A1"].alignment = centered
    ws_sum.merge_cells("A1:C1")

    ws_sum["A2"] = "Section"
    ws_sum["B2"] = "Content Preview"
    ws_sum["C2"] = "Lines"
    for col in ("A2", "B2", "C2"):
        ws_sum[col].font  = Font(bold=True, color=WHITE, size=11)
        ws_sum[col].fill  = PatternFill("solid", fgColor=TEAL)
        ws_sum[col].alignment = centered

    for i, sec in enumerate(sections):
        row = i + 3
        preview = sec["content"].strip()[:120].replace("\n", " ")
        line_count = len([l for l in sec["content"].splitlines() if l.strip()])
        ws_sum.cell(row=row, column=1, value=sec["heading"]).font = Font(bold=True)
        ws_sum.cell(row=row, column=2, value=preview).alignment  = left_al
        ws_sum.cell(row=row, column=3, value=line_count)
        if i % 2 == 0:
            for c in (1, 2, 3):
                ws_sum.cell(row=row, column=c).fill = alt_fill
        for c in (1, 2, 3):
            ws_sum.cell(row=row, column=c).border = border

    # Line count chart
    if len(sections) >= 2:
        chart = BarChart()
        chart.type  = "col"
        chart.title = f"Content Volume per Section – {title[:40]}"
        chart.y_axis.title = "Lines"
        chart.x_axis.title = "Section"
        chart.style = 10
        data_ref = Reference(ws_sum, min_col=3, min_row=2, max_row=2 + len(sections))
        cats_ref = Reference(ws_sum, min_col=1, min_row=3, max_row=2 + len(sections))
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats_ref)
        chart.shape = 4
        ws_sum.add_chart(chart, "E3")

    # Auto width (Summary sheet)
    from openpyxl.cell.cell import MergedCell
    for col in ws_sum.columns:
        first_real = next((c for c in col if not isinstance(c, MergedCell)), None)
        if first_real is None:
            continue
        max_len = max((len(str(c.value)) if c.value and not isinstance(c, MergedCell) else 0) for c in col)
        ws_sum.column_dimensions[first_real.column_letter].width = min(max_len + 4, 60)

    # ── Per-section sheets ────────────────────────────────────────────────
    numeric_ws = None  # Will track a sheet suitable for formula demo

    for sec in sections:
        safe_name = re.sub(r'[\\/:*?\[\]]', '', sec["heading"])[:28] or "Sheet"
        ws = wb.create_sheet(title=safe_name)

        # Section heading row
        ws.row_dimensions[1].height = 24
        ws["A1"] = sec["heading"]
        ws["A1"].font  = hdr_font
        ws["A1"].fill  = hdr_fill
        ws["A1"].alignment = centered
        ws.merge_cells("A1:D1")

        # Try to parse pipe-table rows inside this section
        table_rows = _parse_table_from_content(sec["content"])

        if table_rows and len(table_rows) >= 2:
            # Write table with header
            header = table_rows[0]
            data   = table_rows[1:]

            for c_idx, cell_val in enumerate(header, start=1):
                cell = ws.cell(row=2, column=c_idx, value=cell_val)
                cell.font  = Font(bold=True, color=WHITE, size=11)
                cell.fill  = PatternFill("solid", fgColor=TEAL)
                cell.alignment = centered
                cell.border = border

            for r_i, row in enumerate(data, start=3):
                for c_i, val in enumerate(row, start=1):
                    cell = ws.cell(row=r_i, column=c_i, value=_coerce_value(val))
                    cell.alignment = left_al
                    cell.border    = border
                    if r_i % 2 == 1:
                        cell.fill = alt_fill

            # Add SUM formula under the last numeric column
            last_data_row = 2 + len(data)
            for c_i in range(1, len(header) + 1):
                # Check if this column has numeric values
                has_nums = any(
                    isinstance(_coerce_value(row[c_i - 1] if c_i - 1 < len(row) else ""), (int, float))
                    for row in data
                )
                if has_nums:
                    col_ltr = get_column_letter(c_i)
                    total_cell = ws.cell(row=last_data_row + 1, column=c_i,
                                         value=f"=SUM({col_ltr}3:{col_ltr}{last_data_row})")
                    total_cell.font   = Font(bold=True)
                    total_cell.fill   = PatternFill("solid", fgColor=NAVY)
                    total_cell.font   = Font(bold=True, color=WHITE)
                    total_cell.border = border
                    # Mark this sheet for chart generation
                    numeric_ws = (ws, 2, last_data_row, 1, len(header))

            # Auto width for section sheets
            from openpyxl.cell.cell import MergedCell as MC
            for col in ws.columns:
                first_real = next((c for c in col if not isinstance(c, MC)), None)
                if first_real is None:
                    continue
                max_len = max((len(str(c.value)) if c.value and not isinstance(c, MC) else 0) for c in col)
                ws.column_dimensions[first_real.column_letter].width = min(max_len + 4, 50)

        else:
            # Fallback: write raw content as wrapped text
            for r_i, line in enumerate(sec["content"].splitlines(), start=2):
                if line.strip():
                    cell = ws.cell(row=r_i, column=1, value=line.strip())
                    cell.alignment = left_al
                    if r_i % 2 == 0:
                        cell.fill = alt_fill
            ws.column_dimensions["A"].width = 80

    # Add bar chart to the first numeric sheet found
    if numeric_ws:
        ws_n, min_row, max_row, min_col, max_col = numeric_ws
        chart2 = BarChart()
        chart2.type   = "col"
        chart2.title  = f"Data Chart – {ws_n.title}"
        chart2.style  = 10
        chart2.y_axis.title = "Value"
        d_ref = Reference(ws_n, min_col=min_col + 1, max_col=max_col,
                           min_row=min_row, max_row=max_row)
        c_ref = Reference(ws_n, min_col=min_col, min_row=min_row + 1, max_row=max_row)
        chart2.add_data(d_ref, titles_from_data=True)
        chart2.set_categories(c_ref)
        ws_n.add_chart(chart2, f"{get_column_letter(max_col + 2)}{min_row}")

    # ── Formulas sheet ────────────────────────────────────────────────────
    ws_f = wb.create_sheet(title="Formulas & Stats")
    ws_f["A1"] = "Statistical Summary"
    ws_f["A1"].font  = hdr_font
    ws_f["A1"].fill  = hdr_fill
    ws_f.merge_cells("A1:C1")

    rows_info = [
        ("Metric", "Description", "Formula / Value"),
        ("Section count", "Total number of sections", len(sections)),
        ("Avg content length", "Avg chars per section",
         f"=AVERAGE({','.join(str(len(s['content'])) for s in sections)})"),
        ("Max content length", "Longest section (chars)",
         f"=MAX({','.join(str(len(s['content'])) for s in sections)})"),
        ("Min content length", "Shortest section (chars)",
         f"=MIN({','.join(str(len(s['content'])) for s in sections)})"),
        ("Total words (approx)", "Words across all content",
         sum(len(s["content"].split()) for s in sections)),
    ]
    for r_i, row in enumerate(rows_info, start=2):
        for c_i, val in enumerate(row, start=1):
            cell = ws_f.cell(row=r_i, column=c_i, value=val)
            cell.border = border
            if r_i == 2:
                cell.font = Font(bold=True, color=WHITE)
                cell.fill = PatternFill("solid", fgColor=TEAL)
            elif r_i % 2 == 1:
                cell.fill = alt_fill

    ws_f.column_dimensions["A"].width = 25
    ws_f.column_dimensions["B"].width = 35
    ws_f.column_dimensions["C"].width = 40

    wb.save(path)
    return path


def _parse_table_from_content(content: str) -> list[list[str]]:
    """Extract pipe-delimited table rows from content, skip separator rows."""
    rows = []
    for line in content.splitlines():
        stripped = line.strip()
        if "|" in stripped and not re.match(r"^[-|+ ]+$", stripped):
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if cells:
                rows.append(cells)
    return rows if len(rows) >= 2 else []


def _coerce_value(val: str):
    """Attempt to convert a string to int or float; fall back to string."""
    val = val.strip().replace(",", "").replace("$", "").replace("%", "").replace("£", "")
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        return val
