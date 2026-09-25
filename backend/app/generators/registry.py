"""Generator registry — the catalogue of question archetypes.

Each archetype declares its classification (strand / topic / spec ref / grade
band / marks / calculator requirement) alongside its builder. From this single
list we derive: the `/topics` picker, the paper assembler's candidate pool, and
the back-compatible single-question `/generate` lookup.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..schema import GenerateRequest, Item
from .algebra import (
    build_algebraic_fractions,
    build_algfrac_quadratic,
    build_chained_proportion,
    build_completing_square,
    build_functions,
    build_nth_term,
    build_quadratic_expression,
    build_quadratic_sequence,
    build_simultaneous,
)
from .algebra_more import (
    build_changing_subject,
    build_factorise_hard,
    build_forming_equations,
    build_function_machines,
    build_inequalities,
    build_iteration,
    build_quadratic_formula,
    build_quadratic_simultaneous,
    build_rearrange_hard,
    build_simplify_algebra,
    build_solving_quadratics,
    build_substitution,
)
from .basics import (
    build_fraction_arithmetic,
    build_linear_equation,
    build_share_ratio,
)
from .geometry import (
    build_polygon_angles,
    build_right_triangle_trig,
    build_sector,
    build_similar_shapes,
    build_sine_cosine_rule,
    build_volume,
)
from .foundation import (
    build_add_subtract,
    build_bidmas,
    build_calculation_problems,
    build_multiply_divide,
    build_negative_numbers,
    build_place_value,
    build_time_calc,
)
from .geometry_more import (
    build_angle_facts,
    build_arc_length,
    build_area_perimeter,
    build_bearings,
    build_circle_measures,
    build_circle_theorems,
    build_congruent_triangles,
    build_enlargement,
    build_exact_trig,
    build_parallel_angles,
    build_pythagoras_3d,
    build_scale_drawings,
    build_spheres_cones,
    build_surface_area,
    build_transformations,
    build_triangle_area,
    build_vectors,
    build_similar_area_volume,
)
from .graphs import (
    build_conversion_graphs,
    build_coordinates,
    build_cubic_reciprocal,
    build_distance_time,
    build_equation_of_line,
    build_gradient,
    build_inequalities_graph,
    build_linear_graphs,
    build_parallel_perpendicular,
    build_quadratic_graphs,
    build_simultaneous_graph,
    build_velocity_time,
)
from .number import (
    build_index_problem,
    build_indices,
    build_percentages,
    build_recurring_decimal,
    build_standard_form,
    build_surds,
)
from .number_ratio import (
    build_best_buy,
    build_bounds,
    build_compound_interest,
    build_compound_measures,
    build_error_intervals,
    build_estimating,
    build_exchange_rates,
    build_fdp,
    build_fraction_of_amount,
    build_hcf_lcm,
    build_proportion,
    build_rounding,
)
from .probability import (
    build_conditional_probability,
    build_frequency_trees,
    build_probability,
    build_probability_equation,
    build_probability_trees,
    build_product_rule,
    build_sample_space,
    build_venn_diagrams,
)
from .pythagoras import build_pythagoras_item
from .remaining import (
    build_algebraic_proof,
    build_circle_theorem_proof,
    build_loci_construction,
    build_ratio_as_fraction,
    build_simplify_ratio,
    build_trig_exp_graphs,
    build_unit_conversion,
    build_vectors_proof,
    build_writing_expression,
)
from .statistics import (
    build_averages,
    build_averages_frequency,
    build_bar_charts,
    build_box_plots,
    build_cumulative_frequency,
    build_frequency_polygons,
    build_histograms,
    build_pictograms,
    build_pie_charts,
    build_scatter_graphs,
    build_stem_leaf,
    build_two_way_tables,
)

Generator = Callable[[GenerateRequest], Item]

# Display order for strands in the topic picker.
STRAND_ORDER = [
    "Number",
    "Algebra",
    "Ratio & proportion",
    "Geometry & measures",
    "Probability",
    "Statistics",
]


@dataclass(frozen=True)
class ArchetypeSpec:
    archetype: str
    topic: str
    topic_slug: str
    strand: str
    spec_ref: str
    grade_band: str
    typical_marks: int
    requires_calculator: bool  # if True, excluded from non-calculator papers
    build: Generator


# Phase N: past-paper-coverage additions (styles found missing vs the MathsGenie bank).
from .algebra import build_expand_triple
from .algebra_more import build_quadratic_inequalities
from .graphs import (
    build_circle_tangent,
    build_matching_graphs,
    build_quadratic_features,
    build_transforming_graphs,
    build_vt_curved,
    build_vt_trapezium,
)
from .number_ratio import build_capture_recapture
from .probability import build_systematic_listing
from .statistics import build_construct_pie_chart
from .geometry_more import build_plans_elevations


ARCHETYPES: list[ArchetypeSpec] = [
    ArchetypeSpec(
        archetype="fraction-arithmetic",
        topic="Fractions",
        topic_slug="fractions",
        strand="Number",
        spec_ref="N8",
        grade_band="3-4",
        typical_marks=3,
        requires_calculator=False,
        build=build_fraction_arithmetic,
    ),
    ArchetypeSpec(
        archetype="linear-equation",
        topic="Linear equations",
        topic_slug="linear-equations",
        strand="Algebra",
        spec_ref="A17",
        grade_band="3-4",
        typical_marks=2,
        requires_calculator=False,
        build=build_linear_equation,
    ),
    ArchetypeSpec(
        archetype="share-ratio",
        topic="Ratio",
        topic_slug="ratio",
        strand="Ratio & proportion",
        spec_ref="R5",
        grade_band="3-4",
        typical_marks=3,
        requires_calculator=False,
        build=build_share_ratio,
    ),
    ArchetypeSpec(
        archetype="pythagoras-hypotenuse",
        topic="Pythagoras' theorem",
        topic_slug="pythagoras",
        strand="Geometry & measures",
        spec_ref="G20",
        grade_band="4-6",
        typical_marks=3,
        requires_calculator=False,
        build=build_pythagoras_item,
    ),
    ArchetypeSpec(
        archetype="pythagoras-shorter-side",
        topic="Pythagoras' theorem",
        topic_slug="pythagoras",
        strand="Geometry & measures",
        spec_ref="G20",
        grade_band="4-6",
        typical_marks=3,
        requires_calculator=False,
        build=build_pythagoras_item,
    ),
    # --- Phase D: broader library across the strands a real paper leans on --- #
    ArchetypeSpec(
        archetype="standard-form",
        topic="Standard form",
        topic_slug="standard-form",
        strand="Number",
        spec_ref="N9",
        grade_band="5-7",
        typical_marks=2,
        requires_calculator=False,
        build=build_standard_form,
    ),
    ArchetypeSpec(
        archetype="indices",
        topic="Indices",
        topic_slug="indices",
        strand="Number",
        spec_ref="N7",
        grade_band="5-8",
        typical_marks=2,
        requires_calculator=False,
        build=build_indices,
    ),
    ArchetypeSpec(
        archetype="expand-quadratic",
        topic="Quadratic expressions",
        topic_slug="quadratics",
        strand="Algebra",
        spec_ref="A4",
        grade_band="5-7",
        typical_marks=2,
        requires_calculator=False,
        build=build_quadratic_expression,
    ),
    ArchetypeSpec(
        archetype="factorise-quadratic",
        topic="Quadratic expressions",
        topic_slug="quadratics",
        strand="Algebra",
        spec_ref="A4",
        grade_band="5-7",
        typical_marks=2,
        requires_calculator=False,
        build=build_quadratic_expression,
    ),
    ArchetypeSpec(
        archetype="nth-term",
        topic="Sequences (nth term)",
        topic_slug="sequences",
        strand="Algebra",
        spec_ref="A25",
        grade_band="4-6",
        typical_marks=2,
        requires_calculator=False,
        build=build_nth_term,
    ),
    ArchetypeSpec(
        archetype="percentage-change",
        topic="Percentages",
        topic_slug="percentages",
        strand="Ratio & proportion",
        spec_ref="R9",
        grade_band="4-6",
        typical_marks=3,
        requires_calculator=False,
        build=build_percentages,
    ),
    ArchetypeSpec(
        archetype="reverse-percentage",
        topic="Percentages",
        topic_slug="percentages",
        strand="Ratio & proportion",
        spec_ref="R9",
        grade_band="4-6",
        typical_marks=2,  # real Edexcel reverse-percentage is a 2-mark question
        requires_calculator=False,
        build=build_percentages,
    ),
    ArchetypeSpec(
        archetype="polygon-interior-angle",
        topic="Angles in polygons",
        topic_slug="angles",
        strand="Geometry & measures",
        spec_ref="G3",
        grade_band="4-6",
        typical_marks=3,
        requires_calculator=False,
        build=build_polygon_angles,
    ),
    ArchetypeSpec(
        archetype="polygon-sides",
        topic="Angles in polygons",
        topic_slug="angles",
        strand="Geometry & measures",
        spec_ref="G3",
        grade_band="4-6",
        typical_marks=3,
        requires_calculator=False,
        build=build_polygon_angles,
    ),
    ArchetypeSpec(
        archetype="volume",
        topic="Volume",
        topic_slug="volume",
        strand="Geometry & measures",
        spec_ref="G17",
        grade_band="4-6",
        typical_marks=3,
        requires_calculator=False,
        build=build_volume,
    ),
    # --- Phase F: grade 8-9 archetypes (several with diagrams) --- #
    ArchetypeSpec(
        archetype="surds",
        topic="Surds",
        topic_slug="surds",
        strand="Number",
        spec_ref="N8",
        grade_band="7-9",
        typical_marks=2,
        requires_calculator=False,
        build=build_surds,
    ),
    ArchetypeSpec(
        archetype="algebraic-fractions",
        topic="Algebraic fractions",
        topic_slug="algebraic-fractions",
        strand="Algebra",
        spec_ref="A4",
        grade_band="7-9",
        typical_marks=2,
        requires_calculator=False,
        build=build_algebraic_fractions,
    ),
    ArchetypeSpec(
        archetype="quadratic-sequence",
        topic="Quadratic sequences",
        topic_slug="quadratic-sequences",
        strand="Algebra",
        spec_ref="A25",
        grade_band="7-9",
        typical_marks=3,
        requires_calculator=False,
        build=build_quadratic_sequence,
    ),
    ArchetypeSpec(
        archetype="simultaneous-equations",
        topic="Simultaneous equations",
        topic_slug="simultaneous-equations",
        strand="Algebra",
        spec_ref="A19",
        grade_band="6-8",
        typical_marks=3,
        requires_calculator=False,
        build=build_simultaneous,
    ),
    ArchetypeSpec(
        archetype="completing-square",
        topic="Completing the square",
        topic_slug="completing-square",
        strand="Algebra",
        spec_ref="A18",
        grade_band="7-9",
        typical_marks=3,
        requires_calculator=False,
        build=build_completing_square,
    ),
    ArchetypeSpec(
        archetype="functions",
        topic="Functions",
        topic_slug="functions",
        strand="Algebra",
        spec_ref="A7",
        grade_band="7-9",
        typical_marks=5,
        requires_calculator=False,
        build=build_functions,
    ),
    ArchetypeSpec(
        archetype="sector-area",
        topic="Sector area & arc length",
        topic_slug="sector",
        strand="Geometry & measures",
        spec_ref="G18",
        grade_band="5-7",
        typical_marks=5,
        requires_calculator=False,
        build=build_sector,
    ),
    ArchetypeSpec(
        archetype="right-triangle-trig",
        topic="Trigonometry",
        topic_slug="trigonometry",
        strand="Geometry & measures",
        spec_ref="G20",
        grade_band="5-7",
        typical_marks=3,
        requires_calculator=True,  # arbitrary-angle trig needs a calculator
        build=build_right_triangle_trig,
    ),
    ArchetypeSpec(
        archetype="sine-cosine-rule",
        topic="Sine & cosine rule",
        topic_slug="sine-cosine-rule",
        strand="Geometry & measures",
        spec_ref="G22",
        grade_band="7-9",
        typical_marks=3,
        requires_calculator=True,
        build=build_sine_cosine_rule,
    ),
    ArchetypeSpec(
        archetype="similar-shapes",
        topic="Similar shapes",
        topic_slug="similar-shapes",
        strand="Ratio & proportion",
        spec_ref="R12",
        grade_band="5-7",
        typical_marks=3,
        requires_calculator=False,
        build=build_similar_shapes,
    ),
    # --- Phase G: Statistics strand --- #
    ArchetypeSpec("averages", "Averages", "averages", "Statistics", "S4", "2-3", 5, False, build_averages),
    ArchetypeSpec("averages-frequency", "Averages from a frequency table", "averages-frequency", "Statistics", "S4", "4-5", 3, False, build_averages_frequency),
    ArchetypeSpec("bar-charts", "Bar charts", "bar-charts", "Statistics", "S2", "2-3", 2, False, build_bar_charts),
    ArchetypeSpec("pictograms", "Pictograms", "pictograms", "Statistics", "S2", "1-2", 2, False, build_pictograms),
    ArchetypeSpec("pie-charts", "Pie charts", "pie-charts", "Statistics", "S3", "2-3", 2, False, build_pie_charts),
    ArchetypeSpec("stem-leaf", "Stem and leaf", "stem-leaf", "Statistics", "S2", "2-3", 3, False, build_stem_leaf),
    ArchetypeSpec("frequency-polygons", "Frequency polygons", "frequency-polygons", "Statistics", "S2", "2-4", 2, False, build_frequency_polygons),
    ArchetypeSpec("two-way-tables", "Two-way tables", "two-way-tables", "Statistics", "S5", "3-4", 2, False, build_two_way_tables),
    ArchetypeSpec("scatter-graphs", "Scatter graphs", "scatter-graphs", "Statistics", "S6", "3-5", 2, False, build_scatter_graphs),
    ArchetypeSpec("cumulative-frequency", "Cumulative frequency", "cumulative-frequency", "Statistics", "S5", "5-7", 8, False, build_cumulative_frequency),
    ArchetypeSpec("box-plots", "Box plots", "box-plots", "Statistics", "S5", "5-7", 3, False, build_box_plots),
    ArchetypeSpec("histograms", "Histograms", "histograms", "Statistics", "S3", "6-8", 2, False, build_histograms),
    # --- Phase G: Probability strand --- #
    ArchetypeSpec("probability", "Probability", "probability", "Probability", "P1", "2-4", 3, False, build_probability),
    ArchetypeSpec("sample-space", "Sample space", "sample-space", "Probability", "P2", "2-3", 2, False, build_sample_space),
    ArchetypeSpec("frequency-trees", "Frequency trees", "frequency-trees", "Probability", "P3", "3-4", 3, False, build_frequency_trees),
    ArchetypeSpec("probability-trees", "Probability trees", "probability-trees", "Probability", "P4", "4-6", 5, False, build_probability_trees),
    ArchetypeSpec("venn-diagrams", "Venn diagrams", "venn-diagrams", "Probability", "P6", "4-6", 3, False, build_venn_diagrams),
    ArchetypeSpec("product-rule", "Product rule for counting", "product-rule", "Probability", "P8", "5-7", 2, False, build_product_rule),
    ArchetypeSpec("conditional-probability", "Conditional probability", "conditional-probability", "Probability", "P9", "6-8", 2, False, build_conditional_probability),
    # --- Phase G: top-band stretch (grade 8-9) --- #
    ArchetypeSpec("recurring-decimal", "Recurring decimals", "recurring-decimals", "Number", "N10", "7-8", 4, False, build_recurring_decimal),
    ArchetypeSpec("index-problem", "Indices", "indices", "Number", "N7", "7-9", 3, False, build_index_problem),
    ArchetypeSpec("algfrac-quadratic", "Solving equations (surd form)", "algfrac-quadratic", "Algebra", "A18", "8-9", 4, False, build_algfrac_quadratic),
    ArchetypeSpec("chained-proportion", "Direct & inverse proportion", "chained-proportion", "Ratio & proportion", "R13", "8-9", 4, False, build_chained_proportion),
    ArchetypeSpec("probability-equation", "Probability (form an equation)", "probability-equation", "Probability", "P7", "8-9", 4, False, build_probability_equation),
    # --- Phase H: Graphs & coordinate geometry --- #
    ArchetypeSpec("coordinates", "Coordinates", "coordinates", "Geometry & measures", "G11", "1-3", 2, False, build_coordinates),
    ArchetypeSpec("linear-graphs", "Linear graphs", "linear-graphs", "Algebra", "A9", "2-4", 2, False, build_linear_graphs),
    ArchetypeSpec("gradient", "Gradient of a line", "gradient", "Algebra", "A10", "4-5", 2, False, build_gradient),
    ArchetypeSpec("equation-of-line", "Equation of a line", "equation-of-line", "Algebra", "A10", "5-6", 3, False, build_equation_of_line),
    ArchetypeSpec("parallel-perpendicular", "Parallel & perpendicular lines", "parallel-perpendicular", "Algebra", "A10", "6-7", 2, False, build_parallel_perpendicular),
    ArchetypeSpec("quadratic-graphs", "Quadratic graphs", "quadratic-graphs", "Algebra", "A12", "4-6", 3, False, build_quadratic_graphs),
    ArchetypeSpec("cubic-reciprocal", "Cubic & reciprocal graphs", "cubic-reciprocal", "Algebra", "A12", "5-6", 2, False, build_cubic_reciprocal),
    ArchetypeSpec("simultaneous-graph", "Simultaneous equations (graphical)", "simultaneous-graph", "Algebra", "A19", "4-6", 2, False, build_simultaneous_graph),
    ArchetypeSpec("distance-time", "Distance–time graphs", "distance-time", "Ratio & proportion", "R14", "4-5", 2, False, build_distance_time),
    ArchetypeSpec("velocity-time", "Velocity–time graphs", "velocity-time", "Ratio & proportion", "R15", "7-9", 3, False, build_velocity_time),
    ArchetypeSpec("conversion-graphs", "Conversion graphs", "conversion-graphs", "Ratio & proportion", "R11", "3-4", 2, False, build_conversion_graphs),
    ArchetypeSpec("inequalities-graph", "Inequalities on a graph", "inequalities-graph", "Algebra", "A22", "5-7", 2, False, build_inequalities_graph),
    # --- Phase I: Number & ratio quick wins --- #
    ArchetypeSpec("rounding", "Rounding", "rounding", "Number", "N15", "1-3", 3, False, build_rounding),
    ArchetypeSpec("estimating", "Estimating", "estimating", "Number", "N14", "3-4", 3, False, build_estimating),
    ArchetypeSpec("error-intervals", "Error intervals", "error-intervals", "Number", "N15", "3-5", 2, False, build_error_intervals),
    ArchetypeSpec("bounds", "Bounds", "bounds", "Number", "N15", "6-8", 3, True, build_bounds),
    ArchetypeSpec("hcf-lcm", "Prime factors, HCF & LCM", "hcf-lcm", "Number", "N4", "3-5", 5, False, build_hcf_lcm),
    ArchetypeSpec("fdp", "Fractions, decimals & percentages", "fdp", "Number", "N10", "2-3", 2, False, build_fdp),
    ArchetypeSpec("fraction-of-amount", "Fraction of an amount", "fraction-of-amount", "Number", "N8", "2-3", 2, False, build_fraction_of_amount),
    ArchetypeSpec("best-buy", "Best buy", "best-buy", "Ratio & proportion", "R9", "3-4", 3, False, build_best_buy),
    ArchetypeSpec("exchange-rates", "Exchange rates", "exchange-rates", "Ratio & proportion", "R9", "3-4", 2, False, build_exchange_rates),
    ArchetypeSpec("compound-measures", "Speed & density", "compound-measures", "Ratio & proportion", "R11", "4-6", 2, False, build_compound_measures),
    ArchetypeSpec("proportion", "Direct & inverse proportion", "proportion", "Ratio & proportion", "R10", "4-6", 5, False, build_proportion),
    ArchetypeSpec("compound-interest", "Compound interest & depreciation", "compound-interest", "Ratio & proportion", "R16", "4-6", 3, True, build_compound_interest),
    # --- Phase J: Algebra gaps (complete the strand) --- #
    ArchetypeSpec("simplify-algebra", "Simplifying algebra", "simplify-algebra", "Algebra", "A4", "2-3", 2, False, build_simplify_algebra),
    ArchetypeSpec("substitution", "Substitution", "substitution", "Algebra", "A2", "2-4", 2, False, build_substitution),
    ArchetypeSpec("function-machines", "Function machines", "function-machines", "Algebra", "A5", "2-3", 3, False, build_function_machines),
    ArchetypeSpec("forming-equations", "Forming & solving equations", "forming-equations", "Algebra", "A21", "3-5", 3, False, build_forming_equations),
    ArchetypeSpec("inequalities", "Inequalities", "inequalities", "Algebra", "A22", "4-5", 3, False, build_inequalities),
    ArchetypeSpec("changing-subject", "Changing the subject", "changing-subject", "Algebra", "A5", "5-6", 2, False, build_changing_subject),
    ArchetypeSpec("solving-quadratics", "Solving quadratics", "solving-quadratics", "Algebra", "A18", "5-6", 3, False, build_solving_quadratics),
    ArchetypeSpec("quadratic-formula", "Quadratic formula", "quadratic-formula", "Algebra", "A18", "6-8", 3, True, build_quadratic_formula),
    ArchetypeSpec("factorise-hard", "Factorising harder quadratics", "factorise-hard", "Algebra", "A4", "6-8", 2, False, build_factorise_hard),
    ArchetypeSpec("rearrange-hard", "Rearranging harder formulae", "rearrange-hard", "Algebra", "A5", "7-8", 3, False, build_rearrange_hard),
    ArchetypeSpec("iteration", "Iteration", "iteration", "Algebra", "A20", "7-8", 3, True, build_iteration),
    ArchetypeSpec("quadratic-simultaneous", "Quadratic simultaneous equations", "quadratic-simultaneous", "Algebra", "A19", "8-9", 5, False, build_quadratic_simultaneous),
    # --- Phase K: Geometry gaps --- #
    ArchetypeSpec("area-perimeter", "Area & perimeter", "area-perimeter", "Geometry & measures", "G16", "2-4", 5, False, build_area_perimeter),
    ArchetypeSpec("angle-facts", "Angle facts", "angle-facts", "Geometry & measures", "G3", "2-3", 2, False, build_angle_facts),
    ArchetypeSpec("parallel-angles", "Angles in parallel lines", "parallel-angles", "Geometry & measures", "G3", "4-5", 2, False, build_parallel_angles),
    ArchetypeSpec("circle-measures", "Area & circumference of circles", "circle-measures", "Geometry & measures", "G17", "3-5", 4, False, build_circle_measures),
    ArchetypeSpec("surface-area", "Surface area", "surface-area", "Geometry & measures", "G17", "4-6", 3, False, build_surface_area),
    ArchetypeSpec("spheres-cones", "Spheres & cones", "spheres-cones", "Geometry & measures", "G17", "5-7", 3, False, build_spheres_cones),
    ArchetypeSpec("arc-length", "Arc length & sector perimeter", "arc-length", "Geometry & measures", "G18", "5-7", 3, False, build_arc_length),
    ArchetypeSpec("transformations", "Transformations", "transformations", "Geometry & measures", "G7", "3-6", 2, False, build_transformations),
    ArchetypeSpec("enlargement", "Enlargement", "enlargement", "Geometry & measures", "G7", "5-7", 3, False, build_enlargement),
    ArchetypeSpec("bearings", "Bearings", "bearings", "Geometry & measures", "G15", "4-5", 2, False, build_bearings),
    ArchetypeSpec("vectors", "Vectors", "vectors", "Geometry & measures", "G25", "5-7", 2, False, build_vectors),
    ArchetypeSpec("exact-trig", "Exact trig values", "exact-trig", "Geometry & measures", "G21", "5-6", 2, False, build_exact_trig),
    ArchetypeSpec("congruent-triangles", "Congruent triangles", "congruent-triangles", "Geometry & measures", "G5", "5-7", 2, False, build_congruent_triangles),
    ArchetypeSpec("circle-theorems", "Circle theorems", "circle-theorems", "Geometry & measures", "G10", "6-8", 2, False, build_circle_theorems),
    ArchetypeSpec("pythagoras-3d", "3D Pythagoras", "pythagoras-3d", "Geometry & measures", "G20", "6-8", 3, True, build_pythagoras_3d),
    ArchetypeSpec("triangle-area", "Area of any triangle", "triangle-area", "Geometry & measures", "G16", "6-8", 3, True, build_triangle_area),
    ArchetypeSpec("scale-drawings", "Scale drawings & maps", "scale-drawings", "Ratio & proportion", "R6", "3-4", 3, False, build_scale_drawings),
    ArchetypeSpec("similar-area-volume", "Similar shapes (area & volume)", "similar-area-volume", "Ratio & proportion", "R12", "6-8", 3, False, build_similar_area_volume),
    # --- Phase L: Foundation Grade 1-2 arithmetic --- #
    ArchetypeSpec("place-value", "Place value", "place-value", "Number", "N1", "1-2", 2, False, build_place_value),
    ArchetypeSpec("negative-numbers", "Negative numbers", "negative-numbers", "Number", "N2", "1-2", 3, False, build_negative_numbers),
    ArchetypeSpec("bidmas", "BIDMAS", "bidmas", "Number", "N3", "1-2", 2, False, build_bidmas),
    ArchetypeSpec("time-calc", "Time", "time-calc", "Number", "N13", "1-2", 2, False, build_time_calc),
    ArchetypeSpec("add-subtract", "Addition & subtraction", "add-subtract", "Number", "N2", "1-2", 2, False, build_add_subtract),
    ArchetypeSpec("multiply-divide", "Multiplication & division", "multiply-divide", "Number", "N2", "2-3", 4, False, build_multiply_divide),
    ArchetypeSpec("calculation-problems", "Calculation problems", "calculation-problems", "Number", "N2", "2-3", 3, False, build_calculation_problems),
    # --- Phase M: loci, proofs, trig/exp graphs + minor gaps (spec-complete) --- #
    ArchetypeSpec("loci-construction", "Loci & construction", "loci-construction", "Geometry & measures", "G2", "4-6", 2, False, build_loci_construction),
    ArchetypeSpec("algebraic-proof", "Algebraic proof", "algebraic-proof", "Algebra", "A6", "7-9", 3, False, build_algebraic_proof),
    ArchetypeSpec("vectors-proof", "Vectors proof", "vectors-proof", "Geometry & measures", "G25", "7-9", 3, False, build_vectors_proof),
    ArchetypeSpec("circle-theorem-proof", "Proof of circle theorems", "circle-theorem-proof", "Geometry & measures", "G10", "8-9", 4, False, build_circle_theorem_proof),
    ArchetypeSpec("trig-exp-graphs", "Trig & exponential graphs", "trig-exp-graphs", "Algebra", "A12", "6-8", 2, False, build_trig_exp_graphs),
    ArchetypeSpec("writing-expression", "Writing an expression", "writing-expression", "Algebra", "A1", "2-3", 2, False, build_writing_expression),
    ArchetypeSpec("simplify-ratio", "Writing & simplifying ratio", "simplify-ratio", "Ratio & proportion", "R5", "2-4", 1, False, build_simplify_ratio),
    ArchetypeSpec("unit-conversion", "Conversions & units", "unit-conversion", "Number", "N13", "2-4", 2, False, build_unit_conversion),
    ArchetypeSpec("ratio-as-fraction", "Ratio as a fraction", "ratio-as-fraction", "Ratio & proportion", "R7", "4-5", 2, False, build_ratio_as_fraction),
    # --- Phase N: past-paper-coverage additions (missing MathsGenie styles) --- #
    ArchetypeSpec("expand-triple-brackets", "Quadratic expressions", "quadratics", "Algebra", "A4", "7-9", 3, False, build_expand_triple),
    ArchetypeSpec("quadratic-inequalities", "Quadratic inequalities", "quadratic-inequalities", "Algebra", "A22", "7-9", 3, False, build_quadratic_inequalities),
    ArchetypeSpec("circle-tangent", "Equation of a tangent", "circle-tangent", "Algebra", "A16", "8-9", 3, False, build_circle_tangent),
    ArchetypeSpec("quadratic-graph-features", "Quadratic graphs", "quadratic-graphs", "Algebra", "A12", "4-6", 3, False, build_quadratic_features),
    ArchetypeSpec("vt-trapezium", "Velocity–time (trapezium)", "vt-trapezium", "Ratio & proportion", "R15", "7-9", 4, False, build_vt_trapezium),
    ArchetypeSpec("capture-recapture", "Capture–recapture", "capture-recapture", "Ratio & proportion", "R7", "4-6", 3, False, build_capture_recapture),
    ArchetypeSpec("systematic-listing", "Systematic listing", "systematic-listing", "Probability", "P8", "4-6", 3, False, build_systematic_listing),
    ArchetypeSpec("construct-pie-chart", "Constructing pie charts", "construct-pie-chart", "Statistics", "S3", "3-5", 3, False, build_construct_pie_chart),
    ArchetypeSpec("plans-elevations", "Plans & elevations", "plans-elevations", "Geometry & measures", "G13", "4-6", 3, False, build_plans_elevations),
    ArchetypeSpec("transforming-graphs", "Transforming graphs", "transforming-graphs", "Algebra", "A13", "7-9", 2, False, build_transforming_graphs),
    ArchetypeSpec("matching-graphs", "Matching real-life graphs", "matching-graphs", "Ratio & proportion", "R14", "3-5", 1, False, build_matching_graphs),
    ArchetypeSpec("vt-curved", "Velocity–time (curved)", "vt-curved", "Ratio & proportion", "R15", "7-9", 4, True, build_vt_curved),
]

_BY_ARCHETYPE: dict[str, ArchetypeSpec] = {s.archetype: s for s in ARCHETYPES}

# --------------------------------------------------------------------------- #
# Reasoning-step tags (Task 5: marks must be earned by structure)
# --------------------------------------------------------------------------- #
# A question's marks may not exceed the work in it: marks <= steps + parts - 1,
# where `steps` is the count of genuinely distinct reasoning operations. Every
# archetype's mark scheme is built to award exactly one mark per named operation
# (see the M-mark audit), so its reasoning-step count equals its mark count —
# except where a re-audit found a padded mark. `_STEPS` records those exceptions;
# everything else defaults to its mark count. (parallel-perpendicular was the one
# inflated case found — its padding "use the point" mark was removed, taking it
# from 3 marks to 2, so steps and marks now agree and it needs no override here.)
#
# The entries below are archetypes with an optional extra part, whose fullest
# variant does more work than their single-part `typical_marks` implies; steps is
# their operation count at that fullest variant.
_STEPS: dict[str, int] = {
    "fraction-arithmetic": 4,  # common denom, combine, simplify (+ spot-the-error)
    "share-ratio": 4,          # total parts, one part, scale each (+ the fraction)
    "nth-term": 4,             # differences, the rule (+ is-a-term-in-it check)
    "percentage-change": 4,    # find %, apply it (+ the reasoning follow-up)
    "standard-form": 3,        # write in standard form + the calculation
    "indices": 3,              # evaluate each power and combine
    "expand-quadratic": 3,     # expand each product and collect
}


def reasoning_steps(archetype: str) -> int:
    """The count of distinct reasoning operations a question requires."""
    spec = _BY_ARCHETYPE.get(archetype)
    if spec is None:
        return 1
    return _STEPS.get(archetype, spec.typical_marks)


DEFAULT_ARCHETYPE = "pythagoras-hypotenuse"


def get_generator(archetype: str | None) -> Generator:
    """Return the requested generator, or the default if unset/unknown."""
    spec = _BY_ARCHETYPE.get(archetype or DEFAULT_ARCHETYPE)
    return spec.build if spec else build_pythagoras_item


def specs_for_topic(topic_slug: str, *, paper_calculator: bool) -> list[ArchetypeSpec]:
    """Archetypes under a topic, filtered for the paper's calculator setting."""
    return [
        s
        for s in ARCHETYPES
        if s.topic_slug == topic_slug
        and (paper_calculator or not s.requires_calculator)
    ]


def topics_catalog() -> list[dict]:
    """Pickable topics grouped by strand, each with an archetype count.

    The UI only ever offers topics we can actually generate.
    """
    # Collapse archetypes into topics (a topic may have several archetypes).
    topics: dict[str, dict] = {}
    for s in ARCHETYPES:
        t = topics.setdefault(
            s.topic_slug,
            {
                "slug": s.topic_slug,
                "name": s.topic,
                "strand": s.strand,
                "spec_ref": s.spec_ref,
                "grade_band": s.grade_band,
                "typical_marks": s.typical_marks,
                "archetype_count": 0,
                "requires_calculator": True,
            },
        )
        t["archetype_count"] += 1
        # A topic is non-calc-friendly if ANY of its archetypes is.
        if not s.requires_calculator:
            t["requires_calculator"] = False

    # Group by strand in display order.
    grouped: list[dict] = []
    for strand in STRAND_ORDER:
        in_strand = sorted(
            (t for t in topics.values() if t["strand"] == strand),
            key=lambda t: t["name"],
        )
        if in_strand:
            grouped.append({"strand": strand, "topics": in_strand})
    return grouped
