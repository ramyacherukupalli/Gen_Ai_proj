"""Convert generated notes into downloadable PDF or Markdown files."""

from dataclasses import dataclass
from html import escape
from io import BytesIO

from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class NotesExportError(RuntimeError):
    """Raised when a requested notes export cannot be produced."""


@dataclass(frozen=True)
class ExportedNotes:
    """In-memory file returned by the export service."""

    content: bytes
    media_type: str
    filename: str


def export_notes(content: str, export_format: str) -> ExportedNotes:
    """Export trusted, request-validated notes without persisting user content."""

    if export_format == "markdown":
        return ExportedNotes(
            content=content.encode("utf-8"),
            media_type="text/markdown; charset=utf-8",
            filename="ml-study-notes.md",
        )
    if export_format == "pdf":
        return ExportedNotes(
            content=_build_pdf(content),
            media_type="application/pdf",
            filename="ml-study-notes.pdf",
        )
    raise NotesExportError(f"Unsupported export format: {export_format}")


def _build_pdf(content: str) -> bytes:
    """Render Markdown-like notes as a clean, paginated PDF."""

    buffer = BytesIO()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "NotesTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "NotesHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "NotesBody",
        parent=styles["BodyText"],
        alignment=TA_LEFT,
        fontSize=10,
        leading=14,
        spaceAfter=5,
    )
    bullet_style = ParagraphStyle(
        "NotesBullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
    )
    formula_style = ParagraphStyle(
        "NotesFormula",
        parent=body_style,
        fontName="Courier",
        backColor="#F0F9FF",
        borderColor="#BAE6FD",
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=5,
        spaceAfter=8,
    )

    story = []
    lines = content.splitlines()
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 4))
        elif line.startswith("```mermaid"):
            diagram_lines = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                diagram_lines.append(lines[index])
                index += 1
            diagram_text = escape("\n".join(diagram_lines))
            story.append(Paragraph(f"<b>Learning diagram</b><br/>{diagram_text.replace(chr(10), '<br/>')}", formula_style))
        elif line.startswith("$$"):
            if line.endswith("$$") and len(line) > 4:
                formula_lines = [line[2:-2].strip()]
            else:
                formula_lines = [line[2:].strip()]
                index += 1
                while index < len(lines) and "$$" not in lines[index]:
                    formula_lines.append(lines[index].strip())
                    index += 1
                if index < len(lines):
                    formula_lines.append(lines[index].replace("$$", "").strip())
            formula = escape(" ".join(part for part in formula_lines if part))
            story.append(Paragraph(formula, formula_style))
        elif line.startswith(("\\(", "\\[")) or line.endswith(("\\)", "\\]")):
            formula = line
            for delimiter in ("\\(", "\\)", "\\[", "\\]"):
                formula = formula.replace(delimiter, "")
            story.append(Paragraph(escape(formula.strip()), formula_style))
        elif line.startswith("# "):
            story.append(Paragraph(escape(line[2:]), title_style))
        elif line.startswith("## ") or line.startswith("### "):
            story.append(Paragraph(escape(line.lstrip("# ")), heading_style))
        elif line.startswith(("- ", "* ")):
            story.append(Paragraph(f"&#8226; {escape(line[2:])}", bullet_style))
        else:
            inline = escape(line)
            for delimiter in ("$$", "$", "\\(", "\\)", "\\[", "\\]"):
                inline = inline.replace(delimiter, "")
            story.append(Paragraph(inline, body_style))
        index += 1

    if not story:
        raise NotesExportError("Cannot export empty notes.")

    try:
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title="ML Study Notes",
        )
        document.build(story)
    except Exception as exc:
        raise NotesExportError("PDF export could not be created.") from exc
    return buffer.getvalue()
