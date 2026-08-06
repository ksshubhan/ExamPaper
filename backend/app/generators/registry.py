"""Generator registry — the catalogue of question archetypes.

Each archetype declares its classification (strand / topic / spec ref / grade
band / marks / calculator requirement) alongside its builder. From this single
list we derive: the `/topics` picker, the paper assembler's candidate pool, and
the back-compatible single-question `/generate` lookup.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..schema import GenerateRequest, Item
from .basics import (
    build_fraction_arithmetic,
    build_linear_equation,
    build_share_ratio,
)
from .pythagoras import build_pythagoras_item

Generator = Callable[[GenerateRequest], Item]

# Display order for strands in the topic picker.
STRAND_ORDER = [
    "Number",
    "Algebra",
    "Ratio & proportion",
    "Geometry & measures",
    "Probability",
    "Statistics",
]


@dataclass(frozen=True)
class ArchetypeSpec:
    archetype: str
    topic: str
    topic_slug: str
    strand: str
    spec_ref: str
    grade_band: str
    typical_marks: int
    requires_calculator: bool  # if True, excluded from non-calculator papers
    build: Generator


ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec(
        archetype="fraction-arithmetic",
        topic="Fractions",
        topic_slug="fractions",
        strand="Number",
        spec_ref="N8",
        grade_band="3-4",
        typical_marks=3,
        requires_calculator=False,
        build=build_fraction_arithmetic,
    ),
    ArchetypeSpec(
        archetype="linear-equation",
        topic="Linear equations",
        topic_slug="linear-equations",
        strand="Algebra",
        spec_ref="A17",
        grade_band="3-4",
        typical_marks=2,
        requires_calculator=False,
        build=build_linear_equation,
    ),
    ArchetypeSpec(
        archetype="share-ratio",
        topic="Ratio",
        topic_slug="ratio",
        strand="Ratio & proportion",
        spec_ref="R5",
        grade_band="3-4",
        typical_marks=3,
        requires_calculator=False,
        build=build_share_ratio,
    ),
    ArchetypeSpec(
        archetype="pythagoras-hypotenuse",
        topic="Pythagoras' theorem",
        topic_slug="pythagoras",
        strand="Geometry & measures",
        spec_ref="G20",
        grade_band="4-6",
        typical_marks=3,
        requires_calculator=False,
        build=build_pythagoras_item,
    ),
    ArchetypeSpec(
        archetype="pythagoras-shorter-side",
        topic="Pythagoras' theorem",
        topic_slug="pythagoras",
        strand="Geometry & measures",
        spec_ref="G20",
        grade_band="4-6",
        typical_marks=3,
        requires_calculator=False,
        build=build_pythagoras_item,
    ),
]

_BY_ARCHETYPE: dict[str, ArchetypeSpec] = {s.archetype: s for s in ARCHETYPES}

DEFAULT_ARCHETYPE = "pythagoras-hypotenuse"


def get_generator(archetype: str | None) -> Generator:
    """Return the requested generator, or the default if unset/unknown."""
    spec = _BY_ARCHETYPE.get(archetype or DEFAULT_ARCHETYPE)
    return spec.build if spec else build_pythagoras_item


def specs_for_topic(topic_slug: str, *, paper_calculator: bool) -> list[ArchetypeSpec]:
    """Archetypes under a topic, filtered for the paper's calculator setting."""
    return [
        s
        for s in ARCHETYPES
        if s.topic_slug == topic_slug
        and (paper_calculator or not s.requires_calculator)
    ]


def topics_catalog() -> list[dict]:
    """Pickable topics grouped by strand, each with an archetype count.

    The UI only ever offers topics we can actually generate.
    """
    # Collapse archetypes into topics (a topic may have several archetypes).
    topics: dict[str, dict] = {}
    for s in ARCHETYPES:
        t = topics.setdefault(
            s.topic_slug,
            {
                "slug": s.topic_slug,
                "name": s.topic,
                "strand": s.strand,
                "spec_ref": s.spec_ref,
                "grade_band": s.grade_band,
                "typical_marks": s.typical_marks,
                "archetype_count": 0,
                "requires_calculator": True,
            },
        )
        t["archetype_count"] += 1
        # A topic is non-calc-friendly if ANY of its archetypes is.
        if not s.requires_calculator:
            t["requires_calculator"] = False

    # Group by strand in display order.
    grouped: list[dict] = []
    for strand in STRAND_ORDER:
        in_strand = sorted(
            (t for t in topics.values() if t["strand"] == strand),
            key=lambda t: t["name"],
        )
        if in_strand:
            grouped.append({"strand": strand, "topics": in_strand})
    return grouped
