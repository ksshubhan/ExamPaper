"""Every diagram primitive must return well-formed, theme-safe SVG."""

import unittest
import xml.dom.minidom as minidom

from app.generators import diagrams as D
from app.generators import stats_diagrams as S
from app.generators import geometry_diagrams as G
from app.generators.graph_diagrams import (
    function_sketch_svg,
    graph_panels_svg,
    graph_svg,
    speed_time_svg,
)

CASES = [
    D.right_triangle_svg(base_label="8 cm", vert_label="6 cm", hyp_label="x"),
    D.regular_polygon_svg(7),
    D.circle_sector_svg(radius_label="6 cm", theta=120),
    D.cylinder_svg(radius_label="3 cm", height_label="8 cm"),
    D.cuboid_svg(length_label="5 cm", width_label="4 cm", height_label="3 cm"),
    D.triangular_prism_svg(base_label="6 cm", height_label="4 cm", length_label="7 cm"),
    D.triangle_svg(side_bc="8 cm", side_ca="x", angle_a="37°", right_angle_at="B"),
    D.similar_triangles_svg(left_base="6 cm", right_base="15 cm", left_side="8 cm", right_side="x"),
    S.bar_chart_svg(["A", "B", "C"], [4, 7, 5]),
    S.pie_chart_svg(["R", "G", "B"], [3, 4, 5]),
    S.pictogram_svg(["Mon", "Tue"], [10, 15], key_value=5),
    S.histogram_svg([(0, 10, 2.0), (10, 30, 1.5), (30, 60, 0.5)], x_label="d"),
    S.box_plot_svg(5, 10, 14, 20, 28, axis_min=0, axis_max=30, label="Speed"),
    S.cumulative_frequency_svg([(10, 5), (20, 18), (30, 40), (40, 52), (50, 60)]),
    S.scatter_svg([(1, 2), (2, 3), (3, 3), (4, 5)], x_label="x", y_label="y"),
    S.frequency_polygon_svg([5, 15, 25, 35], [3, 8, 6, 2]),
    S.probability_tree_svg(stage1=("H", "T"), leaves=("H", "T"), p1=("0.6", "0.4"),
                           p2_top=("0.6", "0.4"), p2_bot=("0.6", "0.4")),
    S.venn2_svg(set_a="A", set_b="B", only_a="3", both="2", only_b="5", outside="4"),
    graph_svg(xrange=(-6, 6), yrange=(-6, 6),
              polylines=[{"points": [(-6, -4), (6, 8)], "label": "L"}],
              points=[(2, 5, "P", True)]),
    G.circle_svg(radius_label="7 cm"),
    G.compound_shape_svg(W=10, H=8, nw=4, nh=3),
    G.angle_facts_svg(kind="triangle", known=(50, 60)),
    G.parallel_lines_svg(known=72),
    G.sphere_svg(radius_label="5 cm"),
    G.cone_svg(radius_label="3 cm", height_label="8 cm", slant_label="l"),
    G.bearing_svg(bearing=70),
    G.circle_points_svg(points={"A": 200, "B": 340, "C": 90},
                        segments=[("O", "A"), ("O", "B"), ("C", "A"), ("C", "B")],
                        angle_labels=[("C", "40°"), ("O", "x°")]),
    G.loci_field_svg(points=[("A", 3, 4), ("B", 8, 4)]),
    # Phase N primitives (past-paper-style additions)
    speed_time_svg([(0, 0), (4, 12), (9, 12), (13, 0)],
                   guides=[(4, 12, "4", "12"), (9, 12, "9", ""), (13, 0, "T", "")]),
    function_sketch_svg(marked_label="P", opens_up=False),
    graph_panels_svg([{"points": [(0, 0), (1, 1)], "label": "A"},
                      {"points": [(0, 0), (0.4, 0.8), (0.7, 0.8), (1, 0)], "label": "B"},
                      {"points": [(0, 0), (0.3, 0.7), (1, 1)], "label": "C"},
                      {"points": [(0, 0), (0.5, 0), (1, 1)], "label": "D"}]),
    S.blank_pie_svg(),
]


class TestDiagrams(unittest.TestCase):
    def test_all_primitives_well_formed(self):
        for i, svg in enumerate(CASES):
            with self.subTest(case=i):
                minidom.parseString(svg)                    # valid XML
                self.assertTrue(svg.startswith("<svg") and svg.endswith("</svg>"))
                self.assertIn("currentColor", svg)          # theme-safe ink

    def test_bar_heights_encode_frequency(self):
        import re
        svg = S.bar_chart_svg(["A", "B", "C", "D"], [4, 8, 2, 6])
        heights = [float(h) for h in re.findall(r'<rect[^>]*height="([\d.]+)"', svg)]
        # bar heights must be proportional to the frequencies 4,8,2,6
        self.assertAlmostEqual(heights[1] / heights[0], 8 / 4, places=2)
        self.assertAlmostEqual(heights[2] / heights[0], 2 / 4, places=2)

    def test_sector_draws_true_central_angle_including_reflex(self):
        import re
        for theta in (60, 90, 240, 300):
            svg = D.circle_sector_svg(radius_label="5 cm", theta=theta)
            # printed label matches the angle the wedge was built from
            self.assertIn(f"{theta}°", svg)
            # the enclosed wedge takes its large-arc flag straight from theta:
            # a reflex angle (> 180) must be drawn as the MAJOR arc.
            m = re.search(
                r"M 150 150 L [\d.]+ [\d.]+ A [\d.]+ [\d.]+ 0 (\d) (\d)", svg)
            self.assertIsNotNone(m, f"wedge path not found for {theta}")
            self.assertEqual(m.group(1), "1" if theta > 180 else "0",
                             f"large-arc flag wrong for {theta}")

    def test_graph_grid_cells_are_square(self):
        import re
        # A labelled square must be the same size horizontally and vertically,
        # even when the x- and y-ranges (and steps) differ — otherwise the grid
        # squares come out as rectangles.
        cases = [
            dict(xrange=(-6, 6), yrange=(-6, 6)),                       # equal spans
            dict(xrange=(-5, 5), yrange=(-6, 10)),                      # taller y span
            dict(xrange=(0, 10), yrange=(0, 40), xstep=1, ystep=5),    # unequal steps
            dict(xrange=(-3, 3), yrange=(-9, 9), ystep=3),             # cubic layout
        ]
        for kw in cases:
            svg = graph_svg(polylines=[{"points": [(0, 0)]}], **kw)
            # Pull the gridline coordinates back out of the rendered SVG.
            vlines = sorted({float(x) for x in re.findall(
                r'<line x1="([\d.]+)" y1="[\d.]+" x2="\1" ', svg)})
            hlines = sorted({float(y) for y in re.findall(
                r'<line x1="[\d.]+" y1="([\d.]+)" x2="[\d.]+" y2="\1"', svg)})
            # A grid square's pixel size is the spacing of adjacent gridlines.
            # For the cells to be true squares it must be identical on both axes,
            # whatever the data ranges or steps.
            dx = min(b - a for a, b in zip(vlines, vlines[1:]))
            dy = min(b - a for a, b in zip(hlines, hlines[1:]))
            self.assertAlmostEqual(dx, dy, places=1,
                                   msg=f"non-square cells for {kw}")

    def test_regular_polygon_vertex_count(self):
        import re
        for n in (5, 6, 8, 9, 10, 12):
            svg = D.regular_polygon_svg(n)
            pts = re.search(r'points="([^"]+)"', svg).group(1).split()
            self.assertEqual(len(pts), n)


if __name__ == "__main__":
    unittest.main()
