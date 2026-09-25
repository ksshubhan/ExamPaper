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
from .context import make_item, mk_part, pick, reason_step, two_names

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
        tier=(req.tier or "higher"),
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
        if sympy.igcd(m, n) != 1:  # real papers give ratios in simplest form
            continue
        per_part = rng.randint(4, 40)
        total = per_part * (m + n)
        share_m, share_n = per_part * m, per_part * n
        if share_m + share_n != total:  # sympy-free invariant check
            continue

        a_name, b_name = two_names(rng)
        stem = f"{a_name} and {b_name} share £{total} in the ratio {m} : {n}."
        ms = [
            MarkSchemeStep(
                code="M1", mark_type="M",
                description=f"for {total} ÷ ({m} + {n}) (= {per_part})",
                working=None,
            ),
            MarkSchemeStep(
                code="M1", mark_type="M",
                description=f"for {per_part} × {m} and {per_part} × {n}",
                working=None,
            ),
            MarkSchemeStep(
                code="A1", mark_type="A", description="cao (both values)",
                working=f"£{share_m} and £{share_n}",
            ),
        ]
        working_a = (
            f"Total parts = {m} + {n} = {m + n}\n"
            f"One part = £{total} ÷ {m + n} = £{per_part}\n"
            f"{a_name}: £{per_part} × {m} = £{share_m},  "
            f"{b_name}: £{per_part} × {n} = £{share_n}"
        )
        prompt_a = f"Work out how much {a_name} and {b_name} each receive."
        answer_a = f"{a_name} £{share_m}, {b_name} £{share_n}"

        # ~40%: add (b) — what fraction of the total is one person's share.
        if rng.random() < 0.4:
            frac = sympy.Rational(m, m + n)
            part_a = mk_part(label="a", prompt=prompt_a, marks=3, answer=answer_a,
                             working=working_a, mark_scheme=ms)
            part_b = mk_part(
                label="b",
                prompt=f"What fraction of the £{total} does {a_name} receive? "
                f"Give your answer in its simplest form.",
                marks=1, answer=f"{frac.p}/{frac.q}",
                working=f"{a_name}'s share = {m}/({m}+{n}) = {frac.p}/{frac.q}",
                mark_scheme=[
                    MarkSchemeStep(code="B1", mark_type="B", description="cao",
                                   working=f"{frac.p}/{frac.q}")
                ],
            )
            return make_item(
                req, seed, archetype="share-ratio", topic="Ratio",
                topic_slug="ratio", strand="Ratio & proportion", spec_ref="R5",
                grade_band="3-5", stem=stem, parts=[part_a, part_b],
            )

        return _item(
            req, seed, archetype="share-ratio", topic="Ratio", topic_slug="ratio",
            strand="Ratio & proportion", spec_ref="R5", grade_band="3-4", marks=3,
            stem=stem, prompt=prompt_a, answer=answer_a, working=working_a,
            mark_scheme=ms,
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
        stem = f"Work out  {n1}/{d1} {op_word} {n2}/{d2}"
        working = (
            f"{n1}/{d1} {op_word} {n2}/{d2} = {cn1}/{common} {op_word} {cn2}/{common}\n"
            f"= {combined}/{common}\n= {ans}"
        )
        ms = [
            MarkSchemeStep(
                code="M1", mark_type="M",
                description=f"for a common denominator: {cn1}/{common} {op_word} "
                f"{cn2}/{common}",
                working=None,
            ),
            MarkSchemeStep(
                code="M1", mark_type="M",
                description=f"for {cn1}/{common} {op_word} {cn2}/{common} "
                f"= {combined}/{common}",
                working=None,
            ),
            MarkSchemeStep(
                code="A1", mark_type="A",
                description="for the answer in its simplest form", working=ans,
            ),
        ]

        # ~30%: add (b) — spot the classic "added across" error on the same sum.
        if rng.random() < 0.3:
            name = pick(rng, ["Kevin", "Sara", "Owen", "Priya", "Jack"])
            wrong_num = n1 + n2 if op == "+" else n1 - n2
            wrong_den = d1 + d2
            wrong = f"{n1}/{d1} {op_word} {n2}/{d2} = {wrong_num}/{wrong_den}"
            part_a = mk_part(
                label="a",
                prompt=f"Work out  {n1}/{d1} {op_word} {n2}/{d2}\n"
                "Give your answer as a fraction in its simplest form.",
                marks=3, answer=ans, working=working, mark_scheme=ms,
            )
            mistake = (
                f"{name} added the numerators and added the denominators instead of "
                f"writing the fractions over a common denominator."
                if op == "+" else
                f"{name} subtracted the numerators and the denominators instead of "
                f"writing the fractions over a common denominator."
            )
            part_b = mk_part(
                label="b",
                prompt=(
                    f"{name} was asked to work out  {n1}/{d1} {op_word} {n2}/{d2}\n"
                    f"Here is {name}'s working.\n{wrong}\n"
                    f"{name}'s answer is wrong.\nWhat mistake has {name} made?"
                ),
                marks=1, answer=mistake, working=wrong,
                mark_scheme=[
                    MarkSchemeStep(code="B1", mark_type="B",
                                   description="for identifying the error (no common "
                                   "denominator used)", working=None)
                ],
            )
            return make_item(
                req, seed, archetype="fraction-arithmetic", topic="Fractions",
                topic_slug="fractions", strand="Number", spec_ref="N8",
                grade_band="3-5", ao="AO2", stem="", parts=[part_a, part_b],
            )

        return _item(
            req, seed, archetype="fraction-arithmetic", topic="Fractions",
            topic_slug="fractions", strand="Number", spec_ref="N8", grade_band="3-4",
            marks=3, stem=stem,
            prompt="Give your answer as a fraction in its simplest form.",
            answer=ans, working=working, mark_scheme=ms,
        )
    raise RuntimeError("fraction-arithmetic generator failed to produce a valid item.")
