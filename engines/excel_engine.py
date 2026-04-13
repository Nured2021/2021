"""
Excel Engine — Generates XLSX spreadsheets with formatting, formulas, and charts.
"""
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

BRAND_FILL = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
LIGHT_FILL = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
WHITE_FONT = Font(color="FFFFFF", bold=True, size=11)
HEADER_FONT = Font(bold=True, size=11, color="1E40AF")
NORMAL_FONT = Font(size=10)
THIN_BORDER = Border(
    left=Side(style="thin", color="D1D5DB"),
    right=Side(style="thin", color="D1D5DB"),
    top=Side(style="thin", color="D1D5DB"),
    bottom=Side(style="thin", color="D1D5DB"),
)


def generate_financial_data(prompt: str) -> dict:
    return {
        "title": prompt[:60].strip().title(),
        "sheets": [
            {
                "name": "Summary",
                "headers": ["Category", "Q1", "Q2", "Q3", "Q4", "Total"],
                "rows": [
                    ["Revenue", 125000, 148000, 162000, 185000, "=SUM(B{r}:E{r})"],
                    ["Cost of Goods", 45000, 52000, 58000, 64000, "=SUM(B{r}:E{r})"],
                    ["Gross Profit", "=B2-B3", "=C2-C3", "=D2-D3", "=E2-E3", "=SUM(B{r}:E{r})"],
                    ["Operating Expenses", 35000, 38000, 41000, 44000, "=SUM(B{r}:E{r})"],
                    ["Marketing", 15000, 18000, 20000, 22000, "=SUM(B{r}:E{r})"],
                    ["R&D", 12000, 14000, 16000, 18000, "=SUM(B{r}:E{r})"],
                    ["Net Income", "=B4-B5-B6-B7", "=C4-C5-C6-C7", "=D4-D5-D6-D7", "=E4-E5-E6-E7", "=SUM(B{r}:E{r})"],
                ],
            },
            {
                "name": "Monthly Breakdown",
                "headers": ["Month", "Revenue", "Expenses", "Profit", "Margin %"],
                "rows": [
                    ["January", 42000, 28000, "=B2-C2", "=D2/B2*100"],
                    ["February", 38000, 26000, "=B3-C3", "=D3/B3*100"],
                    ["March", 45000, 30000, "=B4-C4", "=D4/B4*100"],
                    ["April", 48000, 31000, "=B5-C5", "=D5/B5*100"],
                    ["May", 50000, 33000, "=B6-C6", "=D6/B6*100"],
                    ["June", 52000, 34000, "=B7-C7", "=D7/B7*100"],
                    ["July", 54000, 35000, "=B8-C8", "=D8/B8*100"],
                    ["August", 55000, 36000, "=B9-C9", "=D9/B9*100"],
                    ["September", 53000, 35000, "=B10-C10", "=D10/B10*100"],
                    ["October", 58000, 38000, "=B11-C11", "=D11/B11*100"],
                    ["November", 62000, 40000, "=B12-C12", "=D12/B12*100"],
                    ["December", 65000, 42000, "=B13-C13", "=D13/B13*100"],
                ],
            },
        ],
    }


def generate_xlsx(prompt: str) -> str:
    data = generate_financial_data(prompt)
    filename = f"sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    wb = Workbook()
    wb.remove(wb.active)

    for sheet_data in data["sheets"]:
        ws = wb.create_sheet(title=sheet_data["name"])

        for col_idx, header in enumerate(sheet_data["headers"], 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = WHITE_FONT
            cell.fill = BRAND_FILL
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = THIN_BORDER

        for row_idx, row_data in enumerate(sheet_data["rows"], 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                if isinstance(value, str) and value.startswith("="):
                    cell.value = value.replace("{r}", str(row_idx))
                else:
                    cell.value = value

                cell.border = THIN_BORDER
                cell.alignment = Alignment(horizontal="center" if col_idx > 1 else "left")

                if col_idx == 1:
                    cell.font = HEADER_FONT
                else:
                    cell.font = NORMAL_FONT
                    if isinstance(value, (int, float)):
                        cell.number_format = '#,##0'

                if row_idx % 2 == 0:
                    cell.fill = LIGHT_FILL

        for col_idx in range(1, len(sheet_data["headers"]) + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 18

        ws.sheet_properties.tabColor = "2563EB"

    wb.save(filepath)
    return filename
