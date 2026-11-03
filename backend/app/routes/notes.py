"""Notes generation routes."""

from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.request import ExportNotesRequest, GenerateNotesRequest
from app.schemas.response import GeneratedNotesResponse
from app.services.export_service import NotesExportError, export_notes
from app.services.llm_service import (
    LLMProviderError,
    ProviderConfigurationError,
    ProviderResponseError,
)
from app.services.notes_service import NotesService
from app.services.prompt_service import PromptNotAvailableError
from app.services.validation_service import GeneratedNotesValidationError

router = APIRouter(prefix="/notes", tags=["notes"])
notes_service = NotesService()


@router.post("/generate", response_model=GeneratedNotesResponse)
def generate_notes(request: GenerateNotesRequest) -> GeneratedNotesResponse:
    """Generate validated notes for an algorithm supported in this phase."""

    try:
        return notes_service.generate(request)
    except PromptNotAvailableError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except (LLMProviderError, ProviderResponseError, GeneratedNotesValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/export")
def export_generated_notes(request: ExportNotesRequest) -> Response:
    """Download supplied generated notes in the requested export format."""

    try:
        exported_notes = export_notes(request.content, request.export_format)
    except NotesExportError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return Response(
        content=exported_notes.content,
        media_type=exported_notes.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{exported_notes.filename}"'
        },
    )
