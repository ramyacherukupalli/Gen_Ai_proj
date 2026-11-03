from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.routes import notes
from app.schemas.request import GenerateNotesRequest
from app.services.llm_service import (
    GeminiLLMService,
    LLMProviderError,
    ProviderResponseError,
)
from app.services.notes_service import NotesService
from app.services.prompt_service import build_notes_prompt


def logistic_request() -> GenerateNotesRequest:
    return GenerateNotesRequest(
        algorithm="logistic_regression",
        difficulty="intermediate",
        notes_format="detailed",
        optional_sections=["formulas", "examples"],
    )


def test_logistic_regression_prompt_adapts_to_request_choices() -> None:
    prompt = build_notes_prompt(logistic_request())

    assert "Logistic Regression" in prompt
    assert "technical explanations" in prompt
    assert "formulas, examples" in prompt


@pytest.mark.parametrize(
    ("algorithm", "display_name"),
    [
        ("logistic_regression", "Logistic Regression"),
        ("decision_tree", "Decision Tree"),
        ("random_forest", "Random Forest"),
        ("svm", "Support Vector Machine (SVM)"),
        ("naive_bayes", "Naive Bayes"),
        ("knn", "K-Nearest Neighbors (KNN)"),
    ],
)
def test_all_supported_algorithms_build_a_specific_prompt(
    algorithm: str, display_name: str
) -> None:
    request = logistic_request().model_copy(update={"algorithm": algorithm})

    assert display_name in build_notes_prompt(request)


def test_notes_service_generates_valid_response_with_mocked_provider() -> None:
    fake_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **_: SimpleNamespace(
                text="# Logistic Regression\n\nA classification algorithm.\n\n## Formulas\n\n$$p = \\sigma(z)$$\n\n## Examples\n\nA binary classification example."
            )
        )
    )
    service = NotesService(GeminiLLMService(api_key="test-key", client=fake_client))

    response = service.generate(logistic_request())

    assert response.algorithm == "logistic_regression"
    assert response.notes.startswith("# Logistic Regression")


def test_notes_service_requests_only_missing_selected_sections() -> None:
    prompts: list[str] = []
    responses = iter(
        [
            "# Logistic Regression\n\n## Formulas\n\n$$p = \\sigma(z)$$",
            "## Examples\n\nA worked example.",
        ]
    )

    fake_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: (
                prompts.append(kwargs["contents"]) or SimpleNamespace(text=next(responses))
            )
        )
    )
    service = NotesService(GeminiLLMService(api_key="test-key", client=fake_client))

    response = service.generate(logistic_request())

    assert len(prompts) == 2
    assert "Examples" in prompts[1]
    assert "## Examples" in response.notes


def test_gemini_service_rejects_empty_provider_text() -> None:
    fake_client = SimpleNamespace(
        models=SimpleNamespace(generate_content=lambda **_: SimpleNamespace(text="   "))
    )
    service = GeminiLLMService(api_key="test-key", client=fake_client)

    with pytest.raises(ProviderResponseError):
        service.generate("prompt")


def test_gemini_service_normalizes_provider_errors() -> None:
    def raise_provider_error(**_: object) -> None:
        raise RuntimeError("network unavailable")

    fake_client = SimpleNamespace(models=SimpleNamespace(generate_content=raise_provider_error))
    service = GeminiLLMService(api_key="test-key", client=fake_client)

    with pytest.raises(LLMProviderError):
        service.generate("prompt")


def test_groq_configuration_uses_chat_completion_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="# Groq notes\n\nReady."))]
                )
            )
        )
    )
    service = GeminiLLMService(api_key="test-key", model="llama-3.3-70b-versatile", client=fake_client)

    assert service.generate("prompt") == "# Groq notes\n\nReady."


def test_generate_route_reports_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(notes, "notes_service", NotesService(GeminiLLMService(api_key="")))

    with pytest.raises(HTTPException) as exc_info:
        notes.generate_notes(logistic_request())

    assert exc_info.value.status_code == 503
