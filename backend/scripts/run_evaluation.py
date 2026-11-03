"""Run the live, reproducible Gemini prompt comparison."""

import argparse
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from evaluation.runner import run_experiment


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare basic and adaptive ML-notes prompts.")
    parser.add_argument("--model", default=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
    parser.add_argument("--output", type=Path, default=Path("evaluation/results/latest.json"))
    parser.add_argument("--case-limit", type=int, default=None)
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is required for a live evaluation; no results were generated.", file=sys.stderr)
        return 2
    if args.case_limit is not None and args.case_limit < 1:
        parser.error("--case-limit must be at least 1")

    result = run_experiment(
        api_key=api_key,
        model=args.model,
        output_path=args.output,
        case_limit=args.case_limit,
    )
    print(
        f"Wrote {result['measurement_count']} measurements across {result['case_count']} cases to {args.output}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
