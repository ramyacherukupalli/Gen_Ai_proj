from app.main import app
from app.routes.general import get_models, get_options, health_check
from app.schemas.request import GenerateNotesRequest

def test_health_endpoint_is_registered_and_returns_ok_status() -> None:
    paths = {route.path for route in app.routes}

    assert "/health" in paths
    assert health_check().status == "ok"


def test_models_endpoint_lists_all_supported_algorithms() -> None:
    paths = {route.path for route in app.routes}
    model_ids = {model.id for model in get_models().models}

    assert "/api/models" in paths
    assert model_ids == {
        "logistic_regression",
        "decision_tree",
        "random_forest",
        "svm",
        "naive_bayes",
        "knn",
    }


def test_options_endpoint_returns_all_selection_categories() -> None:
    paths = {route.path for route in app.routes}
    options = get_options()

    assert "/api/options" in paths
    assert set(options.model_dump()) == {
        "difficulties",
        "notes_formats",
        "optional_sections",
    }


def test_notes_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/notes/generate" in paths
    assert "/api/notes/export" in paths


def test_generate_request_rejects_an_unknown_algorithm() -> None:
    invalid_request = {
        "algorithm": "linear_regression",
        "difficulty": "beginner",
        "notes_format": "detailed",
    }

    try:
        GenerateNotesRequest.model_validate(invalid_request)
    except ValueError:
        pass
    else:
        raise AssertionError("An unsupported algorithm should be rejected")
