"""Universal structural + determinism checks across EVERY registered archetype.

This is the regression backbone: if any generator ever produces an item whose
marks don't add up, whose answer is empty, whose SVG is malformed, or that isn't
reproducible from its seed, this test fails and names the archetype.
"""

import unittest

from app.generators.registry import ARCHETYPES, reasoning_steps
from tests.helpers import assert_item_valid, content, req

SEEDS = 30


class TestEveryArchetype(unittest.TestCase):
    def test_structure_and_determinism(self):
        for spec in ARCHETYPES:
            modes = [True] if spec.requires_calculator else [False, True]
            for calc in modes:
                for seed in range(SEEDS):
                    with self.subTest(archetype=spec.archetype, calc=calc, seed=seed):
                        it = spec.build(req(spec.archetype, calc, seed=seed))
                        assert_item_valid(self, it)
                        # same seed -> identical item (id aside)
                        again = spec.build(req(spec.archetype, calc, seed=seed))
                        self.assertEqual(content(it), content(again))

    def test_metadata_matches_registry(self):
        for spec in ARCHETYPES:
            with self.subTest(archetype=spec.archetype):
                it = spec.build(req(spec.archetype,
                                    True if spec.requires_calculator else None))
                self.assertEqual(it.metadata.topic_slug, spec.topic_slug)
                self.assertEqual(it.metadata.strand, spec.strand)

    def test_marks_earned_by_structure(self):
        # Task 5: a question's marks may not exceed the work in it —
        # marks <= steps + parts - 1. Guards against re-introducing padded marks.
        for spec in ARCHETYPES:
            steps = reasoning_steps(spec.archetype)
            modes = [True] if spec.requires_calculator else [False, True]
            for calc in modes:
                for seed in range(SEEDS):
                    with self.subTest(archetype=spec.archetype, calc=calc, seed=seed):
                        it = spec.build(req(spec.archetype, calc, seed=seed))
                        self.assertLessEqual(
                            it.total_marks, steps + len(it.parts) - 1,
                            f"{spec.archetype}: {it.total_marks} marks exceeds "
                            f"steps({steps}) + parts({len(it.parts)}) - 1")

    def test_no_archetype_raises(self):
        # every generator must produce an item for a spread of seeds, both modes
        for spec in ARCHETYPES:
            modes = [True] if spec.requires_calculator else [False, True]
            for calc in modes:
                for seed in range(SEEDS):
                    with self.subTest(archetype=spec.archetype, calc=calc, seed=seed):
                        spec.build(req(spec.archetype, calc, seed=seed))


if __name__ == "__main__":
    unittest.main()
