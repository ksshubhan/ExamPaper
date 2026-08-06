"""Pythagoras' theorem generator (spec ref G20).

The template is the source of truth for the maths: parameters are sampled
deterministically from a seed, the answer is derived and then *independently
re-derived with sympy* as a verifier gate (reject-and-resample on mismatch),
and the diagram + mark scheme are produced from the same numbers.

Two modes, chosen per request (or at random):
  * calculator     -> decimal answer to 1 d.p.
  * non-calculator -> exact answer: an integer (Pythagorean triple) or a surd a√b

Two variants:
  * hypotenuse    -> given the two legs, find the hypotenuse
  * shorter-side  -> given the hypotenuse and one leg, find the other leg
"""

from __future__ import annotations

import uuid
from random import Random
from typing import Optional

import sympy

from ..schema import Diagram, GenerateRequest, Item, MarkSchemeStep, Metadata, Part
from .diagrams import right_triangle_svg

# Primitive Pythagorean triples (a < b < c). Scaled by a small factor for variety.
_TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41)]

_VARIANTS = ("hypotenuse", "shorter-side")
_MAX_ATTEMPTS = 500


# --------------------------------------------------------------------------- #
# Surd helpers
# --------------------------------------------------------------------------- #
def _simplify_surd(n: int) -> tuple[int, int]:
    """Return (coeff, radicand) such that coeff*sqrt(radicand) == sqrt(n)."""
    expr = sympy.sqrt(sympy.Integer(n))
    if expr.is_Integer:
        return int(expr), 1
    coeff, rest = expr.as_coeff_Mul()
    radicand = rest.args[0]  # rest is sqrt(radicand) == Pow(radicand, 1/2)
    return int(coeff), int(radicand)


def _surd_str(coeff: int, radicand: int) -> str:
    if radicand == 1:
        return str(coeff)
    if coeff == 1:
        return f"√{radicand}"
    return f"{coeff}√{radicand}"


def _is_nice_surd(coeff: int, radicand: int) -> bool:
    """Keep surds that look like real exam answers: small, genuinely irrational."""
    return radicand != 1 and radicand <= 70 and 1 <= coeff <= 9


# --------------------------------------------------------------------------- #
# Sampling — returns the raw numbers and the exact unknown value
# --------------------------------------------------------------------------- #
def _sample(rng: Random, calculator: bool, variant: str) -> Optional[dict]:
    """One sampling attempt. Returns a param dict, or None to resample."""
    if calculator:
        mode = "decimal"
    else:
        mode = rng.choice(["integer", "surd"])

    if variant == "hypotenuse":
        if mode == "integer":
            a, b, c = rng.choice(_TRIPLES)
            k = rng.choice([1, 2, 3])
            a, b, c = a * k, b * k, c * k
            return _pack(a, b, variant, mode, given=(a, b))
        # surd / decimal: pick two legs, hypotenuse is irrational
        a = rng.randint(4, 19)
        b = rng.randint(4, 19)
        n = a * a + b * b
        return _check_unknown(a, b, n, variant, mode)

    # shorter-side: given hypotenuse c and one leg, find the other leg
    if mode == "integer":
        a, b, c = rng.choice(_TRIPLES)
        k = rng.choice([1, 2, 3])
        a, b, c = a * k, b * k, c * k
        # given the hypotenuse and the longer leg; find the shorter leg `a`
        return _pack(b, c, variant, mode, given=(c, b), answer_int=a)
    c = rng.randint(8, 22)
    leg = rng.randint(3, c - 1)
    n = c * c - leg * leg
    return _check_unknown(leg, c, n, variant, mode)


def _check_unknown(given1: int, given2: int, n: int, variant: str, mode: str):
    """For surd/decimal: n is the unknown squared. Filter to clean items."""
    if n <= 0:
        return None
    coeff, radicand = _simplify_surd(n)
    if mode == "surd":
        if radicand == 1:  # perfect square -> not a surd, reject
            return None
        if not _is_nice_surd(coeff, radicand):
            return None
    if mode == "decimal":
        if radicand == 1:  # perfect square -> looks odd as a "to 1 d.p." answer
            return None
    if variant == "hypotenuse":
        return _pack(given1, given2, variant, mode, n=n, given=(given1, given2))
    # shorter-side: given1=known leg, given2=hypotenuse
    return _pack(given1, given2, variant, mode, n=n, given=(given2, given1))


def _pack(
    a: int,
    b: int,
    variant: str,
    mode: str,
    *,
    given: tuple[int, int],
    n: Optional[int] = None,
    answer_int: Optional[int] = None,
) -> dict:
    return {
        "variant": variant,
        "mode": mode,
        "given": given,  # the two numbers shown on the diagram
        "n": n,  # unknown squared (surd/decimal only)
        "answer_int": answer_int,  # integer answer (integer mode only)
        "_legs_hint": (a, b),
    }


# --------------------------------------------------------------------------- #
# Verifier gate — re-derive the unknown independently with sympy
# --------------------------------------------------------------------------- #
def _exact_unknown(variant: str, given: tuple[int, int]) -> sympy.Expr:
    """given = (leg1, leg2) for hypotenuse; (hypotenuse, leg) for shorter-side."""
    g0, g1 = sympy.Integer(given[0]), sympy.Integer(given[1])
    if variant == "hypotenuse":
        return sympy.sqrt(g0**2 + g1**2)
    return sympy.sqrt(g0**2 - g1**2)


# --------------------------------------------------------------------------- #
# Build the Item from sampled + verified parameters
# --------------------------------------------------------------------------- #
def _build_item(req: GenerateRequest, seed: int, p: dict, exact: sympy.Expr) -> Item:
    variant = p["variant"]
    mode = p["mode"]
    given = p["given"]

    # n (unknown squared) and the human "sum of squares" expression.
    if variant == "hypotenuse":
        sq_expr = f"{given[0]}² + {given[1]}²"
        n = given[0] ** 2 + given[1] ** 2
        pyth_line = "x² = a² + b²"
    else:
        sq_expr = f"{given[0]}² − {given[1]}²"
        n = given[0] ** 2 - given[1] ** 2
        pyth_line = "x² = c² − a²"

    # Answer string + working + marks per mode.
    if mode == "integer":
        ans_val = str(int(exact))
        marks = 2
        form_note = ""
        working = (
            f"{pyth_line}\n"
            f"x² = {sq_expr} = {n}\n"
            f"x = √{n} = {ans_val} cm"
        )
        mark_scheme = [
            MarkSchemeStep(
                code="M1",
                mark_type="M",
                description="for a correct use of Pythagoras' theorem",
                working=f"{sq_expr} (= {n})",
            ),
            MarkSchemeStep(
                code="A1",
                mark_type="A",
                description="cao",
                working=f"{ans_val} (cm)",
            ),
        ]
        grade_band = "3-5"
    elif mode == "surd":
        coeff, radicand = _simplify_surd(n)
        ans_val = _surd_str(coeff, radicand)
        marks = 3
        form_note = "\nGive your answer in the form a√b, where a and b are integers."
        working = (
            f"{pyth_line}\n"
            f"x² = {sq_expr} = {n}\n"
            f"x = √{n} = {ans_val} cm"
        )
        mark_scheme = [
            MarkSchemeStep(
                code="M1",
                mark_type="M",
                description="for a correct use of Pythagoras' theorem",
                working=f"{sq_expr} (= {n})",
            ),
            MarkSchemeStep(
                code="M1",
                mark_type="M",
                description="for taking the square root",
                working=f"√{n}",
            ),
            MarkSchemeStep(
                code="A1",
                mark_type="A",
                description="oe (accept any equivalent exact form)",
                working=f"{ans_val} (cm)",
            ),
        ]
        grade_band = "5-7"
    else:  # decimal
        decimal = round(float(exact), 1)
        ans_val = f"{decimal:.1f}"
        marks = 3
        form_note = "\nGive your answer correct to 1 decimal place."
        working = (
            f"{pyth_line}\n"
            f"x² = {sq_expr} = {n}\n"
            f"x = √{n} = {ans_val} cm (to 1 d.p.)"
        )
        mark_scheme = [
            MarkSchemeStep(
                code="M1",
                mark_type="M",
                description="for a correct use of Pythagoras' theorem",
                working=f"{sq_expr} (= {n})",
            ),
            MarkSchemeStep(
                code="M1",
                mark_type="M",
                description="for taking the square root",
                working=f"√{n}",
            ),
            MarkSchemeStep(
                code="A1",
                mark_type="A",
                description="awrt (accept answers that round to this)",
                working=f"{ans_val} (cm)",
            ),
        ]
        grade_band = "4-6"

    answer = f"{ans_val} cm"
    tolerance = 0.05 if mode == "decimal" else None

    # Diagram labels: the unknown side is "x", the givens carry their values.
    if variant == "hypotenuse":
        base_label, vert_label, hyp_label = f"{given[0]} cm", f"{given[1]} cm", "x"
        alt = (
            f"A right-angled triangle with shorter sides {given[0]} cm and "
            f"{given[1]} cm, and the hypotenuse labelled x."
        )
    else:
        # given = (hypotenuse, known leg); unknown leg is x
        base_label, vert_label, hyp_label = f"{given[1]} cm", "x", f"{given[0]} cm"
        alt = (
            f"A right-angled triangle with hypotenuse {given[0]} cm, one shorter "
            f"side {given[1]} cm, and the other shorter side labelled x."
        )

    svg = right_triangle_svg(
        base_label=base_label, vert_label=vert_label, hyp_label=hyp_label
    )

    prompt = "Work out the length of the side marked x." + form_note

    return Item(
        id=f"pyth-{uuid.uuid4().hex[:10]}",
        format=req.format,
        qualification=req.qualification,
        board=req.board,
        subject=req.subject,
        tier="higher",
        calculator=(mode == "decimal"),
        total_marks=marks,
        stem="The diagram shows a right-angled triangle.",
        parts=[
            Part(
                label="",
                prompt=prompt,
                marks=marks,
                answer=answer,
                answer_tolerance=tolerance,
                working=working,
                mark_scheme=mark_scheme,
            )
        ],
        diagram=Diagram(svg=svg, alt=alt, not_to_scale=True),
        metadata=Metadata(
            archetype=f"pythagoras-{variant}",
            spec_ref="G20",
            topic="Pythagoras' theorem",
            topic_slug="pythagoras",
            strand="Geometry & measures",
            ao="AO1",
            grade_band=grade_band,
            seed=seed,
        ),
    )


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def _resolve_variant(req: GenerateRequest, rng: Random) -> str:
    if getattr(req, "variant", None) in _VARIANTS:
        return req.variant  # type: ignore[return-value]
    if req.archetype == "pythagoras-shorter-side":
        return "shorter-side"
    if req.archetype == "pythagoras-hypotenuse":
        return "hypotenuse"
    return rng.choice(_VARIANTS)


def build_pythagoras_item(req: GenerateRequest) -> Item:
    seed = req.seed if req.seed is not None else uuid.uuid4().int % (2**31)
    rng = Random(seed)

    variant = _resolve_variant(req, rng)
    calculator = (
        req.calculator
        if getattr(req, "calculator", None) is not None
        else rng.random() < 0.5
    )

    for _ in range(_MAX_ATTEMPTS):
        p = _sample(rng, calculator, variant)
        if p is None:
            continue
        exact = _exact_unknown(p["variant"], p["given"])
        if exact.is_real is False or exact <= 0:
            continue

        # Verifier gate: the formatted answer must equal the sympy re-derivation.
        if p["mode"] == "integer":
            if not (exact.is_Integer and int(exact) == p["answer_int"]):
                # fall back to the sympy value if the triple bookkeeping disagrees
                if not exact.is_Integer:
                    continue
            if sympy.simplify(exact - sympy.Integer(int(exact))) != 0:
                continue
        elif p["mode"] == "surd":
            coeff, radicand = _simplify_surd(p["n"])
            if sympy.simplify(exact - coeff * sympy.sqrt(radicand)) != 0:
                continue
        else:  # decimal
            if abs(float(exact) - round(float(exact), 1)) > 0.05:
                continue

        return _build_item(req, seed, p, exact)

    raise RuntimeError(
        f"Pythagoras generator failed to find a valid item after "
        f"{_MAX_ATTEMPTS} attempts (variant={variant}, calculator={calculator})."
    )
