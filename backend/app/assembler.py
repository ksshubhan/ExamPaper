"""Paper assembly engine.

Given a set of chosen topics and a mark target, assemble an ordered, verified
paper: fill toward the target while spreading across the selected topics, then
sort easy -> hard to reproduce the real Edexcel difficulty ramp.
"""

from __future__ import annotations

import uuid
from random import Random

from .generators.registry import specs_for_topic
from .schema import GenerateRequest, GeneratePaperRequest, Item, Paper

_MAX_QUESTIONS = 40  # safety cap on paper length
_GUARD = 2000  # safety cap on assembly attempts


def _grade_low(grade_band: str) -> int:
    """Lower bound of a grade band like '4-6' (-> 4) for ramp ordering."""
    try:
        return int(grade_band.split("-")[0])
    except (ValueError, AttributeError):
        return 99


def _duration_minutes(marks: int) -> int:
    """Edexcel is ~90 min per 80 marks; round to the nearest 5."""
    raw = marks * 90 / 80
    return int(round(raw / 5.0) * 5)


def _title(req: GeneratePaperRequest) -> str:
    tier = "Higher" if req.tier == "higher" else "Foundation"
    calc = "Calculator" if req.calculator else "Non-calculator"
    return f"Edexcel GCSE (9-1) Mathematics — {tier} Tier ({calc})"


def _instructions(calculator: bool) -> list[str]:
    rules = [
        "Use black ink or ball-point pen.",
        "Answer all questions.",
        "Answer the questions in the spaces provided — there may be more space "
        "than you need.",
        "You must show all your working.",
        "Diagrams are NOT accurately drawn, unless otherwise indicated.",
    ]
    rules.append(
        "You may use a calculator." if calculator else "You must NOT use a calculator."
    )
    return rules


def build_paper(req: GeneratePaperRequest) -> Paper:
    seed = req.seed if req.seed is not None else uuid.uuid4().int % (2**31)
    rng = Random(seed)
    notes: list[str] = []

    # Candidate pool: only topics we can actually generate for this paper type.
    pool: dict[str, list] = {}
    for slug in req.topics:
        specs = specs_for_topic(slug, paper_calculator=req.calculator)
        if specs:
            pool[slug] = specs
    dropped = [s for s in req.topics if s not in pool]
    if dropped:
        notes.append(
            "Skipped topics with no available questions for this paper type: "
            + ", ".join(dropped)
            + "."
        )

    items: list[Item] = []
    achieved = 0

    if pool:
        cycle = list(pool.keys())
        i = 0
        guard = 0
        while (
            achieved < req.target_marks
            and len(items) < _MAX_QUESTIONS
            and guard < _GUARD
        ):
            guard += 1
            slug = cycle[i % len(cycle)]
            i += 1
            spec = rng.choice(pool[slug])
            qreq = GenerateRequest(
                format=req.format,
                qualification=req.qualification,
                board=req.board,
                subject=req.subject,
                archetype=spec.archetype,
                calculator=req.calculator,
                seed=rng.randrange(2**31),
            )
            try:
                item = spec.build(qreq)
            except Exception:  # a bad sample shouldn't sink the whole paper
                continue
            items.append(item)
            achieved += item.total_marks
    else:
        notes.append("No generatable topics were selected.")

    # Difficulty ramp: easy -> hard, then shorter questions first within a band.
    items.sort(key=lambda it: (_grade_low(it.metadata.grade_band), it.total_marks))

    if 0 < achieved < req.target_marks:
        notes.append(
            f"Reached {achieved} of {req.target_marks} marks from the selected "
            f"topics — add more topics for a longer paper."
        )

    return Paper(
        id=f"paper-{uuid.uuid4().hex[:10]}",
        format=req.format,
        qualification=req.qualification,
        board=req.board,
        subject=req.subject,
        title=_title(req),
        tier=req.tier,
        calculator=req.calculator,
        target_marks=req.target_marks,
        total_marks=achieved,
        duration_minutes=_duration_minutes(achieved),
        instructions=_instructions(req.calculator),
        include_answers=req.include_answers,
        questions=items,
        notes=notes,
        seed=seed,
    )
