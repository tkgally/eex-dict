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


class NoFallbackTest(unittest.TestCase):
    """The owner's ruling C1 of 2026-10-24: a back-link only where one sense clearly matches."""

    def test_unclear_target_gets_nothing(self):
        target = entry("drive", "control a car, bus, or other vehicle so that it moves",
                       "travel somewhere in a car", "take someone somewhere in a car")
        source = entry("run", "take someone or something somewhere quickly, especially in a car")
        self.assertIsNone(crossref.add_backlink(target, "synonyms", "run-v", source, 0))
        self.assertFalse(any(s.get("synonyms") for s in target["senses"]))

    def test_one_sense_target_is_clear(self):
        target = entry("flee", "run away from danger")
        self.assertEqual(crossref.add_backlink(target, "synonyms", "escape-v", entry("escape", "get away"), 0), "senses[0].synonyms")

    def test_the_one_sense_using_the_source_headword_is_clear(self):
        target = entry("sharp", "able to cut easily", "quick to understand and clever", "sudden and large")
        self.assertEqual(crossref.clear_sense(target, "clever-adj", "clever"), 1)
        target["senses"][2]["definition"] = "clever and sudden"
        self.assertIsNone(crossref.clear_sense(target, "clever-adj", "clever"))

    def test_two_senses_naming_the_source_are_not_clear(self):
        target = entry("cut", "divide with a knife", "reduce an amount")
        target["senses"][0]["compare"] = [{"slug": "chop-v", "note": None}]
        target["senses"][1]["compare"] = [{"slug": "chop-v", "note": None}]
        self.assertIsNone(crossref.clear_sense(target, "chop-v", "chop"))

    def test_ruled_out_targets(self):
        import eexlib
        rows = [{"headword": "look at", "pos": "phrv", "status": "duplicate", "note": "verb + preposition fence"},
                {"headword": "ing", "pos": "suffix", "status": "duplicate", "note": "hyphen lost"},
                {"headword": "-ing", "pos": "suffix", "status": "done", "note": ""}]
        ruled = eexlib.ruled_out_targets(rows)
        self.assertIn("look-at-phrv", ruled)
        self.assertIn("out-of-prep", ruled)            # the fenced list
        self.assertNotIn("ing-suffix", ruled)          # its real row is live

    def test_missing_senses_report(self):
        run = entry("run", "move quickly on foot", "manage a business")
        run["slug"] = "run-v"
        run["senses"][0]["synonyms"] = [{"slug": "control-v", "note": None}]      # the old fallback's placement
        control = entry("control", "have power over a business or a group")
        control["slug"] = "control-v"
        control["senses"][0]["synonyms"] = [{"slug": "run-v", "note": None}]
        lines = crossref.missing_senses({"run-v": (None, run), "control-v": (None, control)}, ["control-v"])
        self.assertEqual(len(lines), 1)
        self.assertIn("run-v (names it only on sense 1) for control-v sense", lines[0])


class OtherTypeLinkTest(unittest.TestCase):
    """2026-09-26: contain/include and tell/inform became both synonym and compare."""

    def test_compare_blocks_a_synonym_backlink(self):
        target = entry("contain", "have something inside")
        target["senses"][0]["compare"] = [{"slug": "include-v", "note": None}]
        self.assertEqual(crossref.other_type_link(target, "synonyms", "include-v"), "compare")

    def test_synonym_blocks_a_compare_backlink(self):
        target = entry("tell", "give information to someone", "order someone")
        target["senses"][1]["synonyms"] = [{"slug": "inform-v", "note": None}]
        self.assertEqual(crossref.other_type_link(target, "compare", "inform-v"), "synonyms")

    def test_same_type_or_no_link_is_none(self):
        target = entry("tell", "give information to someone")
        target["senses"][0]["synonyms"] = [{"slug": "inform-v", "note": None}]
        self.assertIsNone(crossref.other_type_link(target, "synonyms", "inform-v"))
        self.assertIsNone(crossref.other_type_link(target, "antonyms", "ask-v"))


if __name__ == "__main__":
    unittest.main()
