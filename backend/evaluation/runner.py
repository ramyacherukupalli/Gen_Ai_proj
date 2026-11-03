"""Live Gemini prompt comparison and JSON/CSV artifact generation."""

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from google import genai
from groq import Groq

from app.schemas.request import GenerateNotesRequest
from app.services.prompt_service import build_notes_prompt
from evaluation.cases import EVALUATION_CASES, EvaluationCase
from evaluation.metrics import concept_coverage, difficulty_alignment, readability


@dataclass(frozen=True)
class GenerationMeasurement:
    """One prompt variant's observed response and measurements."""

    case_id: str
    variant: str
    algorithm: str
    difficulty: str
    notes_format: str
    notes: str
    latency_ms: float
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    concept_coverage: dict[str, object]
    readability: dict[str, float | int]
    difficulty_alignment: dict[str, object]
    correctness_score: None = None
    correctness_status: str = "requires human review"


def build_basic_prompt(case: EvaluationCase) -> str:
    """Baseline prompt intentionally omits algorithm-specific adaptive instructions."""

    return (
        f"Create {case.notes_format} study notes about {case.algorithm_name} for a "
        f"{case.difficulty} learner. Return Markdown."
    )


def build_adaptive_prompt(case: EvaluationCase) -> str:
    """Build the product prompt for the matching fixed evaluation case."""

    return build_notes_prompt(
        GenerateNotesRequest(
            algorithm=case.algorithm,
            difficulty=case.difficulty,
            notes_format=case.notes_format,
            optional_sections=["formulas", "examples", "advantages_disadvantages"],
        )
    )


def run_experiment(
    api_key: str,
    model: str,
    output_path: Path,
    case_limit: int | None = None,
    client: Any | None = None,
) -> dict[str, object]:
    """Generate both variants per fixed case and write reproducible result files."""

    selected_cases = EVALUATION_CASES[:case_limit] if case_limit else EVALUATION_CASES
    active_client = client or Groq(api_key=api_key)
    measurements: list[GenerationMeasurement] = []

    for index, case in enumerate(selected_cases, start=1):
        case_id = f"case-{index:02d}-{case.algorithm}-{case.difficulty}"
        for variant, prompt in (
            ("basic", build_basic_prompt(case)),
            ("adaptive", build_adaptive_prompt(case)),
        ):
            started_at = perf_counter()
            response = active_client.models.generate_content(model=model, contents=prompt)
            latency_ms = round((perf_counter() - started_at) * 1_000, 2)
            text = getattr(response, "text", None)
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"{case_id}/{variant} returned no usable text.")
            usage = getattr(response, "usage_metadata", None)
            measurements.append(
                GenerationMeasurement(
                    case_id=case_id,
                    variant=variant,
                    algorithm=case.algorithm,
                    difficulty=case.difficulty,
                    notes_format=case.notes_format,
                    notes=text.strip(),
                    latency_ms=latency_ms,
                    prompt_tokens=_usage_value(usage, "prompt_token_count"),
                    output_tokens=_usage_value(usage, "candidates_token_count"),
                    total_tokens=_usage_value(usage, "total_token_count"),
                    concept_coverage=concept_coverage(text, case.expected_concepts),
                    readability=readability(text),
                    difficulty_alignment=difficulty_alignment(text, case.difficulty),
                )
            )

    result = {
        "model": model,
        "case_count": len(selected_cases),
        "measurement_count": len(measurements),
        "correctness_note": "Correctness scores require blinded human review; no scores are inferred.",
        "summary": summarize_measurements(measurements),
        "measurements": [asdict(measurement) for measurement in measurements],
    }
    _write_results(output_path, result)
    _write_annotation_template(output_path.with_name(f"{output_path.stem}-annotations.csv"), measurements)
    return result


def summarize_measurements(measurements: list[GenerationMeasurement]) -> dict[str, dict[str, float | int | None]]:
    """Aggregate observed metrics by prompt variant without inventing correctness."""

    summary: dict[str, dict[str, float | int | None]] = {}
    for variant in ("basic", "adaptive"):
        subset = [measurement for measurement in measurements if measurement.variant == variant]
        summary[variant] = {
            "count": len(subset),
            "avg_latency_ms": _average([measurement.latency_ms for measurement in subset]),
            "avg_prompt_tokens": _average(
                [measurement.prompt_tokens for measurement in subset if measurement.prompt_tokens is not None]
            ),
            "avg_output_tokens": _average(
                [measurement.output_tokens for measurement in subset if measurement.output_tokens is not None]
            ),
            "avg_total_tokens": _average(
                [measurement.total_tokens for measurement in subset if measurement.total_tokens is not None]
            ),
            "avg_concept_coverage_percent": _average(
                [float(measurement.concept_coverage["percent"]) for measurement in subset]
            ),
            "avg_readability_score": _average(
                [float(measurement.readability["flesch_reading_ease"]) for measurement in subset]
            ),
            "avg_difficulty_alignment_percent": _average(
                [float(measurement.difficulty_alignment["percent"]) for measurement in subset]
            ),
            "avg_correctness_score": None,
        }
    return summary


def _usage_value(usage: Any, attribute: str) -> int | None:
    value = getattr(usage, attribute, None) if usage is not None else None
    return value if isinstance(value, int) else None


def _average(values: list[int | float]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def _write_results(path: Path, result: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")


def _write_annotation_template(path: Path, measurements: list[GenerationMeasurement]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("case_id", "variant", "correctness_score_1_to_5", "reviewer_notes"),
        )
        writer.writeheader()
        for measurement in measurements:
            writer.writerow(
                {
                    "case_id": measurement.case_id,
                    "variant": measurement.variant,
                    "correctness_score_1_to_5": "",
                    "reviewer_notes": "",
                }
            )
