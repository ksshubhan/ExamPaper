"""Coordinate-grid plotting for graph questions.

One flexible primitive draws a gridded Cartesian plane (axes through the origin,
numbered ticks) and plots lines, curves, points and piecewise graphs — all to
scale from the question's own numbers, reusing the diagrams.py house style.
"""

from __future__ import annotations

from .diagrams import _svg, _text, _line, _arrow, _graph_paper

# Every labelled square is drawn this many user units on a side — the SAME value
# for both axes, which is what makes the grid squares true squares. The plot's
# pixel size is then derived from how many squares each axis holds, so the whole
# figure grows/shrinks with its range instead of being crushed into a fixed box.
# (Minor squares are a fifth of this.) The SVG renders with the default
# preserveAspectRatio, so the viewBox's square cells stay square on screen.
_CELL = 24
# Asymmetric margins: extra room along the bottom and left edges, where the axis
# number labels now sit (in the margin, outside the grid) so they never cross a
# gridline or the axes. Top/right stay tight.
_M_LEFT, _M_RIGHT, _M_TOP, _M_BOTTOM = 36, 16, 16, 34


def _fmt(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


def graph_svg(*, xrange: tuple[float, float], yrange: tuple[float, float],
              polylines: list[dict] | None = None,
              points: list[tuple] | None = None,
              xlabel: str = "x", ylabel: str = "y",
              xstep: float = 1, ystep: float = 1) -> str:
    """A Cartesian grid with plotted lines/curves/points.

    Grid squares are always drawn square: one labelled square is `_CELL` pixels
    on both axes, so a labelled square spans `xstep` in x and `ystep` in y but is
    the same physical size either way (exactly as printed graph paper works).

    polylines: list of {"points": [(x,y), …], "label": str, "dashed": bool}
               (a straight line is just a 2-point polyline).
    points:    list of (x, y, label, filled).
    """
    polylines = polylines or []
    points = points or []
    xmin, xmax = xrange
    ymin, ymax = yrange
    # Pixels per data unit — different per axis when the steps differ, but chosen
    # so that one labelled square (xstep by ystep) is _CELL by _CELL: square.
    px_x = _CELL / xstep
    px_y = _CELL / ystep
    x0, y0 = _M_LEFT, _M_TOP
    x1 = x0 + (xmax - xmin) * px_x
    y1 = y0 + (ymax - ymin) * px_y
    _W = x1 + _M_RIGHT
    _H = y1 + _M_BOTTOM

    def sx(x):
        return x0 + (x - xmin) * px_x

    def sy(y):
        return y1 - (y - ymin) * px_y

    def _seq(lo, hi, step):
        vals, v = [], lo
        while v <= hi + 1e-9:
            vals.append(v)
            v += step
        return vals

    # Exam graph paper: faint minor squares (5 per labelled interval) under
    # heavier major gridlines at each xstep/ystep.
    body = _graph_paper(
        x0, y0, x1, y1,
        minor_x=[sx(v) for v in _seq(xmin, xmax, xstep / 5)],
        minor_y=[sy(v) for v in _seq(ymin, ymax, ystep / 5)],
        major_x=[sx(v) for v in _seq(xmin, xmax, xstep)],
        major_y=[sy(v) for v in _seq(ymin, ymax, ystep)],
    )
    # Axes through the origin (clamped into the plot if the origin is off-range),
    # with arrowheads on the positive ends always and on the negative ends only
    # where the range actually extends there — the four-quadrant exam look.
    ax = min(max(0, xmin), xmax)
    ay = min(max(0, ymin), ymax)
    axx, ayy = round(sx(ax), 1), round(sy(ay), 1)
    body += _line(x0, ayy, x1, ayy, w=1.5) + _line(axx, y0, axx, y1, w=1.5)
    body += _arrow(x1, ayy, "right") + _arrow(axx, y0, "up")
    if xmin < 0:
        body += _arrow(x0, ayy, "left")
    if ymin < 0:
        body += _arrow(axx, y1, "down")
    if xmin <= 0 <= xmax and ymin <= 0 <= ymax:
        body += _text("O", axx - 9, ayy + 15, anchor="end")
    # Number labels on the major lines, kept in the bottom/left margins (outside
    # the grid, away from the possibly-interior axes) so they never sit on a line.
    for v in _seq(xmin, xmax, xstep):
        if v != 0:
            body += _text(_fmt(v), sx(v), y1 + 18)
    for v in _seq(ymin, ymax, ystep):
        if v != 0:
            body += _text(_fmt(v), x0 - 8, sy(v) + 5, anchor="end")
    body += _text(xlabel, x1, ayy - 6, anchor="end", italic=True, halo=True)
    body += _text(ylabel, axx + 8, y0 + 2, anchor="start", italic=True, halo=True)

    # polylines (lines / curves)
    for pl in polylines:
        pts = pl["points"]
        d = "M " + " L ".join(f"{round(sx(px),1)} {round(sy(py),1)}" for px, py in pts)
        dash = ' stroke-dasharray="5 4"' if pl.get("dashed") else ""
        body += (f'<path d="{d}" fill="none" stroke="currentColor" '
                 f'stroke-width="2"{dash}/>')
        if pl.get("label"):
            lx, ly = pts[-1]
            body += _text(pl["label"], sx(lx) - 6, sy(ly) - 6, anchor="end",
                          italic=True, halo=True)
    # points
    for pt in points:
        x, y = pt[0], pt[1]
        label = pt[2] if len(pt) > 2 else ""
        filled = pt[3] if len(pt) > 3 else True
        cx, cy = round(sx(x), 1), round(sy(y), 1)
        if filled:
            body += f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="currentColor"/>'
        else:
            body += (f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="none" '
                     f'stroke="currentColor" stroke-width="2"/>')
        if label:
            body += _text(label, cx + 6, cy - 6, anchor="start", halo=True)
    return _svg(body, round(_W, 1), round(_H, 1))


def speed_time_svg(points, *, xlabel: str = "Time (s)",
                   ylabel: str = "Velocity (m/s)", guides=None) -> str:
    """A sketch (not-to-scale) speed/velocity–time graph in exam style: arrowed
    axes, no grid, a bold piecewise line, and dashed guide lines running from
    each turning point to the axes, where the key values are labelled.

    points: the line's vertices in data coords, e.g. [(0, 0), (t1, v), (t2, v)].
    guides: list of (x, y, x_label, y_label); for each, a dashed vertical drops
            to the x-axis (labelled x_label if given) and a dashed horizontal
            runs to the y-axis (labelled y_label if given)."""
    guides = guides or []
    W, H = 380, 300
    ox, oy = 96, 250           # origin
    x_end, y_top = 356, 40     # axis line ends (arrow tips just beyond)
    xdmax, ydtop = 322, 74     # where the largest data x / y map to
    xmax = max((p[0] for p in points), default=1) or 1
    ymax = max((p[1] for p in points), default=1) or 1

    def sx(x):
        return ox + (xdmax - ox) * x / xmax

    def sy(v):
        return oy - (oy - ydtop) * v / ymax

    dash = ' stroke-dasharray="4 3"'

    def line(x1, y1, x2, y2, w=2, extra=""):
        return (f'<line x1="{round(x1,1)}" y1="{round(y1,1)}" x2="{round(x2,1)}" '
                f'y2="{round(y2,1)}" stroke="currentColor" stroke-width="{w}"{extra}/>')

    body = ""
    # Dashed guide lines + the key values labelled on the axes.
    for gx, gy, xl, yl in guides:
        px, py = sx(gx), sy(gy)
        body += line(px, py, px, oy, 1, dash)          # vertical to x-axis
        if xl:
            body += _text(xl, px, oy + 18, size=12)
        if yl:
            body += line(ox, py, px, py, 1, dash)      # horizontal to y-axis
            body += _text(yl, ox - 8, py + 4, anchor="end", size=12)
    # The bold speed–time line.
    d = "M " + " L ".join(f"{round(sx(x),1)} {round(sy(y),1)}" for x, y in points)
    body += f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="2.5"/>'
    # Arrowed axes.
    body += line(ox, oy, ox, y_top) + line(ox, oy, x_end, oy)
    body += _arrow(ox, y_top, "up") + _arrow(x_end, oy, "right")
    body += _text("0", ox, oy + 18, size=12)
    # Axis titles: x centred below, y split over two lines to the left, centred.
    body += _text(xlabel, (ox + x_end) / 2, H - 10, size=12)
    ylines = ylabel.split()
    top = (y_top + oy) / 2 - (len(ylines) - 1) * 9
    for i, word in enumerate(ylines):
        body += _text(word, 8, top + i * 18, anchor="start", size=12)
    return _svg(body, W, H)


def function_sketch_svg(*, marked_label: str = "P", opens_up: bool = True) -> str:
    """A schematic (not-to-scale) sketch of y = f(x): four-quadrant arrowed axes,
    a single smooth curve with one turning point, and that point marked and
    labelled. The numeric coordinates live in the question text — the drawing is
    deliberately schematic, so transformations stay trivially verifiable."""
    W, H = 300, 260
    cx, cy = 150, 132
    x0, x1, y0, y1 = 22, W - 16, 16, H - 30
    # four-quadrant arrowed axes + origin
    body = _line(x0, cy, x1, cy, w=1.5) + _line(cx, y0, cx, y1, w=1.5)
    body += (_arrow(x1, cy, "right") + _arrow(x0, cy, "left")
             + _arrow(cx, y0, "up") + _arrow(cx, y1, "down"))
    body += _text("O", cx - 9, cy + 15, anchor="end")
    # a smooth parabola with a clear turning point in the upper-right quadrant
    vx, vy = cx + 42, cy - 30
    k = 0.02
    sgn = -1 if opens_up else 1     # screen y grows down: U-valley curves upward
    pts = []
    x = x0 + 6
    while x <= x1 - 6:
        y = vy + sgn * k * (x - vx) ** 2
        if y0 + 4 <= y <= y1 - 4:
            pts.append((x, y))
        x += 4
    d = "M " + " L ".join(f"{round(px,1)} {round(py,1)}" for px, py in pts)
    body += f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="2.5"/>'
    body += f'<circle cx="{vx}" cy="{round(vy,1)}" r="3.5" fill="currentColor"/>'
    body += _text(marked_label, vx + 8, vy - 6, anchor="start", halo=True)
    return _svg(body, W, H)


def graph_panels_svg(panels, *, cols: int = 2) -> str:
    """A 2×N grid of small labelled sketch graphs (each arrowed axes + a polyline
    in normalised 0..1 coords) — for 'which graph matches the journey?' items."""
    W = 340
    pw, ph, gx, gy = 150, 116, 16, 30
    rows = (len(panels) + cols - 1) // cols
    H = 16 + rows * (ph + gy)
    body = ""
    for i, pan in enumerate(panels):
        r, c = divmod(i, cols)
        ox = 16 + c * (pw + gx)
        oy = 24 + r * (ph + gy) + ph - 16
        body += _line(ox, oy, ox, oy - ph + 20, w=1.5) + _line(ox, oy, ox + pw - 10, oy, w=1.5)
        body += _arrow(ox, oy - ph + 20, "up") + _arrow(ox + pw - 10, oy, "right")

        def sx(x, ox=ox):
            return ox + (pw - 26) * x

        def sy(y, oy=oy):
            return oy - (ph - 34) * y

        pts = pan["points"]
        d = "M " + " L ".join(f"{round(sx(x),1)} {round(sy(y),1)}" for x, y in pts)
        body += f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="2.5"/>'
        body += _text(pan["label"], ox + (pw - 10) / 2, oy - ph + 8, size=12)
    return _svg(body, W, H)
