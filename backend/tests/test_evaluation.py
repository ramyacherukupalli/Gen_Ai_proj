from types import SimpleNamespace

from evaluation.cases import EVALUATION_CASES
from evaluation.metrics import concept_coverage, difficulty_alignment, readability
from evaluation.runner import build_adaptive_prompt, build_basic_prompt, run_experiment


def test_evaluation_matrix_covers_every_algorithm_and_difficulty() -> None:
    assert len(EVALUATION_CASES) == 18
    assert {case.algorithm for case in EVALUATION_CASES} == {
        "logistic_regression",
        "decision_tree",
        "random_forest",
        "svm",
        "naive_bayes",
        "knn",
    }
    assert {case.difficulty for case in EVALUATION_CASES} == {
        "beginner",
        "intermediate",
        "advanced",
    }


def test_adaptive_prompt_has_more_specific_context_than_basic_prompt() -> None:
    case = EVALUATION_CASES[0]

    assert len(build_adaptive_prompt(case)) > len(build_basic_prompt(case))
    assert "Algorithm-specific coverage" in build_adaptive_prompt(case)


def test_metrics_report_expected_observable_values() -> None:
    notes = "A simple example explains the sigmoid formula and regularization."

    assert concept_coverage(notes, ("sigmoid", "regularization"))["percent"] == 100.0
    assert difficulty_alignment(notes, "beginner")["percent"] == 50.0
    assert readability(notes)["word_count"] == 9


def test_runner_writes_measurements_and_annotation_template(tmp_path) -> None:
    fake_response = SimpleNamespace(
        text="A simple example covers sigmoid, log-odds, and regularization.",
        usage_metadata=SimpleNamespace(
            prompt_token_count=10,
            candidates_token_count=20,
            total_token_count=30,
        ),
    )
    fake_client = SimpleNamespace(
        models=SimpleNamespace(generate_content=lambda **_: fake_response)
    )
    output_path = tmp_path / "evaluation.json"

    result = run_experiment(
        api_key="test-key",
        model="test-model",
        output_path=output_path,
        case_limit=1,
        client=fake_client,
    )

    assert result["measurement_count"] == 2
    assert result["summary"]["basic"]["avg_total_tokens"] == 30.0
    assert result["summary"]["adaptive"]["avg_correctness_score"] is None
    assert output_path.exists()
    assert output_path.with_name("evaluation-annotations.csv").exists()
