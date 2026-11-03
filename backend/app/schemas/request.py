"""Input contracts for notes-related API operations."""

from typing import Literal

from pydantic import BaseModel, Field


AlgorithmId = Literal[
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "svm",
    "naive_bayes",
    "knn",
]
Difficulty = Literal["beginner", "intermediate", "advanced"]
NotesFormat = Literal["detailed", "exam_oriented", "quick_revision"]
OptionalSection = Literal[
    "formulas",
    "examples",
    "advantages_disadvantages",
    "applications",
    "comparisons",
    "important_questions",
]


class GenerateNotesRequest(BaseModel):
    """Validated user choices for a future notes-generation request."""

    algorithm: AlgorithmId
    difficulty: Difficulty
    notes_format: NotesFormat
    optional_sections: list[OptionalSection] = Field(default_factory=list)


class ExportNotesRequest(BaseModel):
    """Validated payload for a future export request."""

    content: str = Field(min_length=1, max_length=100_000)
    export_format: Literal["pdf", "markdown"]
