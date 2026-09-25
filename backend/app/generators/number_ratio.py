"""Number & ratio 'quick win' generators (mostly arithmetic / proportion).

Text-only, deterministic from a seed, every answer exact and independently
re-derivable. Reuses the shared item/part factories and formatting helpers.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from random import Random

import sympy

from ..schema import GenerateRequest, Item, MarkSchemeStep
from .basics import _item, _seed
from .context import make_item, mk_part, pick, sig_figs
from .number import _fr, _money

_MAX_ATTEMPTS = 300


def _M1(d, w=None): return MarkSchemeStep(code="M1", mark_type="M", description=d, working=w)
def _A1(d, w=None): return MarkSchemeStep(code="A1", mark_type="A", description=d, working=w)
def _B1(d, w=None): return MarkSchemeStep(code="B1", mark_type="B", description=d, working=w)


# --------------------------------------------------------------------------- #
# Rounding — nearest 100 / 2 d.p. / 2 s.f.  (N15)
# --------------------------------------------------------------------------- #
def build_rounding(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        whole = rng.randint(1000, 9999)
        frac = rng.randint(1, 999)
        d = Decimal(f"{whole}.{frac:03d}")
        f = float(d)
        n100 = int((d / 100).quantize(Decimal("1"), ROUND_HALF_UP) * 100)
        d2 = d.quantize(Decimal("0.01"), ROUND_HALF_UP)
        sf2 = sig_figs(f, 2)
        # Only keep unambiguous cases (round-half-up agrees with Python's round),
        # so the harness can re-derive independently with round().
        if round(f / 100) * 100 != n100:
            continue
        if abs(round(f, 2) - float(d2)) > 1e-9:
            continue
        parts = [
            mk_part(label="a", prompt="Round the number to the nearest 100.", marks=1,
                    answer=str(n100), working=f"{d} → {n100}", mark_scheme=[_B1("cao")]),
            mk_part(label="b", prompt="Round the number to 2 decimal places.", marks=1,
                    answer=str(d2), working=f"{d} → {d2}", mark_scheme=[_B1("cao")]),
            mk_part(label="c", prompt="Round the number to 2 significant figures.",
                    marks=1, answer=sf2, working=f"{d} → {sf2}", mark_scheme=[_B1("cao")]),
        ]
        return make_item(req, seed, archetype="rounding", topic="Rounding",
                         topic_slug="rounding", strand="Number", spec_ref="N15",
                         grade_band="1-3", stem=f"Here is a number.\n{d}", parts=parts)
    raise RuntimeError("rounding generator failed.")


# --------------------------------------------------------------------------- #
# Estimating — round each to 1 s.f. then compute  (N14)
# --------------------------------------------------------------------------- #
def build_estimating(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        a1 = rng.choice([200, 300, 400, 500, 600, 800])
        b1 = rng.choice([20, 30, 40, 50, 60])
        c1 = rng.choice([20, 30, 40, 50])
        est = sympy.Rational(a1 * b1, c1)
        if est.q != 1:
            continue
        est = int(est)
        a = a1 + rng.randint(-40, 40)
        b = b1 + rng.randint(-4, 4)
        c = c1 + rng.randint(-4, 4)
        if a <= 0 or b <= 0 or c <= 0:
            continue
        # sanity: rounding each original to 1 s.f. gives back a1,b1,c1
        if float(sig_figs(a, 1)) != a1 or float(sig_figs(b, 1)) != b1 or float(sig_figs(c, 1)) != c1:
            continue
        part = mk_part(
            prompt=f"Work out an estimate for  ({a} × {b}) ÷ {c}", marks=3, answer=str(est),
            working=f"≈ ({a1} × {b1}) ÷ {c1} = {a1 * b1} ÷ {c1} = {est}",
            mark_scheme=[_M1(f"for rounding each to 1 s.f. ({a1}, {b1}, {c1})"),
                         _M1(f"for ({a1} × {b1}) ÷ {c1} (= {est})"),
                         _A1("cao", str(est))])
        return make_item(req, seed, archetype="estimating", topic="Estimating",
                         topic_slug="estimating", strand="Number", spec_ref="N14",
                         grade_band="3-4", stem="", parts=[part])
    raise RuntimeError("estimating generator failed.")


# --------------------------------------------------------------------------- #
# Error intervals  (N15)
# --------------------------------------------------------------------------- #
def build_error_intervals(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    kind = rng.choice(["1dp", "nearest10", "integer"])
    if kind == "1dp":
        val = sympy.Rational(rng.randint(10, 99), 10)
        half = sympy.Rational(1, 20)
        desc = "1 decimal place"
    elif kind == "nearest10":
        val = sympy.Integer(rng.randint(2, 40) * 10)
        half = sympy.Integer(5)
        desc = "the nearest 10"
    else:
        val = sympy.Integer(rng.randint(20, 200))
        half = sympy.Rational(1, 2)
        desc = "the nearest whole number"
    lo, hi = val - half, val + half
    ans = f"{_frstr(lo)} ≤ x < {_frstr(hi)}"
    part = mk_part(
        prompt=f"A number x is rounded to {desc}. The result is {_frstr(val)}. "
        "Write down the error interval for x.", marks=2, answer=ans,
        working=f"{_frstr(val)} ± {_frstr(half)} → {ans}",
        mark_scheme=[_B1(f"for a lower bound {_frstr(lo)}"),
                     _B1(f"for the interval {ans}")])
    return make_item(req, seed, archetype="error-intervals", topic="Error intervals",
                     topic_slug="error-intervals", strand="Number", spec_ref="N15",
                     grade_band="3-5", stem="", parts=[part])


def _frstr(r) -> str:
    r = sympy.Rational(r)
    return str(r.p) if r.q == 1 else f"{float(r):g}"


# --------------------------------------------------------------------------- #
# Bounds — upper/lower bound of a calculation  (N15)
# --------------------------------------------------------------------------- #
def build_bounds(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    op = rng.choice(["+", "−", "×", "÷"])
    a = sympy.Rational(rng.randint(50, 200), 10)   # 1 d.p.
    b = sympy.Rational(rng.randint(20, 90), 10)
    h = sympy.Rational(1, 20)
    aU, aL, bU, bL = a + h, a - h, b + h, b - h
    which = rng.choice(["upper", "lower"])
    # The bound-maximising / minimising combination of operands for each op.
    if which == "upper":
        o1, o2 = (aU, bU) if op in ("+", "×") else (aU, bL)
    else:
        o1, o2 = (aL, bL) if op in ("+", "×") else (aL, bU)
    if op == "+":
        res = o1 + o2
    elif op == "−":
        res = o1 - o2
    elif op == "×":
        res = o1 * o2
    else:
        res = o1 / o2
    expr = f"a {op} b"
    comb = f"{float(o1):g} {op} {float(o2):g}"
    three_sf = op in ("×", "÷")   # products/quotients rarely terminate cleanly
    ans = sig_figs(float(res), 3) if three_sf else f"{float(res):g}"
    part = mk_part(
        prompt=f"a = {float(a):g} and b = {float(b):g}, each correct to 1 decimal place. "
        f"Work out the {which} bound of  {expr}."
        + (" Give your answer to 3 significant figures." if three_sf else ""),
        marks=3, answer=str(ans),
        working=(f"a: {float(aL):g}–{float(aU):g}, b: {float(bL):g}–{float(bU):g}\n"
                 f"{which} bound = {ans}"),
        mark_scheme=[_M1(f"for the bounds a: {float(aL):g}–{float(aU):g}, "
                         f"b: {float(bL):g}–{float(bU):g}"),
                     _M1(f"for {comb} (= {ans})"),
                     _A1("cao", str(ans))])
    return make_item(req, seed, archetype="bounds", topic="Bounds", topic_slug="bounds",
                     strand="Number", spec_ref="N15", grade_band="6-8", stem="",
                     parts=[part])


# --------------------------------------------------------------------------- #
# HCF, LCM & prime factors  (N4)
# --------------------------------------------------------------------------- #
def _prime_factor_str(n: int) -> str:
    f = sympy.factorint(n)
    parts = []
    for p in sorted(f):
        e = f[p]
        parts.append(str(p) if e == 1 else f"{p}{_sup(e)}")
    return " × ".join(parts)


_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
def _sup(n): return str(n).translate(_SUP)


def build_hcf_lcm(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        A = rng.randint(24, 120)
        B = rng.randint(24, 120)
        if A == B or sympy.isprime(A) or sympy.isprime(B):
            continue
        lcm = int(sympy.ilcm(A, B))
        hcf = int(sympy.igcd(A, B))
        if hcf == 1:
            continue
        parts = [
            mk_part(label="a", prompt=f"Write {A} as a product of its prime factors.",
                    marks=2, answer=_prime_factor_str(A),
                    working=f"{A} = {_prime_factor_str(A)}",
                    mark_scheme=[_M1(f"for dividing {A} down by primes (→ {_prime_factor_str(A)})"),
                                 _A1("cao", _prime_factor_str(A))]),
            mk_part(label="b", prompt=f"Find the highest common factor (HCF) of {A} and {B}.",
                    marks=1, answer=str(hcf), working=f"HCF = {hcf}", mark_scheme=[_B1("cao")]),
            mk_part(label="c", prompt=f"Find the lowest common multiple (LCM) of {A} and {B}.",
                    marks=2, answer=str(lcm), working=f"LCM = ({A} × {B}) ÷ {hcf} = {lcm}",
                    mark_scheme=[_M1(f"for ({A} × {B}) ÷ {hcf} (= {lcm})"),
                                 _A1("cao", str(lcm))]),
        ]
        return make_item(req, seed, archetype="hcf-lcm",
                         topic="Prime factors, HCF & LCM", topic_slug="hcf-lcm",
                         strand="Number", spec_ref="N4", grade_band="3-5", stem="",
                         parts=parts)
    raise RuntimeError("hcf-lcm generator failed.")


# --------------------------------------------------------------------------- #
# Fractions ↔ decimals ↔ percentages — order them  (N10)
# --------------------------------------------------------------------------- #
_FDP_POOL = [
    ("0.6", sympy.Rational(3, 5)), ("3/5", sympy.Rational(3, 5)),
    ("0.7", sympy.Rational(7, 10)), ("3/4", sympy.Rational(3, 4)),
    ("68%", sympy.Rational(17, 25)), ("2/5", sympy.Rational(2, 5)),
    ("0.55", sympy.Rational(11, 20)), ("7/10", sympy.Rational(7, 10)),
    ("45%", sympy.Rational(9, 20)), ("0.8", sympy.Rational(4, 5)),
    ("5/8", sympy.Rational(5, 8)), ("72%", sympy.Rational(18, 25)),
    ("1/3", sympy.Rational(1, 3)), ("0.35", sympy.Rational(7, 20)),
]


def build_fdp(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        chosen = rng.sample(_FDP_POOL, 4)
        vals = [v for _, v in chosen]
        if len(set(vals)) != 4:
            continue
        display = [d for d, _ in chosen]
        ordered = [d for d, _ in sorted(chosen, key=lambda t: t[1])]
        decimals = ", ".join(f"{float(v):g}" for _, v in chosen)
        part = mk_part(
            prompt="Write these numbers in order of size, starting with the smallest.\n"
            + "   ".join(display), marks=2, answer=", ".join(ordered),
            working="Convert each to a decimal, then order:\n" + ", ".join(ordered),
            mark_scheme=[_M1(f"for writing each as a decimal ({decimals})"),
                         _A1("cao (correct order)", ", ".join(ordered))])
        return make_item(req, seed, archetype="fdp",
                         topic="Fractions, decimals & percentages", topic_slug="fdp",
                         strand="Number", spec_ref="N10", grade_band="2-3", stem="",
                         parts=[part])
    raise RuntimeError("fdp generator failed.")


# --------------------------------------------------------------------------- #
# Fraction of an amount  (N8)
# --------------------------------------------------------------------------- #
def build_fraction_of_amount(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        d = rng.randint(3, 8)
        n = rng.randint(2, d - 1)
        per = rng.randint(3, 25)
        total = per * d
        ans = n * per
        part = mk_part(
            prompt=f"Work out  {n}/{d}  of £{total}.", marks=2, answer=f"£{ans}",
            working=f"£{total} ÷ {d} = £{per};  £{per} × {n} = £{ans}",
            mark_scheme=[_M1("for £{t} ÷ {d}".format(t=total, d=d), f"= {per}"),
                         _A1("cao", f"£{ans}")])
        return make_item(req, seed, archetype="fraction-of-amount",
                         topic="Fraction of an amount", topic_slug="fraction-of-amount",
                         strand="Number", spec_ref="N8", grade_band="2-3", stem="",
                         parts=[part])
    raise RuntimeError("fraction-of-amount generator failed.")


# --------------------------------------------------------------------------- #
# Best buy  (R9)
# --------------------------------------------------------------------------- #
def build_best_buy(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    item = pick(rng, ["juice", "rice", "soap", "coffee", "pasta"])
    for _ in range(_MAX_ATTEMPTS):
        qa = rng.choice([4, 5, 6, 8, 10])
        qb = rng.choice([10, 12, 15, 20])
        ppa = sympy.Rational(rng.randint(30, 80), 100)   # price per unit A (£)
        ppb = sympy.Rational(rng.randint(30, 80), 100)
        pa = ppa * qa
        pb = ppb * qb
        if ppa == ppb or pa.q > 100 or pb.q > 100:
            continue
        winner = "A" if ppa < ppb else "B"
        part = mk_part(
            prompt=f"Pack A has {qa} {item} for {_money(pa)}. Pack B has {qb} {item} for "
            f"{_money(pb)}. Which pack is better value for money? You must show your working.",
            marks=3, answer=f"Pack {winner}",
            working=(f"A: {_money(pa)} ÷ {qa} = {_money(ppa)} each\n"
                     f"B: {_money(pb)} ÷ {qb} = {_money(ppb)} each\n"
                     f"Pack {winner} is cheaper per {item[:-1] if item.endswith('s') else item}"),
            mark_scheme=[_M1(f"for unit price of A: {_money(pa)} ÷ {qa} (= {_money(ppa)})"),
                         _M1(f"for unit price of B: {_money(pb)} ÷ {qb} (= {_money(ppb)})"),
                         _A1(f"cao with reason: Pack {winner}")])
        return make_item(req, seed, archetype="best-buy", topic="Best buy",
                         topic_slug="best-buy", strand="Ratio & proportion",
                         spec_ref="R9", grade_band="3-4", ao="AO2", stem="",
                         parts=[part])
    raise RuntimeError("best-buy generator failed.")


# --------------------------------------------------------------------------- #
# Exchange rates  (R9)
# --------------------------------------------------------------------------- #
def build_exchange_rates(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        rate = sympy.Rational(rng.randint(105, 145), 100)  # $ per £
        forward = rng.random() < 0.5
        if forward:
            pounds = rng.randint(20, 400)
            dollars = pounds * rate
            if dollars.q != 1:
                continue
            part = mk_part(
                prompt=f"The exchange rate is £1 = ${float(rate):g}. Change £{pounds} into "
                "dollars.", marks=2, answer=f"${int(dollars)}",
                working=f"{pounds} × {float(rate):g} = {int(dollars)}",
                mark_scheme=[_M1(f"for {pounds} × {float(rate):g} (= {int(dollars)})"),
                             _A1("cao", f"${int(dollars)}")])
        else:
            pounds = rng.randint(20, 400)
            dollars = pounds * rate
            if dollars.q != 1:
                continue
            part = mk_part(
                prompt=f"The exchange rate is £1 = ${float(rate):g}. Change ${int(dollars)} "
                "into pounds.", marks=2, answer=f"£{pounds}",
                working=f"{int(dollars)} ÷ {float(rate):g} = {pounds}",
                mark_scheme=[_M1(f"for {int(dollars)} ÷ {float(rate):g} (= {pounds})"),
                             _A1("cao", f"£{pounds}")])
        return make_item(req, seed, archetype="exchange-rates", topic="Exchange rates",
                         topic_slug="exchange-rates", strand="Ratio & proportion",
                         spec_ref="R9", grade_band="3-4", stem="", parts=[part])
    raise RuntimeError("exchange-rates generator failed.")


# --------------------------------------------------------------------------- #
# Speed / density (compound measures)  (R11)
# --------------------------------------------------------------------------- #
def build_compound_measures(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    kind = rng.choice(["speed", "density"])
    if kind == "speed":
        speed = rng.randint(30, 90)
        t = rng.choice([2, 3, 4, 5])
        dist = speed * t
        part = mk_part(
            prompt=f"A car travels {dist} km in {t} hours. Work out the average speed in km/h.",
            marks=2, answer=f"{speed} km/h",
            working=f"Speed = distance ÷ time = {dist} ÷ {t} = {speed} km/h",
            mark_scheme=[_M1(f"for {dist} ÷ {t} (= {speed})"),
                         _A1("cao", f"{speed} km/h")])
    else:
        density = rng.randint(2, 12)
        v = rng.choice([3, 4, 5, 6, 8])
        mass = density * v
        part = mk_part(
            prompt=f"A block has mass {mass} g and volume {v} cm³. Work out its density in "
            "g/cm³.", marks=2, answer=f"{density} g/cm³",
            working=f"Density = mass ÷ volume = {mass} ÷ {v} = {density} g/cm³",
            mark_scheme=[_M1(f"for {mass} ÷ {v} (= {density})"),
                         _A1("cao", f"{density} g/cm³")])
    return make_item(req, seed, archetype="compound-measures",
                     topic="Speed & density", topic_slug="compound-measures",
                     strand="Ratio & proportion", spec_ref="R11", grade_band="4-6",
                     stem="", parts=[part])


# --------------------------------------------------------------------------- #
# Direct & inverse proportion (simple)  (R10)
# --------------------------------------------------------------------------- #
def build_proportion(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        kind = rng.choice(["direct", "inverse"])
        k = rng.randint(2, 9)
        x0 = rng.randint(2, 6)
        x1 = rng.randint(2, 10)
        x2 = rng.randint(2, 9)
        if kind == "direct":
            y0, y1, y2 = k * x0, k * x1, k * x2
            stem = f"y is directly proportional to x.\ny = {y0} when x = {x0}."
            formula = f"y = {k}x"
            find_k = f"k = y/x = {y0}/{x0} = {k}"
            work_b = f"y = {k} × {x1} = {y1}"
            work_c = f"x = y/{k} = {y2}/{k} = {x2}"
        else:
            y0, y1, y2 = (sympy.Rational(k, x) for x in (x0, x1, x2))
            if any(v.q != 1 for v in (y0, y1, y2)):
                continue
            y0, y1, y2 = int(y0), int(y1), int(y2)
            stem = f"y is inversely proportional to x.\ny = {y0} when x = {x0}."
            formula = f"y = {k}/x"
            find_k = f"k = xy = {x0} × {y0} = {k}"
            work_b = f"y = {k} ÷ {x1} = {y1}"
            work_c = f"x = {k}/y = {k}/{y2} = {x2}"
        parts = [
            mk_part(label="a", prompt="Find a formula for y in terms of x.",
                    marks=2, answer=formula, working=f"{find_k}\nso {formula}",
                    mark_scheme=[_M1(f"for {find_k}"),
                                 _A1("oe (a correct formula)", formula)]),
            mk_part(label="b", prompt=f"Work out the value of y when x = {x1}.",
                    marks=1, answer=str(y1), working=work_b,
                    mark_scheme=[_B1("cao", str(y1))]),
            mk_part(label="c", prompt=f"Work out the value of x when y = {y2}.",
                    marks=2, answer=str(x2), working=work_c,
                    mark_scheme=[_M1(f"for {work_c}"),
                                 _A1("cao", str(x2))]),
        ]
        return make_item(req, seed, archetype="proportion",
                         topic="Direct & inverse proportion", topic_slug="proportion",
                         strand="Ratio & proportion", spec_ref="R10", grade_band="4-6",
                         stem=stem, parts=parts)
    raise RuntimeError("proportion generator failed.")


# --------------------------------------------------------------------------- #
# Compound interest / depreciation  (R16)
# --------------------------------------------------------------------------- #
def build_compound_interest(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    grow = rng.random() < 0.6
    P = rng.choice([1000, 1500, 2000, 2500, 3000, 5000])
    r = rng.choice([2, 3, 4, 5])
    n = rng.choice([2, 3, 4])
    mult = sympy.Rational(100 + r, 100) if grow else sympy.Rational(100 - r, 100)
    value = P * mult ** n
    val2 = Decimal(str(float(value))).quantize(Decimal("0.01"), ROUND_HALF_UP)
    if grow:
        stem = (f"Priya invests £{P} in a savings account. The account pays {r}% compound "
                f"interest each year.")
        prompt = f"Work out the value of the investment after {n} years. Give your answer to the nearest penny."
    else:
        stem = (f"A car is worth £{P}. Its value depreciates by {r}% each year.")
        prompt = f"Work out the value of the car after {n} years. Give your answer to the nearest penny."
    part = mk_part(
        prompt=prompt, marks=3, answer=f"£{val2}",
        working=f"{P} × ({float(mult):g})^{n} = £{val2}",
        mark_scheme=[_M1(f"for the multiplier (100 {'+' if grow else '−'} {r}) ÷ 100 "
                         f"(= {float(mult):g})"),
                     _M1(f"for {P} × {float(mult):g}^{n} (= £{val2})"),
                     _A1("cao", f"£{val2}")])
    return make_item(req, seed, archetype="compound-interest",
                     topic="Compound interest & depreciation",
                     topic_slug="compound-interest", strand="Ratio & proportion",
                     spec_ref="R16", grade_band="4-6", stem=stem, parts=[part])


# --------------------------------------------------------------------------- #
# Capture–recapture  (R7, grade 4-6)
# --------------------------------------------------------------------------- #
def build_capture_recapture(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    animals = [("fish", "lake"), ("birds", "wood"), ("rabbits", "field"),
               ("deer", "forest")]
    for _ in range(_MAX_ATTEMPTS):
        S = rng.choice([40, 50, 60, 80, 100, 120])   # first sample, tagged
        m = rng.randint(3, 12)                        # tagged in 2nd sample
        n = rng.choice([40, 50, 60, 75, 80, 100])     # 2nd sample size
        if (S * n) % m != 0:
            continue
        N = S * n // m
        if N <= max(S, n) or N > 5000:
            continue
        # Independent check: N·m = S·n (the proportion equation).
        if N * m != S * n:
            continue
        creature, place = rng.choice(animals)
        return make_item(
            req, seed, archetype="capture-recapture",
            topic="Capture–recapture", topic_slug="capture-recapture",
            strand="Ratio & proportion", spec_ref="R7", grade_band="4-6",
            stem=(f"Bob wants to estimate the number of {creature} in a {place}. "
                  f"He catches {S} {creature}, tags them and releases them. "
                  f"Later he catches {n} {creature}, of which {m} are tagged."),
            parts=[
                mk_part(label="a",
                        prompt=f"Work out an estimate for the number of {creature} in the "
                        f"{place}.", marks=2, answer=str(N),
                        working=f"{m}/{n} = {S}/N  →  N = {S} × {n} ÷ {m} = {N}",
                        mark_scheme=[_M1(f"for {S} × {n} ÷ {m}"), _A1("cao", str(N))]),
                mk_part(label="b",
                        prompt="Write down one assumption you have made.", marks=1,
                        answer="The number of animals has not changed (and the tagged "
                        "ones have mixed evenly with the rest).",
                        working="",
                        mark_scheme=[_B1("a sensible assumption, e.g. the population is "
                                        "unchanged / tagged animals mix uniformly")]),
            ], ao="AO2")
    raise RuntimeError("capture-recapture generator failed.")
