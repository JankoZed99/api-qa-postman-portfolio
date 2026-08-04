from __future__ import annotations
from datetime import date
import csv
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
OUTPUT = REPORTS / "API_QA_Portfolio_Report.pdf"
GENERATED_DATE = f"{date.today().day} {date.today():%B %Y}"
NAVY = colors.HexColor("#14213D")
BLUE = colors.HexColor("#1D4ED8")
BLUE_LIGHT = colors.HexColor("#EAF1FF")
GREEN = colors.HexColor("#15803D")
GREEN_LIGHT = colors.HexColor("#ECFDF3")
AMBER = colors.HexColor("#B45309")
AMBER_LIGHT = colors.HexColor("#FFF7ED")
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#5B6475")
LINE = colors.HexColor("#D9DEE8")
PAPER = colors.HexColor("#F6F8FC")


def read_csv(name: str) -> list[dict[str, str]]:
    with (REPORTS / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


with (REPORTS / "newman-run.json").open(encoding="utf-8") as handle:
    newman = json.load(handle)

stats = newman["run"]["stats"]
timings = newman["run"]["timings"]
matrix_rows = read_csv("test-matrix.csv")
defect_rows = read_csv("defect-log.csv")

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=NAVY,
        spaceAfter=4 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="Subtitle",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=MUTED,
        spaceAfter=5 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=NAVY,
        spaceBefore=2 * mm,
        spaceAfter=3 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="BodySmall",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=INK,
        spaceAfter=2.5 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="Cell",
        fontName="Helvetica",
        fontSize=7.2,
        leading=9.3,
        textColor=INK,
    )
)
styles.add(
    ParagraphStyle(
        name="CellBold",
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9.3,
        textColor=INK,
    )
)
styles.add(
    ParagraphStyle(
        name="CellHeader",
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9.3,
        textColor=colors.white,
    )
)
styles.add(
    ParagraphStyle(
        name="KpiValue",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=20,
        textColor=NAVY,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="KpiLabel",
        fontName="Helvetica",
        fontSize=7.5,
        leading=9,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="Callout",
        fontName="Helvetica",
        fontSize=8.2,
        leading=11,
        textColor=INK,
    )
)


def P(text: str, style: str = "Cell") -> Paragraph:
    return Paragraph(text, styles[style])


def page_chrome(canvas, doc):
    canvas.saveState()
    width, height = landscape(A4)
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 7 * mm, width, 7 * mm, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(colors.white)
    canvas.drawString(16 * mm, height - 4.7 * mm, "TASKFLOW · API QA PORTFOLIO")
    canvas.setStrokeColor(LINE)
    canvas.line(16 * mm, 12 * mm, width - 16 * mm, 12 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(16 * mm, 7.5 * mm, f"Synthetic portfolio demonstration · Generated {GENERATED_DATE}")
    canvas.drawRightString(width - 16 * mm, 7.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def kpi_cell(value: str, label: str):
    return [Paragraph(value, styles["KpiValue"]), Spacer(1, 1.2 * mm), Paragraph(label, styles["KpiLabel"])]


doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=landscape(A4),
    rightMargin=16 * mm,
    leftMargin=16 * mm,
    topMargin=17 * mm,
    bottomMargin=17 * mm,
    title="TaskFlow API QA Portfolio Report",
    author="API QA Portfolio Demonstration",
)

story = []
story.append(Paragraph("API QA Test Report", styles["ReportTitle"]))
story.append(
    Paragraph(
        "TaskFlow REST API · Postman, Newman and pytest verification · Release candidate 1.0",
        styles["Subtitle"],
    )
)

disclosure = Table(
    [[P("<b>Portfolio disclosure</b><br/>TaskFlow is a fictional QA target built for demonstration. The historical defects below are seeded examples, not claims about a real client.", "Callout")]],
    colWidths=[265 * mm],
)
disclosure.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), AMBER_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#FED7AA")),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ]
    )
)
story.extend([disclosure, Spacer(1, 5 * mm)])

requests_total = stats["requests"]["total"]
assertions_total = stats["assertions"]["total"]
assertions_failed = stats["assertions"]["failed"]
average_ms = f"{timings['responseAverage']:.1f}"
kpis = Table(
    [[
        kpi_cell(str(requests_total), "REQUESTS EXECUTED"),
        kpi_cell(str(assertions_total), "POSTMAN ASSERTIONS"),
        kpi_cell(str(assertions_failed), "FAILED ASSERTIONS"),
        kpi_cell("11 / 11", "PYTEST CHECKS PASSED"),
        kpi_cell(f"{average_ms} ms", "AVG. LOCAL RESPONSE"),
    ]],
    colWidths=[53 * mm] * 5,
)
kpis.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), PAPER),
            ("BOX", (0, 0), (-1, -1), 0.6, LINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.6, LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
        ]
    )
)
story.extend([kpis, Spacer(1, 5 * mm)])

summary_left = [
    P("<b>Objective</b>", "BodySmall"),
    P("Verify core API behavior, error handling, response contracts and a create-to-delete workflow before release.", "BodySmall"),
    P("<b>Coverage</b>", "BodySmall"),
    P("Health, login, bearer authorization, validation, pagination, user lookup, task creation and deletion.", "BodySmall"),
]
summary_right = [
    P("<b>Release recommendation</b>", "BodySmall"),
    P("<font color='#15803D'><b>PASS — suitable for demonstration release.</b></font>", "BodySmall"),
    P(f"All {assertions_total} Newman assertions and 11 pytest regression checks passed. No open seeded defects remain in this version.", "BodySmall"),
]
summary = Table([[summary_left, summary_right]], colWidths=[130 * mm, 130 * mm])
summary.setStyle(
    TableStyle(
        [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (1, 0), (1, 0), GREEN_LIGHT),
            ("BOX", (0, 0), (0, 0), 0.6, LINE),
            ("BOX", (1, 0), (1, 0), 0.7, colors.HexColor("#BBF7D0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5 * mm),
        ]
    )
)
story.append(summary)

story.append(PageBreak())
story.append(Paragraph("Test Coverage Matrix", styles["Section"]))
story.append(Paragraph("Status and expected behavior for each request in the recorded Newman run.", styles["BodySmall"]))

matrix_header = ["ID", "Area", "Method", "Endpoint", "Scenario", "Expected result", "Type", "Status"]
matrix_data = [[P(h, "CellHeader") for h in matrix_header]]
for row in matrix_rows:
    matrix_data.append(
        [
            P(row["ID"], "CellBold"),
            P(row["Area"]),
            P(row["Method"], "CellBold"),
            P(row["Endpoint"]),
            P(row["Scenario"]),
            P(row["Expected result"]),
            P(row["Test type"]),
            P(f"<font color='#15803D'><b>{row['Status']}</b></font>"),
        ]
    )
matrix = Table(
    matrix_data,
    repeatRows=1,
    colWidths=[14 * mm, 25 * mm, 18 * mm, 48 * mm, 48 * mm, 70 * mm, 23 * mm, 19 * mm],
)
matrix.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.45, LINE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ]
    )
)
story.append(matrix)

story.append(PageBreak())
story.append(Paragraph("Defect Verification", styles["Section"]))
story.append(
    Paragraph(
        "Seeded defect history shows how findings are prioritized, communicated and retested after a fix.",
        styles["BodySmall"],
    )
)

defect_header = ["ID", "Severity", "Area", "Finding", "Previous behavior", "Expected behavior", "Resolution", "Verification"]
defect_data = [[P(h, "CellHeader") for h in defect_header]]
for row in defect_rows:
    severity_color = "#B91C1C" if row["Severity"] == "High" else "#B45309" if row["Severity"] == "Medium" else "#1D4ED8"
    defect_data.append(
        [
            P(row["ID"], "CellBold"),
            P(f"<font color='{severity_color}'><b>{row['Severity']}</b></font>"),
            P(row["Area"]),
            P(row["Summary"]),
            P(row["Previous behavior"]),
            P(row["Expected behavior"]),
            P(row["Resolution"]),
            P(f"<font color='#15803D'><b>{row['Verification']}</b></font>"),
        ]
    )
defects = Table(
    defect_data,
    repeatRows=1,
    colWidths=[16 * mm, 20 * mm, 25 * mm, 47 * mm, 44 * mm, 45 * mm, 35 * mm, 33 * mm],
)
defects.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.45, LINE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2.3 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3 * mm),
        ]
    )
)
story.extend([defects, Spacer(1, 7 * mm)])

severity_note = Table(
    [[
        P("<b>High</b><br/>Core workflow or reliability risk", "Callout"),
        P("<b>Medium</b><br/>Incorrect behavior with a viable workaround", "Callout"),
        P("<b>Low</b><br/>Contract or standards inconsistency", "Callout"),
    ]],
    colWidths=[88 * mm] * 3,
)
severity_note.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#FEF2F2")),
            ("BACKGROUND", (1, 0), (1, 0), AMBER_LIGHT),
            ("BACKGROUND", (2, 0), (2, 0), BLUE_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.5, LINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ]
    )
)
story.append(severity_note)

story.append(PageBreak())
story.append(Paragraph("Method and Deliverables", styles["Section"]))

method_data = [
    [P("1", "CellBold"), P("Understand the contract", "CellBold"), P("Review Swagger/OpenAPI, authentication, environments, business rules and success criteria.")],
    [P("2", "CellBold"), P("Design coverage", "CellBold"), P("Map happy paths, negative paths, missing/invalid fields, boundaries, status codes and response schemas.")],
    [P("3", "CellBold"), P("Execute and automate", "CellBold"), P("Build an organized Postman collection, capture variables, write assertions and execute with Newman.")],
    [P("4", "CellBold"), P("Report findings", "CellBold"), P("Log severity, exact reproduction steps, expected/actual behavior, evidence and business impact.")],
    [P("5", "CellBold"), P("Verify fixes", "CellBold"), P("Rerun affected cases and regression coverage, then provide a release recommendation.")],
]
method = Table(method_data, colWidths=[14 * mm, 60 * mm, 188 * mm])
method.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (0, -1), BLUE_LIGHT),
            ("GRID", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2.7 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.7 * mm),
        ]
    )
)
story.extend([method, Spacer(1, 6 * mm)])

deliverables = Table(
    [[
        [P("<b>Included files</b>", "BodySmall"), P("Postman collection and environment<br/>Test matrix<br/>Defect log<br/>Newman JSON evidence<br/>pytest suite<br/>README and CI workflow", "BodySmall")],
        [P("<b>Demonstrated skills</b>", "BodySmall"), P("REST API QA<br/>Authentication and authorization<br/>Negative and boundary testing<br/>JSON contract checks<br/>Postman and Newman<br/>pytest, FastAPI and CI", "BodySmall")],
        [P("<b>Scope boundary</b>", "BodySmall"), P("This report demonstrates functional API QA. It is not a penetration test, load test, production audit or guarantee of defect-free software.", "BodySmall")],
    ]],
    colWidths=[88 * mm] * 3,
)
deliverables.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), PAPER),
            ("BOX", (0, 0), (-1, -1), 0.6, LINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.6, LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5 * mm),
        ]
    )
)
story.extend([deliverables, Spacer(1, 5 * mm)])
story.append(
    Paragraph(
        "<b>Evidence integrity:</b> counts in this report are read directly from <font name='Courier'>reports/newman-run.json</font>; the source API and all automated tests are included with the portfolio.",
        styles["BodySmall"],
    )
)

doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
print(OUTPUT)
