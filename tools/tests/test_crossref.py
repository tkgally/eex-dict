"""Tests for crossref.py's back-link sense placement."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import crossref  # noqa: E402


def entry(headword, *defs):
    return {"headword": headword, "senses": [{"definition": d, "explanation": None} for d in defs]}


class BestSenseTest(unittest.TestCase):
    def test_picks_overlapping_sense(self):
        target = entry("drive", "control a car, bus, or other vehicle so that it moves",
                       "travel somewhere in a car", "take someone somewhere in a car")
        source = entry("run", "take someone or something somewhere quickly, especially in a car")
        self.assertEqual(crossref.best_sense(target, source["senses"][0], "run"), 2)

    def test_weak_overlap_stays_on_first_sense(self):
        target = entry("drop", "let something fall, by accident or on purpose",
                       "become lower in amount, level, or value")
        source = entry("catch", "take hold of something that is moving through the air")
        self.assertEqual(crossref.best_sense(target, source["senses"][0], "catch"), 0)

    def test_no_source_sense_is_first(self):
        self.assertEqual(crossref.best_sense(entry("x", "a", "b"), None), 0)

    def test_existing_mention_wins(self):
        target = entry("cut", "divide with a knife", "reduce an amount")
        target["senses"][1]["compare"] = [{"slug": "chop-v", "note": None}]
        source = entry("chop", "divide with a knife into pieces")
        loc = crossref.add_backlink(target, "synonyms", "chop-v", source, 0)
        self.assertEqual(loc, "senses[1].synonyms")
        self.assertEqual(target["senses"][1]["synonyms"], [{"slug": "chop-v", "note": None}])


if __name__ == "__main__":
    unittest.main()
