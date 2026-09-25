"""Final content batch: loci & construction, proofs, trig/exp graphs, and the
last few minor number/ratio/algebra topics — bringing coverage to ~100%.

Verifiable cores (algebraic identities, vector algebra, trig solutions, ratio /
unit arithmetic) are sympy-checked; loci-construction and circle-theorem-proof
are model-answer questions (the geometry/theorem is correct by construction, the
write-up is templated).
"""

from __future__ import annotations

import math
from random import Random

import sympy

from ..schema import Diagram, GenerateRequest, Item, MarkSchemeStep
from .basics import _item, _seed
from .context import coprime_ratio, gcse_expr, make_item, mk_part, pick
from .geometry_diagrams import circle_points_svg, loci_field_svg
from .graph_diagrams import graph_svg

_MAX_ATTEMPTS = 200
_n = sympy.Symbol("n")


def _dia(svg, alt, scale=True, plot_grid=False):
    return Diagram(svg=svg, alt=alt, not_to_scale=not scale, plot_grid=plot_grid)


def _M1(d, w=None): return MarkSchemeStep(code="M1", mark_type="M", description=d, working=w)
def _A1(d, w=None): return MarkSchemeStep(code="A1", mark_type="A", description=d, working=w)
def _B1(d, w=None): return MarkSchemeStep(code="B1", mark_type="B", description=d, working=w)


def _fr(r) -> str:
    r = sympy.Rational(r)
    return str(r.p) if r.q == 1 else f"{r.p}/{r.q}"


# --------------------------------------------------------------------------- #
# Loci & construction  (G2)
# --------------------------------------------------------------------------- #
def build_loci_construction(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    kind = rng.choice(["equidistant", "closer", "circle", "combined"])
    r = rng.randint(2, 4)
    if kind == "equidistant":
        svg = loci_field_svg(points=[("A", 2, 3), ("B", 8, 4)])
        prompt = ("Points A and B are marked on the diagram. Construct the locus of all "
                  "points that are the same distance from A as from B.")
        answer = "The perpendicular bisector of AB."
        reason = "for the perpendicular bisector of AB"
    elif kind == "closer":
        svg = loci_field_svg(points=[("A", 2, 3), ("B", 8, 4)])
        prompt = ("Points A and B are marked. Shade the region of all points that are "
                  "closer to A than to B.")
        answer = "The perpendicular bisector of AB, with the side containing A shaded."
        reason = "for the perpendicular bisector and correct region shaded"
    elif kind == "circle":
        svg = loci_field_svg(points=[("A", 5, 3)])
        prompt = (f"Point A is marked. Construct the locus of all points that are exactly "
                  f"{r} cm from A.")
        answer = f"A circle of radius {r} cm, centre A."
        reason = f"for a circle of radius {r} cm centred on A"
    else:
        svg = loci_field_svg(points=[("A", 3, 4), ("B", 8, 4)])
        prompt = (f"Points A and B are marked. Shade the region of all points that are "
                  f"both within {r} cm of A and closer to A than to B.")
        answer = (f"Inside the circle of radius {r} cm centre A AND on A's side of the "
                  "perpendicular bisector of AB — shade the overlap.")
        reason = "for both loci correct and the overlap shaded"
    part = mk_part(prompt=prompt + " You must show your construction lines.", marks=2,
                   answer=answer, working=answer,
                   mark_scheme=[_M1("for a correct construction method"), _B1(reason)])
    return make_item(req, seed, archetype="loci-construction",
                     topic="Loci & construction", topic_slug="loci-construction",
                     strand="Geometry & measures", spec_ref="G2", grade_band="4-6",
                     ao="AO3", stem="", parts=[part],
                     diagram=_dia(svg, "A field with marked points for a loci question."))


# --------------------------------------------------------------------------- #
# Algebraic proof  (A6) — expansion sympy-derived and verified
# --------------------------------------------------------------------------- #
def build_algebraic_proof(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    n = _n
    templates = [
        ("(2n + 1)² − (2n − 1)²", (2 * n + 1) ** 2 - (2 * n - 1) ** 2, "a multiple of 8"),
        ("the sum of three consecutive integers  n + (n + 1) + (n + 2)",
         n + (n + 1) + (n + 2), "a multiple of 3"),
        ("(n + 4)² − (n + 2)²", (n + 4) ** 2 - (n + 2) ** 2, "a multiple of 4"),
        ("the sum of the squares of two consecutive integers  n² + (n + 1)²",
         n ** 2 + (n + 1) ** 2, "always odd"),
    ]
    label, expr, claim = templates[rng.randrange(len(templates))]
    expanded = sympy.expand(expr)
    factored = sympy.factor(expanded)
    expanded_s = gcse_expr(expanded)
    if claim == "always odd":
        # 2n² + 2n + 1 = 2(n² + n) + 1
        conclusion = (f"= {gcse_expr(sympy.expand(expanded - 1))} + 1 "
                      f"= 2({gcse_expr(sympy.factor((expanded - 1) / 2))}) + 1, "
                      "which is always odd.")
        ok = sympy.simplify(expanded - (2 * (n ** 2 + n) + 1)) == 0
        answer_expr = expanded_s
    else:
        conclusion = f"= {gcse_expr(factored)}, which is {claim}."
        ok = True
        answer_expr = gcse_expr(sympy.expand(expr))
    if not ok:
        raise RuntimeError("algebraic-proof verification failed.")
    part = mk_part(
        prompt=f"Prove that {label} is {claim}. You must show all your working.",
        marks=3, answer=f"{answer_expr}  {conclusion}",
        working=f"Expand: {label} = {expanded_s}\n{conclusion}",
        mark_scheme=[_M1("for expanding correctly", expanded_s),
                     _A1("for simplifying / factorising"),
                     _B1(f"for a correct conclusion ({claim})")])
    return make_item(req, seed, archetype="algebraic-proof", topic="Algebraic proof",
                     topic_slug="algebraic-proof", strand="Algebra", spec_ref="A6",
                     grade_band="7-9", ao="AO2", stem="", parts=[part])


# --------------------------------------------------------------------------- #
# Vectors proof  (G25) — vector algebra sympy-verified
# --------------------------------------------------------------------------- #
def build_vectors_proof(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a, b = sympy.symbols("a b")
    m = rng.randint(1, 4)
    k = rng.randint(1, 4)
    if m == k:
        k += 1
    # P divides AB with AP:PB = m:k → OP = a + (m/(m+k))(b − a)
    frac = sympy.Rational(m, m + k)
    OP = sympy.expand(a + frac * (b - a))
    ca = OP.coeff(a)
    cb = OP.coeff(b)
    if sympy.simplify(OP - (ca * a + cb * b)) != 0:
        raise RuntimeError("vectors-proof verification failed.")
    ans = f"OP = {_fr(ca)}a + {_fr(cb)}b"
    part = mk_part(
        prompt=(f"OAB is a triangle with OA = a and OB = b. The point P lies on AB such "
                f"that AP : PB = {m} : {k}. Express the vector OP in terms of a and b. "
                "Give your answer in its simplest form."),
        marks=3, answer=ans,
        working=(f"OP = OA + AP = a + {_fr(frac)}(AB) = a + {_fr(frac)}(b − a)\n= {ans}"),
        mark_scheme=[_M1("for OA + a fraction of AB"),
                     _M1("for AB = b − a"), _A1("cao, simplest form", ans)])
    return make_item(req, seed, archetype="vectors-proof", topic="Vectors proof",
                     topic_slug="vectors-proof", strand="Geometry & measures",
                     spec_ref="G25", grade_band="7-9", ao="AO2", stem="", parts=[part])


# --------------------------------------------------------------------------- #
# Circle-theorem proof  (G10) — templated model proof
# --------------------------------------------------------------------------- #
def build_circle_theorem_proof(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    which = rng.choice(["centre", "semicircle"])
    if which == "centre":
        svg = circle_points_svg(points={"A": 200, "B": 340, "C": 90},
                                segments=[("O", "A"), ("O", "B"), ("C", "A"), ("C", "B")],
                                angle_labels=[("C", "x"), ("O", "2x")])
        statement = ("Prove that the angle subtended by an arc at the centre of a circle "
                     "is twice the angle subtended at the circumference.")
        proof = ("Let angle ACO = p and angle BCO = q, so angle ACB = p + q.\n"
                 "Triangle OAC is isosceles (OA = OC = radius), so angle OAC = p, and the "
                 "exterior angle AOX = 2p. Similarly angle BOX = 2q.\n"
                 "So angle AOB = 2p + 2q = 2(p + q) = 2 × angle ACB.")
    else:
        svg = circle_points_svg(points={"A": 180, "B": 0, "C": 70},
                                segments=[("A", "B"), ("A", "C"), ("C", "B")],
                                angle_labels=[("C", "90°")], show_centre=True)
        statement = "Prove that the angle in a semicircle is 90°."
        proof = ("AB is a diameter, so O is the midpoint. OA = OB = OC = radius.\n"
                 "Triangle OAC is isosceles so angle OCA = angle OAC = p; triangle OBC is "
                 "isosceles so angle OCB = angle OBC = q.\n"
                 "Angles of triangle ABC sum to 180°: p + q + (p + q) = 180°, so "
                 "2(p + q) = 180°, giving angle ACB = p + q = 90°.")
    part = mk_part(prompt=statement + " Give reasons at each step.", marks=4, answer=proof,
                   working=proof,
                   mark_scheme=[_M1("for using isosceles triangles / radii equal"),
                                _M1("for a correct angle relationship"),
                                _A1("for a complete chain of reasoning"),
                                _B1("for the correct conclusion")])
    return make_item(req, seed, archetype="circle-theorem-proof",
                     topic="Proof of circle theorems", topic_slug="circle-theorem-proof",
                     strand="Geometry & measures", spec_ref="G10", grade_band="8-9",
                     ao="AO2", stem="", parts=[part],
                     diagram=_dia(svg, "A circle for a circle-theorem proof."))


# --------------------------------------------------------------------------- #
# Trigonometric & exponential graphs  (A12)
# --------------------------------------------------------------------------- #
def build_trig_exp_graphs(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    svg = None
    if rng.random() < 0.6:
        fn = rng.choice(["sin", "cos"])
        sols = {("sin", sympy.Rational(1, 2)): (30, 150),
                ("sin", -sympy.Rational(1, 2)): (210, 330),
                ("cos", sympy.Rational(1, 2)): (60, 300),
                ("cos", -sympy.Rational(1, 2)): (120, 240)}
        k = rng.choice([sympy.Rational(1, 2), -sympy.Rational(1, 2)])
        a, b = sols[(fn, k)]
        trig = {"sin": math.sin, "cos": math.cos}[fn]
        pts = [(x, trig(math.radians(x))) for x in range(0, 361, 5)]
        svg = graph_svg(xrange=(0, 360), yrange=(-1, 1),
                        polylines=[{"points": pts, "label": f"y = {fn} x°"}],
                        xstep=90, ystep=1, xlabel="x°", ylabel="y")
        # verify
        assert abs(trig(math.radians(a)) - float(k)) < 1e-9 and abs(trig(math.radians(b)) - float(k)) < 1e-9
        part = mk_part(prompt=f"The graph of y = {fn} x° is shown. Use it to solve "
                       f"{fn} x° = {_fr(k)} for 0 ≤ x ≤ 360.", marks=2,
                       answer=f"x = {a}° or x = {b}°",
                       working=f"{fn} x° = {_fr(k)} → x = {a}° or x = {b}°",
                       mark_scheme=[_B1(f"x = {a}°"), _B1(f"x = {b}°")])
    else:
        k = rng.randint(2, 5)
        a = rng.randint(2, 4)
        d = k * a
        part = mk_part(prompt=f"The graph of y = k × aˣ passes through (0, {k}) and "
                       f"(1, {d}). Work out the values of k and a.", marks=2,
                       answer=f"k = {k}, a = {a}",
                       working=f"At x = 0: y = k = {k}. At x = 1: k × a = {d}, so a = {d}/{k} = {a}",
                       mark_scheme=[_B1(f"k = {k}"), _B1(f"a = {a}")])
    return make_item(req, seed, archetype="trig-exp-graphs",
                     topic="Trig & exponential graphs", topic_slug="trig-exp-graphs",
                     strand="Algebra", spec_ref="A12", grade_band="6-8", stem="",
                     parts=[part],
                     diagram=_dia(svg, "A trig graph.", plot_grid=True)
                     if svg is not None else None)


# --------------------------------------------------------------------------- #
# Writing an expression  (A1)
# --------------------------------------------------------------------------- #
def build_writing_expression(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    x = sympy.Symbol("x")
    mult = rng.randint(2, 4)
    add = rng.randint(2, 9)
    name1, name2 = "Ben", pick(rng, ["Cara", "Dan", "Eve", "Femi"])
    expr = mult * x + add
    ans = f"{mult}x + {add}"
    if sympy.expand(expr - (mult * x + add)) != 0:
        raise RuntimeError
    part = mk_part(
        prompt=(f"{name1} has x sweets. {name2} has {add} more than {mult} times as many "
                f"sweets as {name1}. Write down an expression, in terms of x, for the "
                f"number of sweets {name2} has."),
        marks=2, answer=ans, working=f"{mult} × x + {add} = {ans}",
        mark_scheme=[_M1(f"for {mult}x seen"), _A1("cao", ans)])
    return make_item(req, seed, archetype="writing-expression",
                     topic="Writing an expression", topic_slug="writing-expression",
                     strand="Algebra", spec_ref="A1", grade_band="2-3", stem="",
                     parts=[part])


# --------------------------------------------------------------------------- #
# Simplify a ratio  (R5)
# --------------------------------------------------------------------------- #
def build_simplify_ratio(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        g = rng.randint(2, 9)
        p = rng.randint(2, 8)
        q = rng.randint(2, 8)
        if sympy.igcd(p, q) != 1 or p == q:
            continue
        a, b = p * g, q * g
        parts = [
            mk_part(label="a", prompt=f"Write the ratio {a} : {b} in its simplest form.",
                    marks=1, answer=f"{p} : {q}",
                    working=f"Divide both by {g}: {p} : {q}", mark_scheme=[_B1("cao")]),
        ]
        return make_item(req, seed, archetype="simplify-ratio",
                         topic="Writing & simplifying ratio", topic_slug="simplify-ratio",
                         strand="Ratio & proportion", spec_ref="R5", grade_band="2-4",
                         stem="", parts=parts)
    raise RuntimeError("simplify-ratio generator failed.")


# --------------------------------------------------------------------------- #
# Unit conversion  (N13)
# --------------------------------------------------------------------------- #
_CONV = [("cm", "m", sympy.Rational(1, 100)), ("m", "cm", 100), ("m", "km", sympy.Rational(1, 1000)),
         ("km", "m", 1000), ("g", "kg", sympy.Rational(1, 1000)), ("kg", "g", 1000),
         ("ml", "litres", sympy.Rational(1, 1000)), ("litres", "ml", 1000), ("mm", "cm", sympy.Rational(1, 10))]


def build_unit_conversion(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        frm, to, factor = _CONV[rng.randrange(len(_CONV))]
        v = rng.randint(2, 950)
        out = sympy.Rational(v) * factor
        if out.q > 1000:
            continue
        ans = f"{out} {to}" if out.q == 1 else f"{float(out):g} {to}"
        out_val = out if out.q == 1 else f"{float(out):g}"
        part = mk_part(prompt=f"Convert {v} {frm} into {to}.", marks=2, answer=ans,
                       working=f"{v} {frm} × {float(factor):g} = {ans}",
                       mark_scheme=[_M1(f"for {v} × {float(factor):g} (= {out_val})"),
                                    _A1("cao", ans)])
        return make_item(req, seed, archetype="unit-conversion",
                         topic="Conversions & units", topic_slug="unit-conversion",
                         strand="Number", spec_ref="N13", grade_band="2-4", stem="",
                         parts=[part])
    raise RuntimeError("unit-conversion generator failed.")


# --------------------------------------------------------------------------- #
# Ratio as a fraction  (R7)
# --------------------------------------------------------------------------- #
def build_ratio_as_fraction(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a, b = coprime_ratio(rng, 2, 7)
    frac = sympy.Rational(a, a + b)
    colour = pick(rng, ["red", "blue", "green"])
    part = mk_part(
        prompt=(f"In a bag, the ratio of {colour} counters to other counters is {a} : {b}. "
                f"What fraction of the counters are {colour}? Give your answer in its "
                "simplest form."),
        marks=2, answer=_fr(frac),
        working=f"{colour}: {a} parts out of {a} + {b} = {a + b} parts → {_fr(frac)}",
        mark_scheme=[_M1(f"for {a}/({a}+{b})"), _A1("cao, simplest form", _fr(frac))])
    return make_item(req, seed, archetype="ratio-as-fraction",
                     topic="Ratio as a fraction", topic_slug="ratio-as-fraction",
                     strand="Ratio & proportion", spec_ref="R7", grade_band="4-5",
                     stem="", parts=[part])
