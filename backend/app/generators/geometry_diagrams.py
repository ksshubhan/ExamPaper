"""Extra geometry SVG primitives for Phase K.

Same house style as diagrams.py (fixed viewBox, stroke=currentColor, schematic).
Reuses the shared low-level helpers; grids/triangles/solids/sectors are drawn by
the existing primitives, so this module only adds what was missing.
"""

from __future__ import annotations

import math

from .diagrams import _line, _mid, _poly, _svg, _text


def _circle(cx, cy, r, dashed=False, w=2):
    d = ' stroke-dasharray="4 4"' if dashed else ""
    return (f'<circle cx="{round(cx,1)}" cy="{round(cy,1)}" r="{round(r,1)}" '
            f'fill="none" stroke="currentColor" stroke-width="{w}"{d}/>')


def _ellipse(cx, cy, rx, ry, dashed=False):
    d = ' stroke-dasharray="4 4"' if dashed else ""
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" '
            f'stroke="currentColor" stroke-width="2"{d}/>')


def _dot(cx, cy, r=2.5):
    return f'<circle cx="{round(cx,1)}" cy="{round(cy,1)}" r="{r}" fill="currentColor"/>'


# --------------------------------------------------------------------------- #
# Plain circle with a radius or diameter label
# --------------------------------------------------------------------------- #
def circle_svg(*, radius_label: str = "", diameter_label: str = "") -> str:
    cx, cy, r = 130, 120, 92
    body = _circle(cx, cy, r) + _dot(cx, cy)
    if diameter_label:
        body += _line(cx - r, cy, cx + r, cy)
        body += _text(diameter_label, cx, cy - 8)
    else:
        body += _line(cx, cy, cx + r, cy)
        body += _text(radius_label, cx + r / 2, cy - 8)
    return _svg(body, 260, 240)


# --------------------------------------------------------------------------- #
# Compound rectilinear (L-shaped) region, drawn to scale
# --------------------------------------------------------------------------- #
def compound_shape_svg(*, W: float, H: float, nw: float, nh: float,
                       unit: str = "cm") -> str:
    # L-shape = W×H rectangle with an nw×nh notch removed from the bottom-right.
    scale = 150 / max(W, H)
    ox, oy = 40, 30

    def X(x): return ox + x * scale
    def Y(y): return oy + y * scale
    pts = [(0, 0), (W, 0), (W, H - nh), (W - nw, H - nh), (W - nw, H), (0, H)]
    body = _poly([(X(x), Y(y)) for x, y in pts])
    lab = lambda t: f"{t} {unit}"
    body += _text(lab(W), X(W / 2), Y(0) - 6)
    body += _text(lab(H - nh), X(W) + 6, Y((H - nh) / 2), anchor="start")
    body += _text(lab(nw), X(W - nw / 2), Y(H - nh) - 6, size=13)
    body += _text(lab(nh), X(W - nw) - 6, Y(H - nh / 2), anchor="end", size=13)
    body += _text(lab(W - nw), X((W - nw) / 2), Y(H) + 14)
    body += _text(lab(H), X(0) - 6, Y(H / 2), anchor="end")
    return _svg(body, int(X(W)) + 50, int(Y(H)) + 40)


# --------------------------------------------------------------------------- #
# Angle facts — straight line or triangle
# --------------------------------------------------------------------------- #
def angle_facts_svg(*, kind: str, known, unknown: str = "x") -> str:
    if kind == "triangle":
        A, B, C = (150, 45), (55, 200), (250, 200)
        body = _poly([A, B, C])
        body += _text(str(known[0]) + "°", B[0] + 26, B[1] - 8, size=13)
        body += _text(str(known[1]) + "°", C[0] - 26, C[1] - 8, size=13)
        body += _text(unknown + "°", A[0], A[1] + 26, size=13, italic=True)
        return _svg(body, 300, 240)
    # straight line: base line with a ray, two adjacent angles
    O = (150, 170)
    body = _line(30, O[1], 270, O[1])
    ray = (O[0] + 95 * math.cos(math.radians(50)), O[1] - 95 * math.sin(math.radians(50)))
    body += _line(*O, *ray)
    body += _dot(*O)
    body += _text(str(known) + "°", O[0] - 40, O[1] - 12, size=13)
    body += _text(unknown + "°", O[0] + 34, O[1] - 12, size=13, italic=True)
    return _svg(body, 300, 210)


# --------------------------------------------------------------------------- #
# Angles in parallel lines (two parallels + a transversal)
# --------------------------------------------------------------------------- #
def parallel_lines_svg(*, known, unknown: str = "x") -> str:
    body = _line(30, 70, 260, 70) + _line(30, 160, 260, 160)
    # arrow marks to show they're parallel
    body += _text("→", 250, 64, size=12) + _text("→", 250, 154, size=12)
    # transversal
    body += _line(70, 40, 220, 190)
    # known angle at the top intersection, x at the bottom
    body += _text(str(known) + "°", 120, 60, size=13)
    body += _text(unknown + "°", 158, 150, size=13, italic=True)
    return _svg(body, 290, 220)


# --------------------------------------------------------------------------- #
# Sphere
# --------------------------------------------------------------------------- #
def sphere_svg(*, radius_label: str) -> str:
    cx, cy, r = 120, 115, 88
    body = _circle(cx, cy, r) + _ellipse(cx, cy, r, r * 0.32, dashed=True)
    body += _line(cx, cy, cx + r, cy) + _dot(cx, cy)
    body += _text(radius_label, cx + r / 2, cy - 8)
    return _svg(body, 250, 230)


# --------------------------------------------------------------------------- #
# Cone
# --------------------------------------------------------------------------- #
def cone_svg(*, radius_label: str = "", height_label: str = "",
             slant_label: str = "") -> str:
    apex = (130, 30)
    bl, br = (60, 190), (200, 190)
    cx, cy = 130, 190
    body = _line(*apex, *bl) + _line(*apex, *br)
    body += _ellipse(cx, cy, 70, 18)
    if height_label:
        body += _line(apex[0], apex[1], cx, cy, dashed=True)
        body += _text(height_label, cx + 6, (apex[1] + cy) / 2, anchor="start", size=13)
    if radius_label:
        body += _line(cx, cy, br[0], cy)
        body += _text(radius_label, (cx + br[0]) / 2, cy + 15, size=13)
    if slant_label:
        body += _text(slant_label, _mid(apex, br)[0] + 8, _mid(apex, br)[1],
                      anchor="start", size=13)
    return _svg(body, 260, 230)


# --------------------------------------------------------------------------- #
# Bearing (North arrow + line to target at a three-figure bearing)
# --------------------------------------------------------------------------- #
def bearing_svg(*, bearing: int, from_label: str = "A", to_label: str = "B") -> str:
    A = (110, 150)
    body = _line(A[0], A[1], A[0], 40)          # north line
    body += _text("N", A[0], 32)
    body += f'<polyline points="{A[0]-4},48 {A[0]},40 {A[0]+4},48" fill="none" stroke="currentColor" stroke-width="2"/>'
    ang = math.radians(bearing)
    B = (A[0] + 95 * math.sin(ang), A[1] - 95 * math.cos(ang))
    body += _line(*A, *B) + _dot(*A) + _dot(*B)
    body += _text(from_label, A[0] - 10, A[1] + 6)
    body += _text(to_label, B[0] + 8, B[1], anchor="start")
    body += _text(f"{bearing:03d}°", A[0] + 14, A[1] - 30, anchor="start", size=12)
    return _svg(body, 240, 200)


# --------------------------------------------------------------------------- #
# Circle with labelled points (circle theorems)
# --------------------------------------------------------------------------- #
def circle_points_svg(*, points: dict, segments: list, angle_labels: list,
                      show_centre: bool = True) -> str:
    """points: {name: angle_deg}. segments: list of (name1, name2) using point
    names or 'O' for the centre. angle_labels: list of (name, text) placed just
    inside the circle near that point (or centre)."""
    cx, cy, r = 140, 130, 100
    coord = {"O": (cx, cy)}
    for name, deg in points.items():
        a = math.radians(deg)
        coord[name] = (cx + r * math.cos(a), cy - r * math.sin(a))
    body = _circle(cx, cy, r)
    if show_centre:
        body += _dot(cx, cy) + _text("O", cx - 10, cy + 4)
    for p, q in segments:
        body += _line(*coord[p], *coord[q])
    for name, txt in points.items():
        px, py = coord[name]
        ox = 12 if px >= cx else -12
        body += _text(name, px + ox, py + (12 if py >= cy else -6))
    for name, txt in angle_labels:
        vx, vy = coord[name]
        # nudge the label toward the centre
        dx, dy = cx - vx, cy - vy
        L = math.hypot(dx, dy) or 1
        lx, ly = vx + dx / L * 26, vy + dy / L * 26
        body += _text(txt, lx, ly + 4, size=12, italic=(txt == "x°" or txt == "x"))
    return _svg(body, 290, 270)


# --------------------------------------------------------------------------- #
# Loci — a plain field/region with labelled points (student draws the locus)
# --------------------------------------------------------------------------- #
def loci_field_svg(*, points: list, extra: str = "") -> str:
    """points: list of (name, x, y) in a 0..10 by 0..7 field. `extra` is optional
    raw SVG (e.g. a line PQ for an angle bisector)."""
    ox, oy, sc = 24, 20, 22
    W, H = 10, 7

    def X(x): return ox + x * sc
    def Y(y): return oy + (H - y) * sc
    body = f'<rect x="{ox}" y="{oy}" width="{W * sc}" height="{H * sc}" fill="none" stroke="currentColor" stroke-width="1.5"/>'
    body += extra
    for name, x, y in points:
        body += _dot(X(x), Y(y), 3)
        body += _text(name, X(x) + 9, Y(y) - 6, size=13)
    return _svg(body, int(X(W)) + 30, int(Y(0)) + 24)
