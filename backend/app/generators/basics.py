"""Starter generators for non-geometry strands.

These give an assembled paper genuine variety beyond Pythagoras. Each follows
the same contract as the Pythagoras generator: deterministic from a seed, the
answer derived and re-checked with sympy, a faithful Edexcel-style mark scheme.
None of them needs a diagram.
"""

from __future__ import annotations

import uuid
from random import Random
from typing import Optional

import sympy

from ..schema import GenerateRequest, Item, MarkSchemeStep, Metadata, Part

_MAX_ATTEMPTS = 200


def _seed(req: GenerateRequest) -> int:
    return req.seed if req.seed is not None else uuid.uuid4().int % (2**31)


def _sign(n: int) -> str:
    """Render '+ 3' or '- 3' for inline equation display."""
    return f"+ {n}" if n >= 0 else f"- {abs(n)}"


def _item(
    req: GenerateRequest,
    seed: int,
    *,
    archetype: str,
    topic: str,
    topic_slug: str,
    strand: str,
    spec_ref: str,
    grade_band: str,
    marks: int,
    stem: str,
    prompt: str,
    answer: str,
    working: str,
    mark_scheme: list[MarkSchemeStep],
) -> Item:
    return Item(
        id=f"{topic_slug}-{uuid.uuid4().hex[:10]}",
        format=req.format,
        qualification=req.qualification,
        board=req.board,
        subject=req.subject,
        tier="higher",
        calculator=bool(req.calculator),
        total_marks=marks,
        stem=stem,
        parts=[
            Part(
                label="",
                prompt=prompt,
                marks=marks,
                answer=answer,
                answer_tolerance=None,
                working=working,
                mark_scheme=mark_scheme,
            )
        ],
        diagram=None,
        metadata=Metadata(
            archetype=archetype,
            spec_ref=spec_ref,
            topic=topic,
            topic_slug=topic_slug,
            strand=strand,
            ao="AO1",
            grade_band=grade_band,
            seed=seed,
        ),
    )


# --------------------------------------------------------------------------- #
# Algebra: solve a linear equation  ax + b = c   (integer solution)
# --------------------------------------------------------------------------- #
def build_linear_equation(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        a = rng.randint(2, 9)
        x = rng.randint(2, 12)
        b = rng.randint(-12, 20)
        if b == 0:
            continue
        c = a * x + b
        # Verify with sympy.
        sym_x = sympy.Symbol("x")
        sol = sympy.solve(sympy.Eq(a * sym_x + b, c), sym_x)
        if sol != [x]:
            continue
        eqn = f"{a}x {_sign(b)} = {c}"
        step1_rhs = c - b
        working = f"{a}x = {c} {_sign(-b)}\n{a}x = {step1_rhs}\nx = {step1_rhs} ÷ {a} = {x}"
        return _item(
            req,
            seed,
            archetype="linear-equation",
            topic="Linear equations",
            topic_slug="linear-equations",
            strand="Algebra",
            spec_ref="A17",
            grade_band="3-4",
            marks=2,
            stem=f"Solve  {eqn}",
            prompt="",
            answer=f"x = {x}",
            working=working,
            mark_scheme=[
                MarkSchemeStep(
                    code="M1",
                    mark_type="M",
                    description="for a correct first step (isolating the x term)",
                    working=f"{a}x = {step1_rhs}",
                ),
                MarkSchemeStep(
                    code="A1",
                    mark_type="A",
                    description="cao",
                    working=f"x = {x}",
                ),
            ],
        )
    raise RuntimeError("linear-equation generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Ratio: share an amount of money in the ratio m : n
# --------------------------------------------------------------------------- #
def build_share_ratio(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        m = rng.randint(1, 7)
        n = rng.randint(1, 7)
        if m == n:
            continue
        per_part = rng.randint(4, 40)
        total = per_part * (m + n)
        share_m, share_n = per_part * m, per_part * n
        if share_m + share_n != total:  # sympy-free invariant check
            continue
        return _item(
            req,
            seed,
            archetype="share-ratio",
            topic="Ratio",
            topic_slug="ratio",
            strand="Ratio & proportion",
            spec_ref="R5",
            grade_band="3-4",
            marks=3,
            stem=f"Share £{total} in the ratio {m} : {n}",
            prompt="",
            answer=f"£{share_m} and £{share_n}",
            working=(
                f"Total parts = {m} + {n} = {m + n}\n"
                f"One part = £{total} ÷ {m + n} = £{per_part}\n"
                f"£{per_part} × {m} = £{share_m},  £{per_part} × {n} = £{share_n}"
            ),
            mark_scheme=[
                MarkSchemeStep(
                    code="M1",
                    mark_type="M",
                    description="for finding the value of one part",
                    working=f"{total} ÷ ({m} + {n}) (= {per_part})",
                ),
                MarkSchemeStep(
                    code="M1",
                    mark_type="M",
                    description="for scaling by each share",
                    working=f"{per_part} × {m} and {per_part} × {n}",
                ),
                MarkSchemeStep(
                    code="A1",
                    mark_type="A",
                    description="cao (both values)",
                    working=f"£{share_m} and £{share_n}",
                ),
            ],
        )
    raise RuntimeError("share-ratio generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Number: add/subtract two fractions, answer in simplest form
# --------------------------------------------------------------------------- #
def _frac_str(r: sympy.Rational) -> str:
    """Render a positive rational as 'n/d', an integer, or a mixed number."""
    if r.q == 1:
        return str(r.p)
    if r.p > r.q:
        whole, rem = divmod(r.p, r.q)
        return f"{whole} {rem}/{r.q}"
    return f"{r.p}/{r.q}"


def build_fraction_arithmetic(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        d1 = rng.randint(2, 9)
        d2 = rng.randint(2, 9)
        if d1 == d2:
            continue
        n1 = rng.randint(1, d1 - 1)
        n2 = rng.randint(1, d2 - 1)
        op = rng.choice(["+", "-"])
        f1, f2 = sympy.Rational(n1, d1), sympy.Rational(n2, d2)
        result = f1 + f2 if op == "+" else f1 - f2
        if result <= 0:
            continue
        common = d1 * d2 // sympy.igcd(d1, d2)
        cn1, cn2 = n1 * (common // d1), n2 * (common // d2)
        combined = cn1 + cn2 if op == "+" else cn1 - cn2
        ans = _frac_str(result)
        # Skip trivially-already-simplified or whole-number results for interest.
        if result.q == 1:
            continue
        op_word = "+" if op == "+" else "−"
        return _item(
            req,
            seed,
            archetype="fraction-arithmetic",
            topic="Fractions",
            topic_slug="fractions",
            strand="Number",
            spec_ref="N8",
            grade_band="3-4",
            marks=3,
            stem=f"Work out  {n1}/{d1} {op_word} {n2}/{d2}",
            prompt="Give your answer as a fraction in its simplest form.",
            answer=ans,
            working=(
                f"{n1}/{d1} {op_word} {n2}/{d2} = {cn1}/{common} {op_word} {cn2}/{common}\n"
                f"= {combined}/{common}\n"
                f"= {ans}"
            ),
            mark_scheme=[
                MarkSchemeStep(
                    code="M1",
                    mark_type="M",
                    description="for writing both fractions over a common denominator",
                    working=f"{cn1}/{common} {op_word} {cn2}/{common}",
                ),
                MarkSchemeStep(
                    code="M1",
                    mark_type="M",
                    description="for a correct single fraction",
                    working=f"{combined}/{common}",
                ),
                MarkSchemeStep(
                    code="A1",
                    mark_type="A",
                    description="for the answer in its simplest form",
                    working=ans,
                ),
            ],
        )
    raise RuntimeError("fraction-arithmetic generator failed to produce a valid item.")
