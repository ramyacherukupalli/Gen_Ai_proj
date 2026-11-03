"""Application service that coordinates prompt construction and generation."""

from app.schemas.request import GenerateNotesRequest
from app.schemas.response import GeneratedNotesResponse
from app.services.llm_service import GeminiLLMService
from app.services.prompt_service import build_notes_prompt, build_section_correction_prompt
from app.services.validation_service import (
    GeneratedNotesValidationError,
    find_missing_optional_sections,
    validate_generated_notes,
)


class NotesService:
    """Generate validated notes without coupling routes to a provider SDK."""

    def __init__(self, llm_service: GeminiLLMService | None = None) -> None:
        self._llm_service = llm_service or GeminiLLMService()

    def generate(self, request: GenerateNotesRequest) -> GeneratedNotesResponse:
        prompt = build_notes_prompt(request)
        notes = validate_generated_notes(self._llm_service.generate(prompt))
        missing_sections = find_missing_optional_sections(notes, request)
        if missing_sections:
            correction_prompt = build_section_correction_prompt(
                request, notes, missing_sections
            )
            correction = validate_generated_notes(self._llm_service.generate(correction_prompt))
            notes = validate_generated_notes(f"{notes}\n\n{correction}")
            remaining_sections = find_missing_optional_sections(notes, request)
            if remaining_sections:
                missing = ", ".join(remaining_sections)
                raise GeneratedNotesValidationError(
                    f"Generated notes are missing requested sections: {missing}."
                )
        return GeneratedNotesResponse(
            notes=notes,
            algorithm=request.algorithm,
            difficulty=request.difficulty,
            notes_format=request.notes_format,
        )
