"""Number-strand generators: percentages, standard form, indices.

Same contract as the rest of the engine: deterministic from a seed, every
numeric answer independently re-derived and checked with sympy (reject/resample),
and a faithful Edexcel-style mark scheme. Enriched (Phase E) with real-world
context, multi-part (a)/(b) structures and single-topic reasoning devices where
the reference papers use them — while pure index manipulation stays bare.
"""

from __future__ import annotations

from random import Random

import sympy

from ..schema import GenerateRequest, Item, MarkSchemeStep
from .basics import _item, _seed
from .context import (
    SHOP_ITEMS,
    claim_prompt,
    make_item,
    mk_part,
    pick,
    reason_step,
)
from .pythagoras import _simplify_surd, _surd_str

_SQUARE_FREE = [2, 3, 5, 6, 7, 10, 11, 13, 15]

_MAX_ATTEMPTS = 200

# Superscript digits for rendering powers of ten inline, e.g. 3.6 × 10⁸.
_SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def _money(r: sympy.Rational) -> str:
    """Render pounds: '£240' when whole, else '£19.99' to 2 d.p."""
    if r.q == 1:
        return f"£{r.p}"
    return f"£{float(r):.2f}"


# --------------------------------------------------------------------------- #
# Percentages: percentage change (+ optional claim) and reverse percentage (R9)
# --------------------------------------------------------------------------- #
def _pct_variant(req: GenerateRequest) -> str | None:
    v = (req.variant or req.archetype or "").lower()
    if "reverse" in v:
        return "reverse"
    if "change" in v:
        return "change"
    return None


def build_percentages(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    calc = bool(req.calculator)
    variant = _pct_variant(req)

    for _ in range(_MAX_ATTEMPTS):
        v = variant or rng.choice(["change", "reverse"])
        item = pick(rng, SHOP_ITEMS)
        name = pick(rng, ["Mia", "Tom", "Aisha", "Ben", "Lucy", "Sam"])
        up = rng.random() < 0.5

        if calc:
            base = rng.randint(15, 600)
            p = rng.randint(1, 60)
        else:
            base = rng.randrange(40, 420, 20)
            p = rng.choice([5, 10, 15, 20, 25, 30, 40])

        pct = sympy.Rational(p, 100)
        mult = 1 + pct if up else 1 - pct

        if v == "change":
            change = sympy.Rational(base) * pct
            new = sympy.Rational(base) * mult
            if new <= 0:
                continue
            if not calc and new.q != 1:
                continue
            check = (
                sympy.Rational(base) + change if up else sympy.Rational(base) - change
            )
            if sympy.simplify(new - check) != 0:
                continue

            if up:
                stem = (
                    f"The normal price of a {item} is £{base}. "
                    f"The price of the {item} is increased by {p}%."
                )
            else:
                stem = (
                    f"The normal price of a {item} is £{base}. "
                    f"In a sale the price is reduced by {p}%."
                )
            word = "+" if up else "−"
            working_a = (
                f"{p}% of £{base} = {_money(change)}\n"
                f"{'New' if up else 'Sale'} price = £{base} {word} {_money(change)} "
                f"= {_money(new)}"
            )
            ms_a = [
                MarkSchemeStep(
                    code="M1", mark_type="M",
                    description=f"for {p}/100 × £{base} (= {_money(change)})",
                    working=None,
                ),
                MarkSchemeStep(
                    code="M1", mark_type="M",
                    description=f"for £{base} {word} {_money(change)} (= {_money(new)})",
                    working=None,
                ),
                MarkSchemeStep(
                    code="A1", mark_type="A", description="cao", working=_money(new)
                ),
            ]
            prompt_a = f"Work out the {'new' if up else 'sale'} price of the {item}."

            # ~35% of the time, add a reasoning follow-up (b): a claim to test.
            if variant is None and rng.random() < 0.35 or (variant and rng.random() < 0.35):
                delta = sympy.Rational(rng.choice([-10, -5, 5, 10, 15]))
                claim_amt = change + delta
                if claim_amt <= 0:
                    claim_amt = change  # keep it a sensible, non-negative figure
                truth = change > claim_amt
                stmt = (
                    f"The price {'rise' if up else 'reduction'} is more than "
                    f"{_money(claim_amt)}."
                )
                verdict = "Yes" if truth else "No"
                part_a = mk_part(
                    label="a", prompt=prompt_a, marks=3, answer=_money(new),
                    working=working_a, mark_scheme=ms_a,
                )
                part_b = mk_part(
                    label="b", prompt=claim_prompt(name, stmt), marks=1,
                    answer=f"{verdict} — the {'rise' if up else 'reduction'} is "
                    f"{_money(change)}",
                    working=(
                        f"Actual {'rise' if up else 'reduction'} = {_money(change)}; "
                        f"{_money(change)} {'>' if truth else '≤'} {_money(claim_amt)}"
                    ),
                    mark_scheme=[
                        reason_step(
                            f"for the correct conclusion ({verdict}) with a reason "
                            f"comparing {_money(change)} and {_money(claim_amt)}"
                        )
                    ],
                )
                return make_item(
                    req, seed, archetype="percentage-change", topic="Percentages",
                    topic_slug="percentages", strand="Ratio & proportion",
                    spec_ref="R9", grade_band="4-6", ao="AO2", stem=stem,
                    parts=[part_a, part_b],
                )

            return _item(
                req, seed, archetype="percentage-change", topic="Percentages",
                topic_slug="percentages", strand="Ratio & proportion",
                spec_ref="R9", grade_band="4-6", marks=3, stem=stem,
                prompt=prompt_a, answer=_money(new), working=working_a,
                mark_scheme=ms_a,
            )

        # reverse percentage — 2 marks (recalibrated to real papers), contextual
        final = sympy.Rational(base) * mult
        if final <= 0:
            continue
        if not calc and final.q != 1:
            continue
        pct_of = 100 + p if up else 100 - p
        orig = sympy.Symbol("orig")
        sol = sympy.solve(sympy.Eq(orig * mult, final), orig)
        if sol != [sympy.Rational(base)]:
            continue

        if up:
            stem = (
                f"After a {p}% increase, the price of a {item} is {_money(final)}."
            )
        else:
            stem = (
                f"The normal price of a {item} is reduced by {p}% in a sale. "
                f"The price of the {item} in the sale is {_money(final)}."
            )
        working = (
            f"{_money(final)} represents {pct_of}% of the normal price.\n"
            f"Normal price = {_money(final)} ÷ {pct_of} × 100 = £{base}"
        )
        return _item(
            req, seed, archetype="reverse-percentage", topic="Percentages",
            topic_slug="percentages", strand="Ratio & proportion", spec_ref="R9",
            grade_band="4-6", marks=2,
            stem=stem, prompt="Work out the normal price of the " + item + ".",
            answer=f"£{base}", working=working,
            mark_scheme=[
                MarkSchemeStep(
                    code="M1", mark_type="M",
                    description=f"for {_money(final)} ÷ {pct_of} × 100 (= £{base})",
                    working=None,
                ),
                MarkSchemeStep(
                    code="A1", mark_type="A", description="cao", working=f"£{base}"
                ),
            ],
        )
    raise RuntimeError("percentages generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Standard form: calculate (bare), or (a) convert then (b) calculate  (N9)
# --------------------------------------------------------------------------- #
def _sf(mant: sympy.Rational, exp: int) -> str:
    """Render a number in standard form, e.g. '3.6 × 10⁸'."""
    ms = str(mant.p) if mant.q == 1 else f"{float(mant):g}"
    return f"{ms} × 10{str(exp).translate(_SUP)}"


def _normalise(mant: sympy.Rational, exp: int) -> tuple[sympy.Rational, int]:
    while mant >= 10:
        mant /= 10
        exp += 1
    while mant < 1:
        mant *= 10
        exp -= 1
    return mant, exp


def build_standard_form(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        op = rng.choice(["×", "÷"])
        m1 = rng.choice([2, 3, 4, 5, 6, 8])
        m2 = rng.choice([2, 3, 4, 5, 6, 8])
        n1 = rng.randint(-6, 10)
        n2 = rng.randint(-6, 10)

        if op == "×":
            raw_mant, raw_exp = sympy.Rational(m1 * m2), n1 + n2
        else:
            raw_mant, raw_exp = sympy.Rational(m1, m2), n1 - n2
        mant, exp = _normalise(raw_mant, raw_exp)
        if (mant * 10).q != 1:
            continue

        left = sympy.Rational(m1) * sympy.Integer(10) ** n1
        right = sympy.Rational(m2) * sympy.Integer(10) ** n2
        full = left * right if op == "×" else left / right
        if sympy.simplify(full - mant * sympy.Integer(10) ** exp) != 0:
            continue

        pow_op = "×" if op == "×" else "÷"
        working = (
            f"= ({m1} {op} {m2}) × (10{str(n1).translate(_SUP)} {pow_op} "
            f"10{str(n2).translate(_SUP)})\n= {_sf(raw_mant, raw_exp)}\n"
            f"= {_sf(mant, exp)}"
        )
        ms = [
            MarkSchemeStep(
                code="M1", mark_type="M",
                description=f"for ({m1} {op} {m2}) and (10{str(n1).translate(_SUP)} "
                f"{pow_op} 10{str(n2).translate(_SUP)})",
                working=None,
            ),
            MarkSchemeStep(
                code="A1", mark_type="A", description="cao, in standard form",
                working=_sf(mant, exp),
            ),
        ]

        # ~40%: multi-part — (a) write an ordinary number in standard form, then
        # (b) use it in the calculation.
        if n1 >= 2 and rng.random() < 0.4:
            ordinary = str(int(sympy.Rational(m1) * sympy.Integer(10) ** n1))
            part_a = mk_part(
                label="a", prompt=f"Write {ordinary} in standard form.", marks=1,
                answer=_sf(sympy.Rational(m1), n1),
                working=f"{ordinary} = {_sf(sympy.Rational(m1), n1)}",
                mark_scheme=[
                    MarkSchemeStep(
                        code="B1", mark_type="B", description="cao",
                        working=_sf(sympy.Rational(m1), n1),
                    )
                ],
            )
            part_b = mk_part(
                label="b",
                prompt=f"Work out {_sf(sympy.Rational(m1), n1)} {op} "
                f"{_sf(sympy.Rational(m2), n2)}. Give your answer in standard form.",
                marks=2, answer=_sf(mant, exp), working=working, mark_scheme=ms,
            )
            return make_item(
                req, seed, archetype="standard-form", topic="Standard form",
                topic_slug="standard-form", strand="Number", spec_ref="N9",
                grade_band="5-7", stem="", parts=[part_a, part_b],
            )

        return _item(
            req, seed, archetype="standard-form", topic="Standard form",
            topic_slug="standard-form", strand="Number", spec_ref="N9",
            grade_band="5-7", marks=2,
            stem=f"Work out  {_sf(sympy.Rational(m1), n1)} {op} "
            f"{_sf(sympy.Rational(m2), n2)}",
            prompt="Give your answer in standard form.",
            answer=_sf(mant, exp), working=working, mark_scheme=ms,
        )
    raise RuntimeError("standard-form generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Indices: single eval, combined two-term eval, or 'in the form 2ⁿ'  (N7)
# --------------------------------------------------------------------------- #
_ROOT_WORD = {2: "square root", 3: "cube root", 4: "fourth root"}


def _pow_str(value: sympy.Rational) -> str:
    return str(value.p) if value.q == 1 else f"{value.p}/{value.q}"


def _eval_index(rng: Random) -> tuple[int, int, int, sympy.Rational, str, str]:
    """Sample one evaluable power. Returns (base, en, ed, value, working, m1_desc)."""
    fam = rng.choice(["neg", "frac", "negfrac"])
    if fam == "neg":
        base = rng.randint(2, 6)
        n = rng.randint(1, 3)
        en, ed = -n, 1
        value = sympy.Rational(1, base**n)
        working = (
            f"{base}⁻{str(n).translate(_SUP)} = 1/{base}{str(n).translate(_SUP)} "
            f"= 1/{base**n}"
        )
        return base, en, ed, value, working, f"for writing as 1/{base}{str(n).translate(_SUP)}"
    ed = rng.choice([2, 3, 4]) if fam == "frac" else rng.choice([2, 3])
    kmax = {2: 9, 3: 5, 4: 3}[ed]
    k = rng.randint(2, kmax)
    base = k**ed
    en = rng.choice([1, 3] if ed in (2, 4) else [1, 2])
    if sympy.igcd(en, ed) != 1 or en == ed:
        raise ValueError
    if fam == "frac":
        value = sympy.Rational(k**en)
        if value > 400:
            raise ValueError
        working = (
            f"{base}^(1/{ed}) = {k}"
            + ("" if en == 1 else f"\n{base}^({en}/{ed}) = {k}^{en} = {value}")
        )
    else:
        en = -en
        value = sympy.Rational(1, k ** (-en))
        working = (
            f"{base}^({en}/{ed}) = 1/{base}^({-en}/{ed})\n"
            f"= 1/{k}^{-en} = {_pow_str(value)}"
        )
    return base, en, ed, value, working, f"for the {_ROOT_WORD[ed]} of {base} (= {k})"


def build_indices(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        shape = rng.choice(["single", "combined", "form"])

        if shape == "form":
            # Write (a^p × a^q) / a^r in the form aⁿ.
            a = rng.choice([2, 3, 5])
            p, q, r = rng.randint(2, 6), rng.randint(2, 6), rng.randint(1, 4)
            n = p + q - r
            if n <= 1:
                continue
            if sympy.simplify(sympy.Integer(a) ** n
                              - (sympy.Integer(a) ** p * sympy.Integer(a) ** q)
                              / sympy.Integer(a) ** r) != 0:
                continue
            sp = lambda z: str(z).translate(_SUP)
            expr = f"({a}{sp(p)} × {a}{sp(q)}) ÷ {a}{sp(r)}"
            return _item(
                req, seed, archetype="indices", topic="Indices",
                topic_slug="indices", strand="Number", spec_ref="N7",
                grade_band="5-8", marks=2,
                stem=f"Write  {expr}  in the form {a}ⁿ, where n is an integer.",
                prompt="", answer=f"{a}{sp(n)}",
                working=f"{expr} = {a}^({p} + {q} − {r}) = {a}{sp(n)}",
                mark_scheme=[
                    MarkSchemeStep(
                        code="M1", mark_type="M",
                        description=f"for {a}^({p} + {q} − {r}) (= {a}{sp(n)})",
                        working=None,
                    ),
                    MarkSchemeStep(
                        code="A1", mark_type="A", description="cao", working=f"{a}{sp(n)}"
                    ),
                ],
            )

        try:
            base, en, ed, value, working, m1 = _eval_index(rng)
        except ValueError:
            continue
        if sympy.simplify(sympy.Integer(base) ** sympy.Rational(en, ed) - value) != 0:
            continue
        exp_str = str(en) if ed == 1 else f"{en}/{ed}"

        if shape == "combined":
            try:
                base2, en2, ed2, value2, working2, m1b = _eval_index(rng)
            except ValueError:
                continue
            if sympy.simplify(sympy.Integer(base2) ** sympy.Rational(en2, ed2)
                              - value2) != 0:
                continue
            total = value + value2
            exp2 = str(en2) if ed2 == 1 else f"{en2}/{ed2}"
            return _item(
                req, seed, archetype="indices", topic="Indices",
                topic_slug="indices", strand="Number", spec_ref="N7",
                grade_band="6-8", marks=3,
                stem=f"Work out the value of  {base}^({exp_str}) + {base2}^({exp2})",
                prompt="",
                answer=_pow_str(total),
                working=f"{working}\n{working2}\n"
                f"{_pow_str(value)} + {_pow_str(value2)} = {_pow_str(total)}",
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M", description=m1, working=None),
                    MarkSchemeStep(code="M1", mark_type="M", description=m1b, working=None),
                    MarkSchemeStep(code="A1", mark_type="A", description="cao",
                                   working=_pow_str(total)),
                ],
            )

        return _item(
            req, seed, archetype="indices", topic="Indices", topic_slug="indices",
            strand="Number", spec_ref="N7", grade_band="5-8", marks=2,
            stem=f"Work out the value of  {base}^({exp_str})",
            prompt="", answer=_pow_str(value), working=working,
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M", description=m1, working=None),
                MarkSchemeStep(code="A1", mark_type="A", description="cao",
                               working=_pow_str(value)),
            ],
        )
    raise RuntimeError("indices generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# Surds — simplify a sum/difference, or rationalise a denominator  (N8, grade 8)
# --------------------------------------------------------------------------- #
def build_surds(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        shape = rng.choice(["simplify", "rationalise"])

        if shape == "simplify":
            b = rng.choice([2, 3, 5, 6, 7, 10])
            p = rng.randint(2, 6)
            q = rng.randint(1, p - 1)
            op = rng.choice(["+", "−"])
            X, Y = p * p * b, q * q * b
            # √X = p√b, √Y = q√b (b is square-free by construction)
            if _simplify_surd(X) != (p, b) or _simplify_surd(Y) != (q, b):
                continue
            res = p + q if op == "+" else p - q
            if res < 1:
                continue
            lhs = sympy.sqrt(X) + sympy.sqrt(Y) if op == "+" else sympy.sqrt(X) - sympy.sqrt(Y)
            if sympy.simplify(lhs - res * sympy.sqrt(b)) != 0:
                continue
            ans = _surd_str(res, b)
            return _item(
                req, seed, archetype="surds", topic="Surds", topic_slug="surds",
                strand="Number", spec_ref="N8", grade_band="7-9", marks=2,
                stem=f"Simplify fully  √{X} {op} √{Y}",
                prompt="", answer=ans,
                working=(f"√{X} = {p}√{b},  √{Y} = {q}√{b}\n"
                         f"√{X} {op} √{Y} = ({p} {op} {q})√{b} = {ans}"),
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description=f"for simplifying a surd (e.g. √{X} = {p}√{b})",
                                   working=f"{p}√{b}, {q}√{b}"),
                    MarkSchemeStep(code="A1", mark_type="A", description="cao",
                                   working=ans),
                ],
            )

        # rationalise k/√n
        n = rng.choice(_SQUARE_FREE)
        k = rng.choice([1, 1, 2, 3, 4, 6])
        g = sympy.igcd(k, n)
        num, den = k // g, n // g
        # k/√n = k√n/n = (num)√n/(den)
        if sympy.simplify(num * sympy.sqrt(n) / den - k / sympy.sqrt(n)) != 0:
            continue
        num_str = _surd_str(num, n)  # 'num√n' or '√n' when num == 1
        ans = num_str if den == 1 else f"{num_str}/{den}"
        k_str = "1" if k == 1 else str(k)
        return _item(
            req, seed, archetype="surds", topic="Surds", topic_slug="surds",
            strand="Number", spec_ref="N8", grade_band="7-9", marks=2,
            stem=f"Rationalise the denominator of  {k_str}/√{n}\nSimplify your answer "
            f"fully.",
            prompt="", answer=ans,
            working=f"{k_str}/√{n} = {k_str}√{n}/{n} = {ans}",
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for multiplying by √{n}/√{n}",
                               working=f"{k_str}√{n}/{n}"),
                MarkSchemeStep(code="A1", mark_type="A",
                               description="for the fully simplified answer",
                               working=ans),
            ],
        )
    raise RuntimeError("surds generator failed to produce a valid item.")


def _fr(r: sympy.Rational) -> str:
    r = sympy.Rational(r)
    return str(r.p) if r.q == 1 else f"{r.p}/{r.q}"


# --------------------------------------------------------------------------- #
# STRETCH: recurring decimal → fraction (grade 8, N10) — modelled on June2022 Q12
# --------------------------------------------------------------------------- #
def build_recurring_decimal(req: GenerateRequest) -> Item:
    """Multi-part: (a) a one-digit recurring decimal, (b) a two-digit one shown
    with full algebraic working — the standard grade 7-8 build-up."""
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        d = rng.randint(1, 8)                       # (a) 0.d recurring
        block = rng.randint(10, 98)                 # (b) 0.d1d2 recurring
        if block % 11 == 0:
            continue
        fa = sympy.Rational(d, 9)
        fb = sympy.Rational(block, 99)
        # independent checks against block/(10^len − 1)
        if sympy.simplify(fa - sympy.Rational(d, 9)) != 0:
            continue
        if sympy.simplify(fb - sympy.Rational(block, 99)) != 0:
            continue
        ans_a, ans_b = _fr(fa), _fr(fb)
        d1, d2 = divmod(block, 10)
        parts = [
            mk_part(
                label="a", prompt=f"Write 0.{d}̇ as a fraction in its simplest form.",
                marks=1, answer=ans_a,
                working=f"0.{d}{d}… = {d}/9 = {ans_a}",
                mark_scheme=[MarkSchemeStep(code="B1", mark_type="B",
                                            description="cao, simplest form",
                                            working=ans_a)]),
            mk_part(
                label="b",
                prompt=f"Write 0.{d1}̇{d2}̇ as a fraction in its simplest form. "
                "You must show all your working.",
                marks=3, answer=ans_b,
                working=(f"Let x = 0.{d1}{d2}{d1}{d2}…\n"
                         f"100x = {block}.{d1}{d2}{d1}{d2}…\n"
                         f"100x − x = {block}, so 99x = {block}\n"
                         f"x = {block}/99 = {ans_b}"),
                mark_scheme=[
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description=f"for forming x = 0.{d1}{d2}… and "
                                   f"100x = {block}.{d1}{d2}…", working=None),
                    MarkSchemeStep(code="M1", mark_type="M",
                                   description=f"for 100x − x = {block}, so 99x = {block}",
                                   working=None),
                    MarkSchemeStep(code="A1", mark_type="A",
                                   description="cao, simplest form", working=ans_b),
                ]),
        ]
        return make_item(
            req, seed, archetype="recurring-decimal", topic="Recurring decimals",
            topic_slug="recurring-decimals", strand="Number", spec_ref="N10",
            grade_band="7-8", ao="AO2",
            stem="", parts=parts,
        )
    raise RuntimeError("recurring-decimal generator failed to produce a valid item.")


# --------------------------------------------------------------------------- #
# STRETCH: index-law problem with fractional/negative powers (grade 8, N7)
#          modelled on June 2022 Q18
# --------------------------------------------------------------------------- #
def build_index_problem(req: GenerateRequest) -> Item:
    seed = _seed(req)
    rng = Random(seed)
    for _ in range(_MAX_ATTEMPTS):
        a = rng.randint(2, 7)
        b = rng.randint(2, 7)
        if a == b:
            continue
        A, B = a * a, b * b   # A/B is a perfect-square fraction
        k = rng.randint(1, 3)
        # value = (A/B)^(−1/2) × 2^(−k) = (b/a) × 1/2^k
        value = sympy.Rational(b, a) * sympy.Rational(1, 2 ** k)
        check = sympy.Rational(A, B) ** sympy.Rational(-1, 2) * sympy.Integer(2) ** (-k)
        if sympy.simplify(value - check) != 0:
            continue
        if value.q > 20:
            continue
        ans = _fr(value)
        return _item(
            req, seed, archetype="index-problem", topic="Indices",
            topic_slug="indices", strand="Number", spec_ref="N7", grade_band="7-9",
            marks=3,
            stem=f"Work out the value of  ({A}/{B})^(−1/2) × 2^(−{k})",
            prompt="Give your answer as a fraction in its simplest form. You must show "
            "all your working.", answer=ans,
            working=(f"({A}/{B})^(−1/2) = ({B}/{A})^(1/2) = {b}/{a}\n"
                     f"2^(−{k}) = 1/{2 ** k}\n"
                     f"{b}/{a} × 1/{2 ** k} = {ans}"),
            mark_scheme=[
                MarkSchemeStep(code="M1", mark_type="M",
                               description="for dealing with the negative-half power "
                               f"(({B}/{A})^(1/2) = {b}/{a})", working=None),
                MarkSchemeStep(code="M1", mark_type="M",
                               description=f"for 2^(−{k}) = 1/{2 ** k}", working=None),
                MarkSchemeStep(code="A1", mark_type="A", description="cao", working=ans),
            ],
        )
    raise RuntimeError("index-problem generator failed to produce a valid item.")
