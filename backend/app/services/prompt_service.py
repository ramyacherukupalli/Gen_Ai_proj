"""Construct generation prompts from validated user choices."""

from app.prompts.classification import (
    CLASSIFICATION_ALGORITHM_INSTRUCTIONS,
    CLASSIFICATION_ALGORITHM_NAMES,
)
from app.prompts.common import (
    COMMON_INSTRUCTIONS,
    DIFFICULTY_INSTRUCTIONS,
    FORMAT_INSTRUCTIONS,
)
from app.schemas.request import GenerateNotesRequest


class PromptNotAvailableError(ValueError):
    """Raised when an accepted algorithm has not been implemented yet."""


SECTION_LABELS = {
    "formulas": "formulas",
    "examples": "examples",
    "advantages_disadvantages": "advantages and disadvantages",
    "applications": "applications",
    "comparisons": "comparisons with related classifiers",
    "important_questions": "important questions with brief answers",
}


def selected_section_heading(section: str) -> str:
    """Return the required Markdown heading for an optional section."""
    return SECTION_LABELS[section].title()


def build_notes_prompt(request: GenerateNotesRequest) -> str:
    """Build a classification-notes prompt from the validated request."""

    algorithm_instruction = CLASSIFICATION_ALGORITHM_INSTRUCTIONS.get(request.algorithm)
    if algorithm_instruction is None:
        raise PromptNotAvailableError(
            f"Notes generation for '{request.algorithm}' is not available yet."
        )
    algorithm_name = CLASSIFICATION_ALGORITHM_NAMES[request.algorithm]

    if request.optional_sections:
        # Prepend the required ## Markdown syntax directly into the prompt requirements
        section_names = [f"## {selected_section_heading(s)}" for s in request.optional_sections]
        sections_str = ", ".join(section_names)
        requested_sections_prompt = (
            f"\nMANDATORY STRUCTURE REQUIREMENT:\n"
            f"You MUST create a distinct Markdown heading for EVERY ONE of these "
            f"requested sections and populate them with content: {sections_str}.\n"
            f"Do not combine these headings. Do not skip any of them."
        )
    else:
        requested_sections_prompt = "\nMANDATORY STRUCTURE REQUIREMENT:\nDo not add any of the optional sections."

    return f"""{COMMON_INSTRUCTIONS}

Algorithm: {algorithm_name}
Algorithm-specific coverage:
{algorithm_instruction}

Difficulty: {request.difficulty}
Difficulty guidance: {DIFFICULTY_INSTRUCTIONS[request.difficulty]}

Requested format: {request.notes_format}
Format guidance: {FORMAT_INSTRUCTIONS[request.notes_format]}
{requested_sections_prompt}

Create the requested study notes now."""


def build_section_correction_prompt(
    request: GenerateNotesRequest, notes: str, missing_sections: list[str]
) -> str:
    """Build a focused prompt to add only missing requested sections."""

    missing = "\n".join(f"- ## {selected_section_heading(section)}" for section in missing_sections)
    return f"""You are supplying missing sections for an existing Markdown
study guide about
{CLASSIFICATION_ALGORITHM_NAMES[request.algorithm]}.

Return only the following missing, non-empty sections, each with the exact
Markdown heading shown. Do not repeat or summarize existing content:
{missing}

Use accurate, level-appropriate content. Use $...$ or $$...$$ for formulas.
Use a small ```mermaid diagram only if it improves understanding.

Existing study guide context:
{notes}
"""