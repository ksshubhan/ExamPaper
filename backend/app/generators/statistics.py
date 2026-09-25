"""Statistics-strand generators.

Deterministic from a seed; every numeric answer is exactly computable (or given
with a tolerance where a reading is genuinely graphical) and independently
re-derivable. Charts/tables are drawn to scale from the same sampled data.
"""

from __future__ import annotations

import math
from collections import Counter
from random import Random

import sympy

from ..schema import Diagram, GenerateRequest, Item, MarkSchemeStep, Table
from . import stats_diagrams as SD
from .basics import _seed
from .context import make_item, mk_part, pick

_MAX_ATTEMPTS = 300


def _dia(svg: str, alt: str, plot_grid: bool = False) -> Diagram:
    return Diagram(svg=svg, alt=alt, not_to_scale=False, plot_grid=plot_grid)


def _B1(desc, working=None):
    return MarkSchemeStep(code="B1", mark_type="B", description=desc, working=working)


def _M1(desc, working=None):
    return MarkSchemeStep(code="M1", mark_type="M", description=desc, working=working)


def _A1(desc, working=None):
    return MarkSchemeStep(code="A1", mark_type="A", description=desc, working=working)


# --------------------------------------------------------------------------- #
# Averages from a list — mode, median, mean, range  (S4, grade 2)
# --------------------------------------------------------------------------- #
def build_averages(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        n = rng.choice([7, 9, 11])
        data = [rng.randint(1, 20) for _ in range(n)]
        c = Counter(data)
        top = c.most_common()
        if top[0][1] < 2 or sum(1 for v in c.values() if v == top[0][1]) != 1:
            continue  # need a single, genuine mode
        if sum(data) % n != 0:
            continue  # keep the mean a whole number
        mode = top[0][0]
        mean = sum(data) // n
        s = sorted(data)
        median = s[n // 2]
        rng_val = max(data) - min(data)
        stem = "Here are " + str(n) + " numbers.\n" + "   ".join(str(d) for d in data)
        parts = [
            mk_part(label="a", prompt="Write down the mode.", marks=1, answer=str(mode),
                    working=f"{mode} appears most often", mark_scheme=[_B1("cao")]),
            mk_part(label="b", prompt="Find the median.", marks=1, answer=str(median),
                    working=f"Ordered, the middle value is {median}",
                    mark_scheme=[_B1("cao")]),
            mk_part(label="c", prompt="Work out the mean.", marks=2, answer=str(mean),
                    working=f"({' + '.join(str(d) for d in data)}) ÷ {n} = {sum(data)} ÷ {n} = {mean}",
                    mark_scheme=[_M1("for sum ÷ n", f"{sum(data)} ÷ {n}"), _A1("cao", str(mean))]),
            mk_part(label="d", prompt="Work out the range.", marks=1, answer=str(rng_val),
                    working=f"{max(data)} − {min(data)} = {rng_val}",
                    mark_scheme=[_B1("cao")]),
        ]
        return make_item(req, seed, archetype="averages", topic="Averages",
                         topic_slug="averages", strand="Statistics", spec_ref="S4",
                         grade_band="2-3", stem=stem, parts=parts)
    raise RuntimeError("averages generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Mean from a frequency table  (S4, grade 4)
# --------------------------------------------------------------------------- #
def build_averages_frequency(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        values = [1, 2, 3, 4, 5]
        freqs = [rng.randint(1, 9) for _ in values]
        N = sum(freqs)
        fx = sum(v * f for v, f in zip(values, freqs))
        if N < 10 or fx % N != 0:
            continue  # keep the mean exact
        mean = fx // N
        noun = pick(rng, ["goals scored", "pets owned", "books read", "matches won"])
        table = Table(caption=f"Number of {noun}",
                      headers=["Number", "Frequency"],
                      rows=[[str(v), str(f)] for v, f in zip(values, freqs)])
        part = mk_part(
            prompt="Work out the mean number.", marks=3, answer=str(mean),
            working=(f"Σfx = {' + '.join(f'{v}×{f}' for v, f in zip(values, freqs))} = {fx}\n"
                     f"Σf = {N}\nMean = {fx} ÷ {N} = {mean}"),
            mark_scheme=[_M1("for Σfx", f"= {fx}"), _M1("for ÷ Σf", f"{fx} ÷ {N}"),
                         _A1("cao", str(mean))])
        return make_item(req, seed, archetype="averages-frequency",
                         topic="Averages from a frequency table",
                         topic_slug="averages-frequency", strand="Statistics",
                         spec_ref="S4", grade_band="4-5",
                         stem=f"The table shows the number of {noun} by some people.",
                         parts=[part], table=table)
    raise RuntimeError("averages-frequency generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Bar charts  (S2, grade 2)
# --------------------------------------------------------------------------- #
def build_bar_charts(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    cats = pick(rng, [["Red", "Blue", "Green", "Yellow"],
                      ["Walk", "Bus", "Car", "Cycle"],
                      ["Mon", "Tue", "Wed", "Thu"]])
    freqs = [rng.randint(3, 18) for _ in cats]
    i, j = rng.sample(range(len(cats)), 2)
    dia = _dia(SD.bar_chart_svg(cats, freqs),
               "A bar chart showing " + ", ".join(f"{c}: {f}" for c, f in zip(cats, freqs)))
    diff = freqs[i] - freqs[j]
    part = mk_part(
        prompt=f"How many more chose {cats[i]} than {cats[j]}?" if diff >= 0
        else f"How many more chose {cats[j]} than {cats[i]}?",
        marks=2, answer=str(abs(diff)),
        working=f"{max(freqs[i], freqs[j])} − {min(freqs[i], freqs[j])} = {abs(diff)}",
        mark_scheme=[_M1("for reading both bars"), _A1("cao", str(abs(diff)))])
    return make_item(req, seed, archetype="bar-charts", topic="Bar charts",
                     topic_slug="bar-charts", strand="Statistics", spec_ref="S2",
                     grade_band="2-3", stem="The bar chart shows some data.",
                     parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Pictograms  (S2, grade 1)
# --------------------------------------------------------------------------- #
def build_pictograms(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        cats = pick(rng, [["Mon", "Tue", "Wed"], ["Shop A", "Shop B", "Shop C"]])
        key = rng.choice([2, 4, 10])
        counts = [key * rng.randint(1, 5) for _ in cats]
        if len(set(counts)) < 2:
            continue
        total = sum(counts)
        dia = _dia(SD.pictogram_svg(cats, counts, key_value=key),
                   "A pictogram; each symbol represents " + str(key) + ".")
        part = mk_part(
            prompt="Work out the total shown in the pictogram.", marks=2, answer=str(total),
            working=" + ".join(str(c) for c in counts) + f" = {total}",
            mark_scheme=[_M1(f"for using 1 symbol = {key}"), _A1("cao", str(total))])
        return make_item(req, seed, archetype="pictograms", topic="Pictograms",
                         topic_slug="pictograms", strand="Statistics", spec_ref="S2",
                         grade_band="1-2",
                         stem=f"The pictogram shows some data. Each symbol represents {key}.",
                         parts=[part], diagram=dia)
    raise RuntimeError("pictograms generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Pie charts — work out the angle for a category  (S3, grade 2)
# --------------------------------------------------------------------------- #
def build_pie_charts(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        total = rng.choice([30, 36, 40, 45, 60, 72, 90])
        cats = ["Red", "Blue", "Green", "Yellow"]
        freqs = [rng.randint(2, total // 4) for _ in cats[:-1]]
        freqs.append(total - sum(freqs))
        if freqs[-1] < 2:
            continue
        if any((360 * f) % total != 0 for f in freqs):
            continue  # every angle a whole number of degrees
        i = rng.randrange(len(cats))
        angle = 360 * freqs[i] // total
        dia = _dia(SD.pie_chart_svg([f"{c} ({f})" for c, f in zip(cats, freqs)], freqs),
                   "A pie chart of colour frequencies.")
        part = mk_part(
            prompt=f"{total} people were asked. Work out the angle for {cats[i]} on the pie chart.",
            marks=2, answer=f"{angle}°",
            working=f"{freqs[i]}/{total} × 360° = {angle}°",
            mark_scheme=[_M1("for 360 ÷ total × frequency", f"360 ÷ {total} × {freqs[i]}"),
                         _A1("cao", f"{angle}°")])
        return make_item(req, seed, archetype="pie-charts", topic="Pie charts",
                         topic_slug="pie-charts", strand="Statistics", spec_ref="S3",
                         grade_band="2-3",
                         stem=f"{total} people were asked their favourite colour. "
                         "The frequencies are shown.",
                         parts=[part], diagram=dia)
    raise RuntimeError("pie-charts generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Stem and leaf  (S2, grade 2)
# --------------------------------------------------------------------------- #
def build_stem_leaf(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        n = rng.choice([9, 11])
        data = sorted(rng.randint(10, 59) for _ in range(n))
        median = data[n // 2]
        rng_val = data[-1] - data[0]
        stems = {}
        for d in data:
            stems.setdefault(d // 10, []).append(d % 10)
        rows = [[str(s), " ".join(str(l) for l in leaves)]
                for s, leaves in sorted(stems.items())]
        table = Table(caption="Stem | Leaf", headers=["Stem", "Leaf"], rows=rows)
        parts = [
            mk_part(label="a", prompt="Find the median.", marks=2, answer=str(median),
                    working=f"{n} values; the median is the {n // 2 + 1}th = {median}",
                    mark_scheme=[_M1("for identifying the middle value"), _A1("cao", str(median))]),
            mk_part(label="b", prompt="Work out the range.", marks=1, answer=str(rng_val),
                    working=f"{data[-1]} − {data[0]} = {rng_val}", mark_scheme=[_B1("cao")]),
        ]
        return make_item(req, seed, archetype="stem-leaf", topic="Stem and leaf",
                         topic_slug="stem-leaf", strand="Statistics", spec_ref="S2",
                         grade_band="2-3",
                         stem="The stem-and-leaf diagram shows some data. Key: 1 | 2 means 12.",
                         parts=parts, table=table)
    raise RuntimeError("stem-leaf generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Frequency polygons  (S2, grade 2)
# --------------------------------------------------------------------------- #
def build_frequency_polygons(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    mids = [5, 15, 25, 35, 45]
    freqs = [rng.randint(2, 16) for _ in mids]
    modal = mids[freqs.index(max(freqs))]
    total = sum(freqs)
    dia = _dia(SD.frequency_polygon_svg(mids, freqs, y_label="Frequency"),
               "A frequency polygon.", plot_grid=True)
    part = mk_part(
        prompt="Work out the total frequency.", marks=2, answer=str(total),
        working=" + ".join(str(f) for f in freqs) + f" = {total}",
        mark_scheme=[_M1("for adding the frequencies"), _A1("cao", str(total))])
    return make_item(req, seed, archetype="frequency-polygons",
                     topic="Frequency polygons", topic_slug="frequency-polygons",
                     strand="Statistics", spec_ref="S2", grade_band="2-4",
                     stem="The frequency polygon shows some data.", parts=[part],
                     diagram=dia)


# --------------------------------------------------------------------------- #
# Two-way tables  (S5, grade 3)
# --------------------------------------------------------------------------- #
def build_two_way_tables(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    bw = rng.randint(6, 20)   # boys walk
    bb = rng.randint(6, 20)   # boys bus
    gw = rng.randint(6, 20)
    gb = rng.randint(6, 20)
    boys, girls = bw + bb, gw + gb
    walk, bus = bw + gw, bb + gb
    total = boys + girls
    # hide one cell (girls / bus = gb)
    table = Table(caption="", headers=["", "Walk", "Bus", "Total"], rows=[
        ["Boys", str(bw), str(bb), str(boys)],
        ["Girls", str(gw), "?", str(girls)],
        ["Total", str(walk), str(bus), str(total)],
    ])
    part = mk_part(
        prompt="Work out the number of girls who travel by bus (the missing value).",
        marks=2, answer=str(gb),
        working=f"Girls total {girls} − girls who walk {gw} = {gb}   (or bus {bus} − boys bus {bb})",
        mark_scheme=[_M1("for a correct subtraction"), _A1("cao", str(gb))])
    return make_item(req, seed, archetype="two-way-tables", topic="Two-way tables",
                     topic_slug="two-way-tables", strand="Statistics", spec_ref="S5",
                     grade_band="3-4",
                     stem="The two-way table shows how some students travel to school. "
                     "One value is missing.", parts=[part], table=table)


# --------------------------------------------------------------------------- #
# Scatter graphs  (S6, grade 4)
# --------------------------------------------------------------------------- #
def build_scatter_graphs(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    positive = rng.random() < 0.5
    pts = []
    for k in range(9):
        x = 2 * k + rng.randint(0, 1) + 2
        base = x if positive else (24 - x)
        y = base + rng.randint(-2, 2)
        pts.append((x, max(1, y)))
    corr = "positive" if positive else "negative"
    dia = _dia(SD.scatter_svg(pts, x_label="x", y_label="y"),
               f"A scatter graph showing {corr} correlation.", plot_grid=True)
    part = mk_part(
        prompt="Describe the type of correlation shown.", marks=1, answer=corr.capitalize(),
        working=f"The points trend {'upwards' if positive else 'downwards'} → "
        f"{corr} correlation",
        mark_scheme=[_B1(f"for '{corr} correlation'")])
    return make_item(req, seed, archetype="scatter-graphs", topic="Scatter graphs",
                     topic_slug="scatter-graphs", strand="Statistics", spec_ref="S6",
                     grade_band="3-5", ao="AO2",
                     stem="The scatter graph shows some bivariate data.", parts=[part],
                     diagram=dia)


# --------------------------------------------------------------------------- #
# Cumulative frequency — median by interpolation (graphical, tolerance)  (S5, grade 6)
# --------------------------------------------------------------------------- #
def build_cumulative_frequency(req: GenerateRequest) -> Item:
    """Multi-part, as real 1H papers run it: (a) complete the cumulative
    frequency table, (b) read the median off the curve, (c) estimate the IQR."""
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        uppers = [10, 20, 30, 40, 50]
        freqs = [rng.randint(3, 15) for _ in uppers]
        N = sum(freqs)
        if N % 2 != 0:
            continue
        cf, run = [], 0
        for f in freqs:
            run += f
            cf.append(run)

        def interp(pos: float) -> float:
            """The height read off the curve at cumulative frequency `pos`."""
            idx = next(i for i, v in enumerate(cf) if v >= pos)
            low = 0 if idx == 0 else uppers[idx - 1]
            cf_before = 0 if idx == 0 else cf[idx - 1]
            return low + (pos - cf_before) / freqs[idx] * (uppers[idx] - low)

        median, lq, uq = interp(N / 2), interp(N / 4), interp(3 * N / 4)
        iqr = uq - lq

        def band(v: float) -> tuple[int, int]:
            """A reading tolerance band around a value read off the graph — a
            graph read cannot carry more precision than a couple of squares."""
            lo, hi = math.floor(v), math.ceil(v)
            if lo == hi:            # value fell on a gridline — still give a range
                lo, hi = lo - 1, hi + 1
            return lo, hi

        m_lo, m_hi = band(median)
        i_lo, i_hi = band(iqr)
        # (d) reading: how many are taller than a class boundary — read off the
        # curve, so it also carries a tolerance band.
        cut_idx = 2                       # the 30 cm boundary
        cut = uppers[cut_idx]
        taller = N - cf[cut_idx]
        t_lo, t_hi = band(taller)
        cf_str = ", ".join(str(v) for v in cf)

        table = Table(
            caption="",
            headers=["Height, h (cm)", "Frequency", "Cumulative frequency"],
            rows=[[f"{(0 if i == 0 else uppers[i-1])} ≤ h < {uppers[i]}",
                   str(freqs[i]), ""]
                  for i in range(len(uppers))])
        dia = _dia(SD.cumulative_frequency_svg(list(zip(uppers, cf)),
                                               x_label="Height (cm)"),
                   "A blank cumulative frequency grid for the student to plot on.",
                   plot_grid=True)
        parts = [
            mk_part(
                label="a",
                prompt="Complete the cumulative frequency column in the table above.",
                marks=1, answer=cf_str,
                working="Running totals of the frequencies give " + cf_str,
                mark_scheme=[_B1("all cumulative frequencies correct", cf_str)]),
            mk_part(
                label="b",
                prompt="On the grid, draw a cumulative frequency graph for your "
                "completed table.",
                marks=2,
                answer="Plot (10, {}), (20, {}), (30, {}), (40, {}), (50, {}) and "
                "join with a smooth curve.".format(*cf),
                working="Plot each cumulative frequency against the upper boundary "
                "of its class, then join the points with a smooth curve.",
                mark_scheme=[
                    _B1("for all 5 points plotted correctly (± half a square)"),
                    _B1("for a smooth increasing cumulative frequency curve"),
                ]),
            mk_part(
                label="c",
                prompt="Use the cumulative frequency graph to find an estimate for the "
                "median height.",
                marks=2, answer=f"{m_lo} – {m_hi} cm",
                working=f"Read across at cf = {N / 2:g}: median ≈ {median:.1f} cm",
                mark_scheme=[_M1(f"for reading across at cf = {N / 2:g}"),
                             _A1(f"for an answer in the range {m_lo} to {m_hi}")]),
            mk_part(
                label="d",
                prompt="Use the cumulative frequency graph to find an estimate for the "
                "interquartile range.",
                marks=2, answer=f"{i_lo} – {i_hi} cm",
                working=(f"LQ ≈ {lq:.1f} (at cf = {N / 4:g}), "
                         f"UQ ≈ {uq:.1f} (at cf = {3 * N / 4:g})\n"
                         f"IQR = UQ − LQ ≈ {iqr:.1f} cm"),
                mark_scheme=[_M1("for UQ − LQ read from the graph"),
                             _A1(f"for an answer in the range {i_lo} to {i_hi}")]),
            mk_part(
                label="e",
                prompt=f"Use the cumulative frequency graph to estimate the number of "
                f"plants that are taller than {cut} cm.",
                marks=1, answer=f"{t_lo} – {t_hi}",
                working=f"{N} − (cf at {cut}) ≈ {N} − {cf[cut_idx]} = {taller}",
                mark_scheme=[_B1(f"for an answer in the range {t_lo} to {t_hi}")]),
        ]
        return make_item(req, seed, archetype="cumulative-frequency",
                         topic="Cumulative frequency", topic_slug="cumulative-frequency",
                         strand="Statistics", spec_ref="S5", grade_band="5-7",
                         stem="The table and cumulative frequency graph show the heights "
                         "of some plants.", parts=parts, diagram=dia, table=table)
    raise RuntimeError("cumulative-frequency generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Box plots  (S5, grade 6)
# --------------------------------------------------------------------------- #
def build_box_plots(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    mn = rng.randint(2, 12)
    lq = mn + rng.randint(4, 12)
    med = lq + rng.randint(3, 10)
    uq = med + rng.randint(3, 10)
    mx = uq + rng.randint(4, 12)
    iqr = uq - lq
    axis_max = ((mx // 10) + 1) * 10
    dia = _dia(SD.box_plot_svg(mn, lq, med, uq, mx, axis_min=0, axis_max=axis_max,
                               label="Speed (mph)"), "A box plot.", plot_grid=True)
    parts = [
        mk_part(label="a", prompt="Write down the median.", marks=1, answer=str(med),
                working=f"Median line at {med}", mark_scheme=[_B1("cao")]),
        mk_part(label="b", prompt="Work out the interquartile range.", marks=2,
                answer=str(iqr), working=f"UQ − LQ = {uq} − {lq} = {iqr}",
                mark_scheme=[_M1("for UQ − LQ", f"{uq} − {lq}"), _A1("cao", str(iqr))]),
    ]
    return make_item(req, seed, archetype="box-plots", topic="Box plots",
                     topic_slug="box-plots", strand="Statistics", spec_ref="S5",
                     grade_band="5-7", stem="The box plot shows the speeds of some cars.",
                     parts=parts, diagram=dia)


# --------------------------------------------------------------------------- #
# Histograms — estimate a frequency (freq = fd × width)  (S3, grade 7)
# --------------------------------------------------------------------------- #
def build_histograms(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    # bins (low, high, frequency); frequency density = f / width
    edges = [0, 10, 20, 40, 60]
    freqs = [rng.randint(4, 20) for _ in range(len(edges) - 1)]
    bins = []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        fd = sympy.Rational(freqs[i], hi - lo)
        bins.append((lo, hi, float(fd)))
    i = rng.randrange(len(freqs))
    lo, hi = edges[i], edges[i + 1]
    fd = sympy.Rational(freqs[i], hi - lo)
    dia = _dia(SD.histogram_svg(bins, x_label="Distance (miles)"), "A histogram.",
               plot_grid=True)
    part = mk_part(
        prompt=f"Use the histogram to work out the number of values in the class "
        f"{lo} < x ≤ {hi}.", marks=2, answer=str(freqs[i]),
        working=f"Frequency density {fd} × class width {hi - lo} = {freqs[i]}",
        mark_scheme=[_M1("for frequency density × class width",
                         f"{fd} × {hi - lo}"), _A1("cao", str(freqs[i]))])
    return make_item(req, seed, archetype="histograms", topic="Histograms",
                     topic_slug="histograms", strand="Statistics", spec_ref="S3",
                     grade_band="6-8",
                     stem="The histogram shows the distances travelled by some people.",
                     parts=[part], diagram=dia)


# --------------------------------------------------------------------------- #
# Constructing a pie chart  (S3, grade 3-5)
# --------------------------------------------------------------------------- #
def build_construct_pie_chart(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    sports = ["Football", "Rugby", "Tennis", "Cricket", "Swimming", "Hockey"]
    for _ in range(_MAX_ATTEMPTS):
        total = rng.choice([30, 36, 40, 45, 60, 72, 90])
        per = 360 // total                       # whole degrees per person
        cuts = sorted(rng.sample(range(1, total), 3))
        freqs = [cuts[0], cuts[1] - cuts[0], cuts[2] - cuts[1], total - cuts[2]]
        if any(f <= 0 for f in freqs):
            continue
        angles = [f * per for f in freqs]
        # Independent check: whole-degree angles that sum to 360°.
        if sum(angles) != 360 or any(360 * f % total for f in freqs):
            continue
        cats = rng.sample(sports, 4)
        table = Table(caption="", headers=["Sport", "Frequency"],
                      rows=[[cats[i], str(freqs[i])] for i in range(4)])
        ans = ", ".join(f"{cats[i]} {angles[i]}°" for i in range(4))
        return make_item(
            req, seed, archetype="construct-pie-chart",
            topic="Constructing pie charts", topic_slug="construct-pie-chart",
            strand="Statistics", spec_ref="S3", grade_band="3-5",
            stem=f"{total} people were each asked their favourite sport. The table shows "
            "the results.",
            parts=[
                mk_part(label="a", prompt="Work out the angle for each sport.",
                        marks=2, answer=ans,
                        working=f"360° ÷ {total} = {per}° per person; "
                        + ", ".join(f"{freqs[i]}×{per} = {angles[i]}°" for i in range(4)),
                        mark_scheme=[_M1(f"for 360 ÷ {total} (= {per}) or one correct angle"),
                                     _A1("all four angles correct", ans)]),
                mk_part(label="b", prompt="Draw an accurate pie chart for this information.",
                        marks=1, answer="Sectors drawn with the angles from part (a).",
                        working="Measure each angle from the drawn radius with a protractor.",
                        mark_scheme=[_B1("a fully correct pie chart (± 2°)")]),
            ],
            diagram=_dia(SD.blank_pie_svg(), "A blank circle to construct a pie chart on.",
                         plot_grid=True),
            table=table, ao="AO2")
    raise RuntimeError("construct-pie-chart generator failed.")
