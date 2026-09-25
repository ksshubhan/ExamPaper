"""Graph & coordinate-geometry generators.

Questions are generated finished (the line/curve is drawn to scale) and ask the
student to read, interpret or compute — so every answer is exact and
sympy-verifiable. Deterministic from a seed; integer-friendly parameters keep
gradients, intercepts, roots and intersections clean.
"""

from __future__ import annotations

from random import Random

import sympy

from ..schema import Diagram, GenerateRequest, Item, MarkSchemeStep
from .basics import _seed
from .context import make_item, mk_part
from .graph_diagrams import (
    function_sketch_svg,
    graph_panels_svg,
    graph_svg,
    speed_time_svg,
)

_MAX_ATTEMPTS = 300
_x = sympy.Symbol("x")


def _dia(svg: str, alt: str) -> Diagram:
    # Every figure in this module is a coordinate graph / graph-paper plot, so it
    # takes the large plotting box (plot_grid=True) — small boxes leave the grid
    # too cramped to read values off or plot on.
    return Diagram(svg=svg, alt=alt, not_to_scale=False, plot_grid=True)


def _num(v) -> str:
    v = sympy.Rational(v)
    return str(v.p) if v.q == 1 else f"{v.p}/{v.q}"


def _lin(m, c) -> str:
    if m == 1:
        mp = "x"
    elif m == -1:
        mp = "-x"
    else:
        mp = f"{_num(m)}x"
    if c > 0:
        return f"y = {mp} + {c}"
    if c < 0:
        return f"y = {mp} - {abs(c)}"
    return f"y = {mp}"


def _M1(d, w=None): return MarkSchemeStep(code="M1", mark_type="M", description=d, working=w)
def _A1(d, w=None): return MarkSchemeStep(code="A1", mark_type="A", description=d, working=w)
def _B1(d, w=None): return MarkSchemeStep(code="B1", mark_type="B", description=d, working=w)


def _line_points(m, c, xr):
    return [(xr[0], m * xr[0] + c), (xr[1], m * xr[1] + c)]


def _sample(f, xr, yr, step=0.2, skip_zero=False):
    """Sample y=f(x) over xr, keeping only points inside yr (for curves)."""
    pts, x = [], xr[0]
    while x <= xr[1] + 1e-9:
        if not (skip_zero and abs(x) < 0.4):
            y = f(x)
            if yr[0] - 0.5 <= y <= yr[1] + 0.5:
                pts.append((x, y))
        x += step
    return pts


# --------------------------------------------------------------------------- #
# Coordinates & midpoint  (G11)
# --------------------------------------------------------------------------- #
def build_coordinates(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    ax, ay = rng.randint(-5, 5), rng.randint(-5, 5)
    bx, by = rng.randint(-5, 5), rng.randint(-5, 5)
    if (ax, ay) == (bx, by):
        bx += 2
    mx, my = sympy.Rational(ax + bx, 2), sympy.Rational(ay + by, 2)
    svg = graph_svg(xrange=(-6, 6), yrange=(-6, 6),
                    polylines=[{"points": [(ax, ay), (bx, by)], "dashed": True}],
                    points=[(ax, ay, "A", True), (bx, by, "B", True)])
    part = mk_part(
        prompt=f"A is ({ax}, {ay}) and B is ({bx}, {by}). Work out the coordinates of "
        "the midpoint of AB.", marks=2, answer=f"({_num(mx)}, {_num(my)})",
        working=f"Midpoint = (({ax}+{bx})/2, ({ay}+{by})/2) = ({_num(mx)}, {_num(my)})",
        mark_scheme=[_M1("for a correct midpoint method"),
                     _A1("cao", f"({_num(mx)}, {_num(my)})")])
    return make_item(req, seed, archetype="coordinates", topic="Coordinates",
                     topic_slug="coordinates", strand="Geometry & measures",
                     spec_ref="G11", grade_band="1-3",
                     stem="The diagram shows the points A and B.", parts=[part], diagram=_dia(svg, "Two points A and B on a grid."))


# --------------------------------------------------------------------------- #
# Linear graphs — read a value  (A9)
# --------------------------------------------------------------------------- #
def build_linear_graphs(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        m = rng.choice([-2, -1, 1, 2])
        c = rng.randint(-3, 3)
        k = rng.randint(-3, 3)
        y = m * k + c
        if not (-6 <= y <= 6):
            continue
        svg = graph_svg(xrange=(-6, 6), yrange=(-6, 6),
                        polylines=[{"points": _line_points(m, c, (-6, 6)), "label": "L"}])
        part = mk_part(
            prompt=f"The straight line L is shown. Use the graph to find the value of y "
            f"when x = {k}.", marks=2, answer=str(y),
            working=f"On L, {_lin(m, c)}; when x = {k}, y = {m}×{k} + {c} = {y}",
            mark_scheme=[_M1("for reading from the line"), _A1("cao", str(y))])
        return make_item(req, seed, archetype="linear-graphs", topic="Linear graphs",
                         topic_slug="linear-graphs", strand="Algebra", spec_ref="A9",
                         grade_band="2-4", stem="The graph shows a straight line L.",
                         parts=[part], diagram=_dia(svg, "A straight line on a grid."))
    raise RuntimeError("linear-graphs generator failed.")


# --------------------------------------------------------------------------- #
# Gradient of a line  (A10)
# --------------------------------------------------------------------------- #
def build_gradient(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        ax, bx = rng.randint(-5, -1), rng.randint(1, 5)
        m = rng.choice([-2, -1, 1, 2, 3])
        c = rng.randint(-2, 2)
        ay, by = m * ax + c, m * bx + c
        if not (-6 <= ay <= 6 and -6 <= by <= 6):
            continue
        grad = sympy.Rational(by - ay, bx - ax)
        svg = graph_svg(xrange=(-6, 6), yrange=(-6, 6),
                        polylines=[{"points": _line_points(m, c, (-6, 6))}],
                        points=[(ax, ay, "A", True), (bx, by, "B", True)])
        part = mk_part(
            prompt="Work out the gradient of the line.", marks=2, answer=_num(grad),
            working=f"Gradient = (change in y)/(change in x) = ({by} − {ay})/({bx} − {ax}) "
            f"= {_num(grad)}",
            mark_scheme=[_M1("for change in y / change in x",
                            f"({by} − {ay})/({bx} − {ax})"), _A1("cao", _num(grad))])
        return make_item(req, seed, archetype="gradient", topic="Gradient of a line",
                         topic_slug="gradient", strand="Algebra", spec_ref="A10",
                         grade_band="4-5",
                         stem="The line passes through the points A and B shown.",
                         parts=[part], diagram=_dia(svg, "A line through points A and B."))
    raise RuntimeError("gradient generator failed.")


# --------------------------------------------------------------------------- #
# Equation of a line from two points  (A10)
# --------------------------------------------------------------------------- #
def build_equation_of_line(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        ax = rng.randint(-4, 0)
        bx = rng.randint(1, 4)
        m = rng.choice([-2, -1, 1, 2, 3])
        c = rng.randint(-3, 3)
        ay, by = m * ax + c, m * bx + c
        if not (-8 <= ay <= 8 and -8 <= by <= 8):
            continue
        part = mk_part(
            prompt=f"A straight line passes through ({ax}, {ay}) and ({bx}, {by}). "
            "Find the equation of the line.", marks=3, answer=_lin(m, c),
            working=f"Gradient = ({by} − {ay})/({bx} − {ax}) = {m}\n"
            f"y − {ay} = {m}(x − {ax}) → {_lin(m, c)}",
            mark_scheme=[_M1("for the gradient", str(m)),
                         _M1("for using a point"), _A1("cao", _lin(m, c))])
        return make_item(req, seed, archetype="equation-of-line",
                         topic="Equation of a line", topic_slug="equation-of-line",
                         strand="Algebra", spec_ref="A10", grade_band="5-6",
                         stem="", parts=[part])
    raise RuntimeError("equation-of-line generator failed.")


# --------------------------------------------------------------------------- #
# Parallel & perpendicular lines  (A10)
# --------------------------------------------------------------------------- #
def build_parallel_perpendicular(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        m = rng.choice([-2, -1, 1, 2])
        c = rng.randint(-4, 4)
        px, py = rng.randint(-4, 4), rng.randint(-6, 6)
        kind = rng.choice(["parallel", "perpendicular"])
        m2 = sympy.Rational(m) if kind == "parallel" else sympy.Rational(-1, m)
        c2 = sympy.Rational(py) - m2 * px
        if c2.q != 1:
            continue
        c2 = int(c2)
        m2 = int(m2) if m2.q == 1 else m2
        ans = _lin(m2, c2)
        # Two reasoning steps (gradient, then the point) across a single part, so
        # this is a 2-mark task — not the 3 it used to claim.
        part = mk_part(
            prompt=f"Find the equation of the line that is {kind} to  {_lin(m, c)}  and "
            f"passes through the point ({px}, {py}).", marks=2, answer=ans,
            working=(f"{'Parallel → same gradient' if kind == 'parallel' else 'Perpendicular → gradient = −1/m'} "
                     f"= {_num(m2)}\ny − {py} = {_num(m2)}(x − {px}) → {ans}"),
            mark_scheme=[_M1(f"for the correct gradient {_num(m2)} and using ({px}, {py})"),
                         _A1("cao", ans)])
        return make_item(req, seed, archetype="parallel-perpendicular",
                         topic="Parallel & perpendicular lines",
                         topic_slug="parallel-perpendicular", strand="Algebra",
                         spec_ref="A10", grade_band="6-7", stem="", parts=[part])
    raise RuntimeError("parallel-perpendicular generator failed.")


# --------------------------------------------------------------------------- #
# Quadratic graphs — read the roots  (A12)
# --------------------------------------------------------------------------- #
def build_quadratic_graphs(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        p = rng.randint(-3, 1)
        q = rng.randint(p + 1, 3)
        b, c = -(p + q), p * q
        vertex_y = c - sympy.Rational(b * b, 4)
        if vertex_y < -6:
            continue
        yr = (-6, 10)
        pts = _sample(lambda x: x * x + b * x + c, (p - 1.2, q + 1.2), yr, 0.2)
        if len(pts) < 4:
            continue
        svg = graph_svg(xrange=(-5, 5), yrange=yr, polylines=[{"points": pts, "label": "y = f(x)"}],
                        points=[(p, 0, "", True), (q, 0, "", True)])
        expr = sympy.expand((_x - p) * (_x - q))
        if expr != _x**2 + b * _x + c:
            continue
        eqn = f"x² {'+' if b >= 0 else '−'} {abs(b)}x {'+' if c >= 0 else '−'} {abs(c)} = 0"
        curve = (f"y = x² {'+' if b >= 0 else '−'} {abs(b)}x "
                 f"{'+' if c >= 0 else '−'} {abs(c)}")
        parts = [
            mk_part(
                label="a",
                prompt=f"Use the graph to write down the solutions of  {eqn}",
                marks=2, answer=f"x = {p} and x = {q}",
                working=f"The curve crosses the x-axis at x = {p} and x = {q}",
                mark_scheme=[_B1(f"x = {p}"), _B1(f"x = {q}")]),
            mk_part(
                label="b",
                prompt="Write down the coordinates of the point where the curve crosses "
                "the y-axis.",
                marks=1, answer=f"(0, {c})",
                working=f"At x = 0, y = {c}, so the curve crosses the y-axis at (0, {c})",
                mark_scheme=[_B1("cao", f"(0, {c})")]),
        ]
        return make_item(req, seed, archetype="quadratic-graphs",
                         topic="Quadratic graphs", topic_slug="quadratic-graphs",
                         strand="Algebra", spec_ref="A12", grade_band="4-6",
                         stem=f"The graph of  {curve}  is shown.", parts=parts,
                         diagram=_dia(svg, "A parabola crossing the x-axis twice."))
    raise RuntimeError("quadratic-graphs generator failed.")


# --------------------------------------------------------------------------- #
# Cubic & reciprocal graphs — identify + read  (A12)
# --------------------------------------------------------------------------- #
def build_cubic_reciprocal(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        kind = rng.choice(["reciprocal", "cubic"])
        if kind == "reciprocal":
            a = rng.choice([2, 3, 4, 6])
            k = rng.choice([1, 2, 3])
            if a % k != 0:
                continue
            val = sympy.Rational(a, k)
            left = _sample(lambda x: a / x, (-6, -0.4), (-6, 6), 0.15, skip_zero=True)
            right = _sample(lambda x: a / x, (0.4, 6), (-6, 6), 0.15, skip_zero=True)
            svg = graph_svg(xrange=(-6, 6), yrange=(-6, 6),
                            polylines=[{"points": left}, {"points": right}])
            part = mk_part(
                prompt=f"The graph of y = {a}/x is shown. (a) Write down the type of graph. "
                f"(b) Use the graph to find y when x = {k}.", marks=2,
                answer=f"reciprocal; y = {_num(val)}",
                working=f"y = {a}/x is a reciprocal graph; y = {a}/{k} = {_num(val)}",
                mark_scheme=[_B1("reciprocal"), _B1(f"y = {_num(val)}")])
        else:
            # y-step of 3 keeps the tall −9..9 range a balanced 6×6 of square
            # cells (each labelled square is 3 units tall, 1 unit wide).
            svg = graph_svg(xrange=(-3, 3), yrange=(-9, 9), ystep=3,
                            polylines=[{"points": _sample(lambda x: x**3, (-2.2, 2.2), (-9, 9), 0.12)}])
            k = rng.choice([-2, -1, 1, 2])
            part = mk_part(
                prompt=f"The graph of y = x³ is shown. (a) Write down the type of graph. "
                f"(b) Work out y when x = {k}.", marks=2, answer=f"cubic; y = {k**3}",
                working=f"y = x³ is a cubic graph; y = {k}³ = {k**3}",
                mark_scheme=[_B1("cubic"), _B1(f"y = {k**3}")])
        return make_item(req, seed, archetype="cubic-reciprocal",
                         topic="Cubic & reciprocal graphs", topic_slug="cubic-reciprocal",
                         strand="Algebra", spec_ref="A12", grade_band="5-6",
                         stem="The graph shows a curve.", parts=[part],
                         diagram=_dia(svg, "A cubic or reciprocal curve."))
    raise RuntimeError("cubic-reciprocal generator failed.")


# --------------------------------------------------------------------------- #
# Simultaneous equations — graphical  (A19)
# --------------------------------------------------------------------------- #
def build_simultaneous_graph(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        ix, iy = rng.randint(-3, 3), rng.randint(-3, 3)
        m1 = rng.choice([-2, -1, 1, 2])
        m2 = rng.choice([-2, -1, 1, 2])
        if m1 == m2:
            continue
        c1, c2 = iy - m1 * ix, iy - m2 * ix
        if not (-6 <= c1 <= 6 and -6 <= c2 <= 6):
            continue
        svg = graph_svg(xrange=(-6, 6), yrange=(-6, 6), polylines=[
            {"points": _line_points(m1, c1, (-6, 6)), "label": "L₁"},
            {"points": _line_points(m2, c2, (-6, 6)), "label": "L₂"}],
            points=[(ix, iy, "", True)])
        part = mk_part(
            prompt=f"The graphs of {_lin(m1, c1)} and {_lin(m2, c2)} are shown. Use the "
            "graphs to solve the simultaneous equations.", marks=2,
            answer=f"x = {ix}, y = {iy}",
            working=f"The lines cross at ({ix}, {iy}), so x = {ix}, y = {iy}",
            mark_scheme=[_M1("for reading the point of intersection"),
                         _A1("cao", f"x = {ix}, y = {iy}")])
        return make_item(req, seed, archetype="simultaneous-graph",
                         topic="Simultaneous equations (graphical)",
                         topic_slug="simultaneous-graph", strand="Algebra",
                         spec_ref="A19", grade_band="4-6",
                         stem="Two straight lines are shown.", parts=[part],
                         diagram=_dia(svg, "Two lines intersecting on a grid."))
    raise RuntimeError("simultaneous-graph generator failed.")


# --------------------------------------------------------------------------- #
# Distance–time graphs — speed of a segment  (R14)
# --------------------------------------------------------------------------- #
def build_distance_time(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        t1 = rng.randint(1, 3)
        speed = rng.randint(2, 8)
        d1 = speed * t1
        t2 = t1 + rng.randint(1, 2)      # stopped
        t3 = t2 + rng.randint(1, 3)      # return
        if d1 > 30:
            continue
        pts = [(0, 0), (t1, d1), (t2, d1), (t3, 0)]
        svg = graph_svg(xrange=(0, t3 + 1), yrange=(0, d1 + 4),
                        polylines=[{"points": pts}], xlabel="Time (s)", ylabel="Distance (m)",
                        xstep=1, ystep=max(1, (d1 + 4) // 6))
        part = mk_part(
            prompt="Work out the speed during the first part of the journey.", marks=2,
            answer=f"{speed} m/s",
            working=f"Speed = distance ÷ time = {d1} ÷ {t1} = {speed} m/s",
            mark_scheme=[_M1(f"for the gradient {d1} ÷ {t1} (= {speed})"),
                         _A1("cao", f"{speed} m/s")])
        return make_item(req, seed, archetype="distance-time",
                         topic="Distance–time graphs", topic_slug="distance-time",
                         strand="Ratio & proportion", spec_ref="R14", grade_band="4-5",
                         stem="The distance–time graph shows part of a journey.",
                         parts=[part], diagram=_dia(svg, "A distance-time graph."))
    raise RuntimeError("distance-time generator failed.")


# --------------------------------------------------------------------------- #
# Velocity–time graphs — distance = area under  (R15)
# --------------------------------------------------------------------------- #
def build_velocity_time(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        t1 = rng.randint(2, 4)          # accelerate 0..t1
        v = rng.randrange(4, 13, 2)     # even plateau: lands on a 2-unit gridline
        t2 = t1 + rng.randint(2, 5)     # constant v until t2
        # distance = area = ½·t1·v (triangle) + v·(t2−t1) (rectangle)
        area = sympy.Rational(t1 * v, 2) + v * (t2 - t1)
        if area.q != 1:
            continue
        area = int(area)
        pts = [(0, 0), (t1, v), (t2, v)]
        # Exam sketch style: arrowed axes, no grid, dashed guides dropping from
        # the two turning points to the axes where t1, t2 and v are labelled.
        svg = speed_time_svg(pts, xlabel="Time (s)", ylabel="Velocity (m/s)",
                             guides=[(t1, v, str(t1), str(v)),
                                     (t2, v, str(t2), "")])
        part = mk_part(
            prompt="Work out the total distance travelled (the area under the graph).",
            marks=3, answer=f"{area} m",
            working=(f"Triangle: ½ × {t1} × {v} = {sympy.Rational(t1 * v, 2)}\n"
                     f"Rectangle: {v} × {t2 - t1} = {v * (t2 - t1)}\n"
                     f"Total = {area} m"),
            mark_scheme=[_M1(f"for the triangle ½ × {t1} × {v} (= {sympy.Rational(t1 * v, 2)})"),
                         _M1(f"for the rectangle {v} × {t2 - t1} (= {v * (t2 - t1)})"),
                         _A1("cao", f"{area} m")])
        return make_item(req, seed, archetype="velocity-time",
                         topic="Velocity–time graphs", topic_slug="velocity-time",
                         strand="Ratio & proportion", spec_ref="R15", grade_band="7-9",
                         stem="The velocity–time graph shows the motion of an object.",
                         parts=[part], diagram=_dia(svg, "A velocity-time graph."))
    raise RuntimeError("velocity-time generator failed.")


# --------------------------------------------------------------------------- #
# Conversion graphs  (R11)
# --------------------------------------------------------------------------- #
def build_conversion_graphs(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    rate = rng.choice([2, 3, 4])   # dollars per pound (integer → clean readings)
    xmax = rng.choice([8, 10])
    k = rng.randint(2, xmax - 1)
    val = sympy.Integer(rate * k)
    ymax = rate * xmax
    svg = graph_svg(xrange=(0, xmax), yrange=(0, ymax),
                    polylines=[{"points": [(0, 0), (xmax, rate * xmax)]}],
                    xlabel="£ (pounds)", ylabel="$ (dollars)", xstep=max(1, xmax // 8),
                    ystep=max(1, ymax // 6))
    part = mk_part(
        prompt=f"Use the conversion graph to convert £{k} into dollars.", marks=2,
        answer=f"${_num(val)}",
        working=f"Reading up from £{k}: ${_num(val)}",
        mark_scheme=[_M1(f"for reading up from £{k} (= ${_num(val)})"),
                     _A1("cao", f"${_num(val)}")])
    return make_item(req, seed, archetype="conversion-graphs",
                     topic="Conversion graphs", topic_slug="conversion-graphs",
                     strand="Ratio & proportion", spec_ref="R11", grade_band="3-4",
                     stem="The conversion graph converts pounds (£) to dollars ($).",
                     parts=[part], diagram=_dia(svg, "A straight-line conversion graph."))


# --------------------------------------------------------------------------- #
# Inequalities on a graph — point-in-region test  (A22)
# --------------------------------------------------------------------------- #
def build_inequalities_graph(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        m = rng.choice([-1, 1, 2])
        c = rng.randint(-2, 2)
        px, py = rng.randint(-4, 4), rng.randint(-5, 5)
        boundary = m * px + c
        if py == boundary:
            continue
        inside = py < boundary            # region y < mx + c
        svg = graph_svg(xrange=(-6, 6), yrange=(-6, 6),
                        polylines=[{"points": _line_points(m, c, (-6, 6)),
                                    "label": _lin(m, c), "dashed": True}],
                        points=[(px, py, "P", False)])
        verdict = "Yes" if inside else "No"
        part = mk_part(
            prompt=f"The region R is defined by y < {_lin(m, c)[4:]}. Is the point "
            f"P ({px}, {py}) in the region R? You must justify your answer.", marks=2,
            answer=f"{verdict} — at x = {px}, the line gives y = {boundary}, and "
            f"{py} {'<' if inside else '≥'} {boundary}",
            working=f"On the line, y = {m}×{px} + {c} = {boundary}; P has y = {py}; "
            f"{py} {'<' if inside else '≥'} {boundary}",
            mark_scheme=[_M1(f"for testing the point (line value {boundary})"),
                         _B1(f"correct conclusion: {verdict}")])
        return make_item(req, seed, archetype="inequalities-graph",
                         topic="Inequalities on a graph", topic_slug="inequalities-graph",
                         strand="Algebra", spec_ref="A22", grade_band="5-7", ao="AO2",
                         stem="The dashed line is shown on the grid.", parts=[part],
                         diagram=_dia(svg, "A boundary line with a test point P."))
    raise RuntimeError("inequalities-graph generator failed.")


# --------------------------------------------------------------------------- #
# Equation of a tangent to a circle  (A16, grade 8-9)
# --------------------------------------------------------------------------- #
def _qstr(b, c) -> str:
    s = "x²"
    if b:
        s += (" + " if b > 0 else " - ") + ("x" if abs(b) == 1 else f"{abs(b)}x")
    if c:
        s += (" + " if c > 0 else " - ") + f"{abs(c)}"
    return s


def build_circle_tangent(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    for _ in range(_MAX_ATTEMPTS):
        a0, b0, r = rng.choice(triples)
        a = a0 * rng.choice([1, -1])
        b = b0 * rng.choice([1, -1])
        m = sympy.Rational(-a, b)          # tangent gradient (⟂ radius b/a)
        k = sympy.Rational(r * r, b)        # y-intercept = r²/b
        # Independent checks: tangent passes through P and is ⟂ to the radius.
        if m * a + k != b or a + b * m != 0:
            continue
        eq = _lin(m, k)
        return make_item(
            req, seed, archetype="circle-tangent",
            topic="Equation of a tangent", topic_slug="circle-tangent",
            strand="Algebra", spec_ref="A16", grade_band="8-9",
            stem=f"The point P({a}, {b}) lies on the circle  x² + y² = {r * r}.",
            parts=[mk_part(
                prompt="Find the equation of the tangent to the circle at P.",
                marks=3, answer=eq,
                working=(f"Gradient of radius OP = {_num(sympy.Rational(b, a))}\n"
                         f"Gradient of tangent = {_num(m)}\n"
                         f"y − ({b}) = {_num(m)}(x − ({a}))  →  {eq}"),
                mark_scheme=[
                    _M1(f"gradient of radius OP = {_num(sympy.Rational(b, a))}"),
                    _M1(f"perpendicular gradient {_num(m)} through P"),
                    _A1("cao", eq),
                ])],
            ao="AO2")
    raise RuntimeError("circle-tangent generator failed.")


# --------------------------------------------------------------------------- #
# Velocity–time trapezium: solve for T  (R15, grade 7-9)
# --------------------------------------------------------------------------- #
def build_vt_trapezium(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    T = sympy.Symbol("T")
    for _ in range(_MAX_ATTEMPTS):
        t1 = rng.randint(2, 6)              # accelerate 0..t1
        v = rng.randrange(4, 22, 2)         # cruise speed
        t2 = t1 + rng.randint(4, 12)        # cruise until t2
        t3 = t2 + rng.randint(3, 8)         # decelerate to rest at t3 (= answer)
        D = sympy.Rational(t1 * v, 2) + v * (t2 - t1) + sympy.Rational((t3 - t2) * v, 2)
        if D.q != 1:
            continue
        D = int(D)
        # Independent check: solving the area equation for T recovers t3.
        area_T = sympy.Rational(t1 * v, 2) + v * (t2 - t1) + (T - t2) * sympy.Rational(v, 2)
        sol = sympy.solve(sympy.Eq(area_T, D), T)
        if sol != [t3]:
            continue
        pts = [(0, 0), (t1, v), (t2, v), (t3, 0)]
        svg = speed_time_svg(pts, xlabel="Time (t seconds)", ylabel="Speed (m/s)",
                             guides=[(t1, v, str(t1), str(v)), (t2, v, str(t2), ""),
                                     (t3, 0, "T", "")])
        return make_item(
            req, seed, archetype="vt-trapezium",
            topic="Velocity–time (trapezium)", topic_slug="vt-trapezium",
            strand="Ratio & proportion", spec_ref="R15", grade_band="7-9",
            stem=(f"A train accelerates from rest to {v} m/s in {t1} seconds, travels "
                  f"at {v} m/s until t = {t2} seconds, then decelerates at a constant "
                  f"rate, coming to rest at time T seconds. The train travels {D} m in "
                  f"total."),
            parts=[mk_part(
                prompt="Work out the value of T.", marks=4, answer=f"T = {t3}",
                working=(f"Distance = ½·{t1}·{v} + {v}·{t2 - t1} + ½·(T − {t2})·{v} = {D}\n"
                         f"{int(sympy.Rational(t1 * v, 2))} + {v * (t2 - t1)} + "
                         f"{_num(sympy.Rational(v, 2))}(T − {t2}) = {D}\nT = {t3}"),
                mark_scheme=[
                    _M1("area of the trapezium in terms of T"),
                    _M1(f"sets total area = {D}"),
                    _M1("rearranges to solve for T"),
                    _A1("cao", f"T = {t3}"),
                ])],
            diagram=_dia(svg, f"A speed-time trapezium; the train stops at time T."),
            ao="AO2")
    raise RuntimeError("vt-trapezium generator failed.")


# --------------------------------------------------------------------------- #
# Quadratic graph → roots, turning point, line of symmetry  (A12, grade 4-6)
# --------------------------------------------------------------------------- #
def build_quadratic_features(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        width = rng.choice([2, 4])
        p = rng.randint(-3, 3 - width)
        q = p + width
        xv = sympy.Rational(p + q, 2)
        yv = -sympy.Rational(width, 2) ** 2
        # Independent check: vertex from calculus.
        expr = (_x - p) * (_x - q)
        if sympy.diff(sympy.expand(expr), _x).subs(_x, xv) != 0 or expr.subs(_x, xv) != yv:
            continue
        b, c = -(p + q), p * q
        xr = (p - 1, q + 1)
        yr = (int(yv) - 1, (q - p + 1) + 1)
        curve = _sample(lambda t: (t - p) * (t - q), xr, yr, 0.1)
        svg = graph_svg(xrange=xr, yrange=yr,
                        polylines=[{"points": curve}],
                        points=[(int(xv) if xv.q == 1 else float(xv), int(yv), "", True)],
                        xstep=1, ystep=1)
        vertex = f"({_num(xv)}, {_num(yv)})"
        return make_item(
            req, seed, archetype="quadratic-graph-features",
            topic="Quadratic graphs", topic_slug="quadratic-graphs",
            strand="Algebra", spec_ref="A12", grade_band="4-6",
            stem=f"The graph of  y = {_qstr(b, c)}  is shown.",
            parts=[
                mk_part(label="a",
                        prompt="Write down the coordinates of the points where the graph "
                        "crosses the x-axis.",
                        marks=1, answer=f"({p}, 0) and ({q}, 0)",
                        working=f"Roots at x = {p} and x = {q}",
                        mark_scheme=[_B1("both crossing points", f"({p}, 0), ({q}, 0)")]),
                mk_part(label="b",
                        prompt="Write down the coordinates of the turning point.",
                        marks=1, answer=vertex,
                        working=f"Vertex on the line of symmetry x = {_num(xv)}: {vertex}",
                        mark_scheme=[_B1("cao", vertex)]),
                mk_part(label="c",
                        prompt="Write down the equation of the line of symmetry.",
                        marks=1, answer=f"x = {_num(xv)}",
                        working=f"Midway between the roots: x = {_num(xv)}",
                        mark_scheme=[_B1("cao", f"x = {_num(xv)}")]),
            ],
            diagram=_dia(svg, f"A parabola crossing the x-axis at {p} and {q}."),
            ao="AO2")
    raise RuntimeError("quadratic-features generator failed.")


# --------------------------------------------------------------------------- #
# Transforming graphs y = f(x)  (A13, grade 7-9)
# --------------------------------------------------------------------------- #
def build_transforming_graphs(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    p = rng.randint(-4, 4)
    q = rng.choice([i for i in range(-4, 5) if i != 0])
    a = rng.randint(1, 4)
    # (display transform, image of the turning point P(p,q))
    trans = [
        (f"y = f(x) + {a}", (p, q + a)),
        (f"y = f(x + {a})", (p - a, q)),
        (f"y = f(x) − {a}", (p, q - a)),
        (f"y = f(x − {a})", (p + a, q)),
        ("y = −f(x)", (p, -q)),
        ("y = f(−x)", (-p, q)),
    ]
    chosen = rng.sample(trans, 2)
    svg = function_sketch_svg(marked_label="P", opens_up=(q < 0))
    parts = []
    for i, (label, (ix, iy)) in enumerate(chosen):
        # Independent re-derivation of each image is the sample above; assert form.
        parts.append(mk_part(
            label="ab"[i],
            prompt=f"The graph of {label} is a transformation of y = f(x). Write down the "
            "coordinates of the turning point of this graph.",
            marks=1, answer=f"({ix}, {iy})",
            working=f"Apply the transformation to P({p}, {q}): ({ix}, {iy})",
            mark_scheme=[_B1("cao", f"({ix}, {iy})")]))
    return make_item(
        req, seed, archetype="transforming-graphs", topic="Transforming graphs",
        topic_slug="transforming-graphs", strand="Algebra", spec_ref="A13",
        grade_band="7-9",
        stem=f"The diagram shows part of the curve y = f(x). The turning point of the "
        f"curve is P({p}, {q}).",
        parts=parts, diagram=_dia(svg, "A sketch of y = f(x) with turning point P."),
        ao="AO2")


# --------------------------------------------------------------------------- #
# Matching real-life (distance–time) graphs  (R14, grade 3-5)
# --------------------------------------------------------------------------- #
_JOURNEY_SHAPES = {
    "out_stop_back": ([(0, 0), (0.35, 0.85), (0.6, 0.85), (1, 0)],
                      "leaves home, travels away at a steady speed, stops for a while, "
                      "then returns home"),
    "steady": ([(0, 0), (1, 0.9)],
               "travels away from home at a constant speed for the whole journey"),
    "fast_then_slow": ([(0, 0), (0.3, 0.75), (1, 1)],
                       "travels away quickly at first, then continues away more slowly"),
    "wait_then_go": ([(0, 0), (0.4, 0), (1, 0.95)],
                     "waits at home for a while, then travels away at a steady speed"),
    "slow_then_fast": ([(0, 0), (0.6, 0.3), (1, 1)],
                       "travels away slowly at first, then speeds up"),
}


def build_matching_graphs(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    keys = list(_JOURNEY_SHAPES)
    correct = rng.choice(keys)
    others = rng.sample([k for k in keys if k != correct], 3)
    order = [correct] + others
    rng.shuffle(order)
    letters = "ABCD"
    panels = [{"points": _JOURNEY_SHAPES[k][0], "label": letters[i]}
              for i, k in enumerate(order)]
    ans = letters[order.index(correct)]
    # Independent check: exactly one panel is the correct shape.
    assert sum(1 for k in order if k == correct) == 1
    svg = graph_panels_svg(panels)
    desc = _JOURNEY_SHAPES[correct][1]
    return make_item(
        req, seed, archetype="matching-graphs", topic="Matching real-life graphs",
        topic_slug="matching-graphs", strand="Ratio & proportion", spec_ref="R14",
        grade_band="3-5",
        stem="Each graph shows distance from home against time for a journey.",
        parts=[mk_part(
            prompt=f"Rachel {desc}. Write down the letter of the graph that best shows "
            "her journey.", marks=1, answer=ans,
            working=f"The matching distance–time graph is {ans}.",
            mark_scheme=[_B1("cao", ans)])],
        diagram=_dia(svg, "Four distance-time graphs labelled A to D."), ao="AO2")


# --------------------------------------------------------------------------- #
# Velocity–time curved graph — average vs instantaneous acceleration  (R15)
# --------------------------------------------------------------------------- #
def build_vt_curved(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        T = rng.choice([10, 20, 40, 50, 60])
        V = rng.choice([20, 24, 30, 36, 40])
        avg = sympy.Rational(V, T)                       # chord gradient (0,0)→(T,V)
        if avg.q not in (1, 2, 4, 5):                    # keep a tidy decimal
            continue
        # A smooth concave-increasing curve from (0,0) to (T,V).
        curve = _sample(lambda t: V * (t / T) ** 0.7, (0, T), (0, V), step=T / 40)
        curve = [(0, 0)] + [p for p in curve if p[0] > 0] + [(T, V)]
        ystep = 10 if V % 10 == 0 else 5
        svg = graph_svg(xrange=(0, T), yrange=(0, V), polylines=[{"points": curve}],
                        xlabel="Time (s)", ylabel="Velocity (m/s)",
                        xstep=T / 5, ystep=ystep)
        lo, hi = round(0.22 * T), round(0.42 * T)        # tangent∥chord read-off band
        return make_item(
            req, seed, archetype="vt-curved", topic="Velocity–time (curved)",
            topic_slug="vt-curved", strand="Ratio & proportion", spec_ref="R15",
            grade_band="7-9",
            stem=f"The graph shows the velocity of a car during the first {T} seconds of "
            f"a journey. The car reaches a velocity of {V} m/s after {T} seconds.",
            parts=[
                mk_part(label="a",
                        prompt="Work out the average acceleration during the "
                        f"{T} seconds. Give the units of your answer.",
                        marks=2, answer=f"{_num(avg)} m/s²",
                        working=f"Average acceleration = change in velocity ÷ time "
                        f"= {V} ÷ {T} = {_num(avg)} m/s²",
                        mark_scheme=[_M1(f"for {V} ÷ {T}"),
                                     _A1("cao with units m/s²", f"{_num(avg)} m/s²")]),
                mk_part(label="b",
                        prompt="Estimate the time during the journey when the "
                        "instantaneous acceleration is equal to the average acceleration. "
                        "You must show your working on the graph.",
                        marks=2, answer=f"{lo} – {hi} s", answer_tolerance=float(hi - lo),
                        working="Draw a tangent to the curve parallel to the chord from "
                        "(0, 0); read off the time where they are parallel.",
                        mark_scheme=[_M1("draws a tangent parallel to the chord"),
                                     _A1(f"a time in the range {lo} to {hi} s")]),
            ],
            diagram=_dia(svg, f"A curved velocity-time graph reaching {V} m/s at {T} s."),
            ao="AO2")
    raise RuntimeError("vt-curved generator failed.")
