"""Geometry generators (Phase K) — the bulk of the remaining geometry topics.

Finished-figure read/compute questions, deterministic from a seed, every answer
re-derived and checked with sympy. Reuses the diagram engine (existing + the new
geometry_diagrams / graph_svg primitives).
"""

from __future__ import annotations

import math
from random import Random

import sympy

from ..schema import Diagram, GenerateRequest, Item, MarkSchemeStep
from .basics import _seed
from .context import make_item, mk_part, pick, sig_figs
from .diagrams import cuboid_svg, cylinder_svg, circle_sector_svg, triangle_svg
from .geometry_diagrams import (
    angle_facts_svg,
    bearing_svg,
    circle_points_svg,
    circle_svg,
    compound_shape_svg,
    cone_svg,
    parallel_lines_svg,
    sphere_svg,
)
from .graph_diagrams import graph_svg
from .pythagoras import _simplify_surd, _surd_str

_MAX_ATTEMPTS = 300


def _dia(svg, alt, scale=True, plot_grid=False):
    return Diagram(svg=svg, alt=alt, not_to_scale=not scale, plot_grid=plot_grid)


def _M1(d, w=None): return MarkSchemeStep(code="M1", mark_type="M", description=d, working=w)
def _A1(d, w=None): return MarkSchemeStep(code="A1", mark_type="A", description=d, working=w)
def _B1(d, w=None): return MarkSchemeStep(code="B1", mark_type="B", description=d, working=w)


# --------------------------------------------------------------------------- #
# Area & perimeter of a compound (L-shaped) region  (G16)
# --------------------------------------------------------------------------- #
def build_area_perimeter(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    W = rng.randint(7, 14)
    H = rng.randint(6, 12)
    nw = rng.randint(2, W - 3)
    nh = rng.randint(2, H - 3)
    area = W * H - nw * nh
    perim = 2 * (W + H)
    dia = _dia(compound_shape_svg(W=W, H=H, nw=nw, nh=nh),
               f"An L-shape from a {W} by {H} rectangle with a {nw} by {nh} corner removed.")
    parts = [
        mk_part(label="a", prompt="Work out the area of the shape.", marks=3,
                answer=f"{area} cm²",
                working=f"{W} × {H} − {nw} × {nh} = {W * H} − {nw * nh} = {area} cm²",
                mark_scheme=[_M1("for a complete method (split or subtract)"),
                             _M1("for the areas"), _A1("cao", f"{area} cm²")]),
        mk_part(label="b", prompt="Work out the perimeter of the shape.", marks=2,
                answer=f"{perim} cm", working=f"2 × ({W} + {H}) = {perim} cm",
                mark_scheme=[_M1("for adding all the sides"), _A1("cao", f"{perim} cm")]),
    ]
    return make_item(req, seed, archetype="area-perimeter", topic="Area & perimeter",
                     topic_slug="area-perimeter", strand="Geometry & measures",
                     spec_ref="G16", grade_band="2-4", stem="The diagram shows a shape.",
                     parts=parts, diagram=dia)


# --------------------------------------------------------------------------- #
# Angle facts (triangle / straight line)  (G3)
# --------------------------------------------------------------------------- #
def build_angle_facts(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    kind = rng.choice(["triangle", "line"])
    if kind == "triangle":
        a = rng.randint(35, 80)
        b = rng.randint(35, 80)
        if a + b >= 170:
            b = 170 - a
        x = 180 - a - b
        dia = _dia(angle_facts_svg(kind="triangle", known=(a, b)),
                   f"A triangle with angles {a}°, {b}° and x.")
        working = f"Angles in a triangle sum to 180°: x = 180 − {a} − {b} = {x}"
        reason = "angles in a triangle sum to 180°"
    else:
        a = rng.randint(40, 140)
        x = 180 - a
        dia = _dia(angle_facts_svg(kind="line", known=a),
                   f"Angles {a}° and x on a straight line.")
        working = f"Angles on a straight line sum to 180°: x = 180 − {a} = {x}"
        reason = "angles on a straight line sum to 180°"
    part = mk_part(prompt="Work out the size of the angle marked x. Give a reason for "
                   "your answer.", marks=2, answer=f"x = {x}°",
                   working=working, mark_scheme=[_M1("for a correct method"),
                                                 _B1(f"cao with reason ({reason})")])
    return make_item(req, seed, archetype="angle-facts", topic="Angle facts",
                     topic_slug="angle-facts", strand="Geometry & measures",
                     spec_ref="G3", grade_band="2-3", ao="AO2", stem="", parts=[part],
                     diagram=dia)


# --------------------------------------------------------------------------- #
# Angles in parallel lines  (G3)
# --------------------------------------------------------------------------- #
def build_parallel_angles(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a = rng.randint(40, 140)
    rel = rng.choice(["alternate", "co-interior", "corresponding"])
    x = a if rel != "co-interior" else 180 - a
    reason = {"alternate": "alternate angles are equal",
              "co-interior": "co-interior angles sum to 180°",
              "corresponding": "corresponding angles are equal"}[rel]
    dia = _dia(parallel_lines_svg(known=a), f"Two parallel lines with a transversal; "
               f"one angle {a}° and x.")
    part = mk_part(prompt="Work out the size of the angle marked x. Give a reason for "
                   "your answer.", marks=2, answer=f"x = {x}°",
                   working=f"{reason}: x = {x}°",
                   mark_scheme=[_B1(f"x = {x}"), _B1(f"reason: {reason}")])
    return make_item(req, seed, archetype="parallel-angles",
                     topic="Angles in parallel lines", topic_slug="parallel-angles",
                     strand="Geometry & measures", spec_ref="G3", grade_band="4-5",
                     ao="AO2", stem="", parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Circle area & circumference  (G17)
# --------------------------------------------------------------------------- #
def build_circle_measures(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    calc = bool(req.calculator)
    r = rng.randint(3, 12)
    area_c, circ_c = r * r, 2 * r
    if calc:
        area = f"{sig_figs(math.pi * r * r, 3)} cm²"
        circ = f"{sig_figs(2 * math.pi * r, 3)} cm"
        note = " Give your answer correct to 3 significant figures."
    else:
        area, circ = f"{area_c}π cm²", f"{circ_c}π cm"
        note = " Give your answer in terms of π."
    dia = _dia(circle_svg(radius_label=f"{r} cm"), f"A circle of radius {r} cm.")
    parts = [
        mk_part(label="a", prompt="Work out the area of the circle." + note, marks=2,
                answer=area, working=f"πr² = π × {r}² = {area}",
                mark_scheme=[_M1("for π × r²"), _A1("cao", area)]),
        mk_part(label="b", prompt="Work out the circumference of the circle." + note,
                marks=2, answer=circ, working=f"2πr = 2 × π × {r} = {circ}",
                mark_scheme=[_M1("for 2πr"), _A1("cao", circ)]),
    ]
    return make_item(req, seed, archetype="circle-measures",
                     topic="Area & circumference of circles", topic_slug="circle-measures",
                     strand="Geometry & measures", spec_ref="G17", grade_band="3-5",
                     stem="", parts=parts, diagram=dia)


# --------------------------------------------------------------------------- #
# Surface area (cuboid / cylinder)  (G17)
# --------------------------------------------------------------------------- #
def build_surface_area(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    calc = bool(req.calculator)
    shape = "cylinder" if (calc and rng.random() < 0.5) else "cuboid"
    if shape == "cuboid":
        l, w, h = rng.randint(3, 10), rng.randint(2, 8), rng.randint(2, 8)
        sa = 2 * (l * w + l * h + w * h)
        dia = _dia(cuboid_svg(length_label=f"{l} cm", width_label=f"{w} cm",
                              height_label=f"{h} cm"), f"A cuboid {l}×{w}×{h} cm.")
        part = mk_part(prompt="Work out the total surface area of the cuboid.", marks=3,
                       answer=f"{sa} cm²",
                       working=f"2({l}×{w} + {l}×{h} + {w}×{h}) = {sa} cm²",
                       mark_scheme=[_M1("for the areas of the faces"),
                                    _M1("for a complete method"), _A1("cao", f"{sa} cm²")])
    else:
        r, h = rng.randint(2, 7), rng.randint(4, 12)
        coeff = 2 * r * r + 2 * r * h
        exact = math.pi * coeff
        answer = f"{sig_figs(exact, 3)} cm²"
        dia = _dia(cylinder_svg(radius_label=f"{r} cm", height_label=f"{h} cm"),
                   f"A cylinder radius {r} cm, height {h} cm.")
        part = mk_part(prompt="Work out the total surface area of the cylinder. Give your "
                       "answer correct to 3 significant figures.", marks=3, answer=answer,
                       working=f"2πr² + 2πrh = π({2 * r * r} + {2 * r * h}) = {answer}",
                       mark_scheme=[_M1("for 2πr²"), _M1("for 2πrh"), _A1("awrt", answer)])
    return make_item(req, seed, archetype="surface-area", topic="Surface area",
                     topic_slug="surface-area", strand="Geometry & measures",
                     spec_ref="G17", grade_band="4-6", stem="", parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Spheres & cones  (G17) — formula supplied in the question
# --------------------------------------------------------------------------- #
def build_spheres_cones(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    calc = bool(req.calculator)
    if rng.random() < 0.5:
        r = rng.choice([3, 6, 9]) if not calc else rng.randint(2, 9)
        coeff = sympy.Rational(4, 3) * r**3
        exact = math.pi * float(coeff)
        answer = f"{sig_figs(exact, 3)} cm³" if calc else f"{coeff}π cm³"
        note = " Give your answer correct to 3 s.f." if calc else " Give your answer in terms of π."
        dia = _dia(sphere_svg(radius_label=f"{r} cm"), f"A sphere of radius {r} cm.")
        part = mk_part(prompt=f"A sphere has radius {r} cm. The volume of a sphere is "
                       f"V = 4/3 πr³. Work out its volume." + note, marks=3, answer=answer,
                       working=f"4/3 × π × {r}³ = {answer}",
                       mark_scheme=[_M1("for r³"), _M1("for 4/3 πr³"), _A1("cao", answer)])
    else:
        r = rng.choice([3, 6]) if not calc else rng.randint(2, 8)
        h = rng.choice([3, 6, 9]) if not calc else rng.randint(3, 12)
        coeff = sympy.Rational(1, 3) * r**2 * h
        exact = math.pi * float(coeff)
        answer = f"{sig_figs(exact, 3)} cm³" if calc else f"{coeff}π cm³"
        note = " Give your answer correct to 3 s.f." if calc else " Give your answer in terms of π."
        dia = _dia(cone_svg(radius_label=f"{r} cm", height_label=f"{h} cm"),
                   f"A cone radius {r} cm, height {h} cm.")
        part = mk_part(prompt=f"A cone has base radius {r} cm and height {h} cm. The volume "
                       f"of a cone is V = 1/3 πr²h. Work out its volume." + note, marks=3,
                       answer=answer, working=f"1/3 × π × {r}² × {h} = {answer}",
                       mark_scheme=[_M1("for πr²h"), _M1("for 1/3"), _A1("cao", answer)])
    return make_item(req, seed, archetype="spheres-cones", topic="Spheres & cones",
                     topic_slug="spheres-cones", strand="Geometry & measures",
                     spec_ref="G17", grade_band="5-7", stem="", parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Arc length & sector perimeter  (G18)
# --------------------------------------------------------------------------- #
def build_arc_length(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    calc = bool(req.calculator)
    theta = rng.choice([30, 45, 60, 90, 120, 135, 150, 180, 270])
    r = rng.randint(3, 12)
    arc_c = sympy.Rational(theta * 2 * r, 360)
    if not calc and arc_c.q != 1:
        r = 6  # ensure a clean coefficient in terms of π
        arc_c = sympy.Rational(theta * 2 * r, 360)
    arc_exact = float(arc_c) * math.pi
    answer = f"{sig_figs(arc_exact, 3)} cm" if calc else f"{arc_c}π cm"
    note = " Give your answer correct to 3 s.f." if calc else " Give your answer in terms of π."
    dia = _dia(circle_sector_svg(radius_label=f"{r} cm", theta=theta),
               f"A sector radius {r} cm, angle {theta}°.")
    part = mk_part(prompt="Work out the length of the arc of the sector." + note, marks=3,
                   answer=answer, working=f"({theta}/360) × 2π × {r} = {answer}",
                   mark_scheme=[_M1("for 2πr"), _M1("for × θ/360"), _A1("cao", answer)])
    return make_item(req, seed, archetype="arc-length",
                     topic="Arc length & sector perimeter", topic_slug="arc-length",
                     strand="Geometry & measures", spec_ref="G18", grade_band="5-7",
                     stem="", parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Transformations — image coordinates  (G7)
# --------------------------------------------------------------------------- #
def build_transformations(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    px, py = rng.randint(-4, 4), rng.randint(-4, 4)
    kind = rng.choice(["reflect-y", "reflect-x", "reflect-yx", "rotate-180",
                       "rotate-90cw", "translate"])
    if kind == "reflect-y":
        img, desc = (-px, py), "reflect in the y-axis"
    elif kind == "reflect-x":
        img, desc = (px, -py), "reflect in the x-axis"
    elif kind == "reflect-yx":
        img, desc = (py, px), "reflect in the line y = x"
    elif kind == "rotate-180":
        img, desc = (-px, -py), "rotate 180° about the origin"
    elif kind == "rotate-90cw":
        img, desc = (py, -px), "rotate 90° clockwise about the origin"
    else:
        a, b = rng.randint(-4, 4), rng.randint(-4, 4)
        img, desc = (px + a, py + b), f"translate by the vector ({a}, {b})"
    svg = graph_svg(xrange=(-6, 6), yrange=(-6, 6), points=[(px, py, "P", True)])
    part = mk_part(prompt=f"The point P has coordinates ({px}, {py}). Work out the "
                   f"coordinates of the image of P after a {desc}.", marks=2,
                   answer=f"({img[0]}, {img[1]})",
                   working=f"P({px}, {py}) → ({img[0]}, {img[1]})",
                   mark_scheme=[_M1("for a correct method"),
                                _A1("cao", f"({img[0]}, {img[1]})")])
    return make_item(req, seed, archetype="transformations", topic="Transformations",
                     topic_slug="transformations", strand="Geometry & measures",
                     spec_ref="G7", grade_band="3-6", stem="", parts=[part],
                     diagram=_dia(svg, f"Point P at ({px}, {py}) on a grid.",
                                  plot_grid=True))


# --------------------------------------------------------------------------- #
# Enlargement — image under a scale factor  (G7)
# --------------------------------------------------------------------------- #
def build_enlargement(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        cx, cy = rng.randint(-2, 2), rng.randint(-2, 2)
        px, py = rng.randint(-4, 4), rng.randint(-4, 4)
        k = rng.choice([2, 3, -1, -2, sympy.Rational(1, 2)])
        ix, iy = cx + k * (px - cx), cy + k * (py - cy)
        if sympy.Rational(ix).q != 1 or sympy.Rational(iy).q != 1:
            continue
        ix, iy = int(ix), int(iy)
        if not (-9 <= ix <= 9 and -9 <= iy <= 9):
            continue
        svg = graph_svg(xrange=(-9, 9), yrange=(-9, 9),
                        points=[(px, py, "P", True), (cx, cy, "O", True)],
                        xstep=2, ystep=2)
        part = mk_part(prompt=f"Enlarge the point P ({px}, {py}) by scale factor {k} with "
                       f"centre of enlargement ({cx}, {cy}). Work out the coordinates of "
                       "the image of P.", marks=3, answer=f"({ix}, {iy})",
                       working=f"image = centre + {k}×(P − centre) = ({ix}, {iy})",
                       mark_scheme=[_M1("for the vector from the centre to P"),
                                    _M1(f"for multiplying by {k}"),
                                    _A1("cao", f"({ix}, {iy})")])
        return make_item(req, seed, archetype="enlargement", topic="Enlargement",
                         topic_slug="enlargement", strand="Geometry & measures",
                         spec_ref="G7", grade_band="5-7", stem="", parts=[part],
                         diagram=_dia(svg, f"Point P and centre on a grid.",
                                      plot_grid=True))
    raise RuntimeError("enlargement generator failed.")


# --------------------------------------------------------------------------- #
# Bearings — back bearing  (G15)
# --------------------------------------------------------------------------- #
def build_bearings(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    bearing = rng.randint(20, 340)
    back = (bearing + 180) % 360
    dia = _dia(bearing_svg(bearing=bearing), f"The bearing of B from A is {bearing:03d}°.")
    part = mk_part(prompt=f"The bearing of B from A is {bearing:03d}°. Work out the "
                   "bearing of A from B.", marks=2, answer=f"{back:03d}°",
                   working=f"{bearing} {'+' if bearing < 180 else '−'} 180 = {back:03d}°",
                   mark_scheme=[_M1("for ± 180°"), _A1("cao (3 figures)", f"{back:03d}°")])
    return make_item(req, seed, archetype="bearings", topic="Bearings",
                     topic_slug="bearings", strand="Geometry & measures", spec_ref="G15",
                     grade_band="4-5", stem="", parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Vectors — column vector arithmetic  (G25)
# --------------------------------------------------------------------------- #
def build_vectors(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a = (rng.randint(-4, 5), rng.randint(-4, 5))
    b = (rng.randint(-4, 5), rng.randint(-4, 5))
    s = rng.choice([2, 3])
    res = (s * a[0] - b[0], s * a[1] - b[1])
    svg = graph_svg(xrange=(-6, 6), yrange=(-6, 6),
                    polylines=[{"points": [(0, 0), a], "label": "a"},
                               {"points": [(0, 0), b], "label": "b"}])
    part = mk_part(prompt=f"a = ({a[0]}, {a[1]}) and b = ({b[0]}, {b[1]}) are vectors. "
                   f"Work out {s}a − b. Give your answer in the form (x, y).", marks=2,
                   answer=f"({res[0]}, {res[1]})",
                   working=f"{s}({a[0]}, {a[1]}) − ({b[0]}, {b[1]}) = ({res[0]}, {res[1]})",
                   mark_scheme=[_M1("for a correct method"),
                                _A1("cao", f"({res[0]}, {res[1]})")])
    return make_item(req, seed, archetype="vectors", topic="Vectors",
                     topic_slug="vectors", strand="Geometry & measures", spec_ref="G25",
                     grade_band="5-7", stem="", parts=[part],
                     diagram=_dia(svg, "Vectors a and b on a grid.", plot_grid=True))


# --------------------------------------------------------------------------- #
# Exact trig values  (G21)
# --------------------------------------------------------------------------- #
_EXACT = {
    ("sin", 30): ("1/2", sympy.Rational(1, 2)),
    ("sin", 45): ("√2/2", sympy.sqrt(2) / 2),
    ("sin", 60): ("√3/2", sympy.sqrt(3) / 2),
    ("cos", 30): ("√3/2", sympy.sqrt(3) / 2),
    ("cos", 45): ("√2/2", sympy.sqrt(2) / 2),
    ("cos", 60): ("1/2", sympy.Rational(1, 2)),
    ("tan", 30): ("√3/3", sympy.sqrt(3) / 3),
    ("tan", 45): ("1", sympy.Integer(1)),
    ("tan", 60): ("√3", sympy.sqrt(3)),
}


def build_exact_trig(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    keys = rng.sample(list(_EXACT), 2)
    parts = []
    for i, (fn, deg) in enumerate(keys):
        s, val = _EXACT[(fn, deg)]
        trig = {"sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan}[fn]
        assert sympy.simplify(trig(sympy.rad(deg)) - val) == 0
        parts.append(mk_part(label=chr(97 + i),
                     prompt=f"Write down the exact value of {fn} {deg}°.", marks=1,
                     answer=s, working=f"{fn} {deg}° = {s}", mark_scheme=[_B1("cao")]))
    return make_item(req, seed, archetype="exact-trig", topic="Exact trig values",
                     topic_slug="exact-trig", strand="Geometry & measures",
                     spec_ref="G21", grade_band="5-6", stem="", parts=parts)


# --------------------------------------------------------------------------- #
# Congruent triangles — corresponding measurement  (G5)
# --------------------------------------------------------------------------- #
def build_congruent_triangles(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    ab = rng.randint(5, 12)
    bc = rng.randint(5, 12)
    ang = rng.randint(40, 100)
    dia = _dia(triangle_svg(side_ab=f"{ab} cm", side_bc=f"{bc} cm", angle_b=f"{ang}°"),
               "Two congruent triangles ABC and DEF.")
    part = mk_part(prompt=f"Triangle ABC is congruent to triangle DEF, with AB = {ab} cm, "
                   f"BC = {bc} cm and angle ABC = {ang}°. Write down the length of EF and "
                   "the size of angle DEF.", marks=2,
                   answer=f"EF = {bc} cm, angle DEF = {ang}°",
                   working=f"Congruent → corresponding parts equal: EF = BC = {bc} cm, "
                   f"angle DEF = angle ABC = {ang}°",
                   mark_scheme=[_B1(f"EF = {bc} cm"), _B1(f"angle DEF = {ang}°")])
    return make_item(req, seed, archetype="congruent-triangles",
                     topic="Congruent triangles", topic_slug="congruent-triangles",
                     strand="Geometry & measures", spec_ref="G5", grade_band="5-7",
                     stem="", parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Circle theorems — find the angle + name the theorem  (G10)
# --------------------------------------------------------------------------- #
def build_circle_theorems(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    which = rng.choice(["centre", "semicircle", "cyclic"])
    if which == "centre":
        circ = rng.randint(20, 70)
        x = 2 * circ
        pts = {"A": 200, "B": 340, "C": 90}
        dia = circle_points_svg(points=pts, segments=[("O", "A"), ("O", "B"),
                                ("C", "A"), ("C", "B")],
                                angle_labels=[("C", f"{circ}°"), ("O", "x°")])
        reason = "the angle at the centre is twice the angle at the circumference"
        prompt = (f"A, B and C are points on a circle, centre O. Angle ACB = {circ}°. "
                  "Work out the size of angle AOB, marked x. Give a reason.")
    elif which == "semicircle":
        other = rng.randint(25, 65)
        x = 90 - other
        pts = {"A": 180, "B": 0, "C": 70}
        dia = circle_points_svg(points=pts, segments=[("A", "B"), ("A", "C"), ("C", "B")],
                                angle_labels=[("A", f"{other}°"), ("C", "x°")],
                                show_centre=False)
        reason = "the angle in a semicircle is 90°, then angles in a triangle sum to 180°"
        prompt = (f"AB is a diameter of the circle. C is a point on the circle. "
                  f"Angle CAB = {other}°. Work out the size of angle ABC, marked x. "
                  "Give a reason for your answer.")
    else:
        opp = rng.randint(70, 110)
        x = 180 - opp
        pts = {"A": 140, "B": 40, "C": 320, "D": 220}
        dia = circle_points_svg(points=pts, segments=[("A", "B"), ("B", "C"),
                                ("C", "D"), ("D", "A")],
                                angle_labels=[("A", f"{opp}°"), ("C", "x°")],
                                show_centre=False)
        reason = "opposite angles of a cyclic quadrilateral sum to 180°"
        prompt = (f"ABCD is a cyclic quadrilateral. Angle DAB = {opp}°. Work out the size "
                  "of angle BCD, marked x. Give a reason.")
    part = mk_part(prompt=prompt, marks=2, answer=f"x = {x}°",
                   working=f"{reason}: x = {x}°",
                   mark_scheme=[_M1(f"for using: {reason}"), _B1(f"x = {x}° with reason")])
    return make_item(req, seed, archetype="circle-theorems", topic="Circle theorems",
                     topic_slug="circle-theorems", strand="Geometry & measures",
                     spec_ref="G10", grade_band="6-8", ao="AO2", stem="", parts=[part],
                     diagram=_dia(dia, "A circle with points and a marked angle."))


# --------------------------------------------------------------------------- #
# 3D Pythagoras — space diagonal of a cuboid  (G20)
# --------------------------------------------------------------------------- #
def build_pythagoras_3d(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    l, w, h = rng.randint(3, 12), rng.randint(3, 12), rng.randint(3, 12)
    diag = math.sqrt(l * l + w * w + h * h)
    ans = sig_figs(diag, 3)
    dia = _dia(cuboid_svg(length_label=f"{l} cm", width_label=f"{w} cm",
                          height_label=f"{h} cm"), f"A cuboid {l}×{w}×{h} cm.")
    part = mk_part(prompt="Work out the length of the longest diagonal of the cuboid. "
                   "Give your answer correct to 3 significant figures.", marks=3,
                   answer=f"{ans} cm", answer_tolerance=0.05,
                   working=f"√({l}² + {w}² + {h}²) = √{l * l + w * w + h * h} = {ans} cm",
                   mark_scheme=[_M1("for l² + w² + h²"), _M1("for the square root"),
                                _A1("awrt", ans)])
    return make_item(req, seed, archetype="pythagoras-3d", topic="3D Pythagoras",
                     topic_slug="pythagoras-3d", strand="Geometry & measures",
                     spec_ref="G20", grade_band="6-8", stem="", parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Scale drawings & maps  (R6)
# --------------------------------------------------------------------------- #
def build_scale_drawings(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    n = rng.choice([25000, 50000, 100000])
    d = rng.randint(3, 12)
    real_cm = d * n
    real_km = sympy.Rational(real_cm, 100000)  # cm → km
    part = mk_part(prompt=f"A map has a scale of 1 : {n:,}. Two towns are {d} cm apart on "
                   "the map. Work out the real distance between the towns, in kilometres.",
                   marks=3, answer=f"{real_km} km",
                   working=f"{d} × {n:,} = {real_cm:,} cm = {real_km} km",
                   mark_scheme=[_M1(f"for {d} × {n:,}"), _M1("for cm → km (÷100000)"),
                                _A1("cao", f"{real_km} km")])
    return make_item(req, seed, archetype="scale-drawings", topic="Scale drawings & maps",
                     topic_slug="scale-drawings", strand="Ratio & proportion",
                     spec_ref="R6", grade_band="3-4", stem="", parts=[part])


# --------------------------------------------------------------------------- #
# Area of any triangle — ½ab sin C  (G16)
# --------------------------------------------------------------------------- #
def build_triangle_area(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a = rng.randint(5, 15)
    b = rng.randint(5, 15)
    C = rng.randint(30, 140)
    area = 0.5 * a * b * math.sin(math.radians(C))
    ans = sig_figs(area, 3)
    dia = _dia(triangle_svg(side_ab=f"{a} cm", side_ca=f"{b} cm", angle_a=f"{C}°",
                            side_bc="", ), f"A triangle with sides {a} cm, {b} cm and "
               f"included angle {C}°.")
    part = mk_part(prompt="Work out the area of the triangle. Give your answer correct to "
                   "3 significant figures.", marks=3, answer=f"{ans} cm²",
                   answer_tolerance=0.05,
                   working=f"Area = ½ × {a} × {b} × sin {C}° = {ans} cm²",
                   mark_scheme=[_M1("for ½ab sin C with values"),
                                _M1("for evaluating"), _A1("awrt", ans)])
    return make_item(req, seed, archetype="triangle-area", topic="Area of any triangle",
                     topic_slug="triangle-area", strand="Geometry & measures",
                     spec_ref="G16", grade_band="6-8", stem="", parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Similar shapes — area & volume scale factors  (R12)
# --------------------------------------------------------------------------- #
def build_similar_area_volume(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        h1, h2 = rng.randint(2, 5), rng.randint(3, 8)
        if h1 >= h2 or h2 % h1 != 0:
            continue
        k = sympy.Rational(h2, h1)
        which = rng.choice(["area", "volume"])
        if which == "area":
            a1 = rng.randint(4, 20)
            a2 = a1 * k**2
            if a2.q != 1:
                continue
            prompt = (f"Two similar shapes have heights {h1} cm and {h2} cm. The area of "
                      f"the smaller shape is {a1} cm². Work out the area of the larger shape.")
            answer, working = f"{int(a2)} cm²", f"area SF = ({h2}/{h1})² = {k**2}; {a1} × {k**2} = {int(a2)} cm²"
            m2_desc = f"for the area factor ({h2}/{h1})² = {k**2}, then {a1} × {k**2} (= {int(a2)})"
        else:
            v1 = rng.randint(4, 20)
            v2 = v1 * k**3
            if v2.q != 1:
                continue
            prompt = (f"Two similar solids have heights {h1} cm and {h2} cm. The volume of "
                      f"the smaller solid is {v1} cm³. Work out the volume of the larger solid.")
            answer, working = f"{int(v2)} cm³", f"volume SF = ({h2}/{h1})³ = {k**3}; {v1} × {k**3} = {int(v2)} cm³"
            m2_desc = f"for the volume factor ({h2}/{h1})³ = {k**3}, then {v1} × {k**3} (= {int(v2)})"
        part = mk_part(prompt=prompt, marks=3, answer=answer, working=working,
                       mark_scheme=[_M1(f"for the length scale factor {h2} ÷ {h1} (= {k})"),
                                    _M1(m2_desc), _A1("cao", answer)])
        return make_item(req, seed, archetype="similar-area-volume",
                         topic="Similar shapes (area & volume)",
                         topic_slug="similar-area-volume", strand="Ratio & proportion",
                         spec_ref="R12", grade_band="6-8", stem="", parts=[part])
    raise RuntimeError("similar-area-volume generator failed.")


# --------------------------------------------------------------------------- #
# Plans and elevations  (G13, grade 4-6)
# --------------------------------------------------------------------------- #
def build_plans_elevations(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a, b, c = rng.sample(range(2, 9), 3)      # length, depth, height (distinct)
    svg = cuboid_svg(length_label=f"{a} cm", width_label=f"{b} cm",
                     height_label=f"{c} cm")
    return make_item(
        req, seed, archetype="plans-elevations",
        topic="Plans & elevations", topic_slug="plans-elevations",
        strand="Geometry & measures", spec_ref="G13", grade_band="4-6",
        stem=f"The diagram shows a cuboid measuring {a} cm by {b} cm by {c} cm.",
        parts=[
            mk_part(label="a", prompt="Write down the dimensions of the plan (the view "
                    "from above).", marks=1, answer=f"a rectangle {a} cm by {b} cm",
                    working=f"Looking down: length × depth = {a} cm × {b} cm",
                    mark_scheme=[_B1("cao", f"{a} cm by {b} cm")]),
            mk_part(label="b", prompt="Write down the dimensions of the front elevation.",
                    marks=1, answer=f"a rectangle {a} cm by {c} cm",
                    working=f"Front face: length × height = {a} cm × {c} cm",
                    mark_scheme=[_B1("cao", f"{a} cm by {c} cm")]),
            mk_part(label="c", prompt="Write down the dimensions of the side elevation.",
                    marks=1, answer=f"a rectangle {b} cm by {c} cm",
                    working=f"Side face: depth × height = {b} cm × {c} cm",
                    mark_scheme=[_B1("cao", f"{b} cm by {c} cm")]),
        ],
        diagram=_dia(svg, f"A cuboid {a} cm by {b} cm by {c} cm.", scale=False), ao="AO2")
    raise RuntimeError("plans-elevations generator failed.")
