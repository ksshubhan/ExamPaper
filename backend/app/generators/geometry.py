"""Geometry-strand generators.

Deterministic from a seed, every number re-derived/checked with sympy, an
Edexcel-style mark scheme. Phase F attaches diagrams to the angle and volume
questions and adds grade 8-9 archetypes: sector area, right-angled trig
(SOHCAHTOA), the sine & cosine rules, and similar shapes. Calculator answers
are given to 3 significant figures; non-calculator answers are exact / in terms
of π.
"""

from __future__ import annotations

import math
from random import Random

import sympy

from ..schema import Diagram, GenerateRequest, Item, MarkSchemeStep
from .basics import _seed
from .context import make_item, mk_part, pick, sig_figs
from .diagrams import (
    circle_sector_svg,
    cuboid_svg,
    cylinder_svg,
    regular_polygon_svg,
    similar_triangles_svg,
    triangle_svg,
    triangular_prism_svg,
)

_MAX_ATTEMPTS = 200
_NICE_SIDES = [5, 6, 8, 9, 10, 12, 15, 18]

_CYLINDER_CTX = [("A tin of soup", "the tin"), ("A candle", "the candle"),
                 ("A metal rod", "the rod"), ("A water tank", "the tank")]
_PRISM_CTX = [("A doorstop", "the doorstop"), ("A bar of chocolate", "the bar"),
              ("A glass paperweight", "the paperweight")]
_CUBOID_CTX = [("A box", "the box"), ("A water tank", "the tank"),
               ("A concrete block", "the block")]


def _dia(svg: str, alt: str) -> Diagram:
    return Diagram(svg=svg, alt=alt, not_to_scale=True)


# --------------------------------------------------------------------------- #
# Angles in polygons — now with a regular-polygon figure  (G3)
# --------------------------------------------------------------------------- #
def _angle_variant(req: GenerateRequest) -> str | None:
    v = (req.variant or req.archetype or "").lower()
    if "sides" in v:
        return "sides"
    if "interior" in v:
        return "interior"
    return None


def build_polygon_angles(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    variant = _angle_variant(req)
    for _ in range(_MAX_ATTEMPTS):
        family = variant or rng.choice(["interior", "sides"])
        n = pick(rng, _NICE_SIDES)
        exterior = sympy.Rational(360, n)
        interior = 180 - exterior
        if exterior.q != 1 or interior.q != 1:
            continue
        if sympy.Rational((n - 2) * 180, n) != interior:
            continue
        dia = _dia(regular_polygon_svg(n), f"A regular polygon with {n} sides.")

        if family == "sides":
            part = mk_part(
                prompt="Work out the number of sides of the polygon.", marks=3,
                answer=f"{n}",
                working=(f"Exterior angle = 180° − {interior}° = {exterior}°\n"
                         f"Number of sides = 360° ÷ {exterior}° = {n}"),
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description="for the exterior angle 180 − interior",
                                   working=f"180 − {interior} (= {exterior})"),
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description="for 360 ÷ exterior",
                                   working=f"360 ÷ {exterior}"),
                    MarkSchemeStep(code="A1", mark_type="A", description="cao",
                                   working=f"{n}"),
                ],
            )
            return make_item(
                req, seed, archetype="polygon-sides", topic="Angles in polygons",
                topic_slug="angles", strand="Geometry & measures", spec_ref="G3",
                grade_band="4-6",
                stem=f"Each interior angle of a regular polygon is {interior}°.",
                parts=[part], diagram=dia,
            )

        stem = f"The diagram shows a regular polygon with {n} sides."
        if rng.random() < 0.5:
            part_a = mk_part(
                label="a",
                prompt="Work out the size of each exterior angle of the polygon.",
                marks=1, answer=f"{exterior}°",
                working=f"Exterior angle = 360° ÷ {n} = {exterior}°",
                mark_scheme=[MarkSchemeStep(code="B1", mark_type="B", description="cao",
                                            working=f"360 ÷ {n} = {exterior}")],
            )
            part_b = mk_part(
                label="b",
                prompt="Hence work out the size of each interior angle of the polygon.",
                marks=2, answer=f"{interior}°",
                working=f"Interior angle = 180° − {exterior}° = {interior}°",
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description="for 180 − their exterior angle",
                                   working=f"180 − {exterior}"),
                    MarkSchemeStep(code="A1", mark_type="A", description="cao",
                                   working=f"{interior}°"),
                ],
            )
            return make_item(
                req, seed, archetype="polygon-interior-angle",
                topic="Angles in polygons", topic_slug="angles",
                strand="Geometry & measures", spec_ref="G3", grade_band="4-6",
                stem=stem, parts=[part_a, part_b], diagram=dia,
            )

        part = mk_part(
            prompt="Work out the size of each interior angle.", marks=3,
            answer=f"{interior}°",
            working=(f"Exterior angle = 360° ÷ {n} = {exterior}°\n"
                     f"Interior angle = 180° − {exterior}° = {interior}°"),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for the exterior angle 360 ÷ n",
                               working=f"360 ÷ {n} (= {exterior})"),
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for 180 − exterior (or (n−2)×180 ÷ n)",
                               working=f"180 − {exterior}"),
                MarkSchemeStep(code="A1", mark_type="A", description="cao",
                               working=f"{interior}°"),
            ],
        )
        return make_item(
            req, seed, archetype="polygon-interior-angle", topic="Angles in polygons",
            topic_slug="angles", strand="Geometry & measures", spec_ref="G3",
            grade_band="4-6", stem=stem, parts=[part], diagram=dia,
        )
    raise RuntimeError("polygon-angles generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Volume — cylinder / triangular prism / cuboid, each with a figure  (G17)
# --------------------------------------------------------------------------- #
def build_volume(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    calc = bool(req.calculator)
    for _ in range(_MAX_ATTEMPTS):
        shape = rng.choice(["cylinder", "prism", "cuboid"])

        if shape == "cylinder":
            r = rng.randint(3, 9)
            h = rng.randint(4, 15)
            coeff = r * r * h
            v_exact = sympy.pi * r**2 * h
            if sympy.simplify(v_exact - coeff * sympy.pi) != 0:
                continue
            noun, the = pick(rng, _CYLINDER_CTX)
            if calc:
                answer = f"{sig_figs(float(v_exact), 3)} cm³"
                last = f"= {coeff}π = {sig_figs(float(v_exact), 3)} cm³ (3 s.f.)"
                precision = " Give your answer correct to 3 significant figures."
            else:
                answer = f"{coeff}π cm³"
                last = f"= {coeff}π cm³"
                precision = " Give your answer in terms of π."
            dia = _dia(cylinder_svg(radius_label=f"{r} cm", height_label=f"{h} cm"),
                       f"A cylinder with radius {r} cm and height {h} cm.")
            part = mk_part(
                prompt=f"Work out the volume of {the}." + precision, marks=3,
                answer=answer,
                working=f"V = πr²h = π × {r}² × {h}\n= π × {r * r} × {h}\n{last}",
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description=f"for π × r² (= π × {r * r})",
                                   working=f"π × {r}²"),
                    MarkSchemeStep(code="M1", mark_type="M", description="for × height",
                                   working=f"× {h}"),
                    MarkSchemeStep(code="A1", mark_type="A",
                                   description="cao" + ("" if calc else " (in terms of π)"),
                                   working=answer),
                ],
            )
            return make_item(
                req, seed, archetype="volume-cylinder", topic="Volume",
                topic_slug="volume", strand="Geometry & measures", spec_ref="G17",
                grade_band="4-6",
                stem=f"{noun} is in the shape of a solid cylinder with radius {r} cm "
                f"and height {h} cm.",
                parts=[part], diagram=dia,
            )

        if shape == "cuboid":
            l = rng.randint(3, 12)
            w = rng.randint(2, 9)
            h = rng.randint(2, 9)
            volume = l * w * h
            if sympy.Integer(l) * w * h != volume:
                continue
            noun, the = pick(rng, _CUBOID_CTX)
            dia = _dia(
                cuboid_svg(length_label=f"{l} cm", width_label=f"{w} cm",
                           height_label=f"{h} cm"),
                f"A cuboid measuring {l} cm by {w} cm by {h} cm.")
            part = mk_part(
                prompt=f"Work out the volume of {the}.", marks=2,
                answer=f"{volume} cm³",
                working=f"V = {l} × {w} × {h} = {volume} cm³",
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description="for {l} × {w} × {h}".format(l=l, w=w, h=h),
                                   working=f"{l} × {w} × {h}"),
                    MarkSchemeStep(code="A1", mark_type="A", description="cao",
                                   working=f"{volume} cm³"),
                ],
            )
            return make_item(
                req, seed, archetype="volume-cuboid", topic="Volume",
                topic_slug="volume", strand="Geometry & measures", spec_ref="G17",
                grade_band="3-5",
                stem=f"{noun} is in the shape of a cuboid measuring {l} cm by "
                f"{w} cm by {h} cm.",
                parts=[part], diagram=dia,
            )

        # triangular prism
        b = rng.randint(4, 12)
        t = rng.randint(3, 10)
        if (b * t) % 2 != 0:
            continue
        length = rng.randint(5, 15)
        area = sympy.Rational(b * t, 2)
        volume = area * length
        if area.q != 1 or volume.q != 1:
            continue
        noun, the = pick(rng, _PRISM_CTX)
        dia = _dia(
            triangular_prism_svg(base_label=f"{b} cm", height_label=f"{t} cm",
                                 length_label=f"{length} cm"),
            f"A triangular prism, cross-section base {b} cm and height {t} cm, "
            f"length {length} cm.")
        part = mk_part(
            prompt=f"Work out the volume of {the}.", marks=3, answer=f"{volume} cm³",
            working=(f"Area of cross-section = ½ × {b} × {t} = {area} cm²\n"
                     f"Volume = {area} × {length} = {volume} cm³"),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for the area of the triangular cross-section",
                               working=f"½ × {b} × {t} (= {area})"),
                MarkSchemeStep(code="M1", mark_type="M", description="for × length",
                               working=f"{area} × {length}"),
                MarkSchemeStep(code="A1", mark_type="A", description="cao",
                               working=f"{volume} cm³"),
            ],
        )
        return make_item(
            req, seed, archetype="volume-prism", topic="Volume", topic_slug="volume",
            strand="Geometry & measures", spec_ref="G17", grade_band="4-6",
            stem=f"{noun} is in the shape of a prism. Its cross-section is a triangle "
            f"with base {b} cm and perpendicular height {t} cm. "
            f"The prism is {length} cm long.",
            parts=[part], diagram=dia,
        )
    raise RuntimeError("volume generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Sector area (with a circle-sector figure)  (G18)
# --------------------------------------------------------------------------- #
def build_sector(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    calc = bool(req.calculator)
    for _ in range(_MAX_ATTEMPTS):
        theta = rng.choice([30, 40, 45, 60, 90, 120, 135, 150, 180, 240, 270])
        r = rng.randint(3, 12)
        area_coeff = sympy.Rational(theta * r * r, 360)   # area = coeff·π
        arc_coeff = sympy.Rational(theta * 2 * r, 360)    # arc length = coeff·π
        if not calc and (area_coeff.q != 1 or arc_coeff.q != 1):
            continue
        area_exact = area_coeff * sympy.pi
        arc_exact = arc_coeff * sympy.pi
        dia = _dia(circle_sector_svg(radius_label=f"{r} cm", theta=theta),
                   f"A sector of a circle, radius {r} cm, angle {theta} degrees.")
        if calc:
            arc_ans = f"{sig_figs(float(arc_exact), 3)} cm"
            arc_last = f"= {sig_figs(float(arc_exact), 3)} cm (3 s.f.)"
            area_ans = f"{sig_figs(float(area_exact), 3)} cm²"
            area_last = f"= {sig_figs(float(area_exact), 3)} cm² (3 s.f.)"
            precision = " Give your answer correct to 3 significant figures."
        else:
            arc_ans = f"{arc_coeff}π cm"
            arc_last = f"= {arc_coeff}π cm"
            area_ans = f"{area_coeff}π cm²"
            area_last = f"= {area_coeff}π cm²"
            precision = " Give your answer in terms of π."
        exact = "" if calc else " (in terms of π)"
        parts = [
            mk_part(
                label="a",
                prompt="Work out the length of the arc of the sector." + precision,
                marks=2, answer=arc_ans,
                working=(f"Arc = (θ/360) × 2πr = ({theta}/360) × 2 × π × {r}\n{arc_last}"),
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description="for a complete method (θ/360) × 2πr",
                                   working=f"({theta}/360) × 2 × π × {r}"),
                    MarkSchemeStep(code="A1", mark_type="A",
                                   description="cao" + exact, working=arc_ans),
                ]),
            mk_part(
                label="b",
                prompt="Work out the area of the sector." + precision, marks=3,
                answer=area_ans,
                working=(f"Area = (θ/360) × πr² = ({theta}/360) × π × {r}²\n"
                         f"= ({theta}/360) × {r * r}π\n{area_last}"),
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description="for πr² (or the fraction θ/360)",
                                   working=f"π × {r}²  and  {theta}/360"),
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description="for a complete method (θ/360) × πr²",
                                   working=f"({theta}/360) × π × {r}²"),
                    MarkSchemeStep(code="A1", mark_type="A",
                                   description="cao" + exact, working=area_ans),
                ]),
        ]
        return make_item(
            req, seed, archetype="sector-area", topic="Sector area & arc length",
            topic_slug="sector", strand="Geometry & measures", spec_ref="G18",
            grade_band="5-7",
            stem=f"The diagram shows a sector of a circle with radius {r} cm and "
            f"angle {theta}° at the centre.",
            parts=parts, diagram=dia,
        )
    raise RuntimeError("sector generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Right-angled trigonometry — SOHCAHTOA (right-triangle figure)  (G20)
# --------------------------------------------------------------------------- #
def build_right_triangle_trig(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        theta = rng.randint(20, 70)
        # unknown ∈ {opp,adj,hyp}; known is one of the others; θ at A.
        unknown = rng.choice(["opp", "adj", "hyp"])
        known = rng.choice([s for s in ["opp", "adj", "hyp"] if s != unknown])
        known_val = rng.randint(5, 20)
        th = sympy.rad(theta)
        # relations relative to angle A: opp=BC, adj=AB, hyp=AC
        rel = {
            ("adj", "opp"): sympy.tan(th),          # opp = adj·tanθ
            ("hyp", "opp"): sympy.sin(th),          # opp = hyp·sinθ
            ("hyp", "adj"): sympy.cos(th),          # adj = hyp·cosθ
            ("opp", "adj"): 1 / sympy.tan(th),      # adj = opp/tanθ
            ("opp", "hyp"): 1 / sympy.sin(th),      # hyp = opp/sinθ
            ("adj", "hyp"): 1 / sympy.cos(th),      # hyp = adj/cosθ
        }
        key = (known, unknown)
        if key not in rel:
            continue
        val = float(known_val * sympy.N(rel[key]))
        if val <= 0 or not math.isfinite(val):
            continue
        ans = sig_figs(val, 3)

        # ratio name + equation for the working / mark scheme
        ratio_of = {("adj", "opp"): "tan", ("opp", "adj"): "tan",
                    ("hyp", "opp"): "sin", ("opp", "hyp"): "sin",
                    ("hyp", "adj"): "cos", ("adj", "hyp"): "cos"}[key]
        # map to triangle_svg sides: adj->side_ab, opp->side_bc, hyp->side_ca
        side_for = {"adj": "side_ab", "opp": "side_bc", "hyp": "side_ca"}
        kwargs = {"right_angle_at": "B", "angle_a": f"{theta}°",
                  "side_ab": "", "side_bc": "", "side_ca": ""}
        kwargs[side_for[known]] = f"{known_val} cm"
        kwargs[side_for[unknown]] = "x"
        dia = _dia(triangle_svg(**kwargs),
                   f"A right-angled triangle with an angle of {theta}° and a side "
                   f"of {known_val} cm; side x to be found.")

        # '×' when the unknown is the numerator of the ratio, else '÷'.
        op = "×" if key in {("adj", "opp"), ("hyp", "opp"), ("hyp", "adj")} else "÷"
        eq = (f"{ratio_of} {theta}° = x / {known_val}" if op == "×"
              else f"{ratio_of} {theta}° = {known_val} / x")
        working = (
            f"{eq}\nx = {known_val} {op} {ratio_of} {theta}° = {ans} cm (3 s.f.)"
        )
        part = mk_part(
            prompt="Work out the length of the side marked x. Give your answer "
            "correct to 3 significant figures.",
            marks=3, answer=f"{ans} cm", answer_tolerance=0.05, working=working,
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for using {ratio_of} of {theta}°",
                               working=f"{ratio_of} {theta}°"),
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for a correct rearrangement/substitution",
                               working=None),
                MarkSchemeStep(code="A1", mark_type="A",
                               description="awrt (3 s.f.)", working=f"{ans}"),
            ],
        )
        return make_item(
            req, seed, archetype="right-triangle-trig", topic="Trigonometry",
            topic_slug="trigonometry", strand="Geometry & measures", spec_ref="G20",
            grade_band="5-7",
            stem="The diagram shows a right-angled triangle.",
            parts=[part], diagram=dia,
        )
    raise RuntimeError("trigonometry generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Sine & cosine rule (general-triangle figure)  (G22)
# --------------------------------------------------------------------------- #
def build_sine_cosine_rule(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        rule = rng.choice(["cosine", "sine"])

        if rule == "cosine":
            # find side a (BC, opposite A) from b (CA), c (AB), angle A
            b = rng.randint(6, 15)
            c = rng.randint(6, 15)
            A = rng.randint(35, 120)
            a2 = b**2 + c**2 - 2 * b * c * sympy.cos(sympy.rad(A))
            val = float(sympy.sqrt(sympy.N(a2)))
            if val <= 0 or not math.isfinite(val):
                continue
            ans = sig_figs(val, 3)
            dia = _dia(triangle_svg(side_ab=f"{c} cm", side_ca=f"{b} cm",
                                    angle_a=f"{A}°", side_bc="x"),
                       f"A triangle with two sides {b} cm and {c} cm and the "
                       f"included angle {A}°.")
            part = mk_part(
                prompt="Work out the length of the side marked x. Give your answer "
                "correct to 3 significant figures.",
                marks=3, answer=f"{ans} cm", answer_tolerance=0.05,
                working=(f"a² = b² + c² − 2bc·cos A\n"
                         f"x² = {b}² + {c}² − 2×{b}×{c}×cos {A}°\n"
                         f"x = {ans} cm (3 s.f.)"),
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description="for the cosine rule with values",
                                   working=f"{b}² + {c}² − 2×{b}×{c}×cos {A}°"),
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description="for √ of a correct evaluation",
                                   working=None),
                    MarkSchemeStep(code="A1", mark_type="A",
                                   description="awrt (3 s.f.)", working=f"{ans}"),
                ],
            )
            return make_item(
                req, seed, archetype="sine-cosine-rule", topic="Sine & cosine rule",
                topic_slug="sine-cosine-rule", strand="Geometry & measures",
                spec_ref="G22", grade_band="7-9",
                stem="The diagram shows a triangle.",
                parts=[part], diagram=dia,
            )

        # sine rule: find side b (CA, opp B) from angle A, side a (BC), angle B
        A = rng.randint(35, 85)
        B = rng.randint(35, 85)
        if A + B >= 160:
            continue
        a = rng.randint(6, 16)
        # a/sinA = b/sinB  ->  b = a·sinB/sinA
        val = float(a * sympy.sin(sympy.rad(B)) / sympy.sin(sympy.rad(A)))
        if val <= 0 or not math.isfinite(val):
            continue
        ans = sig_figs(val, 3)
        dia = _dia(triangle_svg(side_bc=f"{a} cm", angle_a=f"{A}°", angle_b=f"{B}°",
                                side_ca="x"),
                   f"A triangle with a side {a} cm opposite {A}°, and {B}° at another "
                   f"vertex.")
        part = mk_part(
            prompt="Work out the length of the side marked x. Give your answer "
            "correct to 3 significant figures.",
            marks=3, answer=f"{ans} cm", answer_tolerance=0.05,
            working=(f"a/sin A = b/sin B\n"
                     f"x = {a} × sin {B}° ÷ sin {A}°\n= {ans} cm (3 s.f.)"),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for the sine rule with values",
                               working=f"{a} × sin {B}° ÷ sin {A}°"),
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for a correct rearrangement",
                               working=None),
                MarkSchemeStep(code="A1", mark_type="A",
                               description="awrt (3 s.f.)", working=f"{ans}"),
            ],
        )
        return make_item(
            req, seed, archetype="sine-cosine-rule", topic="Sine & cosine rule",
            topic_slug="sine-cosine-rule", strand="Geometry & measures",
            spec_ref="G22", grade_band="7-9",
            stem="The diagram shows a triangle.", parts=[part], diagram=dia,
        )
    raise RuntimeError("sine-cosine-rule generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Similar shapes (two-triangle figure)  (R12)
# --------------------------------------------------------------------------- #
def build_similar_shapes(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        base1 = rng.randint(3, 9)
        k = rng.choice([sympy.Rational(3, 2), sympy.Integer(2),
                        sympy.Rational(5, 2), sympy.Integer(3)])
        base2 = base1 * k
        if base2.q != 1:
            continue
        side1 = rng.randint(4, 12)
        side2 = side1 * k
        if side2.q != 1:
            continue
        dia = _dia(
            similar_triangles_svg(left_base=f"{base1} cm", left_side=f"{side1} cm",
                                  right_base=f"{base2} cm", right_side="x"),
            f"Two similar triangles; bases {base1} cm and {base2} cm.")
        part = mk_part(
            prompt="Work out the length of the side marked x.",
            marks=3, answer=f"{side2} cm",
            working=(f"Scale factor = {base2} ÷ {base1} = {k}\n"
                     f"x = {side1} × {k} = {side2} cm"),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for the scale factor {base2} ÷ {base1} (= {k})",
                               working=None),
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for {side1} × {k} (= {side2})",
                               working=None),
                MarkSchemeStep(code="A1", mark_type="A", description="cao",
                               working=f"{side2} cm"),
            ],
        )
        return make_item(
            req, seed, archetype="similar-shapes", topic="Similar shapes",
            topic_slug="similar-shapes", strand="Ratio & proportion", spec_ref="R12",
            grade_band="5-7", stem="The two triangles shown are mathematically similar.",
            parts=[part], diagram=dia,
        )
    raise RuntimeError("similar-shapes generator failed to produce a valid item.")
