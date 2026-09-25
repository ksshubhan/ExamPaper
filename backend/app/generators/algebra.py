"""Algebra-strand generators: quadratic expressions and nth-term sequences.

Deterministic from a seed, every answer re-derived/checked with sympy, an
Edexcel-style mark scheme. Pure-algebra items stay bare (that is the authentic
house style); the Phase E enrichment adds a harder triple-bracket expansion and
a multi-part 'is this a term?' reasoning follow-up for sequences.
"""

from __future__ import annotations

from random import Random

import sympy

from ..schema import GenerateRequest, Item, MarkSchemeStep
from .basics import _item, _seed, _sign
from .context import make_item, mk_part

_MAX_ATTEMPTS = 200

_x = sympy.Symbol("x")
_n = sympy.Symbol("n")
_SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def _quad_str(p: int, q: int) -> str:
    """Render x² + px + q with tidy signs and unit coefficients."""
    s = "x²"
    if p != 0:
        term = "x" if abs(p) == 1 else f"{abs(p)}x"
        s += f" + {term}" if p > 0 else f" - {term}"
    if q != 0:
        s += f" + {q}" if q > 0 else f" - {abs(q)}"
    return s


def _poly_in(expr: sympy.Expr, sym: sympy.Symbol, ch: str) -> str:
    """Render an expanded polynomial in `sym` (shown as `ch`), e.g. '2n² - 5n + 3'."""
    poly = sympy.Poly(expr, sym)
    deg = poly.degree()
    coeffs = poly.all_coeffs()
    out = ""
    for i, c in enumerate(coeffs):
        c = int(c)
        if c == 0:
            continue
        power = deg - i
        if power == 0:
            var = ""
        elif power == 1:
            var = ch
        else:
            var = ch + str(power).translate(_SUP)
        mag = abs(c)
        coeff_part = str(mag) if (var == "" or mag != 1) else ""
        token = coeff_part + var
        if out == "":
            out = ("-" if c < 0 else "") + token
        else:
            out += (" - " if c < 0 else " + ") + token
    return out or "0"


def _poly_str(expr: sympy.Expr) -> str:
    """Render an expanded polynomial in x like 'x³ + 2x² − 5x − 6'."""
    return _poly_in(expr, _x, "x")


# --------------------------------------------------------------------------- #
# Quadratic expressions: expand (double / triple bracket), or factorise  (A4)
# --------------------------------------------------------------------------- #
def _quad_variant(req: GenerateRequest) -> str | None:
    v = (req.variant or req.archetype or "").lower()
    if "factor" in v:
        return "factorise"
    if "expand" in v:
        return "expand"
    return None


def _bracket(coeff: int, const: int) -> str:
    """Render a linear bracket like '(2x - 3)' or '(x + 5)'."""
    lead = "x" if coeff == 1 else f"{coeff}x"
    return f"({lead} {_sign(const)})"


def build_quadratic_expression(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    variant = _quad_variant(req)
    for _ in range(_MAX_ATTEMPTS):
        v = variant or rng.choice(["expand", "factorise"])

        if v == "expand":
            shape = rng.choice(["double", "double", "nonmonic", "triple"])
            if shape == "triple":
                a, b, c = (rng.choice([i for i in range(-6, 7) if i != 0]) for _ in range(3))
                factors = [(1, a), (1, b), (1, c)]
                marks = 3
            elif shape == "nonmonic":
                p1, p2 = rng.randint(2, 4), rng.randint(2, 4)
                a = rng.choice([i for i in range(-6, 7) if i != 0])
                b = rng.choice([i for i in range(-6, 7) if i != 0])
                factors = [(p1, a), (p2, b)]
                marks = 2
            else:  # monic double
                a = rng.choice([i for i in range(-9, 10) if i != 0])
                b = rng.choice([i for i in range(-9, 10) if i != 0])
                if a > b:
                    a, b = b, a
                factors = [(1, a), (1, b)]
                marks = 2

            expr = sympy.Integer(1)
            for co, cn in factors:
                expr *= (co * _x + cn)
            expanded = sympy.expand(expr)
            answer = _poly_str(expanded)
            brackets = "".join(_bracket(co, cn) for co, cn in factors)
            return _item(
                req, seed, archetype="expand-quadratic",
                topic="Quadratic expressions", topic_slug="quadratics",
                strand="Algebra", spec_ref="A4",
                grade_band="6-8" if shape == "triple" else "5-7",
                marks=marks,
                stem=f"Expand and simplify  {brackets}",
                prompt="", answer=answer,
                working=f"{brackets} = {answer}",
                mark_scheme=_expand_ms(shape, answer),
            )

        # factorise x² + bx + c  ->  (x+a)(x+b)
        a = rng.choice([i for i in range(-9, 10) if i != 0])
        b = rng.choice([i for i in range(-9, 10) if i != 0])
        if a > b:
            a, b = b, a
        mid, const = a + b, a * b
        if mid == 0:  # difference of two squares — a different skill
            continue
        if sympy.expand((_x + a) * (_x + b)) != _x**2 + mid * _x + const:
            continue
        return _item(
            req, seed, archetype="factorise-quadratic",
            topic="Quadratic expressions", topic_slug="quadratics",
            strand="Algebra", spec_ref="A4", grade_band="5-7", marks=2,
            stem=f"Factorise  {_quad_str(mid, const)}",
            prompt="", answer=f"(x {_sign(a)})(x {_sign(b)})",
            working=(
                f"Two numbers with product {const} and sum {mid}: {a} and {b}\n"
                f"(x {_sign(a)})(x {_sign(b)})"
            ),
            mark_scheme=[
                MarkSchemeStep(
                    code="M1", mark_type="M",
                    description=f"for two numbers with product {const} and sum {mid}",
                    working=f"{a} and {b}",
                ),
                MarkSchemeStep(code="A1", mark_type="A", description="cao",
                               working=f"(x {_sign(a)})(x {_sign(b)})"),
            ],
        )
    raise RuntimeError("quadratic-expression generator failed to produce a valid item.")


def _expand_ms(shape: str, answer: str) -> list[MarkSchemeStep]:
    if shape == "triple":
        return [
            MarkSchemeStep(code="M1", mark_type="M",
                           description="for expanding two of the brackets correctly",
                           working=None),
            MarkSchemeStep(code="M1", mark_type="M",
                           description="for multiplying by the third bracket",
                           working=None),
            MarkSchemeStep(code="A1", mark_type="A", description="cao, simplified",
                           working=answer),
        ]
    return [
        MarkSchemeStep(code="M1", mark_type="M",
                       description="for expanding to give the correct terms",
                       working=None),
        MarkSchemeStep(code="A1", mark_type="A", description="cao, simplified",
                       working=answer),
    ]


# --------------------------------------------------------------------------- #
# Sequences: nth term (+ optional 'is X a term?' reasoning follow-up)  (A25)
# --------------------------------------------------------------------------- #
def _linear_term(d: int, c: int) -> str:
    coeff = "n" if d == 1 else ("-n" if d == -1 else f"{d}n")
    if c > 0:
        return f"{coeff} + {c}"
    if c < 0:
        return f"{coeff} - {abs(c)}"
    return coeff


def build_nth_term(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        d = rng.choice([i for i in range(-6, 10) if abs(i) >= 2])
        first = rng.randint(-8, 12)
        terms = [first + k * d for k in range(4)]
        c = first - d
        expr = d * _n + c
        if any(expr.subs(_n, k + 1) != terms[k] for k in range(4)):
            continue

        seq = ", ".join(str(t) for t in terms)
        nth = _linear_term(d, c)
        first_check = f"{d}×1 {_sign(c)} = {first}" if c != 0 else f"{d}×1 = {first}"
        stem = f"Here are the first four terms of an arithmetic sequence.\n{seq}"
        ms_a = [
            MarkSchemeStep(code="M1", mark_type="M",
                           description=f"for the common difference {d} (or {d}n seen)",
                           working=f"{d}n"),
            MarkSchemeStep(code="A1", mark_type="A", description="cao", working=nth),
        ]
        working_a = (
            f"Common difference = {d}\nnth term = {nth}   (check: {first_check})"
        )
        prompt_a = "Find an expression, in terms of n, for the nth term of the sequence."

        # For increasing sequences, ~50%: add (b) 'Is T a term?' with justification.
        if d > 0 and rng.random() < 0.5:
            want_yes = rng.random() < 0.5
            k = rng.randint(6, 20)
            target = d * k + c if want_yes else d * k + c + 1
            pos = sympy.Rational(target - c, d)
            is_term = pos.q == 1 and pos.p >= 1
            if want_yes and not is_term:
                continue
            if not want_yes and is_term:
                continue
            verdict = (
                f"Yes — it is term {int(pos)}" if is_term
                else f"No — ({target} − {c}) ÷ {d} is not a whole number"
            )
            work_b = (
                f"{d}n {_sign(c)} = {target}  →  n = ({target} − {c}) ÷ {d} = "
                + (f"{int(pos)}" if is_term else f"{float(pos):.2f}…")
            )
            part_a = mk_part(label="a", prompt=prompt_a, marks=2, answer=nth,
                             working=working_a, mark_scheme=ms_a)
            part_b = mk_part(
                label="b",
                prompt=f"Is {target} a term of the sequence? You must give a reason "
                f"for your answer.",
                marks=2, answer=verdict, working=work_b,
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description=f"for solving {nth} = {target} "
                                   f"(or ({target} − {c}) ÷ {d})",
                                   working=f"({target} − {c}) ÷ {d}"),
                    MarkSchemeStep(code="B1", mark_type="B",
                                   description="for the correct conclusion with a reason",
                                   working=None),
                ],
            )
            return make_item(
                req, seed, archetype="nth-term", topic="Sequences (nth term)",
                topic_slug="sequences", strand="Algebra", spec_ref="A25",
                grade_band="5-7", ao="AO2", stem=stem, parts=[part_a, part_b],
            )

        return _item(
            req, seed, archetype="nth-term", topic="Sequences (nth term)",
            topic_slug="sequences", strand="Algebra", spec_ref="A25",
            grade_band="4-6", marks=2, stem=stem, prompt=prompt_a,
            answer=nth, working=working_a, mark_scheme=ms_a,
        )
    raise RuntimeError("nth-term generator failed to produce a valid item.")


def _gx(c: int) -> str:
    return "x" if c == 1 else ("-x" if c == -1 else f"{c}x")


# --------------------------------------------------------------------------- #
# Algebraic fractions — simplify fully  (A4, grade 8)
# --------------------------------------------------------------------------- #
def build_algebraic_fractions(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        shape = rng.choice(["cancel", "dots"])
        if shape == "cancel":
            a = rng.choice([i for i in range(-6, 7) if i != 0])
            b = rng.choice([i for i in range(-6, 7) if i != 0])
            c = rng.choice([i for i in range(-6, 7) if i != 0])
            if len({a, b, c}) < 3:
                continue
            num, den = (_x + a) * (_x + b), (_x + a) * (_x + c)
            if sympy.simplify(sympy.cancel(num / den) - (_x + b) / (_x + c)) != 0:
                continue
            num_s, den_s = _quad_str(a + b, a * b), _quad_str(a + c, a * c)
            ans = f"(x {_sign(b)})/(x {_sign(c)})"
            working = (
                f"({num_s})/({den_s}) = (x {_sign(a)})(x {_sign(b)}) / "
                f"(x {_sign(a)})(x {_sign(c)})\n= {ans}"
            )
        else:  # difference of two squares over a common factor
            a = rng.randint(2, 7)
            num, den = _x**2 - a**2, _x**2 + a * _x
            if sympy.simplify(sympy.cancel(num / den) - (_x - a) / _x) != 0:
                continue
            num_s, den_s = _quad_str(0, -a * a), _quad_str(a, 0)
            ans = f"(x {_sign(-a)})/x"
            working = (
                f"({num_s})/({den_s}) = (x {_sign(-a)})(x {_sign(a)}) / x(x {_sign(a)})"
                f"\n= {ans}"
            )
        return _item(
            req, seed, archetype="algebraic-fractions", topic="Algebraic fractions",
            topic_slug="algebraic-fractions", strand="Algebra", spec_ref="A4",
            grade_band="7-9", marks=2,
            stem=f"Simplify fully  ({num_s})/({den_s})",
            prompt="", answer=ans, working=working,
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for factorising numerator and denominator",
                               working=None),
                MarkSchemeStep(code="A1", mark_type="A",
                               description="for the fully simplified fraction",
                               working=ans),
            ],
        )
    raise RuntimeError("algebraic-fractions generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Quadratic sequences — nth term an²+bn+c  (A25, grade 8)
# --------------------------------------------------------------------------- #
def build_quadratic_sequence(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        a = rng.choice([1, 1, 2, 3])
        b = rng.randint(-4, 5)
        c = rng.randint(-4, 6)
        expr = a * _n**2 + b * _n + c
        terms = [int(expr.subs(_n, k)) for k in range(1, 6)]
        d1 = [terms[i + 1] - terms[i] for i in range(4)]
        d2 = [d1[i + 1] - d1[i] for i in range(3)]
        if any(x != 2 * a for x in d2):
            continue
        nth = _poly_in(expr, _n, "n")
        seq = ", ".join(str(t) for t in terms)
        return _item(
            req, seed, archetype="quadratic-sequence",
            topic="Quadratic sequences", topic_slug="quadratic-sequences",
            strand="Algebra", spec_ref="A25", grade_band="7-9", marks=3,
            stem=f"Here are the first five terms of a quadratic sequence.\n{seq}",
            prompt="Find an expression, in terms of n, for the nth term of this sequence.",
            answer=nth,
            working=(
                f"First differences: {', '.join(str(x) for x in d1)}\n"
                f"Second difference = {2 * a}, so the n² coefficient is {a}\n"
                f"nth term = {nth}"
            ),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for {a}n² from the second difference",
                               working=f"2nd difference {2 * a} → {a}n²"),
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for a correct method for the linear part",
                               working=None),
                MarkSchemeStep(code="A1", mark_type="A", description="cao", working=nth),
            ],
        )
    raise RuntimeError("quadratic-sequence generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Simultaneous equations (linear)  (A19, grade 7)
# --------------------------------------------------------------------------- #
def _yterm(b: int) -> str:
    if b == 1:
        return "+ y"
    if b == -1:
        return "- y"
    return f"+ {b}y" if b > 0 else f"- {abs(b)}y"


def build_simultaneous(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    X, Y = sympy.symbols("x y")
    for _ in range(_MAX_ATTEMPTS):
        x0 = rng.randint(-6, 8)
        y0 = rng.randint(-6, 8)
        a1, a2 = rng.randint(1, 6), rng.randint(1, 6)
        b1 = rng.choice([i for i in range(-6, 7) if i != 0])
        b2 = rng.choice([i for i in range(-6, 7) if i != 0])
        if a1 * b2 - a2 * b1 == 0:
            continue
        c1, c2 = a1 * x0 + b1 * y0, a2 * x0 + b2 * y0
        sol = sympy.solve([a1 * X + b1 * Y - c1, a2 * X + b2 * Y - c2], [X, Y],
                          dict=True)
        if not sol or sol[0][X] != x0 or sol[0][Y] != y0:
            continue
        eq1 = f"{_gx(a1)} {_yterm(b1)} = {c1}"
        eq2 = f"{_gx(a2)} {_yterm(b2)} = {c2}"
        return _item(
            req, seed, archetype="simultaneous-equations",
            topic="Simultaneous equations", topic_slug="simultaneous-equations",
            strand="Algebra", spec_ref="A19", grade_band="6-8", marks=3,
            stem=f"Use algebra to solve the simultaneous equations\n{eq1}\n{eq2}",
            prompt="You must show all your working.",
            answer=f"x = {x0}, y = {y0}",
            working=(
                f"Eliminate one variable, then substitute back.\n"
                f"x = {x0},  y = {y0}"
            ),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for a correct method to eliminate a variable",
                               working=None),
                MarkSchemeStep(code="A1", mark_type="A",
                               description="for one correct value", working=None),
                MarkSchemeStep(code="A1", mark_type="A",
                               description="for the second correct value",
                               working=f"x = {x0}, y = {y0}"),
            ],
        )
    raise RuntimeError("simultaneous generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Completing the square + turning point  (A18, grade 8)
# --------------------------------------------------------------------------- #
def build_completing_square(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        b = rng.choice([i for i in range(-10, 11) if i % 2 == 0 and i != 0])
        c = rng.randint(-8, 10)
        h = b // 2
        q = c - h * h
        if sympy.expand((_x + h) ** 2 + q) != _x**2 + b * _x + c:
            continue
        quad = _quad_str(b, c)
        form = f"(x {_sign(h)})²" + ("" if q == 0 else f" {_sign(q)}")
        tp = f"({-h}, {q})"
        part_a = mk_part(
            label="a",
            prompt=f"Write  {quad}  in the form (x + a)² + b, where a and b are integers.",
            marks=2, answer=form,
            working=f"(x {_sign(h)})² = {_quad_str(b, h * h)}\n"
            f"so {quad} = {form}",
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for (x {_sign(h)})²", working=None),
                MarkSchemeStep(code="A1", mark_type="A", description="cao",
                               working=form),
            ],
        )
        part_b = mk_part(
            label="b",
            prompt=f"Hence write down the coordinates of the turning point of the "
            f"graph of y = {quad}.",
            marks=1, answer=tp,
            working=f"Minimum at x = {-h}, y = {q}: turning point {tp}",
            mark_scheme=[MarkSchemeStep(code="B1", mark_type="B",
                                        description="ft their completed square",
                                        working=tp)],
        )
        return make_item(
            req, seed, archetype="completing-square",
            topic="Completing the square", topic_slug="completing-square",
            strand="Algebra", spec_ref="A18", grade_band="7-9",
            stem="", parts=[part_a, part_b],
        )
    raise RuntimeError("completing-square generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Functions — evaluate, composite, inverse  (A7, grade 8)
# --------------------------------------------------------------------------- #
def build_functions(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        A = rng.randint(2, 12)
        B = rng.randint(1, 6)
        C = rng.choice([i for i in range(-4, 5) if i != 0])
        D = rng.randint(-6, 6)
        divs = [d for d in range(1, A + 1) if A % d == 0]
        # Construct k, m so that f(k) and fg(m) land on integers (d divides A).
        k_choices = [d - B for d in divs if -3 <= d - B <= 6]
        m_choices = [(d - D - B) // C for d in divs
                     if (d - D - B) % C == 0 and -3 <= (d - D - B) // C <= 5]
        if not k_choices or not m_choices:
            continue
        k = rng.choice(k_choices)
        m = rng.choice(m_choices)
        # ginv is exactly t by construction (v = C·t + D).
        t = rng.randint(-5, 6)
        v = C * t + D
        fa = sympy.Rational(A, k + B)
        g_m = C * m + D
        fg = sympy.Rational(A, g_m + B)
        ginv = sympy.Rational(v - D, C)
        if fa.q != 1 or fg.q != 1 or ginv.q != 1:
            continue
        fx = f"{A}/(x {_sign(B)})"
        gx = f"{_gx(C)}" + ("" if D == 0 else f" {_sign(D)}")
        stem = f"The functions f and g are given by\nf(x) = {fx}\ng(x) = {gx}"
        part_a = mk_part(
            label="a", prompt=f"Find f({k}).", marks=1, answer=str(fa),
            working=f"f({k}) = {A}/({k} {_sign(B)}) = {A}/{k + B} = {fa}",
            mark_scheme=[MarkSchemeStep(code="B1", mark_type="B", description="cao",
                                        working=str(fa))],
        )
        part_b = mk_part(
            label="b", prompt=f"Find fg({m}).", marks=2, answer=str(fg),
            working=f"g({m}) = {g_m};  f({g_m}) = {A}/({g_m} {_sign(B)}) = {fg}",
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for g({m}) = {g_m}", working=None),
                MarkSchemeStep(code="A1", mark_type="A", description="cao",
                               working=str(fg)),
            ],
        )
        part_c = mk_part(
            label="c", prompt=f"Find g⁻¹({v}).", marks=2, answer=str(ginv),
            working=f"y = {gx}  →  x = (y {_sign(-D)})/{C};  g⁻¹({v}) = "
            f"({v} {_sign(-D)})/{C} = {ginv}",
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for a correct method to invert g",
                               working=None),
                MarkSchemeStep(code="A1", mark_type="A", description="cao",
                               working=str(ginv)),
            ],
        )
        return make_item(
            req, seed, archetype="functions", topic="Functions",
            topic_slug="functions", strand="Algebra", spec_ref="A7",
            grade_band="7-9", stem=stem, parts=[part_a, part_b, part_c],
        )
    raise RuntimeError("functions generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# STRETCH: fraction equation → quadratic → surd form (grade 9, A18)
#          modelled on June 2022 Q19
# --------------------------------------------------------------------------- #
def build_algfrac_quadratic(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        a = rng.randint(2, 9)
        c = rng.randint(3, 11)
        D = c * c - 4 * a          # discriminant of x² − c·x + a
        if D <= 0 or sympy.sqrt(D).is_Integer:
            continue               # want two irrational roots (surd form)
        # x + a/x = c  ⇔  x² − c·x + a = 0
        roots = set(sympy.solve(_x + sympy.Rational(a) / _x - c, _x))
        target = {(sympy.Rational(c) + sympy.sqrt(D)) / 2,
                  (sympy.Rational(c) - sympy.sqrt(D)) / 2}
        if roots != target:
            continue
        ans = f"({c} ± √{D})/2"
        return _item(
            req, seed, archetype="algfrac-quadratic",
            topic="Solving equations (surd form)", topic_slug="algfrac-quadratic",
            strand="Algebra", spec_ref="A18", grade_band="8-9", marks=4,
            stem=f"Solve  x + {a}/x = {c}\n"
            f"Give your answer in the form (p ± √q)/2 where p and q are integers.",
            prompt="You must show all your working.", answer=ans,
            working=(f"Multiply by x:  x² + {a} = {c}x\n"
                     f"x² − {c}x + {a} = 0\n"
                     f"x = ({c} ± √({c}² − 4×{a}))/2 = {ans}"),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for clearing the fraction",
                               working=f"x² + {a} = {c}x"),
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for a correct quadratic = 0",
                               working=f"x² − {c}x + {a} = 0"),
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for the quadratic formula with values",
                               working=f"({c} ± √({c * c} − {4 * a}))/2"),
                MarkSchemeStep(code="A1", mark_type="A",
                               description="cao, in the required form", working=ans),
            ],
        )
    raise RuntimeError("algfrac-quadratic generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# STRETCH: chained direct + inverse proportion (grade 9, R13)
#          modelled on June 2022 Q17
# --------------------------------------------------------------------------- #
def build_chained_proportion(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        k = rng.randint(2, 6)
        t0 = rng.choice([4, 9, 16, 25, 36])
        y0 = k * sympy.sqrt(t0)                 # y = k√t, so k = y0/√t0
        if not y0.is_Integer:
            continue
        m = rng.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])
        x1 = rng.choice([2, 3])
        t1 = sympy.Rational(m, x1 ** 3)         # t = m/x³
        if t1.q != 1:
            continue
        rm = sympy.sqrt(m)
        coeff = k * rm                          # y = k√(m/x³) = k√m / x^(3/2)
        xp = sympy.Symbol("x", positive=True)   # a length: positive, so √ simplifies
        y_expr = k * sympy.sqrt(sympy.Rational(m) / xp ** 3)
        if sympy.simplify(y_expr - coeff / xp ** sympy.Rational(3, 2)) != 0:
            continue
        ans = f"y = {coeff}x^(−3/2)"
        return _item(
            req, seed, archetype="chained-proportion",
            topic="Direct & inverse proportion", topic_slug="chained-proportion",
            strand="Ratio & proportion", spec_ref="R13", grade_band="8-9", marks=4,
            stem=(f"y is directly proportional to the square root of t.\n"
                  f"y = {int(y0)} when t = {t0}\n"
                  f"t is inversely proportional to the cube of x.\n"
                  f"t = {int(t1)} when x = {x1}"),
            prompt="Find a formula for y in terms of x. Give your answer in its "
            "simplest form.", answer=ans,
            working=(f"y = k√t with k = {int(y0)}/√{t0} = {k}\n"
                     f"t = m/x³ with m = {int(t1)}×{x1}³ = {m}\n"
                     f"y = {k}√({m}/x³) = {k}×{int(rm)}/x^(3/2) = {coeff}x^(−3/2)"),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for k = {int(y0)}/√{t0} (= {k})", working=None),
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for m = {int(t1)} × {x1}³ (= {m})", working=None),
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for {k}√({m}/x³) = {coeff}x^(−3/2)", working=None),
                MarkSchemeStep(code="A1", mark_type="A",
                               description="cao, simplest form", working=ans),
            ],
        )
    raise RuntimeError("chained-proportion generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Expanding triple brackets  (A4, grade 7-9)
# --------------------------------------------------------------------------- #
def build_expand_triple(req: GenerateRequest) -> Item:
    """Expand and simplify (x+a)(x+b)(x+c) — a dedicated triple-bracket item."""
    seed = _seed(req)
    rng = Random(seed)
    pool = [i for i in range(-6, 7) if i != 0]
    for _ in range(_MAX_ATTEMPTS):
        a, b, c = (rng.choice(pool) for _ in range(3))
        expr = sympy.expand((_x + a) * (_x + b) * (_x + c))
        poly = sympy.Poly(expr, _x)
        # Independent verification: monic cubic whose coefficients are exactly
        # (1, a+b+c, ab+ac+bc, abc).
        expect = [1, a + b + c, a * b + a * c + b * c, a * b * c]
        if poly.degree() != 3 or [int(v) for v in poly.all_coeffs()] != expect:
            continue
        two = sympy.expand((_x + a) * (_x + b))
        answer = _poly_str(expr)
        return _item(
            req, seed, archetype="expand-triple-brackets",
            topic="Quadratic expressions", topic_slug="quadratics",
            strand="Algebra", spec_ref="A4", grade_band="7-9", marks=3,
            stem="",
            prompt=f"Expand and simplify  {_bracket(1, a)}{_bracket(1, b)}{_bracket(1, c)}",
            answer=answer,
            working=(f"{_bracket(1, a)}{_bracket(1, b)} = {_poly_str(two)}\n"
                     f"({_poly_str(two)})(x {_sign(c)}) = {answer}"),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="expands two brackets to a quadratic",
                               working=_poly_str(two)),
                MarkSchemeStep(code="M1", mark_type="M",
                               description="multiplies the quadratic by the third bracket",
                               working=None),
                MarkSchemeStep(code="A1", mark_type="A",
                               description="cao, fully expanded and simplified",
                               working=answer),
            ],
        )
    raise RuntimeError("expand-triple generator failed to produce a valid item.")
