"""Deterministic data-driven SVG charts for the Statistics & Probability strands.

Same house style as diagrams.py (fixed viewBox, stroke=currentColor, schematic).
Unlike the geometry primitives these are drawn *to scale* from the question's own
data — a bar's height is proportional to its frequency, a pie's angle to its
share, a box plot's marks to the five-number summary — so the figure and the
answer always agree.
"""

from __future__ import annotations

import math

from .diagrams import _line, _poly, _svg, _text, _arrow, _graph_paper, _x_title, _y_title


def _num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def _seq(lo: float, hi: float, step: float) -> list[float]:
    vals, v = [], lo
    while v <= hi + 1e-9:
        vals.append(v)
        v += step
    return vals


def _nice_step(vmax: float, divisions: int = 5) -> float:
    """A 'nice' axis step (1/2/2.5/5 × 10ⁿ) giving ~`divisions` gridlines."""
    if vmax <= 0:
        return 1
    raw = vmax / divisions
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if m * mag >= raw - 1e-9:
            return m * mag
    return 10 * mag


def _rect(x: float, y: float, w: float, h: float, *, fill: str = "none") -> str:
    return (
        f'<rect x="{round(x, 1)}" y="{round(y, 1)}" width="{round(w, 1)}" '
        f'height="{round(h, 1)}" fill="{fill}" stroke="currentColor" stroke-width="2"/>'
    )


def _circle(cx: float, cy: float, r: float) -> str:
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="currentColor" '
        f'stroke-width="2"/>'
    )


def _dot(cx: float, cy: float, r: float = 3) -> str:
    return f'<circle cx="{round(cx, 1)}" cy="{round(cy, 1)}" r="{r}" fill="currentColor"/>'


# --------------------------------------------------------------------------- #
# Bar chart
# --------------------------------------------------------------------------- #
def bar_chart_svg(categories: list[str], values: list[int], *,
                  y_label: str = "Frequency") -> str:
    W, H = 340, 250
    x0, y0, xr, yb = 46, 22, W - 14, H - 42
    ploth = yb - y0
    step = _nice_step(max(values) if values else 1)
    vtop = math.ceil((max(values) if values else 1) / step) * step
    body = ""
    t = 0.0
    while t <= vtop + 1e-9:
        y = yb - ploth * t / vtop
        body += _line(x0, y, xr, y, w=1)
        if t != 0:  # origin tick left unlabelled
            body += _text(_num(t), x0 - 6, y + 4, anchor="end", size=10)
        t += step
    body += _line(x0, y0, x0, yb) + _line(x0, yb, xr, yb)
    body += _arrow(x0, y0, "up") + _arrow(xr, yb, "right")
    n = len(categories)
    gap = (xr - x0) / n
    bw = gap * 0.6
    for i, (c, v) in enumerate(zip(categories, values)):
        bx = x0 + gap * i + (gap - bw) / 2
        bh = ploth * v / vtop
        body += _rect(bx, yb - bh, bw, bh)
        body += _text(str(c), bx + bw / 2, yb + 15, size=10)
    body += _text(y_label, x0 - 6, y0 - 8, anchor="start", size=11)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Pie chart (with a small legend)
# --------------------------------------------------------------------------- #
def pie_chart_svg(labels: list[str], values: list[int]) -> str:
    W, H = 340, 220
    cx, cy, r = 110, 110, 88
    total = sum(values) or 1
    body = ""
    ang = -90.0  # start at top
    for lab, v in zip(labels, values):
        sweep = 360 * v / total
        a0 = math.radians(ang)
        a1 = math.radians(ang + sweep)
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        large = 1 if sweep > 180 else 0
        body += (
            f'<path d="M {cx} {cy} L {round(p0[0], 1)} {round(p0[1], 1)} '
            f'A {r} {r} 0 {large} 1 {round(p1[0], 1)} {round(p1[1], 1)} Z" '
            f'fill="none" stroke="currentColor" stroke-width="2"/>'
        )
        ang += sweep
    # legend
    lx, ly = 220, 40
    for i, (lab, v) in enumerate(zip(labels, values)):
        y = ly + i * 22
        body += _rect(lx, y - 10, 12, 12)
        body += _text(f"{lab}", lx + 18, y, anchor="start", size=12)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Pictogram
# --------------------------------------------------------------------------- #
def pictogram_svg(categories: list[str], counts: list[int], *,
                  key_value: int, symbol_label: str = "= {k}") -> str:
    """Rows of circles; each full circle represents `key_value`, halves allowed."""
    W = 340
    row_h = 30
    H = 40 + row_h * len(categories) + 24
    x0 = 96
    body = ""
    for i, (cat, cnt) in enumerate(zip(categories, counts)):
        y = 34 + i * row_h
        body += _text(str(cat), x0 - 10, y + 5, anchor="end", size=12)
        full = cnt // key_value
        half = 1 if (cnt % key_value) else 0
        for j in range(full):
            body += _circle(x0 + 14 + j * 26, y, 9)
        if half:
            j = full
            cx = x0 + 14 + j * 26
            body += (
                f'<path d="M {cx} {y - 9} A 9 9 0 0 0 {cx} {y + 9} Z" '
                f'fill="currentColor" stroke="currentColor" stroke-width="2"/>'
            )
    key = symbol_label.replace("{k}", str(key_value))
    body += _circle(x0 + 14, H - 16, 9)
    body += _text(key, x0 + 30, H - 11, anchor="start", size=12)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Histogram (unequal class widths, height = frequency density)
# --------------------------------------------------------------------------- #
def histogram_svg(bins: list[tuple[float, float, float]], *,
                  x_label: str = "", y_label: str = "Frequency density") -> str:
    W, H = 360, 250
    x0, y0, xr, yb = 48, 22, W - 14, H - 42
    xmin = min(b[0] for b in bins)
    xmax = max(b[1] for b in bins)
    fdmax = max(b[2] for b in bins)
    ystep = _nice_step(fdmax)
    ytop = math.ceil(fdmax / ystep) * ystep
    xstep = _nice_step(xmax - xmin, 6)

    def sx(x):
        return x0 + (xr - x0) * (x - xmin) / (xmax - xmin)

    def sy(v):
        return yb - (yb - y0) * v / ytop

    # Faint graph-paper grid the bars sit on, then the arrowed axes.
    body = _graph_paper(
        x0, y0, xr, yb,
        minor_x=[sx(v) for v in _seq(xmin, xmax, xstep / 5)],
        minor_y=[sy(v) for v in _seq(0, ytop, ystep / 5)],
        major_x=[sx(v) for v in _seq(xmin, xmax, xstep)],
        major_y=[sy(v) for v in _seq(0, ytop, ystep)],
    )
    for t in _seq(0, ytop, ystep):
        if t != 0:  # origin tick left unlabelled
            body += _text(_num(t), x0 - 6, sy(t) + 4, anchor="end", size=10)
    body += _line(x0, y0, x0, yb) + _line(x0, yb, xr, yb)
    body += _arrow(x0, y0, "up") + _arrow(xr, yb, "right")
    for xt in _seq(xmin, xmax, xstep):
        body += _line(sx(xt), yb, sx(xt), yb + 4)
        if xt != 0:  # origin tick left unlabelled
            body += _text(_num(xt), sx(xt), yb + 16, size=10)
    for lo, hi, fd in bins:
        body += _rect(sx(lo), sy(fd), sx(hi) - sx(lo), yb - sy(fd))
    body += _text(y_label, x0 - 6, y0 - 8, anchor="start", size=11)
    if x_label:
        body += _text(x_label, (x0 + xr) / 2, H - 6, size=11)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Box plot
# --------------------------------------------------------------------------- #
def box_plot_svg(minimum, lq, median, uq, maximum, *,
                 axis_min, axis_max, label: str = "") -> str:
    W, H = 360, 150
    x0, xr = 30, W - 20
    yc = 54
    box_h = 40

    def sx(v):
        return x0 + (xr - x0) * (v - axis_min) / (axis_max - axis_min)

    body = ""
    # whiskers
    body += _line(sx(minimum), yc, sx(lq), yc)
    body += _line(sx(uq), yc, sx(maximum), yc)
    body += _line(sx(minimum), yc - 10, sx(minimum), yc + 10)
    body += _line(sx(maximum), yc - 10, sx(maximum), yc + 10)
    # box
    body += _rect(sx(lq), yc - box_h / 2, sx(uq) - sx(lq), box_h)
    body += _line(sx(median), yc - box_h / 2, sx(median), yc + box_h / 2)
    # axis
    ay = 104
    body += _line(x0, ay, xr, ay) + _arrow(xr, ay, "right")
    step = _nice_step(axis_max - axis_min, 6)
    t = axis_min
    while t <= axis_max + 1e-9:
        body += _line(sx(t), ay, sx(t), ay + 4)
        if t != 0:  # origin tick left unlabelled
            body += _text(_num(t), sx(t), ay + 16, size=10)
        t += step
    if label:
        body += _text(label, x0, 24, anchor="start", size=12)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Cumulative frequency curve
# --------------------------------------------------------------------------- #
def cumulative_frequency_svg(points: list[tuple[float, float]], *,
                             x_label: str = "", y_label: str = "Cumulative frequency") -> str:
    """A blank cumulative-frequency plotting grid in exam graph-paper style: fine
    minor squares, heavier major gridlines at the labelled values, and arrowed
    axes. The student draws the curve; `points` only sizes the axes (x to the
    largest class boundary, y up to a 'nice' round total)."""
    W, H = 400, 300
    x0, y0, xr, yb = 62, 26, W - 26, H - 46
    xtop = max(p[0] for p in points)
    ymax = max(p[1] for p in points)
    ystep = _nice_step(ymax)
    ytop = math.ceil(ymax / ystep) * ystep
    xstep = _nice_step(xtop, 6)

    def sx(x):
        return x0 + (xr - x0) * x / xtop

    def sy(v):
        return yb - (yb - y0) * v / ytop

    body = _graph_paper(
        x0, y0, xr, yb,
        minor_x=[sx(v) for v in _seq(0, xtop, xstep / 5)],
        minor_y=[sy(v) for v in _seq(0, ytop, ystep / 5)],
        major_x=[sx(v) for v in _seq(0, xtop, xstep)],
        major_y=[sy(v) for v in _seq(0, ytop, ystep)],
    )
    # Major-line number labels (0 shown once, at the origin, on the x-axis).
    for xt in _seq(0, xtop, xstep):
        body += _text(_num(xt), sx(xt), yb + 17, size=11)
    for yt in _seq(ystep, ytop, ystep):
        body += _text(_num(yt), x0 - 8, sy(yt) + 4, anchor="end", size=11)
    # Arrowed axes.
    body += _line(x0, yb, x0, y0 - 12) + _line(x0, yb, xr + 12, yb)
    body += _arrow(x0, y0 - 12, "up") + _arrow(xr + 12, yb, "right")
    body += _text(y_label, x0 - 8, y0 - 8, anchor="start", size=11)
    if x_label:
        body += _text(x_label, (x0 + xr) / 2, H - 8, size=11)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Scatter graph (optional line of best fit)
# --------------------------------------------------------------------------- #
def scatter_svg(points: list[tuple[float, float]], *, x_label: str = "",
                y_label: str = "", xmin=None, xmax=None, ymin=None, ymax=None) -> str:
    W, H = 340, 250
    x0, y0, xr, yb = 46, 22, W - 14, H - 42
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin = min(xs) if xmin is None else xmin
    xmax = max(xs) if xmax is None else xmax
    ymin = min(ys) if ymin is None else ymin
    ymax = max(ys) if ymax is None else ymax

    def sx(x):
        return x0 + (xr - x0) * (x - xmin) / (xmax - xmin)

    def sy(v):
        return yb - (yb - y0) * (v - ymin) / (ymax - ymin)

    xstep = _nice_step(xmax - xmin, 6)
    ystep = _nice_step(ymax - ymin, 6)
    body = _graph_paper(
        x0, y0, xr, yb,
        minor_x=[sx(v) for v in _seq(xmin, xmax, xstep / 5)],
        minor_y=[sy(v) for v in _seq(ymin, ymax, ystep / 5)],
        major_x=[sx(v) for v in _seq(xmin, xmax, xstep)],
        major_y=[sy(v) for v in _seq(ymin, ymax, ystep)],
    )
    body += _line(x0, y0, x0, yb) + _line(x0, yb, xr, yb)
    body += _arrow(x0, y0, "up") + _arrow(xr, yb, "right")
    for xt in _seq(xmin, xmax, xstep):
        if xt != 0:  # origin tick left unlabelled
            body += _text(_num(xt), sx(xt), yb + 16, size=9)
    for yt in _seq(ymin, ymax, ystep):
        if yt != 0:  # origin tick left unlabelled
            body += _text(_num(yt), x0 - 6, sy(yt) + 4, anchor="end", size=9)
    # Data points as × crosses (the exam convention).
    for x, v in points:
        px, py = sx(x), sy(v)
        body += _line(px - 4, py - 4, px + 4, py + 4) + _line(px - 4, py + 4, px + 4, py - 4)
    if x_label:
        body += _text(x_label, (x0 + xr) / 2, H - 6, size=11)
    if y_label:
        body += _text(y_label, x0 - 6, y0 - 8, anchor="start", size=11)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Frequency polygon
# --------------------------------------------------------------------------- #
def frequency_polygon_svg(midpoints: list[float], freqs: list[int], *,
                          x_label: str = "", y_label: str = "Frequency") -> str:
    W, H = 340, 250
    x0, y0, xr, yb = 46, 22, W - 14, H - 42
    xmin, xmax = min(midpoints), max(midpoints)
    fmax = max(freqs)
    ystep = _nice_step(fmax)
    ytop = math.ceil(fmax / ystep) * ystep

    def sx(x):
        return x0 + (xr - x0) * (x - xmin) / (xmax - xmin)

    def sy(v):
        return yb - (yb - y0) * v / ytop

    xw = midpoints[1] - midpoints[0] if len(midpoints) > 1 else (xmax - xmin or 1)
    body = _graph_paper(
        x0, y0, xr, yb,
        minor_x=[sx(v) for v in _seq(xmin, xmax, xw / 5)],
        minor_y=[sy(v) for v in _seq(0, ytop, ystep / 5)],
        major_x=[sx(v) for v in _seq(xmin, xmax, xw)],
        major_y=[sy(v) for v in _seq(0, ytop, ystep)],
    )
    for t in _seq(0, ytop, ystep):
        if t != 0:  # origin tick left unlabelled
            body += _text(_num(t), x0 - 6, sy(t) + 4, anchor="end", size=10)
    body += _line(x0, y0, x0, yb) + _line(x0, yb, xr, yb)
    body += _arrow(x0, y0, "up") + _arrow(xr, yb, "right")
    for m in midpoints:
        body += _text(_num(m), sx(m), yb + 16, size=10)
    pts = [(sx(m), sy(f)) for m, f in zip(midpoints, freqs)]
    d = "M " + " L ".join(f"{round(px, 1)} {round(py, 1)}" for px, py in pts)
    body += f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="2"/>'
    for px, py in pts:
        body += _dot(px, py)
    body += _text(y_label, x0 - 6, y0 - 8, anchor="start", size=11)
    if x_label:
        body += _text(x_label, (x0 + xr) / 2, H - 6, size=11)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Two-stage probability tree (binary at each stage)
# --------------------------------------------------------------------------- #
def probability_tree_svg(*, stage1=("A", "A'"), leaves=("A", "A'"), p1=("", ""),
                         p2_top=("", ""), p2_bot=("", "")) -> str:
    """Two-stage binary tree. `stage1` labels the first nodes; `leaves` labels the
    four second-stage outcomes (for a repeated event stage1 == leaves; for a
    frequency tree they differ, e.g. Male/Female then Pass/Fail)."""
    W, H = 340, 240
    root = (26, 120)
    s1 = [(150, 62), (150, 178)]     # top, bottom
    s2 = [(266, 34), (266, 90), (266, 150), (266, 206)]
    body = ""
    # stage 1 branches
    for i, node in enumerate(s1):
        body += _line(*root, *node)
        mx, my = (root[0] + node[0]) / 2, (root[1] + node[1]) / 2
        body += _text(p1[i], mx, my - 4, size=11)
        # Node label sits in the open wedge beside the junction — above the top
        # node, below the bottom node, and left of where the next branches fan
        # out (anchor="end") — so it never overlaps a line.
        dy = -10 if i == 0 else 22
        body += _text(stage1[i], node[0] - 8, node[1] + dy, anchor="end", size=12)
    # stage 2 branches
    pairs = [(s1[0], s2[0], p2_top[0], leaves[0]),
             (s1[0], s2[1], p2_top[1], leaves[1]),
             (s1[1], s2[2], p2_bot[0], leaves[0]),
             (s1[1], s2[3], p2_bot[1], leaves[1])]
    for a, b, lbl, out in pairs:
        body += _line(*a, *b)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        body += _text(lbl, mx, my - 4, size=11)
        body += _text(out, b[0] + 8, b[1] + 4, anchor="start", size=12)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Two-set Venn diagram
# --------------------------------------------------------------------------- #
def venn2_svg(*, set_a: str = "A", set_b: str = "B", only_a: str = "",
              both: str = "", only_b: str = "", outside: str = "") -> str:
    W, H = 320, 210
    body = _rect(8, 8, W - 16, H - 16)
    body += _circle(125, 105, 72) + _circle(195, 105, 72)
    body += _text(set_a, 70, 44, size=13) + _text(set_b, 250, 44, size=13)
    body += _text("ℰ", 20, 28, size=13)
    body += _text(str(only_a), 92, 110, size=13)
    body += _text(str(both), 160, 110, size=13)
    body += _text(str(only_b), 228, 110, size=13)
    if outside != "":
        body += _text(str(outside), W - 24, H - 20, size=13)
    return _svg(body, W, H)


# --------------------------------------------------------------------------- #
# Blank pie chart (for the student to construct)
# --------------------------------------------------------------------------- #
def blank_pie_svg() -> str:
    """An empty circle with a centre dot and one radius drawn — the student
    measures and draws the sectors."""
    W, H = 240, 240
    cx, cy, r = 120, 120, 96
    return _svg(_circle(cx, cy, r) + _dot(cx, cy) + _line(cx, cy, cx, cy - r), W, H)
