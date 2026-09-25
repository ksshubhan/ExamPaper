"""Paper-assembly invariants: ramp, tiers, mark consistency, robustness."""

import unittest
from random import Random

from app.assembler import build_paper
from app.generators.registry import topics_catalog
from app.schema import GeneratePaperRequest

ALL_SLUGS = [t["slug"] for g in topics_catalog() for t in g["topics"]]


def _gl(band):
    return int(band.split("-")[0])


class TestAssembler(unittest.TestCase):
    def _paper(self, **kw):
        base = dict(topics=ALL_SLUGS, calculator=False, target_marks=80, seed=7)
        base.update(kw)
        return build_paper(GeneratePaperRequest(**base))

    def test_marks_consistent_and_ramp_monotonic(self):
        p = self._paper()
        grades = [_gl(q.metadata.grade_band) for q in p.questions]
        self.assertEqual(grades, sorted(grades), "questions must ramp easy -> hard")
        for q in p.questions:
            self.assertEqual(q.total_marks, sum(pt.marks for pt in q.parts))
        self.assertGreaterEqual(p.total_marks, p.target_marks - 10)

    def test_higher_reaches_top_band(self):
        p = self._paper(tier="higher")
        self.assertGreaterEqual(max(_gl(q.metadata.grade_band) for q in p.questions), 7)
        self.assertIn("Higher Tier", p.title)
        self.assertTrue(all(q.tier == "higher" for q in p.questions))

    def test_foundation_caps_at_grade_5(self):
        p = self._paper(tier="foundation")
        self.assertLessEqual(max(_gl(q.metadata.grade_band) for q in p.questions), 5)
        self.assertIn("Foundation Tier", p.title)
        self.assertTrue(all(q.tier == "foundation" for q in p.questions))

    def test_front_is_easier_than_back(self):
        p = self._paper()
        g = [_gl(q.metadata.grade_band) for q in p.questions]
        third = len(g) // 3
        self.assertLess(sum(g[:third]) / third, sum(g[-third:]) / third)

    def test_random_papers_robust(self):
        rng = Random(0)
        for _ in range(120):
            k = rng.randint(1, len(ALL_SLUGS))
            topics = rng.sample(ALL_SLUGS, k)
            p = build_paper(GeneratePaperRequest(
                topics=topics, calculator=rng.random() < 0.5,
                tier=rng.choice(["higher", "foundation"]),
                target_marks=rng.choice([40, 60, 80]), seed=rng.randrange(2 ** 31)))
            g = [_gl(q.metadata.grade_band) for q in p.questions]
            self.assertEqual(g, sorted(g))
            for q in p.questions:
                self.assertEqual(q.total_marks, sum(pt.marks for pt in q.parts))

    def test_empty_and_unknown_topics_handled(self):
        p = build_paper(GeneratePaperRequest(topics=[], seed=1))
        self.assertEqual(p.total_marks, 0)
        self.assertTrue(p.notes)
        p2 = build_paper(GeneratePaperRequest(topics=["nonexistent-topic"], seed=1))
        self.assertEqual(p2.total_marks, 0)


if __name__ == "__main__":
    unittest.main()
