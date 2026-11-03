"""General-purpose API routes and static selection options."""

from fastapi import APIRouter

from app.config import settings
from app.schemas.response import (
    HealthResponse,
    ModelOption,
    ModelsResponse,
    OptionItem,
    OptionsResponse,
)

health_router = APIRouter(tags=["general"])
router = APIRouter(tags=["general"])

SUPPORTED_MODELS = [
    ModelOption(id="logistic_regression", name="Logistic Regression"),
    ModelOption(id="decision_tree", name="Decision Tree"),
    ModelOption(id="random_forest", name="Random Forest"),
    ModelOption(id="svm", name="Support Vector Machine (SVM)"),
    ModelOption(id="naive_bayes", name="Naive Bayes"),
    ModelOption(id="knn", name="K-Nearest Neighbors (KNN)"),
]


@health_router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return a lightweight status check without exposing secrets."""

    return HealthResponse(status="ok", environment=settings.environment)


@router.get("/models", response_model=ModelsResponse)
def get_models() -> ModelsResponse:
    """List classification algorithms that can be selected by the client."""

    return ModelsResponse(models=SUPPORTED_MODELS)


@router.get("/options", response_model=OptionsResponse)
def get_options() -> OptionsResponse:
    """List the valid choices used by notes-generation clients."""

    return OptionsResponse(
        difficulties=[
            OptionItem(id="beginner", name="Beginner"),
            OptionItem(id="intermediate", name="Intermediate"),
            OptionItem(id="advanced", name="Advanced"),
        ],
        notes_formats=[
            OptionItem(id="detailed", name="Detailed study notes"),
            OptionItem(id="exam_oriented", name="Exam-oriented notes"),
            OptionItem(id="quick_revision", name="Quick revision notes"),
        ],
        optional_sections=[
            OptionItem(id="formulas", name="Formulas"),
            OptionItem(id="examples", name="Examples"),
            OptionItem(
                id="advantages_disadvantages", name="Advantages and disadvantages"
            ),
            OptionItem(id="applications", name="Applications"),
            OptionItem(id="comparisons", name="Comparisons"),
            OptionItem(id="important_questions", name="Important questions"),
        ],
    )
