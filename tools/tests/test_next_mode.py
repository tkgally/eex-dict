"""Tests for tools/next_mode.py's run count: a run that called metrics.py twice counts once
(wiki/notes/metrics-duplicate-calls.md)."""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import next_mode  # noqa: E402


class DedupeRunsTest(unittest.TestCase):
    def test_duplicate_run_counts_once_with_its_last_row(self):
        rows = [{"run_id": "a", "ts": "1", "mode": "lint"},
                {"run_id": "b", "ts": "2", "mode": "build", "n": 1},
                {"run_id": "b", "ts": "3", "mode": "build", "n": 2},
                {"ts": "4", "mode": "review"},
                {"run_id": "c", "ts": "5", "mode": "review"}]
        out = next_mode.dedupe_runs(rows)
        self.assertEqual([r.get("run_id") for r in out], ["a", "b", None, "c"])
        self.assertEqual(out[1]["n"], 2)


if __name__ == "__main__":
    unittest.main()


class DigestDueTests(unittest.TestCase):
    """The owner's ruling E3 (iv) of 2026-10-24: a weekly digest, due seven days after the last."""

    def test_due_without_a_digest_and_seven_days_after_one(self):
        import tempfile
        from datetime import date
        import digest
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "journal").mkdir()
            self.assertTrue(digest.is_due(root, date(2026, 10, 24)))
            (root / "journal" / "digest-2026-10-20.md").write_text("# Digest\n", encoding="utf-8")
            self.assertFalse(digest.is_due(root, date(2026, 10, 26)))
            self.assertTrue(digest.is_due(root, date(2026, 10, 27)))

    def test_escalation_needs_both_reviewers_rejected_on_meaning(self):
        import digest
        base = {"run_id": "r1", "slug": "bunch-n", "field": "senses[2].labels", "family": "label", "ts": "2026-10-20T00:00:00Z"}
        both = [dict(base, role="reviewer-a", decision="reject"), dict(base, role="reviewer-b", decision="reject")]
        self.assertEqual([x["slug"] for x in digest.escalations(both)], ["bunch-n"])
        one_applied = [dict(base, role="reviewer-a", decision="apply"), dict(base, role="reviewer-b", decision="reject")]
        self.assertEqual(digest.escalations(one_applied), [])
        spelling = [dict(x, family="spelling-or-format") for x in both]
        self.assertEqual(digest.escalations(spelling), [])
