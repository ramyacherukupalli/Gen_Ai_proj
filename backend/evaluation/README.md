# Prompt Evaluation Protocol

This reproducible experiment compares two prompts for every fixed case:

- `basic`: a short generic request naming only the algorithm and difficulty.
- `adaptive`: the product's algorithm-specific, difficulty-adaptive prompt.

The case set covers six algorithms at beginner, intermediate, and advanced
levels (18 cases, 36 generation requests). Each output records observed
latency, Gemini usage metadata (prompt, output, and total tokens), expected
concept coverage, Flesch reading ease, and observable difficulty cues.

Correctness is not inferred from word matching. The runner therefore produces
a CSV template for blinded human scoring on a 1-5 correctness rubric. Only
completed reviewer scores should be aggregated or reported as correctness.

## Run

From `backend`, set a Gemini key in the shell and run:

```powershell
$env:GEMINI_API_KEY = "your-key"
python scripts/run_evaluation.py
```

Use a small, inexpensive smoke run first:

```powershell
python scripts/run_evaluation.py --case-limit 1 --output evaluation/results/smoke.json
```

Each run writes JSON measurements and a matching reviewer-annotation CSV. Do
not compare runs made with different models, case limits, or prompt code.
