"""Foundation (Grade 1-2) arithmetic generators.

Text-only, deterministic from a seed, every answer exactly re-derivable. These
give an assembled paper the genuinely easy openers a real paper starts with.
"""

from __future__ import annotations

from random import Random

import sympy

from ..schema import GenerateRequest, Item, MarkSchemeStep
from .basics import _item, _seed
from .context import make_item, mk_part

_MAX_ATTEMPTS = 200


def _M1(d, w=None): return MarkSchemeStep(code="M1", mark_type="M", description=d, working=w)
def _A1(d, w=None): return MarkSchemeStep(code="A1", mark_type="A", description=d, working=w)
def _B1(d, w=None): return MarkSchemeStep(code="B1", mark_type="B", description=d, working=w)


_PLACES = {1: "ones", 10: "tens", 100: "hundreds", 1000: "thousands",
           10000: "ten thousands"}


# --------------------------------------------------------------------------- #
# Place value  (N1)
# --------------------------------------------------------------------------- #
def build_place_value(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        digits = [rng.randint(1, 9)] + [rng.randint(0, 9) for _ in range(4)]
        num = int("".join(str(d) for d in digits))
        pos = rng.randint(0, 4)                       # 0 = units place
        place = 10 ** pos
        digit = (num // place) % 10
        if digit == 0:
            continue
        value = digit * place
        others = sorted({num, num + rng.randint(1, 900), max(0, num - rng.randint(1, 900)),
                         num + rng.randint(1000, 5000)})
        parts = [
            mk_part(label="a",
                    prompt=f"Write down the value of the {digit} in the number {num:,}.",
                    marks=1, answer=str(value),
                    working=f"The {digit} is in the {_PLACES[place]} column: {value}",
                    mark_scheme=[_B1("cao")]),
            mk_part(label="b",
                    prompt="Write these numbers in order, smallest first.\n"
                    + "   ".join(f"{o:,}" for o in _shuffled(others, rng)),
                    marks=1, answer=", ".join(f"{o:,}" for o in others),
                    working=", ".join(f"{o:,}" for o in others), mark_scheme=[_B1("cao")]),
        ]
        return make_item(req, seed, archetype="place-value", topic="Place value",
                         topic_slug="place-value", strand="Number", spec_ref="N1",
                         grade_band="1-2", stem="", parts=parts)
    raise RuntimeError("place-value generator failed.")


def _shuffled(seq, rng):
    s = list(seq)
    rng.shuffle(s)
    return s


# --------------------------------------------------------------------------- #
# Negative numbers  (N2)
# --------------------------------------------------------------------------- #
def build_negative_numbers(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a = rng.randint(-9, 9)
    b = rng.randint(-9, 9)
    c = rng.randint(-6, 6)
    d = rng.choice([i for i in range(-6, 7) if i != 0])

    def show(n):
        return f"({n})" if n < 0 else str(n)
    parts = [
        mk_part(label="a", prompt=f"Work out  {show(a)} + {show(b)}", marks=1,
                answer=str(a + b), working=f"{a} + {b} = {a + b}", mark_scheme=[_B1("cao")]),
        mk_part(label="b", prompt=f"Work out  {show(c)} − {show(d)}", marks=1,
                answer=str(c - d), working=f"{c} − ({d}) = {c - d}", mark_scheme=[_B1("cao")]),
        mk_part(label="c", prompt=f"Work out  {show(c)} × {show(d)}", marks=1,
                answer=str(c * d), working=f"{c} × {d} = {c * d}", mark_scheme=[_B1("cao")]),
    ]
    return make_item(req, seed, archetype="negative-numbers", topic="Negative numbers",
                     topic_slug="negative-numbers", strand="Number", spec_ref="N2",
                     grade_band="1-2", stem="", parts=parts)


# --------------------------------------------------------------------------- #
# BIDMAS  (N3)
# --------------------------------------------------------------------------- #
def build_bidmas(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        shape = rng.choice(["mul-add", "bracket", "square"])
        if shape == "mul-add":
            a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 9)
            expr = f"{a} + {b} × {c}"
            val = a + b * c
            priority = f"{b} × {c} = {b * c}"  # multiply before add
        elif shape == "bracket":
            a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 6)
            expr = f"({a} + {b}) × {c}"
            val = (a + b) * c
            priority = f"({a} + {b}) = {a + b}"  # bracket first
        else:
            a, b = rng.randint(2, 6), rng.randint(2, 9)
            expr = f"{a}² + {b}"
            val = a * a + b
            priority = f"{a}² = {a * a}"  # index first
        check = int(sympy.sympify(expr.replace("²", "**2").replace("×", "*")))
        if check != val:
            continue
        part = mk_part(prompt=f"Work out  {expr}", marks=2, answer=str(val),
                       working=f"{expr} = {val}  (multiply/index before add)",
                       mark_scheme=[_M1(f"for {priority} first"),
                                    _A1("cao", str(val))])
        return make_item(req, seed, archetype="bidmas", topic="BIDMAS",
                         topic_slug="bidmas", strand="Number", spec_ref="N3",
                         grade_band="1-2", stem="", parts=[part])
    raise RuntimeError("bidmas generator failed.")


# --------------------------------------------------------------------------- #
# Time  (N/R)
# --------------------------------------------------------------------------- #
def build_time_calc(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    start_h = rng.randint(8, 20)
    start_m = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    dur_h = rng.randint(0, 3)
    dur_m = rng.choice([15, 20, 30, 40, 45, 50])
    total = (start_h * 60 + start_m) + (dur_h * 60 + dur_m)
    end_h, end_m = (total // 60) % 24, total % 60
    part = mk_part(
        prompt=(f"A film starts at {start_h:02d}:{start_m:02d} and lasts "
                f"{dur_h} hours {dur_m} minutes. What time does the film end? "
                "Give your answer using the 24-hour clock."),
        marks=2, answer=f"{end_h:02d}:{end_m:02d}",
        working=f"{start_h:02d}:{start_m:02d} + {dur_h} h {dur_m} min = {end_h:02d}:{end_m:02d}",
        mark_scheme=[_M1(f"for adding {dur_h} h {dur_m} min to {start_h:02d}:{start_m:02d}"),
                     _A1("cao", f"{end_h:02d}:{end_m:02d}")])
    return make_item(req, seed, archetype="time-calc", topic="Time",
                     topic_slug="time-calc", strand="Number", spec_ref="N13",
                     grade_band="1-2", stem="", parts=[part])


# --------------------------------------------------------------------------- #
# Add & subtract (integers / decimals)  (N2)
# --------------------------------------------------------------------------- #
def build_add_subtract(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    if rng.random() < 0.5:
        a, b = rng.randint(200, 900), rng.randint(150, 800)
        parts = [
            mk_part(label="a", prompt=f"Work out  {a} + {b}", marks=1, answer=str(a + b),
                    working=f"{a} + {b} = {a + b}", mark_scheme=[_B1("cao")]),
            mk_part(label="b", prompt=f"Work out  {max(a, b)} − {min(a, b)}", marks=1,
                    answer=str(abs(a - b)), working=f"{max(a, b)} − {min(a, b)} = {abs(a - b)}",
                    mark_scheme=[_B1("cao")]),
        ]
    else:
        a = sympy.Rational(rng.randint(100, 900), 10)
        b = sympy.Rational(rng.randint(50, 500), 10)
        hi, lo = max(a, b), min(a, b)
        parts = [
            mk_part(label="a", prompt=f"Work out  {float(a):g} + {float(b):g}", marks=1,
                    answer=f"{float(a + b):g}", working=f"{float(a):g} + {float(b):g} = {float(a + b):g}",
                    mark_scheme=[_B1("cao")]),
            mk_part(label="b", prompt=f"Work out  {float(hi):g} − {float(lo):g}", marks=1,
                    answer=f"{float(hi - lo):g}", working=f"{float(hi):g} − {float(lo):g} = {float(hi - lo):g}",
                    mark_scheme=[_B1("cao")]),
        ]
    return make_item(req, seed, archetype="add-subtract",
                     topic="Addition & subtraction", topic_slug="add-subtract",
                     strand="Number", spec_ref="N2", grade_band="1-2", stem="",
                     parts=parts)


# --------------------------------------------------------------------------- #
# Multiply & divide  (N2)
# --------------------------------------------------------------------------- #
def build_multiply_divide(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a = rng.randint(12, 49)
    b = rng.randint(12, 39)
    prod = a * b
    q = rng.randint(12, 40)
    div = rng.randint(3, 9)
    dividend = q * div
    parts = [
        mk_part(label="a", prompt=f"Work out  {a} × {b}", marks=2, answer=str(prod),
                working=f"{a} × {b} = {prod}",
                mark_scheme=[_M1(f"for a full written multiplication {a} × {b}"),
                             _A1("cao", str(prod))]),
        mk_part(label="b", prompt=f"Work out  {dividend} ÷ {div}", marks=2, answer=str(q),
                working=f"{dividend} ÷ {div} = {q}",
                mark_scheme=[_M1(f"for a full written division {dividend} ÷ {div}"),
                             _A1("cao", str(q))]),
    ]
    return make_item(req, seed, archetype="multiply-divide",
                     topic="Multiplication & division", topic_slug="multiply-divide",
                     strand="Number", spec_ref="N2", grade_band="2-3", stem="",
                     parts=parts)


# --------------------------------------------------------------------------- #
# Calculation problems (worded, multi-step)  (N2)
# --------------------------------------------------------------------------- #
def build_calculation_problems(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    item = rng.choice(["pens", "notebooks", "cakes", "apples", "cards"])
    n = rng.randint(3, 8)
    unit = sympy.Rational(rng.randint(45, 250), 100)   # £ each
    paid = rng.choice([10, 20])
    total = n * unit
    change = paid - total
    if change <= 0:
        n = 3
        total = n * unit
        change = paid - total
    part = mk_part(
        prompt=(f"{item.capitalize()} cost £{float(unit):.2f} each. Jamal buys {n} {item} "
                f"and pays with a £{paid} note. How much change should he get?"),
        marks=3, answer=f"£{float(change):.2f}",
        working=(f"Cost = {n} × £{float(unit):.2f} = £{float(total):.2f}\n"
                 f"Change = £{paid} − £{float(total):.2f} = £{float(change):.2f}"),
        mark_scheme=[_M1(f"for the total cost {n} × £{float(unit):.2f} (= £{float(total):.2f})"),
                     _M1(f"for £{paid} − £{float(total):.2f} (= £{float(change):.2f})"),
                     _A1("cao", f"£{float(change):.2f}")])
    return make_item(req, seed, archetype="calculation-problems",
                     topic="Calculation problems", topic_slug="calculation-problems",
                     strand="Number", spec_ref="N2", grade_band="2-3", ao="AO2",
                     stem="", parts=[part])
