"""Shared helpers for the test suite.

Written on stdlib `unittest` so the suite runs with the project's own
interpreter (no extra install), while staying pytest-compatible.
"""

from __future__ import annotations

import re
import xml.dom.minidom as minidom

from sympy.parsing.sympy_parser import parse_expr

from app.schema import GenerateRequest


def req(archetype=None, calculator=None, tier=None, seed=0):
    return GenerateRequest(
        format="past-papers", qualification="gcse", board="edexcel",
        subject="maths", archetype=archetype, calculator=calculator, tier=tier,
        seed=seed,
    )


def content(item):
    """Everything that must be stable for a given seed (the id is a random uuid)."""
    d = item.model_dump()
    d.pop("id", None)
    return d


def assert_item_valid(tc, it):
    """Structural invariants every generated Item must satisfy."""
    tc.assertGreaterEqual(it.total_marks, 1)
    tc.assertEqual(it.total_marks, sum(p.marks for p in it.parts),
                   "total_marks must equal the sum of part marks")
    for p in it.parts:
        tc.assertEqual(sum(s.marks for s in p.mark_scheme), p.marks,
                       "mark-scheme marks must sum to the part's marks")
        tc.assertTrue(p.answer.strip(), "answer must be non-empty")
        tc.assertTrue(p.prompt.strip() or it.stem.strip(),
                      "a part must have a prompt or the item a stem")
    if it.diagram:
        minidom.parseString(it.diagram.svg)                 # well-formed XML
        tc.assertIn("currentColor", it.diagram.svg)
        tc.assertTrue(it.diagram.svg.startswith("<svg"))
    if it.table:
        for row in it.table.rows:
            tc.assertEqual(len(row), len(it.table.headers),
                           "every table row must match the header width")


# --- parsing helpers for independent numeric re-derivation ------------------ #
def poly(s, loc=None):
    """Parse a GCSE-style expression ('3x²', '(x-5)(x+2)') into sympy."""
    s = (s.replace("²", "**2").replace("³", "**3").replace("−", "-")
         .replace(")(", ")*("))
    s = re.sub(r"(\d)([a-zA-Z(])", r"\1*\2", s)   # 3x -> 3*x, 2( -> 2*(
    return parse_expr(s, local_dict=loc or {})
