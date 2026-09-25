# Test suite

Verifies the question engine. Written on stdlib `unittest` so it runs with the
project's own interpreter (no extra install), and is also discovered by `pytest`
if you add it.

## Run it

From the `backend/` directory:

```bash
# stdlib — no install needed (uses the project venv)
../.venv/bin/python -m unittest discover -s tests -t . -v
```

Or, if you install pytest into a dev environment (see `requirements-dev.txt`):

```bash
pytest tests -q
```

## What it covers

| File | What it checks |
|---|---|
| `test_structural.py` | **Every** registered archetype × both calculator modes × 30 seeds: total marks = Σ part marks, each mark scheme sums to its part, answers non-empty, SVG well-formed, tables rectangular, **determinism** (same seed → same item), metadata matches the registry, and no generator raises. |
| `test_diagrams.py` | Every diagram primitive returns well-formed, theme-safe (`currentColor`) SVG; bar heights encode frequency; polygons have the right vertex count. |
| `test_assembler.py` | Papers ramp easy→hard, marks are consistent, Higher reaches grade 7+, **Foundation caps at grade 5**, tier flows to each item, and 120 random papers assemble without error. |
| `test_numeric.py` | **Independent sympy re-derivation** of the answer from the question text for 27 archetypes spanning every strand (fractions, percentages, indices, standard form, quadratics, surds, sequences, gradient/line/midpoint, circle measures, bearings, vectors, area, HCF/LCM, averages, probability, ratios, substitution, quadratic formula, algebraic proof, …). |

The structural suite is the regression backbone (covers all 119 archetypes); the
numeric suite proves the maths for the computational core of each strand.
