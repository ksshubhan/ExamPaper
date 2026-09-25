"""Shared contextualization toolkit for the generators.

Real Edexcel Higher papers wrap roughly half their questions in a named
real-world scenario, use multi-part (a)/(b) structures, and lean on a few
signature "reasoning" devices (a person makes a claim to confirm/refute; a
spot-the-error prompt). This module holds the reusable pieces so every
generator can adopt that house style without duplicating it:

  * name / scenario banks styled on the reference papers
  * `make_item` — a multi-part Item factory (generalises basics._item)
  * `mk_part` — a Part builder
  * `claim_prompt` / `spot_error_prompt` — the two reasoning-device scaffolds
  * `sig_figs` — round-to-n-significant-figures with trailing zeros kept

Everything that involves a choice takes an `rng` so output stays deterministic.
"""

from __future__ import annotations

import math
import re
import uuid
from typing import Optional

from ..schema import (
    Diagram,
    GenerateRequest,
    Item,
    MarkSchemeStep,
    Metadata,
    Part,
    Table,
)

# Single first names, as the papers use (a person + a quantity/scenario).
NAMES = [
    "Petra", "Kasim", "Len", "Tina", "Mano", "Leila", "Dan", "Mel", "Nawal",
    "Alice", "Kevin", "Sophie", "Andy", "Luke", "Priya", "Omar", "Grace",
    "Ravi", "Chloe", "Jamal",
]

# Items that go on sale (for percentage / money contexts).
SHOP_ITEMS = [
    "coat", "jacket", "laptop", "phone", "bicycle", "sofa", "television",
    "watch", "mattress", "kettle", "camera", "dress", "guitar", "printer",
]


def pick(rng, seq):
    """Deterministic choice from a sequence."""
    return seq[rng.randrange(len(seq))]


def two_names(rng) -> tuple[str, str]:
    """Two distinct names."""
    a = pick(rng, NAMES)
    b = a
    while b == a:
        b = pick(rng, NAMES)
    return a, b


def coprime_ratio(rng, lo: int = 2, hi: int = 9) -> tuple[int, int]:
    """A two-term ratio a : b as real papers present it — in its simplest form.

    Guarantees the terms are coprime and unequal, so the sampler can never emit
    a ratio like 7 : 7 (equal terms) or 2 : 4 (a common factor). Any archetype
    that shows a ratio to the student should source it here rather than roll its
    own bounds check.
    """
    while True:
        a = rng.randint(lo, hi)
        b = rng.randint(lo, hi)
        if a != b and math.gcd(a, b) == 1:
            return a, b


# --------------------------------------------------------------------------- #
# Numeric formatting
# --------------------------------------------------------------------------- #
_SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def gcse_expr(expr) -> str:
    """Render a sympy expression (or any string) in GCSE notation — the single
    place algebra is stringified for display, so Python operators never leak
    into a rendered paper.

    Implicit multiplication and superscript powers:
      3*(n + 1)        -> 3(n + 1)
      2*n**2 + 2*n     -> 2n² + 2n
      8*n              -> 8n
    """
    s = str(expr)
    s = re.sub(r"\*\*(\d+)", lambda m: m.group(1).translate(_SUPERSCRIPT), s)
    return s.replace("*", "")


def sig_figs(x: float, sf: int = 3) -> str:
    """Round x to `sf` significant figures, keeping trailing zeros.

    e.g. sig_figs(16.43) -> '16.4', sig_figs(8.062) -> '8.06', sig_figs(13.0) -> '13.0'.
    """
    if x == 0:
        return "0"
    decimals = sf - 1 - int(math.floor(math.log10(abs(x))))
    r = round(x, decimals)
    if decimals <= 0:
        return str(int(round(r)))
    return f"{r:.{decimals}f}"


# --------------------------------------------------------------------------- #
# Item / Part construction
# --------------------------------------------------------------------------- #
def mk_part(
    *,
    prompt: str,
    marks: int,
    answer: str,
    working: str,
    mark_scheme: list[MarkSchemeStep],
    label: str = "",
    answer_tolerance: Optional[float] = None,
) -> Part:
    return Part(
        label=label,
        prompt=prompt,
        marks=marks,
        answer=answer,
        answer_tolerance=answer_tolerance,
        working=working,
        mark_scheme=mark_scheme,
    )


def make_item(
    req: GenerateRequest,
    seed: int,
    *,
    archetype: str,
    topic: str,
    topic_slug: str,
    strand: str,
    spec_ref: str,
    grade_band: str,
    stem: str,
    parts: list[Part],
    ao: str = "AO1",
    diagram: Optional[Diagram] = None,
    table: Optional[Table] = None,
) -> Item:
    """Build an Item from one or more Parts (total marks = sum of part marks)."""
    total = sum(p.marks for p in parts)
    return Item(
        id=f"{topic_slug}-{uuid.uuid4().hex[:10]}",
        format=req.format,
        qualification=req.qualification,
        board=req.board,
        subject=req.subject,
        tier=(req.tier or "higher"),
        calculator=bool(req.calculator),
        total_marks=total,
        stem=stem,
        parts=parts,
        diagram=diagram,
        table=table,
        metadata=Metadata(
            archetype=archetype,
            spec_ref=spec_ref,
            topic=topic,
            topic_slug=topic_slug,
            strand=strand,
            ao=ao,
            grade_band=grade_band,
            seed=seed,
        ),
    )


# --------------------------------------------------------------------------- #
# Reasoning-device scaffolds (prompt wording only; the caller supplies the
# verified numbers, the answer, and the mark scheme incl. a B1 for the reason)
# --------------------------------------------------------------------------- #
def claim_prompt(name: str, statement: str) -> str:
    return (
        f"{name} says\n“{statement}”\n"
        f"Is {name} correct? You must show how you get your answer."
    )


def spot_error_prompt(name: str, task: str, wrong_working: str) -> str:
    return (
        f"{name} was asked to {task}.\n"
        f"Here is {name}'s working.\n{wrong_working}\n"
        f"{name}'s answer is wrong.\nWhat mistake has {name} made?"
    )


def reason_step(description: str, code: str = "B1") -> MarkSchemeStep:
    """A B-mark awarding the written reason/conclusion of a reasoning question."""
    return MarkSchemeStep(
        code=code, mark_type="B", description=description, working=None
    )
