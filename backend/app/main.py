"""ExamPaper question-generation API.

Phase 0: a single `/generate` endpoint returning a stub Pythagoras item, so the
frontend Generate button has a live round-trip to build against.
"""

from __future__ import annotations

from fastapi import FastAPI, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .assembler import build_paper
from .generators.registry import get_generator, topics_catalog
from .pdf import render_pdf
from .schema import GeneratePaperRequest, GenerateRequest, Item, Paper

app = FastAPI(title="ExamPaper API", version="0.0.1")

# The Vite dev server proxies /api -> here, so same-origin in practice. CORS is
# kept permissive in dev as a safety net for direct calls.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=Item)
def generate(req: GenerateRequest) -> Item:
    """Generate one question for the given context."""
    generator = get_generator(req.archetype)
    return generator(req)


@app.get("/topics")
def topics() -> list[dict]:
    """Pickable topics grouped by strand, each with an archetype count."""
    return topics_catalog()


@app.post("/generate-paper", response_model=Paper)
def generate_paper(req: GeneratePaperRequest) -> Paper:
    """Assemble a full custom paper from the chosen topics."""
    return build_paper(req)


class RenderPdfRequest(BaseModel):
    """A rendered HTML document + its stylesheet, to be printed to PDF."""

    html: str
    css: str
    filename: str = "paper.pdf"


@app.post("/render-pdf")
async def render_pdf_endpoint(req: RenderPdfRequest) -> Response:
    """Print a paper (or mark scheme) to a clean, chrome-free A4 PDF.

    The client renders the document to HTML and hands us its CSS; we run it
    through headless Chromium so no browser-injected header/footer appears.
    """
    pdf = await run_in_threadpool(render_pdf, req.html, req.css)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{req.filename}"'},
    )
