"""Deterministic SVG diagram primitives.

Diagrams are drawn from the question's parameters — never from an image model —
so they are reproducible, accessible, and cheap. Geometry here is fixed and
deliberately *not to scale* (matching Edexcel's "Diagrams are NOT accurately
drawn" convention); only the labels change.
"""

from __future__ import annotations

import math

# Minimum label font size, in viewBox user units. Diagrams are shown in a
# ~60 mm-tall box, where the busiest viewBox (300 units tall) renders at
# ~0.2 mm/unit — so 8 pt (2.82 mm) needs ~14 units. 15 keeps every label at
# 8 pt or larger with a little headroom. All label helpers clamp to this, so no
# call site can drop text below the legibility floor.
_MIN_LABEL_FONT = 15

# Fixed right-angled triangle. Right angle at bottom-left.
#   top-left (40,70) --- hypotenuse ---> bottom-right (260,210)
#        |                                   /
#     vertical leg                      base leg
#        |                                 /
#   bottom-left (40,210) -- base -- bottom-right (260,210)
_BL = (40, 210)  # bottom-left  (right angle)
_BR = (260, 210)  # bottom-right
_TL = (40, 70)  # top-left


def _label(text: str, x: int, y: int, variable: str, anchor: str = "middle") -> str:
    italic = ' font-style="italic"' if text == variable else ""
    size = max(16, _MIN_LABEL_FONT)
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
        f'fill="currentColor"{italic}>{text}</text>'
    )


def right_triangle_svg(
    *,
    base_label: str,
    vert_label: str,
    hyp_label: str,
    variable: str = "x",
) -> str:
    """Render a right-angled triangle with the three sides labelled.

    `base_label`  -> bottom (horizontal) side
    `vert_label`  -> left (vertical) side
    `hyp_label`   -> hypotenuse (the sloping side)
    Any label equal to `variable` is rendered in italic, like a real paper.
    """
    return (
        '<svg viewBox="0 0 300 260" xmlns="http://www.w3.org/2000/svg" '
        'role="img" font-family="-apple-system, system-ui, sans-serif">'
        f'<polygon points="{_BL[0]},{_BL[1]} {_BR[0]},{_BR[1]} {_TL[0]},{_TL[1]}" '
        'fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linejoin="round"/>'
        # Right-angle marker at bottom-left. This is the only cue that fixes the
        # hypotenuse: it is the side opposite the right angle (the slope), so the
        # square must be unmistakable — a clear filled corner box, not a hairline.
        '<polygon points="40,188 62,188 62,210 40,210" fill="currentColor" '
        'fill-opacity="0.18" stroke="currentColor" stroke-width="2" '
        'stroke-linejoin="round"/>'
        + _label(base_label, 150, 232, variable)
        + _label(vert_label, 22, 145, variable)
        + _label(hyp_label, 165, 130, variable)
        + "</svg>"
    )


# --------------------------------------------------------------------------- #
# Shared SVG helpers for the Phase F primitives
# --------------------------------------------------------------------------- #
def _svg(body: str, w: int = 300, h: int = 260) -> str:
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" font-family="-apple-system, system-ui, sans-serif">{body}</svg>'
    )


def _text(text: str, x: float, y: float, *, size: int = 15,
          anchor: str = "middle", italic: bool = False, halo: bool = False) -> str:
    it = ' font-style="italic"' if italic else ""
    size = max(size, _MIN_LABEL_FONT)  # never render below the 8 pt floor
    # A halo — a paper-coloured outline drawn *behind* the glyphs — lets a label
    # sit over a grid without gridlines showing through it. The paper sheet is
    # always white, so the halo is white; the glyph fill stays currentColor.
    h = (' paint-order="stroke" stroke="#ffffff" stroke-width="4" '
         'stroke-linejoin="round"' if halo else "")
    return (
        f'<text x="{round(x, 1)}" y="{round(y, 1)}" text-anchor="{anchor}" '
        f'font-size="{size}" fill="currentColor"{h}{it}>{text}</text>'
    )


def _line(x1: float, y1: float, x2: float, y2: float, *,
          dashed: bool = False, w: int = 2) -> str:
    d = ' stroke-dasharray="4 4"' if dashed else ""
    return (
        f'<line x1="{round(x1, 1)}" y1="{round(y1, 1)}" x2="{round(x2, 1)}" '
        f'y2="{round(y2, 1)}" stroke="currentColor" stroke-width="{w}"{d}/>'
    )


# --------------------------------------------------------------------------- #
# Shared exam house-style helpers (arrowheads, graph-paper grid, axis titles).
# Every graph/chart primitive reuses these so the whole paper reads as one set.
# --------------------------------------------------------------------------- #
def _arrow(x: float, y: float, direction: str, size: float = 5) -> str:
    """A small filled-triangle arrowhead with its tip at (x, y)."""
    s = size
    tips = {
        "up": (-s, 1.8 * s, 2 * s, 0),
        "down": (-s, -1.8 * s, 2 * s, 0),
        "left": (1.8 * s, -s, 0, 2 * s),
        "right": (-1.8 * s, -s, 0, 2 * s),
    }
    a, b, c, d = (round(v, 1) for v in tips[direction])
    return f'<path d="M {round(x,1)} {round(y,1)} l {a} {b} l {c} {d} Z" fill="currentColor"/>'


def _grid_lines(x0: float, y0: float, x1: float, y1: float,
                xs, ys, w: float, op: float) -> str:
    body = ""
    for x in xs:
        body += (f'<line x1="{round(x,1)}" y1="{round(y0,1)}" x2="{round(x,1)}" '
                 f'y2="{round(y1,1)}" stroke="currentColor" stroke-width="{w}" '
                 f'opacity="{op}"/>')
    for y in ys:
        body += (f'<line x1="{round(x0,1)}" y1="{round(y,1)}" x2="{round(x1,1)}" '
                 f'y2="{round(y,1)}" stroke="currentColor" stroke-width="{w}" '
                 f'opacity="{op}"/>')
    return body


def _graph_paper(x0: float, y0: float, x1: float, y1: float, *,
                 minor_x=(), minor_y=(), major_x=(), major_y=()) -> str:
    """Two-tier exam graph-paper grid inside the screen rectangle (x0,y0)-(x1,y1)
    (y0 top, y1 bottom). Positions are screen coords; minor lines faint, major
    lines heavier — the MathsGenie plotting-grid look."""
    return (_grid_lines(x0, y0, x1, y1, minor_x, minor_y, 0.4, 0.22)
            + _grid_lines(x0, y0, x1, y1, major_x, major_y, 0.9, 0.5))


def _x_title(text: str, cx: float, y: float) -> str:
    """x-axis title, centred below the axis."""
    return _text(text, cx, y, size=12)


def _y_title(text: str, x: float, y_center: float, *, anchor: str = "start") -> str:
    """y-axis title to the left of the axis, stacked over its words (horizontal,
    not rotated) and vertically centred — the exam-paper convention."""
    words = text.split()
    top = y_center - (len(words) - 1) * 9
    return "".join(_text(w, x, top + i * 18, anchor=anchor, size=12)
                   for i, w in enumerate(words))


def _poly(points: list[tuple[float, float]], *, dashed: bool = False) -> str:
    pts = " ".join(f"{round(x, 1)},{round(y, 1)}" for x, y in points)
    d = ' stroke-dasharray="4 4"' if dashed else ""
    return (
        f'<polygon points="{pts}" fill="none" stroke="currentColor" '
        f'stroke-width="2" stroke-linejoin="round"{d}/>'
    )


def _mid(p: tuple[float, float], q: tuple[float, float]) -> tuple[float, float]:
    return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)


# --------------------------------------------------------------------------- #
# Regular polygon (angles in polygons)
# --------------------------------------------------------------------------- #
def regular_polygon_svg(n: int) -> str:
    """A regular n-sided polygon, drawn schematically (not to scale)."""
    cx, cy, r = 130, 130, 95
    pts = []
    for k in range(n):
        ang = -math.pi / 2 + 2 * math.pi * k / n
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return _svg(_poly(pts), 260, 260)


# --------------------------------------------------------------------------- #
# Circle sector (sector area / arc length)
# --------------------------------------------------------------------------- #
def circle_sector_svg(*, radius_label: str, theta: float) -> str:
    """A sector OAB whose wedge *and* label show the true central angle `theta`
    (in degrees), including reflex angles (> 180°).

    Everything the reader uses to judge the angle is derived from the one
    `theta`: the enclosed region, the arc A→B, the little angle marker at O, and
    the printed number. The large-arc flag comes straight from `theta`
    (> 180° ⇒ the major arc), and `theta` is never reduced modulo 360 or folded
    to its minor twin — so the picture can never disagree with the value.
    """
    cx, cy, R = 150, 150, 90
    label = f"{theta:g}°"
    # Radii placed symmetrically about "up" (screen y grows downward). The sector
    # always contains the up bisector, so a reflex angle opens the wedge past a
    # semicircle instead of collapsing onto its minor twin.
    up = math.radians(-90)
    a_ang = up - math.radians(theta) / 2
    b_ang = up + math.radians(theta) / 2

    def on_circle(ang: float, rad: float = R) -> tuple[float, float]:
        return (cx + rad * math.cos(ang), cy + rad * math.sin(ang))

    A = on_circle(a_ang)
    B = on_circle(b_ang)
    large = 1 if theta > 180 else 0   # large-arc flag, taken straight from theta
    sweep = 1                         # A→B by increasing angle, i.e. over the top

    # The wedge as one closed path (O → A → arc → B → O): its outline *is* the
    # enclosed region, so minor vs reflex is unambiguous. A faint fill helps.
    wedge = (f'<path d="M {cx} {cy} L {round(A[0], 1)} {round(A[1], 1)} '
             f'A {R} {R} 0 {large} {sweep} {round(B[0], 1)} {round(B[1], 1)} Z" '
             f'fill="currentColor" fill-opacity="0.06" stroke="currentColor" '
             f'stroke-width="2" stroke-linejoin="round"/>')
    # Angle marker at O — same flags, so it wraps the same (possibly reflex) angle.
    m1, m2 = on_circle(a_ang, 32), on_circle(b_ang, 32)
    marker = (f'<path d="M {round(m1[0], 1)} {round(m1[1], 1)} '
              f'A 32 32 0 {large} {sweep} {round(m2[0], 1)} {round(m2[1], 1)}" '
              f'fill="none" stroke="currentColor" stroke-width="1.5"/>')
    a_out, b_out = on_circle(a_ang, R + 14), on_circle(b_ang, R + 14)
    # Radius label beside the OA radius, offset to its *outer* side (the normal
    # pointing away from the wedge centre) so it sits next to the line, never on
    # it — and set anchor="end" so it reads leftwards, away from the wedge.
    # Radius label beside the OA radius. Its offset points to OA's OUTER side —
    # away from the wedge interior, which always lies toward the up bisector — so
    # the label never lands on the shaded shape (e.g. for a horizontal OA at
    # θ=180 that is straight down, out of the semicircle).
    ux, uy = A[0] - cx, A[1] - cy
    ul = math.hypot(ux, uy) or 1
    ux, uy = ux / ul, uy / ul                 # unit O→A
    nx, ny = -uy, ux                          # a perpendicular to OA
    if nx * math.cos(up) + ny * math.sin(up) > 0:
        nx, ny = -nx, -ny                     # ...flipped to the outer side
    anchor = "start" if nx >= 0 else "end"
    if theta <= 180:
        # Sector lies wholly on OA's interior side: hug the radius on its outer
        # side, offset far enough that the whole label clears the line.
        p = 17 * abs(nx) + 9 * abs(ny) + 7
        r_pos = ((cx + A[0]) / 2 + nx * p, (cy + A[1]) / 2 + ny * p)
    else:
        # Reflex: the notch beside OA is too tight for a horizontal label, so sit
        # just outside the arc along OA, in open space clear of the disk.
        base = on_circle(a_ang, R + 20)
        r_pos = (base[0] + nx * 18, base[1] + ny * 18)
    # Angle label on the bisector, pushed out far enough that even a narrow wedge
    # is wide enough (half-width = ang_r·sin(θ/2)) to hold the number clear of
    # both radii; capped so it stays inside the arc for wide/reflex angles.
    half = math.sin(math.radians(theta) / 2) or 1e-6
    lbl = on_circle(up, min(72.0, max(46.0, 18.0 / half)))
    body = (
        wedge + marker
        + _text("O", cx, cy + 16)
        + _text("A", a_out[0], a_out[1])
        + _text("B", b_out[0], b_out[1])
        + _text(radius_label, r_pos[0], r_pos[1], size=14, anchor=anchor)
        + _text(label, lbl[0], lbl[1], size=13)
    )
    svg = _svg(body, 300, 300)
    # The path and the label were built from the same `theta`; prove the rendered
    # SVG carries it, so the figure and the number can never drift apart.
    assert label in svg, f"sector SVG is missing its angle label {label!r}"
    return svg


# --------------------------------------------------------------------------- #
# Cylinder (volume)
# --------------------------------------------------------------------------- #
def cylinder_svg(*, radius_label: str, height_label: str) -> str:
    cx, top, bot, rx, ry = 150, 70, 200, 70, 20
    body = (
        f'<ellipse cx="{cx}" cy="{top}" rx="{rx}" ry="{ry}" fill="none" '
        f'stroke="currentColor" stroke-width="2"/>'
        + _line(cx - rx, top, cx - rx, bot)
        + _line(cx + rx, top, cx + rx, bot)
        # front bottom arc (solid), back bottom arc (dashed)
        + f'<path d="M {cx - rx} {bot} A {rx} {ry} 0 0 0 {cx + rx} {bot}" '
        f'fill="none" stroke="currentColor" stroke-width="2"/>'
        + f'<path d="M {cx - rx} {bot} A {rx} {ry} 0 0 1 {cx + rx} {bot}" '
        f'fill="none" stroke="currentColor" stroke-width="1.5" '
        f'stroke-dasharray="4 4"/>'
        # radius arrow across the top ellipse
        + _line(cx, top, cx + rx, top)
        + _text(radius_label, cx + rx + 6, top - 4, anchor="start", size=14)
        # height arrow on the right
        + _line(cx + rx + 18, top, cx + rx + 18, bot)
        + _text(height_label, cx + rx + 24, (top + bot) / 2, anchor="start", size=14)
    )
    return _svg(body, 300, 240)


# --------------------------------------------------------------------------- #
# Cuboid (volume)
# --------------------------------------------------------------------------- #
def cuboid_svg(*, length_label: str, width_label: str, height_label: str) -> str:
    # front face
    fTL, fTR, fBL, fBR = (60, 90), (200, 90), (60, 210), (200, 210)
    dx, dy = 45, -32  # depth offset
    bTL = (fTL[0] + dx, fTL[1] + dy)
    bTR = (fTR[0] + dx, fTR[1] + dy)
    bBR = (fBR[0] + dx, fBR[1] + dy)
    body = (
        _poly([fTL, fTR, fBR, fBL])
        + _line(*fTL, *bTL) + _line(*fTR, *bTR) + _line(*fBR, *bBR)
        + _line(*bTL, *bTR) + _line(*bTR, *bBR)
        + _line(bTL[0], bTL[1], bTL[0], bBR[1], dashed=True)  # hidden back-left
        + _line(bTL[0], bBR[1], bBR[0], bBR[1], dashed=True)  # hidden back-bottom
        + _text(length_label, 130, 228, size=14)         # front bottom
        + _text(height_label, 50, 152, anchor="end", size=14)  # front left
        + _text(width_label, 235, 68, anchor="start", size=14)  # top depth
    )
    return _svg(body, 300, 250)


# --------------------------------------------------------------------------- #
# Triangular prism (volume)
# --------------------------------------------------------------------------- #
def triangular_prism_svg(*, base_label: str, height_label: str,
                         length_label: str) -> str:
    fA, fB, fC = (90, 60), (50, 185), (150, 185)  # front triangle (apex, BL, BR)
    dx, dy = 70, -28
    bA = (fA[0] + dx, fA[1] + dy)
    bB = (fB[0] + dx, fB[1] + dy)
    bC = (fC[0] + dx, fC[1] + dy)
    body = (
        _poly([fA, fB, fC])
        + _line(*fA, *bA) + _line(*fC, *bC)
        + _line(*bA, *bB) + _line(*bA, *bC)
        + _line(*bB, *bC, dashed=True)   # hidden back base
        + _line(*fB, *bB, dashed=True)   # hidden back-left
        + _text(base_label, 100, 203, size=14)              # front base
        + _text(height_label, 66, 120, anchor="end", size=14)  # triangle height side
        + _text(length_label, 170, 150, anchor="start", size=14)  # length edge
    )
    return _svg(body, 300, 230)


# --------------------------------------------------------------------------- #
# General / right-angled triangle with labelled sides & angles (trig)
# --------------------------------------------------------------------------- #
def triangle_svg(
    *,
    side_ab: str = "",
    side_bc: str = "",
    side_ca: str = "",
    angle_a: str = "",
    angle_b: str = "",
    angle_c: str = "",
    right_angle_at: str | None = None,
    variable: str = "x",
) -> str:
    """Triangle ABC. If right_angle_at='B', draw a right angle at B.

    side_ab is between A&B, side_bc between B&C, side_ca between C&A. Empty
    labels are skipped. Any label equal to `variable` renders italic.
    """
    if right_angle_at == "B":
        A, B, C = (60, 55), (60, 205), (250, 205)
    else:
        A, B, C = (150, 50), (55, 205), (255, 205)
    body = _poly([A, B, C])
    body += _text("A", A[0], A[1] - 8) + _text("B", B[0] - 10, B[1] + 6)
    body += _text("C", C[0] + 10, C[1] + 6)
    if right_angle_at == "B":
        body += (
            f'<polyline points="{B[0]},{B[1] - 18} {B[0] + 18},{B[1] - 18} '
            f'{B[0] + 18},{B[1]}" fill="none" stroke="currentColor" '
            f'stroke-width="2"/>'
        )

    def side(lbl, p, q, off):
        if not lbl:
            return ""
        mx, my = _mid(p, q)
        return _text(lbl, mx + off[0], my + off[1], size=14,
                     italic=(lbl == variable))
    body += side(side_ab, A, B, (-14, 0))
    body += side(side_bc, B, C, (0, 20))
    body += side(side_ca, C, A, (16, 0))
    if angle_a:
        body += _text(angle_a, A[0], A[1] + 24, size=13)
    if angle_b:
        body += _text(angle_b, B[0] + 26, B[1] - 8, size=13)
    if angle_c:
        body += _text(angle_c, C[0] - 26, C[1] - 8, size=13)
    return _svg(body, 310, 250)


# --------------------------------------------------------------------------- #
# Two similar triangles (similar shapes)
# --------------------------------------------------------------------------- #
def similar_triangles_svg(
    *, left_base: str = "", left_side: str = "", right_base: str = "",
    right_side: str = "", variable: str = "x",
) -> str:
    """Two similar (same-shape, different-size) triangles side by side."""
    lA, lB, lC = (55, 60), (30, 150), (110, 150)
    rA, rB, rC = (200, 40), (165, 190), (295, 190)
    body = _poly([lA, lB, lC]) + _poly([rA, rB, rC])

    def side(lbl, p, q, off):
        if not lbl:
            return ""
        mx, my = _mid(p, q)
        return _text(lbl, mx + off[0], my + off[1], size=13,
                     italic=(lbl == variable))
    body += side(left_base, lB, lC, (0, 18))
    body += side(left_side, lA, lB, (-14, 0))
    body += side(right_base, rB, rC, (0, 18))
    body += side(right_side, rA, rB, (-14, 0))
    return _svg(body, 320, 220)
