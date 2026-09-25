"""Probability-strand generators.

Deterministic from a seed; every probability is an exact `sympy.Rational` so the
answer can be re-derived independently. Trees and Venn diagrams are drawn from
the same sampled numbers.
"""

from __future__ import annotations

from random import Random

import sympy

from ..schema import Diagram, GenerateRequest, Item, MarkSchemeStep, Table
from . import stats_diagrams as SD
from .basics import _seed
from .context import make_item, mk_part, pick

_MAX_ATTEMPTS = 300


def _dia(svg: str, alt: str, scale: bool = True) -> Diagram:
    return Diagram(svg=svg, alt=alt, not_to_scale=not scale)


def _frac(r: sympy.Rational) -> str:
    r = sympy.Rational(r)
    return str(r.p) if r.q == 1 else f"{r.p}/{r.q}"


def _M1(d, w=None):
    return MarkSchemeStep(code="M1", mark_type="M", description=d, working=w)


def _A1(d, w=None):
    return MarkSchemeStep(code="A1", mark_type="A", description=d, working=w)


def _B1(d, w=None):
    return MarkSchemeStep(code="B1", mark_type="B", description=d, working=w)


# --------------------------------------------------------------------------- #
# Single-event probability  (P1, grade 2)
# --------------------------------------------------------------------------- #
def build_probability(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    colours = ["red", "blue", "green", "yellow"]
    counts = [rng.randint(2, 9) for _ in colours]
    total = sum(counts)
    i = rng.randrange(len(colours))
    p = sympy.Rational(counts[i], total)
    parts = [
        mk_part(label="a", prompt=f"Work out the probability that the counter is {colours[i]}.",
                marks=2, answer=_frac(p),
                working=f"P({colours[i]}) = {counts[i]}/{total} = {_frac(p)}",
                mark_scheme=[_M1("for count/total", f"{counts[i]}/{total}"),
                             _A1("cao (simplest form)", _frac(p))]),
        mk_part(label="b", prompt=f"Work out the probability that the counter is NOT {colours[i]}.",
                marks=1, answer=_frac(1 - p),
                working=f"1 − {_frac(p)} = {_frac(1 - p)}", mark_scheme=[_B1("ft", _frac(1 - p))]),
    ]
    desc = ", ".join(f"{counts[k]} {colours[k]}" for k in range(len(colours)))
    return make_item(req, seed, archetype="probability", topic="Probability",
                     topic_slug="probability", strand="Probability", spec_ref="P1",
                     grade_band="2-4",
                     stem=f"A bag contains {desc} counters. A counter is taken at random.",
                     parts=parts)


# --------------------------------------------------------------------------- #
# Sample space of two spinners  (P2, grade 2)
# --------------------------------------------------------------------------- #
def build_sample_space(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a, b = rng.choice([(4, 4), (3, 4), (4, 3), (3, 3)])
    sums = [[i + j for j in range(1, b + 1)] for i in range(1, a + 1)]
    flat = [s for row in sums for s in row]
    target = rng.choice(sorted(set(flat)))
    count = flat.count(target)
    p = sympy.Rational(count, a * b)
    headers = ["+"] + [str(j) for j in range(1, b + 1)]
    rows = [[str(i)] + [str(i + j) for j in range(1, b + 1)] for i in range(1, a + 1)]
    table = Table(caption="Sample space (sum of the two spinners)", headers=headers, rows=rows)
    part = mk_part(
        prompt=f"Work out the probability that the total is {target}.", marks=2,
        answer=_frac(p),
        working=f"{count} of the {a * b} equally likely outcomes give {target}: "
        f"{count}/{a * b} = {_frac(p)}",
        mark_scheme=[_M1("for count of successful outcomes / total", f"{count}/{a * b}"),
                     _A1("cao", _frac(p))])
    return make_item(req, seed, archetype="sample-space", topic="Sample space",
                     topic_slug="sample-space", strand="Probability", spec_ref="P2",
                     grade_band="2-3",
                     stem=f"Two fair spinners, numbered 1 to {a} and 1 to {b}, are spun and "
                     "their scores added. The sample space is shown.",
                     parts=[part], table=table)


# --------------------------------------------------------------------------- #
# Frequency tree  (P3, grade 3)
# --------------------------------------------------------------------------- #
def build_frequency_trees(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    total = rng.choice([50, 60, 80, 100])
    A = rng.randint(total // 3, 2 * total // 3)
    B = total - A
    passA = rng.randint(A // 3, A)
    passB = rng.randint(B // 3, B)
    passes = passA + passB
    p = sympy.Rational(passes, total)
    tree = SD.probability_tree_svg(
        stage1=("Sport", "No sport"), leaves=("Pass", "Fail"),
        p1=(str(A), str(B)), p2_top=(str(passA), str(A - passA)),
        p2_bot=(str(passB), str(B - passB)))
    part = mk_part(
        prompt="A student is chosen at random. Work out the probability that the "
        "student passed.", marks=3, answer=_frac(p),
        working=f"Total passes = {passA} + {passB} = {passes}\n"
        f"P(pass) = {passes}/{total} = {_frac(p)}",
        mark_scheme=[_M1("for total who passed", f"{passA} + {passB}"),
                     _M1("for ÷ total", f"{passes}/{total}"), _A1("cao", _frac(p))])
    return make_item(req, seed, archetype="frequency-trees", topic="Frequency trees",
                     topic_slug="frequency-trees", strand="Probability", spec_ref="P3",
                     grade_band="3-4",
                     stem=f"{total} students were asked whether they play sport and whether "
                     "they passed a test. The frequency tree shows the results.",
                     parts=[part], diagram=_dia(tree, "A frequency tree.", scale=False))


# --------------------------------------------------------------------------- #
# Probability tree — two independent events  (P4, grade 5)
# --------------------------------------------------------------------------- #
def build_probability_trees(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    n = rng.randint(5, 10)
    r = rng.randint(2, n - 1)
    pr = sympy.Rational(r, n)
    pb = 1 - pr
    both = pr * pr            # with replacement: P(red, red)
    both_blue = pb * pb       # P(blue, blue)
    at_least_one = 1 - both_blue  # P(at least one red)
    tree = SD.probability_tree_svg(
        stage1=("Red", "Blue"), leaves=("Red", "Blue"),
        p1=(_frac(pr), _frac(pb)), p2_top=(_frac(pr), _frac(pb)),
        p2_bot=(_frac(pr), _frac(pb)))
    parts = [
        mk_part(
            label="a",
            prompt="Write down the probability that the first counter taken is red.",
            marks=1, answer=_frac(pr),
            working=f"{r} red out of {n}, so P(red) = {_frac(pr)}",
            mark_scheme=[_B1("cao", _frac(pr))]),
        mk_part(
            label="b",
            prompt="Work out the probability that both counters are red.",
            marks=2, answer=_frac(both),
            working=f"P(red and red) = {_frac(pr)} × {_frac(pr)} = {_frac(both)}",
            mark_scheme=[_M1("for multiplying the two probabilities",
                             f"{_frac(pr)} × {_frac(pr)}"),
                         _A1("cao", _frac(both))]),
        mk_part(
            label="c",
            prompt="Work out the probability that at least one counter is red.",
            marks=2, answer=_frac(at_least_one),
            working=(f"P(at least one red) = 1 − P(blue and blue)\n"
                     f"= 1 − {_frac(pb)} × {_frac(pb)} = {_frac(at_least_one)}"),
            mark_scheme=[_M1("for 1 − P(blue, blue)", f"1 − {_frac(both_blue)}"),
                         _A1("cao", _frac(at_least_one))]),
    ]
    return make_item(req, seed, archetype="probability-trees", topic="Probability trees",
                     topic_slug="probability-trees", strand="Probability", spec_ref="P4",
                     grade_band="4-6",
                     stem=f"A bag contains {r} red counters and {n - r} blue counters. "
                     "A counter is taken at random, its colour noted, and then replaced. "
                     "A second counter is then taken.",
                     parts=parts, diagram=_dia(tree, "A probability tree.", scale=False))


# --------------------------------------------------------------------------- #
# Venn diagrams  (P6, grade 5)
# --------------------------------------------------------------------------- #
def build_venn_diagrams(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    only_a = rng.randint(3, 12)
    both = rng.randint(2, 8)
    only_b = rng.randint(3, 12)
    outside = rng.randint(2, 8)
    total = only_a + both + only_b + outside
    pa = sympy.Rational(only_a + both, total)
    venn = SD.venn2_svg(set_a="A", set_b="B", only_a=str(only_a), both=str(both),
                        only_b=str(only_b), outside=str(outside))
    part = mk_part(
        prompt="One of the students is chosen at random. Work out the probability that "
        "the student is in set A.", marks=3, answer=_frac(pa),
        working=f"n(A) = {only_a} + {both} = {only_a + both}\n"
        f"Total = {total}\nP(A) = {only_a + both}/{total} = {_frac(pa)}",
        mark_scheme=[_M1("for n(A)", f"{only_a} + {both}"),
                     _M1("for ÷ total", f"/{total}"), _A1("cao", _frac(pa))])
    return make_item(req, seed, archetype="venn-diagrams", topic="Venn diagrams",
                     topic_slug="venn-diagrams", strand="Probability", spec_ref="P6",
                     grade_band="4-6",
                     stem=f"The Venn diagram shows information about {total} students and "
                     "two sets A and B.", parts=[part],
                     diagram=_dia(venn, "A two-set Venn diagram.", scale=False))


# --------------------------------------------------------------------------- #
# Product rule for counting  (P8, grade 6)
# --------------------------------------------------------------------------- #
def build_product_rule(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    mains = rng.randint(3, 7)
    sides = rng.randint(2, 6)
    drinks = rng.randint(2, 5)
    total = mains * sides * drinks
    part = mk_part(
        prompt="Work out the number of different meal deals possible.", marks=2,
        answer=str(total),
        working=f"{mains} × {sides} × {drinks} = {total}",
        mark_scheme=[_M1("for multiplying the numbers of choices",
                         f"{mains} × {sides} × {drinks}"), _A1("cao", str(total))])
    return make_item(req, seed, archetype="product-rule",
                     topic="Product rule for counting", topic_slug="product-rule",
                     strand="Probability", spec_ref="P8", grade_band="5-7",
                     stem=f"A meal deal has {mains} choices of main, {sides} choices of "
                     f"side and {drinks} choices of drink.", parts=[part])


# --------------------------------------------------------------------------- #
# Conditional probability from a two-way table  (P9, grade 7)
# --------------------------------------------------------------------------- #
def build_conditional_probability(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    bl = rng.randint(4, 14)   # boys, left-handed
    br = rng.randint(10, 30)  # boys, right-handed
    gl = rng.randint(4, 14)
    gr = rng.randint(10, 30)
    boys = bl + br
    p = sympy.Rational(bl, boys)   # P(left-handed | boy)
    table = Table(caption="", headers=["", "Left-handed", "Right-handed", "Total"], rows=[
        ["Boys", str(bl), str(br), str(boys)],
        ["Girls", str(gl), str(gr), str(gl + gr)],
        ["Total", str(bl + gl), str(br + gr), str(boys + gl + gr)],
    ])
    part = mk_part(
        prompt="A boy is chosen at random. Work out the probability that he is "
        "left-handed.", marks=2, answer=_frac(p),
        working=f"P(left | boy) = {bl}/{boys} = {_frac(p)}",
        mark_scheme=[_M1("for left-handed boys / total boys", f"{bl}/{boys}"),
                     _A1("cao", _frac(p))])
    return make_item(req, seed, archetype="conditional-probability",
                     topic="Conditional probability", topic_slug="conditional-probability",
                     strand="Probability", spec_ref="P9", grade_band="6-8",
                     stem="The two-way table shows whether some students are left- or "
                     "right-handed.", parts=[part], table=table)


# --------------------------------------------------------------------------- #
# STRETCH: form and solve an equation from a probability (grade 8-9, P7)
#          modelled on June 2022 Q11 (ratio+prob) and Q16 (exactly one)
# --------------------------------------------------------------------------- #
def build_probability_equation(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    x = sympy.Symbol("x")
    for _ in range(_MAX_ATTEMPTS):
        shape = rng.choice(["ratio", "exactly-one"])

        if shape == "ratio":
            A = rng.randint(4, 9)
            B = rng.randint(2, 7)
            xv = rng.randint(1, 9)
            total = A + B + xv
            P = sympy.Rational(A, total)
            # solving A/(A+B+x) = P recovers x
            sol = sympy.solve(sympy.Rational(A) / (A + B + x) - P, x)
            if sol != [xv]:
                continue
            return make_item(
                req, seed, archetype="probability-equation",
                topic="Probability (form an equation)", topic_slug="probability-equation",
                strand="Probability", spec_ref="P7", grade_band="7-9",
                stem=(f"A bag contains lime, strawberry and orange sweets in the ratio\n"
                      f"lime : strawberry : orange = {A} : {B} : x\n"
                      f"A sweet is taken at random. The probability it is lime is {_frac(P)}."),
                parts=[mk_part(
                    prompt="Work out the value of x.", marks=3, answer=str(xv),
                    working=(f"P(lime) = {A}/({A} + {B} + x) = {_frac(P)}\n"
                             f"{A}+{B}+x = {total}, so x = {xv}"),
                    mark_scheme=[_M1("for forming an equation in x",
                                     f"{A}/({A}+{B}+x) = {_frac(P)}"),
                                 _M1("for a correct method to solve", None),
                                 _A1("cao", str(xv))])])

        # exactly-one: independent events, P(pass A)=pa, P(exactly one)=e, find P(pass B)
        pa = sympy.Rational(rng.choice([1, 2, 3, 4]), rng.choice([5, 10, 20]))
        pb = sympy.Rational(rng.choice([1, 2, 3, 4, 6]), rng.choice([5, 10, 20]))
        if not (0 < pa < 1 and 0 < pb < 1) or pa == pb:
            continue
        e = pa * (1 - pb) + (1 - pa) * pb
        if e.q > 100:
            continue
        p = sympy.Symbol("p")
        sol = sympy.solve(pa * (1 - p) + (1 - pa) * p - e, p)
        if sol != [pb]:
            continue

        def dec(r):
            return f"{float(r):g}" if (r * 100) % 1 == 0 else _frac(r)
        return make_item(
            req, seed, archetype="probability-equation",
            topic="Probability (form an equation)", topic_slug="probability-equation",
            strand="Probability", spec_ref="P7", grade_band="8-9",
            stem=(f"A test has two parts, A and B. The probability of passing part A is "
                  f"{dec(pa)}. The probability of passing exactly one of the two parts is "
                  f"{dec(e)}. The two events are independent."),
            parts=[mk_part(
                prompt="Work out the probability of passing part B.", marks=4,
                answer=dec(pb),
                working=(f"P(exactly one) = P(A)·P(not B) + P(not A)·P(B)\n"
                         f"{dec(pa)}(1 − p) + {dec(1 - pa)}p = {dec(e)}\n"
                         f"p = {dec(pb)}"),
                mark_scheme=[_M1("for P(A)(1−p) + (1−P(A))p", None),
                             _M1("for = P(exactly one)", None),
                             _M1("for solving the linear equation", None),
                             _A1("cao", dec(pb))])])
    raise RuntimeError("probability-equation generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Systematic listing  (P8, grade 4-6)
# --------------------------------------------------------------------------- #
def build_systematic_listing(req: GenerateRequest) -> Item:
    import itertools
    seed = _seed(req)
    rng = Random(seed)
    digits = sorted(rng.sample(range(1, 10), 3))
    nums = sorted(a * 10 + b for a, b in itertools.permutations(digits, 2))
    count = len(nums)                       # = 3 × 2 = 6
    assert count == len(digits) * (len(digits) - 1)   # independent check
    listing = ", ".join(str(x) for x in nums)
    ds = ", ".join(str(d) for d in digits)
    return make_item(
        req, seed, archetype="systematic-listing",
        topic="Systematic listing", topic_slug="systematic-listing",
        strand="Probability", spec_ref="P8", grade_band="4-6",
        stem=f"Here are three digit cards.\n\n{ds}\n\nTwo of the cards are used to make "
        "a two-digit number. No digit may be used more than once.",
        parts=[
            mk_part(label="a",
                    prompt="Write down all the possible two-digit numbers.",
                    marks=2, answer=listing,
                    working=f"Work through each first digit in turn: {listing}",
                    mark_scheme=[_M1("a systematic, complete list (allow one slip)"),
                                 _A1("all correct with no repeats", listing)]),
            mk_part(label="b",
                    prompt="Write down how many two-digit numbers are possible.",
                    marks=1, answer=str(count),
                    working=f"{len(digits)} choices for the first digit × "
                    f"{len(digits) - 1} for the second = {count}",
                    mark_scheme=[_B1("cao", str(count))]),
        ], ao="AO2")
    raise RuntimeError("systematic-listing generator failed.")
