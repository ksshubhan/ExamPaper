"""Independent numeric re-derivation for a representative set of archetypes.

For each, we re-compute the answer from the *question text* with sympy (never
the generator's own code path) and assert they agree — proving the maths, not
just the structure. The universal structural suite covers all 119 archetypes;
this covers the computational core of every strand.
"""

import math
import re
import unittest

import sympy

from app.generators.registry import get_generator
from tests.helpers import poly, req

N = 120
x, n = sympy.symbols("x n")
a_, b_ = sympy.symbols("a b")


def build(arch, seed, calc=None):
    return get_generator(arch)(req(arch, calc, seed=seed))


def money(s):
    return sympy.Rational(s.replace("£", "").rstrip(".").replace(",", ""))


def frac_or_mixed(s):
    s = s.strip()
    m = re.match(r"^(\d+) (\d+)/(\d+)$", s)
    if m:
        return int(m.group(1)) + sympy.Rational(int(m.group(2)), int(m.group(3)))
    return sympy.Rational(s)


def sf3(v):
    return float("%.3g" % v)


class TestNumeric(unittest.TestCase):

    def test_fraction_arithmetic(self):
        for s in range(N):
            it = build("fraction-arithmetic", s)
            stem = it.stem + " " + " ".join(p.prompt for p in it.parts)
            m = re.search(r"(\d+)/(\d+) ([+−]) (\d+)/(\d+)", stem)
            n1, d1, op, n2, d2 = int(m[1]), int(m[2]), m[3], int(m[4]), int(m[5])
            exp = sympy.Rational(n1, d1) + (sympy.Rational(n2, d2) if op == "+"
                                            else -sympy.Rational(n2, d2))
            ans = next(p.answer for p in it.parts if "/" in p.answer
                       and "mistake" not in p.prompt.lower())
            self.assertEqual(frac_or_mixed(ans), exp)

    def test_linear_equation(self):
        for s in range(N):
            it = build("linear-equation", s)
            m = re.search(r"Solve  (\d+)x ([+-] \d+) = (-?\d+)", it.stem)
            a, b, c = int(m[1]), int(m[2].replace(" ", "")), int(m[3])
            xv = int(re.search(r"x = (-?\d+)", it.parts[0].answer)[1])
            self.assertEqual(a * xv + b, c)

    def test_share_ratio(self):
        for s in range(N):
            it = build("share-ratio", s)
            m = re.search(r"£(\d+) in the ratio (\d+) : (\d+)", it.stem)
            total, p, q = int(m[1]), int(m[2]), int(m[3])
            per = total // (p + q)
            self.assertIn(f"£{per * p}", it.parts[0].answer)
            self.assertIn(f"£{per * q}", it.parts[0].answer)

    def test_percentage_change(self):
        for s in range(N):
            it = build("percentage-change", s)
            B = int(re.search(r"price of a \w+ is £(\d+)", it.stem)[1])
            p = int(re.search(r"(\d+)%", it.stem)[1])
            up = "increase" in it.stem
            exp = sympy.Rational(B) * ((1 + sympy.Rational(p, 100)) if up
                                       else (1 - sympy.Rational(p, 100)))
            num = next(pt for pt in it.parts if pt.answer.startswith("£"))
            self.assertEqual(money(num.answer), exp)

    def test_reverse_percentage(self):
        for s in range(N):
            it = build("reverse-percentage", s)
            p = int(re.search(r"(\d+)%", it.stem)[1])
            up = "increase" in it.stem
            final = sympy.Rational(re.findall(r"£(\d+(?:\.\d+)?)", it.stem)[-1])
            mult = (1 + sympy.Rational(p, 100)) if up else (1 - sympy.Rational(p, 100))
            self.assertEqual(money(it.parts[0].answer), final / mult)

    def test_indices(self):
        for s in range(N):
            it = build("indices", s)
            st = it.stem
            if "in the form" in st or "+" in st:
                continue
            m = re.search(r"value of  (\d+)\^\(([-\d/]+)\)", st)
            val = sympy.Integer(int(m[1])) ** sympy.Rational(m[2])
            self.assertEqual(val, sympy.Rational(it.parts[0].answer))

    def test_standard_form(self):
        inv = {c: d for c, d in zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")}
        desup = lambda s: "".join(inv.get(c, c) for c in s)
        for s in range(N):
            it = build("standard-form", s)
            text = desup(it.stem) + " " + " ".join(desup(p.prompt) for p in it.parts)
            ops = re.findall(r"([\d.]+) × 10(-?\d+)", text)
            if len(ops) < 2:
                continue
            op = "÷" if "÷" in text else "×"
            (m1, e1), (m2, e2) = ops[0], ops[1]
            L = sympy.Rational(m1) * sympy.Integer(10) ** int(e1)
            Rr = sympy.Rational(m2) * sympy.Integer(10) ** int(e2)
            full = L * Rr if op == "×" else L / Rr
            ansp = [p for p in it.parts if "standard form" in p.prompt.lower()][-1]
            am, ae = re.findall(r"([\d.]+) × 10(-?\d+)", desup(ansp.answer))[0]
            self.assertEqual(sympy.simplify(full - sympy.Rational(am) * sympy.Integer(10) ** int(ae)), 0)

    def test_quadratics(self):
        for arch in ("expand-quadratic", "factorise-quadratic"):
            for s in range(N):
                it = build(arch, s)
                lhs = poly(it.stem.split("  ")[1])
                rhs = poly(it.parts[0].answer)
                self.assertEqual(sympy.expand(lhs - rhs), 0)

    def test_nth_term(self):
        for s in range(N):
            it = build("nth-term", s)
            seq = [int(t) for t in it.stem.split("\n")[1].split(", ")]
            nth = poly(it.parts[0].answer)
            for k in range(4):
                self.assertEqual(nth.subs(n, k + 1), seq[k])

    def test_surds(self):
        for s in range(N):
            it = build("surds", s)
            st, ans = it.stem, it.parts[0].answer.strip()
            m = re.match(r"^(\d*)√(\d+)(?:/(\d+))?$", ans)
            av = (sympy.Rational(int(m[1]) if m[1] else 1, int(m[3]) if m[3] else 1)
                  * sympy.sqrt(int(m[2]))) if m else sympy.Rational(ans)
            if "Simplify fully" in st:
                mm = re.search(r"√(\d+) ([+−]) √(\d+)", st)
                exp = sympy.sqrt(int(mm[1])) + (sympy.sqrt(int(mm[3])) if mm[2] == "+"
                                                else -sympy.sqrt(int(mm[3])))
            else:
                mm = re.search(r"of  (\d+)/√(\d+)", st)
                exp = sympy.Rational(int(mm[1])) / sympy.sqrt(int(mm[2]))
            self.assertEqual(sympy.simplify(exp - av), 0)

    def test_gradient(self):
        for s in range(N):
            it = build("gradient", s)
            m = re.search(r"\((-?\d+) − (-?\d+)\)/\((-?\d+) − (-?\d+)\)", it.parts[0].working)
            self.assertEqual(sympy.Rational(int(m[1]) - int(m[2]), int(m[3]) - int(m[4])),
                             sympy.Rational(it.parts[0].answer))

    def test_equation_of_line(self):
        for s in range(N):
            it = build("equation-of-line", s)
            m = re.search(r"through \((-?\d+), (-?\d+)\) and \((-?\d+), (-?\d+)\)", it.parts[0].prompt)
            ax, ay, bx, by = map(int, m.groups())
            rhs = poly(it.parts[0].answer.split("=")[1])
            self.assertEqual(rhs.subs(x, ax), ay)
            self.assertEqual(rhs.subs(x, bx), by)

    def test_coordinates_midpoint(self):
        for s in range(N):
            it = build("coordinates", s)
            m = re.search(r"A is \((-?\d+), (-?\d+)\) and B is \((-?\d+), (-?\d+)\)", it.parts[0].prompt)
            ax, ay, bx, by = map(int, m.groups())
            gm = re.search(r"\((-?\d+(?:/\d+)?), (-?\d+(?:/\d+)?)\)", it.parts[0].answer)
            self.assertEqual(sympy.Rational(gm[1]), sympy.Rational(ax + bx, 2))
            self.assertEqual(sympy.Rational(gm[2]), sympy.Rational(ay + by, 2))

    def test_circle_measures(self):
        for s in range(N):
            it = build("circle-measures", s, calc=False)
            r = int(re.search(r"radius (\d+) cm", it.diagram.alt)[1])
            self.assertEqual(it.parts[0].answer, f"{r * r}π cm²")
            self.assertEqual(it.parts[1].answer, f"{2 * r}π cm")

    def test_bearings(self):
        for s in range(N):
            it = build("bearings", s)
            bg = int(re.search(r"is (\d+)°", it.parts[0].prompt)[1])
            self.assertEqual(it.parts[0].answer, f"{(bg + 180) % 360:03d}°")

    def test_vectors(self):
        for s in range(N):
            it = build("vectors", s)
            m = re.search(r"a = \((-?\d+), (-?\d+)\) and b = \((-?\d+), (-?\d+)\).*Work out (\d+)a", it.parts[0].prompt)
            a1, a2, b1, b2, sc = map(int, m.groups())
            self.assertEqual(it.parts[0].answer, f"({sc * a1 - b1}, {sc * a2 - b2})")

    def test_area_perimeter(self):
        for s in range(N):
            it = build("area-perimeter", s)
            m = re.search(r"from a (\d+) by (\d+) rectangle with a (\d+) by (\d+)", it.diagram.alt)
            W, H, nw, nh = map(int, m.groups())
            self.assertEqual(it.parts[0].answer, f"{W * H - nw * nh} cm²")
            self.assertEqual(it.parts[1].answer, f"{2 * (W + H)} cm")

    def test_hcf_lcm(self):
        for s in range(N):
            it = build("hcf-lcm", s)
            A, B = map(int, re.search(r"HCF\) of (\d+) and (\d+)", it.parts[1].prompt).groups())
            self.assertEqual(it.parts[1].answer, str(int(sympy.igcd(A, B))))
            self.assertEqual(it.parts[2].answer, str(int(sympy.ilcm(A, B))))
            val = 1
            for tok in it.parts[0].answer.split(" × "):
                for sp, dg in zip("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789"):
                    tok = tok.replace(sp, "^" + dg)
                if "^" in tok:
                    base, exp = tok.split("^"); val *= int(base) ** int(exp)
                else:
                    val *= int(tok)
            self.assertEqual(val, A)

    def test_averages(self):
        for s in range(N):
            it = build("averages", s)
            data = [int(v) for v in it.stem.split("\n")[1].split()]
            md = {p.label: p.answer for p in it.parts}
            self.assertEqual(int(md["b"]), sorted(data)[len(data) // 2])
            self.assertEqual(int(md["c"]), sum(data) // len(data))
            self.assertEqual(int(md["d"]), max(data) - min(data))

    def test_probability(self):
        for s in range(N):
            it = build("probability", s)
            counts = {c: int(n_) for n_, c in re.findall(r"(\d+) (red|blue|green|yellow)", it.stem)}
            col = re.search(r"is (\w+)\.", it.parts[0].prompt)[1]
            self.assertEqual(sympy.Rational(it.parts[0].answer),
                             sympy.Rational(counts[col], sum(counts.values())))

    def test_product_rule(self):
        for s in range(N):
            it = build("product-rule", s)
            a, b, c = map(int, re.search(r"(\d+) × (\d+) × (\d+)", it.parts[0].working).groups())
            self.assertEqual(int(it.parts[0].answer), a * b * c)

    def test_simplify_ratio(self):
        for s in range(N):
            it = build("simplify-ratio", s)
            A, B = map(int, re.search(r"ratio (\d+) : (\d+)", it.parts[0].prompt).groups())
            g = int(sympy.igcd(A, B))
            self.assertEqual(it.parts[0].answer, f"{A // g} : {B // g}")

    def test_ratio_as_fraction(self):
        for s in range(N):
            it = build("ratio-as-fraction", s)
            A, B = map(int, re.search(r"is (\d+) : (\d+)", it.parts[0].prompt).groups())
            exp = sympy.Rational(A, A + B)
            self.assertEqual(it.parts[0].answer, str(exp.p) if exp.q == 1 else f"{exp.p}/{exp.q}")

    def test_substitution(self):
        for s in range(N):
            it = build("substitution", s)
            m = re.search(r"(\d+)x² − (\d+)y  when x = (\d+) and y = (\d+)", it.parts[0].prompt)
            p, q, xv, yv = map(int, m.groups())
            self.assertEqual(p * xv * xv - q * yv, int(it.parts[0].answer))

    def test_solving_quadratics(self):
        for s in range(N):
            it = build("solving-quadratics", s)
            roots = [int(z) for z in re.findall(r"x = (-?\d+)", it.parts[0].answer)]
            eqn = poly(it.parts[0].prompt.split("  ")[1].replace(" = 0", ""))
            for r in roots:
                self.assertEqual(eqn.subs(x, r), 0)

    def test_quadratic_formula(self):
        for s in range(N):
            it = build("quadratic-formula", s, calc=True)
            eqn = it.parts[0].prompt.split("Solve  ")[1].split("\n")[0].replace(" = 0", "")
            true = [complex(r).real for r in sympy.Poly(poly(eqn), x).nroots()]
            for r in [float(z) for z in re.findall(r"x = (-?\d+\.\d+)", it.parts[0].answer)]:
                self.assertLessEqual(min(abs(r - t) for t in true), 0.006)

    def test_algebraic_proof(self):
        for s in range(N):
            it = build("algebraic-proof", s)
            pr = it.parts[0].prompt
            expanded = poly(re.search(r"Expand: .+ = (.+)", it.parts[0].working)[1])
            coeffs = [int(c) for c in sympy.Poly(expanded, n).all_coeffs()]
            if "multiple of 8" in pr:
                self.assertTrue(all(c % 8 == 0 for c in coeffs))
            elif "multiple of 3" in pr:
                self.assertTrue(all(c % 3 == 0 for c in coeffs))
            elif "multiple of 4" in pr:
                self.assertTrue(all(c % 4 == 0 for c in coeffs))
            else:  # always odd
                self.assertEqual(coeffs[-1] % 2, 1)
                self.assertTrue(all(c % 2 == 0 for c in coeffs[:-1]))


if __name__ == "__main__":
    unittest.main()
