# Intelligent ML Notes

A web application for generating structured study notes for machine-learning
classification algorithms. This repository contains a FastAPI backend and
React + Tailwind frontend.

## Folder structure

```text
GenAI_project/
├── backend/
│   ├── app/
│   │   ├── prompts/          # Shared and algorithm-specific LLM prompts
│   │   ├── routes/           # FastAPI route handlers
│   │   ├── schemas/          # Request and response models
│   │   ├── services/         # Generation, validation, and export services
│   │   ├── config.py         # Environment-based application settings
│   │   └── main.py           # FastAPI application entry point
│   ├── evaluation/           # Prompt evaluation protocol and reports
│   ├── scripts/              # Utility and evaluation scripts
│   ├── tests/                # Backend test suite
│   ├── .env.example          # Environment variable template
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # Topic form, notes display, and export controls
│   │   ├── services/         # Backend API client
│   │   ├── App.jsx           # Main application component
│   │   └── main.jsx          # React entry point
│   ├── index.html            # Vite HTML entry point
│   ├── package.json          # JavaScript dependencies and scripts
│   └── vite.config.js        # Vite configuration
└── README.md
```

## Backend setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is then available at `http://127.0.0.1:8000`. Interactive API docs are
available at `/docs`.

## Available endpoints

- `GET /health`
- `GET /api/models`
- `GET /api/options`
- `POST /api/notes/generate` — supports all six listed classifiers
- `POST /api/notes/export` — downloads supplied notes as PDF or Markdown

Example generation request:

```json
{
  "algorithm": "logistic_regression",
  "difficulty": "intermediate",
  "notes_format": "detailed",
  "optional_sections": ["formulas", "examples"]
}
```

Set `GEMINI_API_KEY` in `backend/.env` before using the generation endpoint.
`GEMINI_MODEL` is optional and defaults to `gemini-3.8-flash`.

## Tests

```powershell
cd backend
pytest
```

## Prompt evaluation

The reproducible live evaluation protocol is documented in
[`backend/evaluation/README.md`](backend/evaluation/README.md). It compares a
basic prompt with the adaptive product prompt and records latency, Gemini token
usage, concept coverage, readability, and difficulty cues. Correctness scores
are collected through a separate human-review CSV; no synthetic scores are
reported.

Copy `.env.example` to `.env` before Phase 2 and set `GEMINI_API_KEY`.

## Frontend setup

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The interface opens at `http://localhost:5173` and connects to the backend at
`http://127.0.0.1:8000/api` by default. Set `VITE_API_BASE_URL` if the backend
uses another address.
