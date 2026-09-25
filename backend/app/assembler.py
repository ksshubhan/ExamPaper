"""Paper assembly engine.

Given a set of chosen topics and a mark target, assemble an ordered, verified
paper that reads like a real Edexcel paper rather than a worksheet:

  * a Higher difficulty floor — nothing below grade 4 on a Higher paper;
  * an explicit target of ~21 questions at *exactly* the mark total (mean ~3.8),
    with at least two 5-mark questions (the multi-part items a real paper leans
    on); and
  * a final easy -> hard sort to reproduce the exam difficulty ramp.
"""

from __future__ import annotations

import json
import math
import uuid
from collections import Counter
from pathlib import Path
from random import Random

from .generators.registry import reasoning_steps, specs_for_topic
from .schema import GenerateRequest, GeneratePaperRequest, Item, Paper

_MAX_QUESTIONS = 40  # safety cap on paper length
_GUARD = 4000  # safety cap on assembly attempts

# The paper blueprint is pure data — question count, total, and the real-paper
# mark distribution all live here, never hardcoded in the assembly code.
_BLUEPRINT = json.loads(
    (Path(__file__).parent / "blueprints" / "edexcel_higher.json").read_text()
)
_DIST: list[tuple[int, float]] = sorted(
    (int(k), float(v)) for k, v in _BLUEPRINT["mark_distribution"].items()
)


def _sample_mark(rng: Random) -> int:
    """Draw a question's mark value from the blueprint distribution."""
    r = rng.random()
    cum = 0.0
    for m, w in _DIST:
        cum += w
        if r <= cum:
            return m
    return _DIST[-1][0]


def _grade_low(grade_band: str) -> int:
    """Lower bound of a grade band like '4-6' (-> 4) for ramp ordering."""
    try:
        return int(grade_band.split("-")[0])
    except (ValueError, AttributeError):
        return 99


def _band_of(grade_low: int, foundation: bool) -> int:
    """Difficulty band for the ramp: 0 easiest .. 2 hardest."""
    if foundation:
        return 0 if grade_low <= 3 else 1
    return 0 if grade_low <= 5 else 1 if grade_low <= 7 else 2


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
    foundation = req.tier == "foundation"

    # Candidate pool: only topics we can actually generate for this paper type.
    pool: dict[str, list] = {}
    tier_dropped: list[str] = []       # had questions, but all above Foundation tier
    for slug in req.topics:
        specs = specs_for_topic(slug, paper_calculator=req.calculator)
        if foundation:
            kept = [s for s in specs if _grade_low(s.grade_band) <= 5]
            if specs and not kept:
                tier_dropped.append(slug)
            specs = kept
        if specs:
            pool[slug] = specs
    dropped = [s for s in req.topics if s not in pool and s not in tier_dropped]
    if dropped:
        notes.append(
            "Skipped topics with no available questions for this paper type: "
            + ", ".join(dropped)
            + "."
        )
    if tier_dropped:
        notes.append(
            f"{len(tier_dropped)} selected topic(s) are above Foundation tier and were "
            "left out of this paper."
        )

    items: list[Item] = []
    achieved = 0

    if pool:
        specs = [sp for slug in pool for sp in pool[slug]]

        # Higher difficulty floor: nothing below grade 4 appears on a Higher paper.
        # (Only applied when it still leaves material to build from.)
        if not foundation:
            floored = [s for s in specs if _grade_low(s.grade_band) >= 4]
            if floored:
                specs = floored

        target = req.target_marks

        # Band the archetypes by difficulty for the ramp, and give each band a
        # share of the marks (front-loaded toward the middle, as a real paper is).
        bands: dict[int, list] = {0: [], 1: [], 2: []}
        for s in specs:
            bands[_band_of(_grade_low(s.grade_band), foundation)].append(s)
        for b in bands.values():
            rng.shuffle(b)
        present = [b for b in (0, 1, 2) if bands[b]]
        weights = {0: 0.5, 1: 0.5, 2: 0.0} if foundation else {0: 0.34, 1: 0.40, 2: 0.26}
        wsum = sum(weights[b] for b in present) or 1
        band_target = {b: target * weights[b] / wsum for b in present}
        band_marks = {0: 0, 1: 0, 2: 0}
        used_arch: set[str] = set()  # no archetype may appear twice in one paper
        mark_counts: Counter = Counter()  # how many questions at each mark value
        # Keep any one mark value below half the paper, so it never reads as a
        # worksheet of identical questions (real papers spread 2..6).
        _expected_q = max(1, round(target / 3.5))
        _value_cap = max(3, int(_expected_q * 0.40))  # keep any value well under half
        _count_max = max(1, round(
            _BLUEPRINT["question_count"]["max"] * target / _BLUEPRINT["total_marks"]))

        def make(spec):
            qreq = GenerateRequest(
                format=req.format, qualification=req.qualification, board=req.board,
                subject=req.subject, archetype=spec.archetype,
                calculator=req.calculator, tier=req.tier, seed=rng.randrange(2**31),
            )
            return spec.build(qreq)  # may raise on a bad sample

        def floor_ok(it: Item) -> bool:
            # Enforce the Higher grade-4 floor on the *built* item — a few
            # archetypes (e.g. integer-mode Pythagoras) carry a lower item grade
            # band than their registry entry, and must not slip onto a Higher paper.
            return foundation or _grade_low(it.metadata.grade_band) >= 4

        def structure_ok(it: Item, spec) -> bool:
            # A question's marks must be earned by its structure (Task 5). Early
            # slots ~ grade < 7, late slots ~ grade >= 7 (the ramp puts them there).
            marks = it.total_marks
            parts = len(it.parts)
            steps = reasoning_steps(spec.archetype)
            grade = _grade_low(it.metadata.grade_band)
            if marks > steps + parts - 1:
                return False  # more marks than there is work in the question
            if grade < 7 and marks >= 5 and parts < 2:
                return False  # a big early question must be multi-part
            if grade >= 7 and marks >= 4 and steps < 3:
                return False  # a 4+ mark late question must have real depth
            return True

        def fits(m: int, remaining: int) -> bool:
            # Never overshoot the target, and never leave a gap of exactly 1
            # (which no question can fill) — so the paper lands on target exactly.
            return m <= remaining and (remaining - m == 0 or remaining - m >= 2)

        def add(it: Item, b: int, spec) -> None:
            nonlocal achieved
            items.append(it)
            achieved += it.total_marks
            band_marks[b] += it.total_marks
            used_arch.add(spec.archetype)  # the registry id, so no archetype repeats
            mark_counts[it.total_marks] += 1

        def try_place(spec, remaining, respect_cap=True):
            """Build spec and return the item if it can be placed: an unused
            archetype (optionally whose mark value isn't already over-represented)
            that clears the grade floor and structure rule and fits exactly."""
            if spec.archetype in used_arch:
                return None
            try:
                it = make(spec)
            except Exception:
                return None
            if respect_cap and mark_counts[it.total_marks] >= _value_cap:
                return None
            if floor_ok(it) and structure_ok(it, spec) and fits(it.total_marks, remaining):
                return it
            return None

        # --- Phase 0: seed the paper's signature big questions — one 6-mark item
        # (if the pool has one) and one hard-band 5+ item — so the ramp spans the
        # full range and the paper always carries a multi-part showpiece. --------
        if target >= 50:
            six = sorted((s for s in specs if s.typical_marks >= 6),
                         key=lambda s: _grade_low(s.grade_band))
            hard5 = sorted(
                (s for s in specs if s.typical_marks >= 5
                 and _band_of(_grade_low(s.grade_band), foundation) == 2),
                key=lambda s: _grade_low(s.grade_band))
            for pick in (six[:1] + hard5[-1:]):
                it = try_place(pick, target - achieved)
                if it:
                    add(it, _band_of(_grade_low(pick.grade_band), foundation), pick)

        # --- Phase 1: fill to exactly the target. Each slot's mark value is drawn
        # from the blueprint's real-paper distribution; we place a not-yet-used
        # archetype nearest that size, drawing from the band furthest below its
        # ramp share, and always finishing exactly on target. --------------------
        guard = 0
        while achieved < target and len(items) < _MAX_QUESTIONS and guard < _GUARD:
            guard += 1
            remaining = target - achieved
            m_target = _sample_mark(rng)
            # Keep the paper on pace to finish within the blueprint's question
            # ceiling: if the marks left need a higher average than the mean, bias
            # this slot up so the paper doesn't spill past ~24 questions.
            slots_left = _count_max - len(items)
            if slots_left >= 1:
                needed = remaining / slots_left
                if needed > 3.2:
                    m_target = max(m_target, min(6, math.ceil(needed)))
            else:
                m_target = min(6, remaining)
            below = [b for b in present if band_marks[b] < band_target[b]]
            b = max(below or present, key=lambda b: band_target[b] - band_marks[b])

            picked = None

            def order_key(s):
                # Deprioritise a mark value that already fills its share of the
                # paper, then prefer the size nearest the sampled target.
                capped = 1 if mark_counts[s.typical_marks] >= _value_cap else 0
                return (capped, abs(s.typical_marks - m_target))

            for bb in [b] + [x for x in present if x != b]:
                for spec in sorted(bands[bb], key=order_key):
                    it = try_place(spec, remaining)
                    if it:
                        picked = (it, bb, spec)
                        break
                if picked:
                    break
            if picked is None:
                # Exact-finish fallback: still an unused archetype (no repeats),
                # but relax the per-value cap so the paper lands precisely on target.
                for spec in sorted((s for bb in present for s in bands[bb]),
                                   key=lambda s: abs(s.typical_marks - remaining)):
                    it = try_place(spec, remaining, respect_cap=False)
                    if it:
                        picked = (it, _band_of(_grade_low(spec.grade_band),
                                               foundation), spec)
                        break
            if picked is None:
                break  # nothing unused fits the remaining gap — stop (shortfall)

            it, bb, spec = picked
            add(it, bb, spec)

        # Warn only when a paper is genuinely repetitive — any one question type
        # appearing 4+ times — not for the unavoidable repeats of a full paper.
        counts = Counter(it.metadata.archetype for it in items)
        if counts and max(counts.values()) >= 4:
            notes.append(
                "Some question types repeat several times — add more topics "
                "(or lower the mark target) for greater variety."
            )
        # If the selection has no hard material, the paper can't ramp to the top.
        # (Expected for Foundation, which is capped at grade 5 — so don't warn.)
        if 2 not in present and req.target_marks >= 40 and not foundation:
            notes.append(
                "No grade 7–9 topics selected, so this paper won't reach exam-level "
                "difficulty at the end — add some harder topics for a full ramp."
            )
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
