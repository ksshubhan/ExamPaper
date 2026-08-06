"""The item schema — the contract for one generated question.

This is the single most important data structure in the system: every
generator produces an `Item`, the verifier checks an `Item`, the API returns
an `Item`, and the frontend renders an `Item`. Keep it stable and explicit.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Tier = Literal["foundation", "higher"]
MarkType = Literal["M", "A", "B"]  # Method, Accuracy, Independent


class Diagram(BaseModel):
    """A figure rendered deterministically from the question's parameters."""

    svg: str = Field(description="Inline SVG markup, ready to render.")
    alt: str = Field(description="Accessible text description of the figure.")
    not_to_scale: bool = Field(
        default=True,
        description="If true, the UI shows 'Diagram NOT accurately drawn'.",
    )


class MarkSchemeStep(BaseModel):
    """One awardable mark, mirroring real Edexcel notation (M1 / A1 / B1)."""

    code: str = Field(description="e.g. 'M1', 'A1', 'B1'.")
    mark_type: MarkType
    marks: int = Field(default=1, ge=1)
    description: str = Field(description="What earns this mark.")
    working: Optional[str] = Field(
        default=None, description="The expression/value at this step."
    )


class Part(BaseModel):
    """A question part. Single-part questions use one Part with label ''."""

    label: str = Field(default="", description="e.g. 'a', 'b', or '' if single.")
    prompt: str = Field(description="The wording the student reads.")
    marks: int = Field(ge=1)
    answer: str = Field(description="The final answer as displayed.")
    answer_tolerance: Optional[float] = Field(
        default=None, description="Absolute tolerance for accepting numeric answers."
    )
    working: str = Field(description="Full worked solution.")
    mark_scheme: list[MarkSchemeStep] = Field(default_factory=list)


class Metadata(BaseModel):
    """Provenance and classification for assembly, filtering, and audit."""

    archetype: str = Field(description="Generator id, e.g. 'pythagoras-hypotenuse'.")
    spec_ref: str = Field(description="Edexcel 1MA1 spec reference, e.g. 'G20'.")
    topic: str = Field(description="Human topic name, e.g. \"Pythagoras' theorem\".")
    topic_slug: str = Field(description="Stable slug for grouping/selection, e.g. 'pythagoras'.")
    strand: str = Field(description="Spec strand, e.g. 'Geometry & measures'.")
    ao: str = Field(description="Assessment objective: 'AO1', 'AO2', or 'AO3'.")
    grade_band: str = Field(description="Target grade range, e.g. '4-6'.")
    seed: int = Field(description="RNG seed — regenerates this exact item.")


class Item(BaseModel):
    """A complete generated question, ready to render or assemble into a paper."""

    id: str = Field(description="Unique id for this generated instance.")

    # Context it was generated for (echoes the request).
    format: str = Field(description="'past-papers' or 'worksheets'.")
    qualification: str
    board: str
    subject: str

    tier: Tier = "higher"
    calculator: bool = True
    total_marks: int = Field(ge=1)

    stem: str = Field(description="Lead-in text shared by all parts.")
    parts: list[Part]
    diagram: Optional[Diagram] = None

    metadata: Metadata


class GenerateRequest(BaseModel):
    """What the frontend sends when the user clicks Generate (single question)."""

    format: str
    qualification: str
    board: str
    subject: str
    # Optional narrowing. If unset, the generator chooses (and the seed makes
    # that choice reproducible).
    archetype: Optional[str] = None
    variant: Optional[str] = None
    calculator: Optional[bool] = None
    seed: Optional[int] = None


class Paper(BaseModel):
    """A full assembled paper: cover metadata + an ordered list of questions.

    The questions are ordered as they appear (question 1 first); the rendered
    question number is just the 1-based index. Each Item already carries its own
    mark scheme, so the answers appendix needs no extra data.
    """

    id: str
    format: str
    qualification: str
    board: str
    subject: str

    title: str
    tier: Tier = "higher"
    calculator: bool = False

    target_marks: int = Field(ge=1, description="Marks the user asked for.")
    total_marks: int = Field(ge=0, description="Marks actually assembled.")
    duration_minutes: int = Field(ge=0)
    instructions: list[str] = Field(default_factory=list)
    include_answers: bool = True

    questions: list[Item] = Field(default_factory=list)
    notes: list[str] = Field(
        default_factory=list, description="User-facing notes, e.g. a mark shortfall."
    )
    seed: int = Field(description="RNG seed — regenerates this exact paper.")


class GeneratePaperRequest(BaseModel):
    """What the frontend sends to assemble a custom paper from chosen topics."""

    format: str = "past-papers"
    qualification: str = "gcse"
    board: str = "edexcel"
    subject: str = "maths"
    tier: Tier = "higher"
    calculator: bool = False
    topics: list[str] = Field(default_factory=list, description="Topic slugs to include.")
    target_marks: int = Field(default=80, ge=1, le=300)
    include_answers: bool = True
    seed: Optional[int] = None
