import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.routes.notes import export_generated_notes
from app.schemas.request import ExportNotesRequest
from app.services.export_service import export_notes
from app.services.validation_service import (
    GeneratedNotesValidationError,
    validate_generated_notes,
)

SAMPLE_NOTES = """# Logistic Regression

## Key idea
Logistic Regression estimates the probability of a class.

- Uses the sigmoid function
- Produces a binary classification decision
"""


def test_markdown_export_preserves_content_and_metadata() -> None:
    exported = export_notes(SAMPLE_NOTES, "markdown")

    assert exported.content.decode("utf-8") == SAMPLE_NOTES
    assert exported.filename == "ml-study-notes.md"
    assert exported.media_type == "text/markdown; charset=utf-8"


def test_pdf_export_creates_a_pdf_document() -> None:
    exported = export_notes(SAMPLE_NOTES, "pdf")

    assert exported.content.startswith(b"%PDF-")
    assert len(exported.content) > 1_000
    assert exported.filename == "ml-study-notes.pdf"


def test_export_route_sets_attachment_headers() -> None:
    response = export_generated_notes(
        ExportNotesRequest(content=SAMPLE_NOTES, export_format="markdown")
    )

    assert response.headers["content-disposition"] == 'attachment; filename="ml-study-notes.md"'
    assert response.body == SAMPLE_NOTES.encode("utf-8")


def test_export_request_rejects_empty_content() -> None:
    with pytest.raises(ValidationError):
        ExportNotesRequest(content="", export_format="pdf")


def test_generated_notes_validation_rejects_control_characters() -> None:
    with pytest.raises(GeneratedNotesValidationError):
        validate_generated_notes("valid\x00invalid")


def test_export_route_handles_service_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.routes import notes

    def fail_export(*_: object) -> None:
        raise notes.NotesExportError("render failed")

    monkeypatch.setattr(notes, "export_notes", fail_export)
    with pytest.raises(HTTPException) as exc_info:
        export_generated_notes(ExportNotesRequest(content=SAMPLE_NOTES, export_format="pdf"))

    assert exc_info.value.status_code == 500
