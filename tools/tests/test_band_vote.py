"""Tests for tools/band_vote.py (the owner's ruling A1 of 2026-10-24): the lower median and the settlements."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import band_vote  # noqa: E402


class LowerMedianTest(unittest.TestCase):
    def test_lower_median(self):
        self.assertEqual(band_vote.lower_median([1, 2, 4]), 2)
        self.assertEqual(band_vote.lower_median([3, 1]), 1)
        self.assertEqual(band_vote.lower_median([None, 2, 3]), 2)
        self.assertIsNone(band_vote.lower_median([]))


class FinalBandsTest(unittest.TestCase):
    rows = [{"slug": "rug-n", "lower_median": "2", "spread": "1"},
            {"slug": "odd-adj", "lower_median": "2", "spread": "3"},
            {"slug": "gone-n", "lower_median": "", "spread": ""}]

    def test_a_wide_split_needs_a_settlement(self):
        bands, unsettled = band_vote.final_bands(self.rows, {}, provisional=False)
        self.assertEqual(bands, {"rug-n": (2, "")})
        self.assertEqual(unsettled, ["odd-adj"])

    def test_settled_and_provisional(self):
        bands, _u = band_vote.final_bands(self.rows, {"odd-adj": (3, "read the votes")}, provisional=False)
        self.assertEqual(bands["odd-adj"][0], 3)
        bands, _u = band_vote.final_bands(self.rows, {}, provisional=True)
        self.assertEqual(bands["odd-adj"][0], 2)

    def test_the_scale_is_the_decision_page_scale(self):
        page = (Path(__file__).resolve().parents[2] / "wiki" / "decisions" / "rebanding.md").read_text(encoding="utf-8")
        for line in band_vote.SCALE.splitlines():
            key = line.split(":", 1)[1].split("(", 1)[0].strip()[:60]
            self.assertIn(key, page.replace("*", ""))

    def test_a_second_vote_of_the_day_keeps_the_first(self):
        old = [{"slug": "a-n", "lower_median": "2"}, {"slug": "b-n", "lower_median": "3"}]
        new = [{"slug": "b-n", "lower_median": "4"}, {"slug": "c-n", "lower_median": "1"}]
        merged = band_vote.merge_rows(old, new)
        self.assertEqual([r["slug"] for r in merged], ["a-n", "b-n", "c-n"])
        self.assertEqual(merged[1]["lower_median"], "4")


if __name__ == "__main__":
    unittest.main()
