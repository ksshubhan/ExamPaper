# ExamPaper

Generates original, exam-style GCSE Higher Mathematics practice papers (Edexcel specification) with mark schemes, exported as print-ready PDFs.

## How it works

ExamPaper uses a **generate-verify pipeline**:

1. **Blueprint.** A paper blueprint (`backend/app/blueprints/edexcel_higher.json`) encodes the structure of real papers: topic weightings, mark distributions and question-type patterns, derived from analysis of the June 2022 and June 2023 Higher papers.
2. **Generate.** An LLM (Anthropic API) fills parameterised question slots defined by the blueprint.
3. **Verify.** Every answer is checked programmatically with **SymPy** before it is used, so a paper never depends on the model's arithmetic.
4. **Assemble.** Questions are assembled to match real paper proportions (~21 questions averaging ~3.8 marks), with a separate mark scheme.
5. **Render.** React components lay out the paper, diagrams are generated as SVG from the same parameters as the question, and **Playwright** renders the result to PDF.

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, FastAPI, SymPy, Anthropic API |
| Frontend | React, TypeScript, Vite, Tailwind CSS v4, React Router |
| PDF output | Playwright |

## Running locally

Requires Python 3.13+, Node.js, and an Anthropic API key.

**Backend** (port 8000), from the repo root:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
export ANTHROPIC_API_KEY=your-key-here
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend** (port 5173, proxies `/api` to the backend):

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173, pick topics, and generate a paper.

## Tests

42 tests covering answer verification, paper assembly, diagram generation and paper structure. With the venv active:

```bash
pip install -r backend/requirements-dev.txt
cd backend
python -m pytest
```

## Status

Working: topic selection, paper generation with verified answers, mark scheme, PDF export.

Next: public deployment, a regression test suite for rendering, and an offline batch pipeline that builds a verified question bank so papers are assembled from pre-checked questions rather than generated live.

## Disclaimer

ExamPaper produces original practice questions. It is not affiliated with or endorsed by Pearson Edexcel, and contains no past paper content.