"""Tests for tools/review_panel.py's family switch-off: an issue from a (role, family) pair
in DISABLED_FAMILIES is downgraded to "ok" before adjudication, per the 2026-09-19 lint run's
30-percent rule (wiki/notes/reviewer-precision.md)."""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

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


if __name__ == "__main__":
    unittest.main()
