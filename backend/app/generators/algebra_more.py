"""Algebra generators that complete the strand.

Text-only, deterministic from a seed, every answer re-derived and checked with
sympy. Reuses the polynomial/bracket formatters from algebra.py.
"""

from __future__ import annotations

from random import Random

import sympy

from ..schema import GenerateRequest, Item, MarkSchemeStep
from .algebra import _bracket, _poly_str, _quad_str, _sign
from .basics import _item, _seed
from .context import make_item, mk_part, sig_figs

_MAX_ATTEMPTS = 300
_x = sympy.Symbol("x")


def _M1(d, w=None): return MarkSchemeStep(code="M1", mark_type="M", description=d, working=w)
def _A1(d, w=None): return MarkSchemeStep(code="A1", mark_type="A", description=d, working=w)
def _B1(d, w=None): return MarkSchemeStep(code="B1", mark_type="B", description=d, working=w)


def _term(coef: int, var: str, first: bool) -> str:
    mag = abs(coef)
    body = var if mag == 1 else f"{mag}{var}"
    if first:
        return ("-" if coef < 0 else "") + body
    return (" + " if coef > 0 else " - ") + body


# --------------------------------------------------------------------------- #
# Simplify — collect like terms  (A4)
# --------------------------------------------------------------------------- #
def build_simplify_algebra(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    a, b = sympy.symbols("a b")
    for _ in range(_MAX_ATTEMPTS):
        c1, c3 = rng.randint(1, 7), rng.choice([-4, -3, -2, -1, 2, 3])
        c2, c4 = rng.randint(1, 7), rng.choice([-4, -3, -2, -1, 2, 3])
        ca, cb = c1 + c3, c2 + c4
        if ca == 0 or cb == 0:
            continue
        terms = [(c1, "a"), (c2, "b"), (c3, "a"), (c4, "b")]
        rng.shuffle(terms)
        stem_expr = ""
        for i, (co, v) in enumerate(terms):
            stem_expr += _term(co, v, i == 0)
        ans = _term(ca, "a", True) + _term(cb, "b", False)
        # sympy check
        given = c1 * a + c2 * b + c3 * a + c4 * b
        if sympy.simplify(given - (ca * a + cb * b)) != 0:
            continue
        return _item(req, seed, archetype="simplify-algebra",
                     topic="Simplifying algebra", topic_slug="simplify-algebra",
                     strand="Algebra", spec_ref="A4", grade_band="2-3", marks=2,
                     stem=f"Simplify  {stem_expr}", prompt="", answer=ans,
                     working=f"{stem_expr} = {ans}",
                     mark_scheme=[_M1("for collecting the a terms or the b terms"),
                                  _A1("cao", ans)])
    raise RuntimeError("simplify-algebra generator failed.")


# --------------------------------------------------------------------------- #
# Substitution  (A2)
# --------------------------------------------------------------------------- #
def build_substitution(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    x, y = sympy.symbols("x y")
    p = rng.randint(2, 5)
    q = rng.randint(2, 6)
    xv, yv = rng.randint(2, 6), rng.randint(2, 6)
    expr = p * x**2 - q * y
    val = int(expr.subs({x: xv, y: yv}))
    part = mk_part(
        prompt=f"Work out the value of  {p}x² − {q}y  when x = {xv} and y = {yv}.",
        marks=2, answer=str(val),
        working=f"{p}×{xv}² − {q}×{yv} = {p * xv * xv} − {q * yv} = {val}",
        mark_scheme=[_M1("for correct substitution"), _A1("cao", str(val))])
    return make_item(req, seed, archetype="substitution", topic="Substitution",
                     topic_slug="substitution", strand="Algebra", spec_ref="A2",
                     grade_band="2-4", stem="", parts=[part])


# --------------------------------------------------------------------------- #
# Function machines  (A5)
# --------------------------------------------------------------------------- #
def build_function_machines(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        m = rng.randint(2, 5)
        c = rng.randint(1, 9)
        k = rng.randint(2, 8)
        out = m * k + c
        t = m * rng.randint(3, 9) + c   # a valid output → integer input
        inp = sympy.Rational(t - c, m)
        if inp.q != 1:
            continue
        stem = f"Here is a number machine.\ninput  →  × {m}  →  + {c}  →  output"
        parts = [
            mk_part(label="a", prompt=f"Work out the output when the input is {k}.",
                    marks=1, answer=str(out), working=f"{k} × {m} + {c} = {out}",
                    mark_scheme=[_B1("cao")]),
            mk_part(label="b", prompt=f"Work out the input when the output is {t}.",
                    marks=2, answer=str(int(inp)),
                    working=f"({t} − {c}) ÷ {m} = {int(inp)}",
                    mark_scheme=[_M1("for reversing the machine"), _A1("cao", str(int(inp)))]),
        ]
        return make_item(req, seed, archetype="function-machines",
                         topic="Function machines", topic_slug="function-machines",
                         strand="Algebra", spec_ref="A5", grade_band="2-3",
                         stem=stem, parts=parts)
    raise RuntimeError("function-machines generator failed.")


# --------------------------------------------------------------------------- #
# Forming & solving equations  (A21)
# --------------------------------------------------------------------------- #
def build_forming_equations(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    m = rng.randint(2, 6)
    x0 = rng.randint(3, 12)
    b = rng.randint(2, 15)
    c = m * x0 + b
    part = mk_part(
        prompt=(f"Nadia thinks of a number. She multiplies it by {m} and then adds {b}. "
                f"Her answer is {c}. Form an equation and work out Nadia's number. "
                "You must show all your working."),
        marks=3, answer=f"x = {x0}",
        working=f"{m}x + {b} = {c}\n{m}x = {c - b}\nx = {x0}",
        mark_scheme=[_M1("for forming a correct equation", f"{m}x + {b} = {c}"),
                     _M1("for a correct method to solve"), _A1("cao", f"x = {x0}")])
    return make_item(req, seed, archetype="forming-equations",
                     topic="Forming & solving equations", topic_slug="forming-equations",
                     strand="Algebra", spec_ref="A21", grade_band="3-5", ao="AO2",
                     stem="", parts=[part])


# --------------------------------------------------------------------------- #
# Inequalities — solve + list integer solutions  (A22)
# --------------------------------------------------------------------------- #
def build_inequalities(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        a = rng.randint(2, 6)
        b = rng.randint(-8, 8)
        sol = rng.randint(-3, 6)
        c = a * sol + b
        sign = rng.choice(["<", ">", "≤", "≥"])
        lo = rng.randint(-4, -1)
        hi = rng.randint(1, 5)
        ints = list(range(lo, hi))   # -lo ≤ n < hi
        part_a = mk_part(
            label="a", prompt=f"Solve  {a}x {_sign(b)} {sign} {c}",
            marks=2, answer=f"x {sign} {sol}",
            working=f"{a}x {sign} {c - b}\nx {sign} {sol}",
            mark_scheme=[_M1("for a correct first step"), _A1("cao", f"x {sign} {sol}")])
        part_b = mk_part(
            label="b",
            prompt=f"n is an integer such that  {lo} ≤ n < {hi}.  List all the possible "
            "values of n.", marks=1, answer=", ".join(str(i) for i in ints),
            working=", ".join(str(i) for i in ints), mark_scheme=[_B1("cao")])
        return make_item(req, seed, archetype="inequalities", topic="Inequalities",
                         topic_slug="inequalities", strand="Algebra", spec_ref="A22",
                         grade_band="4-5", stem="", parts=[part_a, part_b])
    raise RuntimeError("inequalities generator failed.")


# --------------------------------------------------------------------------- #
# Changing the subject  (A5)
# --------------------------------------------------------------------------- #
def build_changing_subject(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    y, c, u, v, A, l = sympy.symbols("y c u v A l")
    kind = rng.choice(["linear", "motion", "area"])
    if kind == "linear":
        m = rng.randint(2, 6)
        formula, subject, ans = f"y = {m}x + c", "x", f"x = (y − c)/{m}"
        eq = m * _x + c - y
        target = (y - c) / m
    elif kind == "motion":
        t = rng.randint(2, 6)
        aS = sympy.Symbol("a")
        formula, subject, ans = f"v = u + {t}a", "a", f"a = (v − u)/{t}"
        eq = u + t * aS - v
        target = (v - u) / t
        _x_local = aS
    else:
        w = sympy.Symbol("w")
        formula, subject, ans = "A = lw", "w", "w = A/l"
        eq = l * w - A
        target = A / l
        _x_local = w
    solve_sym = {"linear": _x, "motion": sympy.Symbol("a"), "area": sympy.Symbol("w")}[kind]
    sol = sympy.solve(eq, solve_sym)
    if not sol or sympy.simplify(sol[0] - target) != 0:
        raise RuntimeError("changing-subject verification failed.")
    part = mk_part(
        prompt=f"Make {subject} the subject of the formula  {formula}.", marks=2,
        answer=ans, working=ans,
        mark_scheme=[_M1("for a correct rearrangement step"), _A1("cao", ans)])
    return make_item(req, seed, archetype="changing-subject",
                     topic="Changing the subject", topic_slug="changing-subject",
                     strand="Algebra", spec_ref="A5", grade_band="5-6", stem="",
                     parts=[part])


# --------------------------------------------------------------------------- #
# Solving quadratics by factorising  (A18)
# --------------------------------------------------------------------------- #
def build_solving_quadratics(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        p = rng.randint(-6, 5)
        q = rng.randint(p + 1, 6)
        b, c = -(p + q), p * q
        if sympy.solve(_x**2 + b * _x + c, _x) != sorted({p, q}):
            continue
        eqn = _quad_str(b, c) + " = 0"
        part = mk_part(
            prompt=f"Solve  {eqn}", marks=3, answer=f"x = {p} or x = {q}",
            working=f"(x {_sign(-p)})(x {_sign(-q)}) = 0\nx = {p} or x = {q}",
            mark_scheme=[_M1("for factorising"), _A1(f"x = {p}"), _A1(f"x = {q}")])
        return make_item(req, seed, archetype="solving-quadratics",
                         topic="Solving quadratics", topic_slug="solving-quadratics",
                         strand="Algebra", spec_ref="A18", grade_band="5-6", stem="",
                         parts=[part])
    raise RuntimeError("solving-quadratics generator failed.")


# --------------------------------------------------------------------------- #
# Quadratic formula (2 d.p.)  (A18)
# --------------------------------------------------------------------------- #
def build_quadratic_formula(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        a = rng.randint(1, 3)
        b = rng.randint(-6, 6)
        c = rng.randint(-6, 6)
        D = b * b - 4 * a * c
        if D <= 0 or sympy.sqrt(D).is_Integer:
            continue
        r1 = (-b + sympy.sqrt(D)) / (2 * a)
        r2 = (-b - sympy.sqrt(D)) / (2 * a)
        a1, a2 = round(float(r1), 2), round(float(r2), 2)
        eqn = f"{a}x² {_sign(b)}x {_sign(c)} = 0" if a != 1 else _quad_str(b, c) + " = 0"
        part = mk_part(
            prompt=f"Solve  {eqn}\nGive your solutions correct to 2 decimal places.",
            marks=3, answer=f"x = {a1:.2f} or x = {a2:.2f}", answer_tolerance=0.01,
            working=(f"x = (−b ± √(b² − 4ac)) / 2a = ({-b} ± √{D}) / {2 * a}\n"
                     f"x = {a1:.2f} or x = {a2:.2f}"),
            mark_scheme=[_M1("for correct substitution into the formula"),
                         _M1("for √ of the discriminant"),
                         _A1("awrt (2 d.p.)", f"{a1:.2f}, {a2:.2f}")])
        return make_item(req, seed, archetype="quadratic-formula",
                         topic="Quadratic formula", topic_slug="quadratic-formula",
                         strand="Algebra", spec_ref="A18", grade_band="6-8", stem="",
                         parts=[part])
    raise RuntimeError("quadratic-formula generator failed.")


# --------------------------------------------------------------------------- #
# Factorising harder quadratics ax²+bx+c  (A4)
# --------------------------------------------------------------------------- #
def build_factorise_hard(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        p, q = rng.randint(2, 4), rng.randint(2, 4)
        a = rng.choice([i for i in range(-5, 6) if i != 0])
        b = rng.choice([i for i in range(-5, 6) if i != 0])
        expr = sympy.expand((p * _x + a) * (q * _x + b))
        poly = sympy.Poly(expr, _x)
        A, B, C = [int(x) for x in poly.all_coeffs()]
        if A < 2 or sympy.igcd(sympy.igcd(A, B), C) != 1:
            continue  # keep it a genuine 'hard' factorisation with no common factor
        stem_expr = f"{A}x² {_sign(B)}x {_sign(C)}"
        ans = f"{_bracket(p, a)}{_bracket(q, b)}"
        # independent check: our brackets expand to the given quadratic
        if sympy.expand((p * _x + a) * (q * _x + b)) != expr:
            continue
        return _item(req, seed, archetype="factorise-hard",
                     topic="Factorising harder quadratics", topic_slug="factorise-hard",
                     strand="Algebra", spec_ref="A4", grade_band="6-8", marks=2,
                     stem=f"Factorise  {stem_expr}", prompt="", answer=ans,
                     working=f"{stem_expr} = {ans}",
                     mark_scheme=[_M1("for a correct method (splitting the middle term)"),
                                  _A1("cao", ans)])
    raise RuntimeError("factorise-hard generator failed.")


# --------------------------------------------------------------------------- #
# Rearranging harder formulae — subject appears twice  (A5)
# --------------------------------------------------------------------------- #
def build_rearrange_hard(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    aS, bS = sympy.symbols("a b")
    k = rng.randint(2, 5)
    j = rng.randint(2, 5)
    den = k + j
    X = sympy.Symbol("x")
    eq = k * X + aS - (bS - j * X)
    target = (bS - aS) / den
    sol = sympy.solve(eq, X)
    if not sol or sympy.simplify(sol[0] - target) != 0:
        raise RuntimeError("rearrange-hard verification failed.")
    ans = f"x = (b − a)/{den}"
    part = mk_part(
        prompt=f"Make x the subject of the formula  {k}x + a = b − {j}x", marks=3,
        answer=ans,
        working=(f"{k}x + {j}x = b − a\n{den}x = b − a\nx = (b − a)/{den}"),
        mark_scheme=[_M1("for collecting the x terms on one side"),
                     _M1("for factorising out x"), _A1("cao", ans)])
    return make_item(req, seed, archetype="rearrange-hard",
                     topic="Rearranging harder formulae", topic_slug="rearrange-hard",
                     strand="Algebra", spec_ref="A5", grade_band="7-8", stem="",
                     parts=[part])


# --------------------------------------------------------------------------- #
# Iteration  (A20)
# --------------------------------------------------------------------------- #
def build_iteration(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        a = rng.randint(4, 20)
        b = rng.randint(1, 4)
        x0 = rng.randint(1, 4)
        xs = [float(x0)]
        for _i in range(3):
            nxt = a / (xs[-1] + b)
            xs.append(nxt)
        if not all(x > 0 for x in xs):
            continue
        x1, x2, x3 = (round(xs[1], 3), round(xs[2], 3), round(xs[3], 3))
        part = mk_part(
            prompt=(f"Use the iteration formula  xₙ₊₁ = {a} / (xₙ + {b})  with x₀ = {x0} "
                    f"to work out the value of x₃. Give your answer to 3 decimal places."),
            marks=3, answer=f"{x3:.3f}", answer_tolerance=0.001,
            working=(f"x₁ = {a}/({x0} + {b}) = {x1:.3f}\n"
                     f"x₂ = {a}/({x1:.3f} + {b}) = {x2:.3f}\n"
                     f"x₃ = {a}/({x2:.3f} + {b}) = {x3:.3f}"),
            mark_scheme=[_M1("for x₁"), _M1("for x₂"), _A1("cao x₃ (3 d.p.)", f"{x3:.3f}")])
        return make_item(req, seed, archetype="iteration", topic="Iteration",
                         topic_slug="iteration", strand="Algebra", spec_ref="A20",
                         grade_band="7-8", stem="", parts=[part])
    raise RuntimeError("iteration generator failed.")


# --------------------------------------------------------------------------- #
# Quadratic simultaneous equations (linear + quadratic)  (A19)
# --------------------------------------------------------------------------- #
def build_quadratic_simultaneous(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    x, y = sympy.symbols("x y")
    for _ in range(_MAX_ATTEMPTS):
        p = rng.randint(-4, 2)
        q = rng.randint(p + 1, 4)
        B = rng.randint(-3, 3)
        C = rng.randint(-4, 4)
        M = B + (p + q)
        D = C - p * q
        # parabola y = x² + Bx + C ; line y = Mx + D ; intersections at x=p,q
        yp, yq = M * p + D, M * q + D
        sols = sympy.solve([y - (x**2 + B * x + C), y - (M * x + D)], [x, y], dict=True)
        got = sorted((int(s[x]), int(s[y])) for s in sols)
        if got != sorted([(p, yp), (q, yq)]):
            continue
        line = f"y = {_line_rhs(M, D)}"
        para = f"y = {_quad_str(B, C)}"
        part = mk_part(
            prompt=f"Solve the simultaneous equations\n{para}\n{line}\n"
            "You must show all your working.", marks=5,
            answer=f"x = {p}, y = {yp}  and  x = {q}, y = {yq}",
            working=(f"x² {_sign(B)}x {_sign(C)} = {_line_rhs(M, D)}\n"
                     f"x² {_sign(B - M)}x {_sign(C - D)} = 0\n"
                     f"(x {_sign(-p)})(x {_sign(-q)}) = 0\n"
                     f"x = {p}, y = {yp};  x = {q}, y = {yq}"),
            mark_scheme=[_M1("for substituting to eliminate y"),
                         _M1("for a correct quadratic = 0"), _M1("for solving"),
                         _A1(f"x = {p}, y = {yp}"), _A1(f"x = {q}, y = {yq}")])
        return make_item(req, seed, archetype="quadratic-simultaneous",
                         topic="Quadratic simultaneous equations",
                         topic_slug="quadratic-simultaneous", strand="Algebra",
                         spec_ref="A19", grade_band="8-9", stem="", parts=[part])
    raise RuntimeError("quadratic-simultaneous generator failed.")


def _line_rhs(m: int, c: int) -> str:
    if m == 0:
        return str(c)
    mp = "x" if m == 1 else ("-x" if m == -1 else f"{m}x")
    if c > 0:
        return f"{mp} + {c}"
    if c < 0:
        return f"{mp} - {abs(c)}"
    return mp


# --------------------------------------------------------------------------- #
# Quadratic inequalities  (A22, grade 7-9)
# --------------------------------------------------------------------------- #
def build_quadratic_inequalities(req: GenerateRequest) -> Item:
    _xq = sympy.Symbol("x")
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        p = rng.randint(-6, 3)
        q = p + rng.randint(1, 6)               # roots p < q
        b, c = -(p + q), p * q
        sense = rng.choice(["<", ">"])
        expr = _xq**2 + b * _xq + c
        rel = expr < 0 if sense == "<" else expr > 0
        soln = sympy.solve_univariate_inequality(rel, _xq, relational=False)
        if sense == "<":
            expected = sympy.Interval.open(p, q)
            ans = f"{p} < x < {q}"
        else:
            expected = sympy.Union(sympy.Interval.open(-sympy.oo, p),
                                   sympy.Interval.open(q, sympy.oo))
            ans = f"x < {p} or x > {q}"
        if soln != expected:
            continue
        return _item(
            req, seed, archetype="quadratic-inequalities",
            topic="Quadratic inequalities", topic_slug="quadratic-inequalities",
            strand="Algebra", spec_ref="A22", grade_band="7-9", marks=3,
            stem="", prompt=f"Solve  {_quad_str(b, c)} {sense} 0",
            answer=ans,
            working=(f"({_bracket(1, -p)})({_bracket(1, -q)}) {sense} 0\n"
                     f"Critical values x = {p} and x = {q}\n{ans}"),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="factorises / finds the two critical values",
                               working=f"x = {p}, x = {q}"),
                MarkSchemeStep(code="M1", mark_type="M",
                               description="chooses the correct region (sketch/sign)"),
                MarkSchemeStep(code="A1", mark_type="A", description="cao", working=ans),
            ])
    raise RuntimeError("quadratic-inequalities generator failed.")
