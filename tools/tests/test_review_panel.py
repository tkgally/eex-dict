"""Tests for tools/review_panel.py's family switch-off: an issue from a (role, family) pair
in DISABLED_FAMILIES is downgraded to "ok" before adjudication, per the 2026-09-19 lint run's
30-percent rule (wiki/notes/reviewer-precision.md); and for --decide's --quote disambiguator,
which fixes the 2026-09-19 collision where two issues on the same field/role logged against
the same last verdict (wiki/notes/review-panel-decide-collisions.md)."""

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import eexlib  # noqa: E402
import review_panel  # noqa: E402

FIELDS = ["headword_and_pos", "senses[0].examples"]


def raw_reply(field, family):
    return {"verdicts": [
        {"field": "headword_and_pos", "verdict": "ok"},
        {"field": field, "verdict": "issue", "severity": "blocking", "family": family, "reason": "x", "quote": "y"},
    ]}


class TestFamilySwitchOff(unittest.TestCase):
    def test_disabled_pair_is_downgraded_to_ok(self):
        role, family = next(iter(review_panel.DISABLED_FAMILIES))
        verdicts, err = review_panel.normalize_verdicts(raw_reply("senses[0].examples", family), FIELDS, role)
        self.assertIsNone(err)
        v = next(v for v in verdicts if v["field"] == "senses[0].examples")
        self.assertEqual(v["verdict"], "ok")
        self.assertIsNone(v["family"])
        self.assertIsNone(v["reason"])

    def test_same_family_stays_an_issue_for_a_role_not_switched_off(self):
        role, family = next(iter(review_panel.DISABLED_FAMILIES))
        other_role = "reviewer-a" if role == "reviewer-b" else "reviewer-b"
        if (other_role, family) in review_panel.DISABLED_FAMILIES:
            self.skipTest("this family is switched off for both roles")
        verdicts, err = review_panel.normalize_verdicts(raw_reply("senses[0].examples", family), FIELDS, other_role)
        self.assertIsNone(err)
        v = next(v for v in verdicts if v["field"] == "senses[0].examples")
        self.assertEqual(v["verdict"], "issue")
        self.assertEqual(v["family"], family)

    def test_unrelated_family_is_unaffected(self):
        verdicts, err = review_panel.normalize_verdicts(raw_reply("senses[0].examples", "pronunciation"),
                                                          FIELDS, "reviewer-a")
        self.assertIsNone(err)
        v = next(v for v in verdicts if v["field"] == "senses[0].examples")
        self.assertEqual(v["verdict"], "issue")
        self.assertEqual(v["family"], "pronunciation")


class TestDecideCollisions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="eex-review-panel-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.old_root = eexlib.ROOT
        eexlib.set_root(self.root)
        self.addCleanup(eexlib.set_root, self.old_root)
        rec = {"run_id": "run1", "slug": "they-pron", "entry_modified": "2026-09-19T00:00:00Z",
               "reviewers": [{"role": "reviewer-a", "verdicts": [
                   {"field": "adaptation", "verdict": "issue", "severity": "blocking", "family": "adaptation",
                    "reason": "scope claim", "quote": "singular they covers a known nonbinary referent"},
                   {"field": "adaptation", "verdict": "issue", "severity": "minor", "family": "adaptation",
                    "reason": "typological hedge", "quote": "many languages mark this"},
               ]}]}
        eexlib.save_json(self.root / "reviews" / "run1" / "they-pron.json", rec)
        self.decisions_path = self.root / "reviews" / "decisions.jsonl"

    def decide(self, **kw):
        defaults = {"slug": "they-pron", "field": "adaptation", "role": "reviewer-a", "decision": "apply",
                    "note": "n", "quote": "", "index": None}
        defaults.update(kw)
        return review_panel.decide(argparse.Namespace(**defaults))

    def test_ambiguous_without_quote_logs_nothing(self):
        code = self.decide()
        self.assertEqual(code, 1)
        self.assertFalse(self.decisions_path.exists())

    def test_quote_disambiguates_and_logs_the_right_severity(self):
        code = self.decide(quote="many languages mark this")
        self.assertEqual(code, 0)
        logged = json.loads(self.decisions_path.read_text(encoding="utf-8").strip())
        self.assertEqual(logged["severity"], "minor")
        self.assertEqual(logged["note"], "n")

    def test_quote_matching_nothing_logs_nothing(self):
        code = self.decide(quote="not in either quote")
        self.assertEqual(code, 1)
        self.assertFalse(self.decisions_path.exists())

    def test_unambiguous_field_needs_no_quote(self):
        rec = eexlib.load_json(self.root / "reviews" / "run1" / "they-pron.json")
        rec["reviewers"][0]["verdicts"] = rec["reviewers"][0]["verdicts"][:1]
        eexlib.save_json(self.root / "reviews" / "run1" / "they-pron.json", rec)
        code = self.decide()
        self.assertEqual(code, 0)

    def test_index_disambiguates_by_position(self):
        code = self.decide(index=2)
        self.assertEqual(code, 0)
        logged = json.loads(self.decisions_path.read_text(encoding="utf-8").strip())
        self.assertEqual(logged["severity"], "minor")

    def test_index_out_of_range_logs_nothing(self):
        code = self.decide(index=3)
        self.assertEqual(code, 1)
        self.assertFalse(self.decisions_path.exists())


class TestDecideSubstringCollision(unittest.TestCase):
    """wiki/notes/review-panel-decide-substring-collision.md: --quote alone cannot separate an
    issue quoting a whole sentence from one quoting just its tail, since the tail is a substring
    of the full quote either way; --index breaks the tie by position."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="eex-review-panel-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.old_root = eexlib.ROOT
        eexlib.set_root(self.root)
        self.addCleanup(eexlib.set_root, self.old_root)
        rec = {"run_id": "run1", "slug": "pick-up-phrv", "entry_modified": "2026-09-20T00:00:00Z",
               "reviewers": [{"role": "reviewer-a", "verdicts": [
                   {"field": "core_idea", "verdict": "issue", "severity": "blocking", "family": "sense-structure",
                    "reason": "two ideas", "quote": "To pick up is to lift something and starting something."},
                   {"field": "core_idea", "verdict": "issue", "severity": "minor", "family": "definition-style",
                    "reason": "tense mismatch", "quote": "starting something"},
               ]}]}
        eexlib.save_json(self.root / "reviews" / "run1" / "pick-up-phrv.json", rec)
        self.decisions_path = self.root / "reviews" / "decisions.jsonl"

    def decide(self, **kw):
        defaults = {"slug": "pick-up-phrv", "field": "core_idea", "role": "reviewer-a", "decision": "apply",
                    "note": "n", "quote": "", "index": None}
        defaults.update(kw)
        return review_panel.decide(argparse.Namespace(**defaults))

    def test_quote_alone_still_ambiguous(self):
        code = self.decide(quote="starting something")
        self.assertEqual(code, 1)
        self.assertFalse(self.decisions_path.exists())

    def test_index_resolves_it(self):
        code = self.decide(quote="starting something", index=2)
        self.assertEqual(code, 0)
        logged = json.loads(self.decisions_path.read_text(encoding="utf-8").strip())
        self.assertEqual(logged["family"], "definition-style")
        self.assertEqual(logged["severity"], "minor")


if __name__ == "__main__":
    unittest.main()
