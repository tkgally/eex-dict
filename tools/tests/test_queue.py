"""Tests for tools/queue.py's stale-claim reset: a `claimed` row that no claim file lists goes back
to `pending` on `queue.py sync` (wiki/notes/queue-stale-claimed-rows.md)."""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("eex_queue", TOOLS / "queue.py")
eex_queue = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eex_queue)


class ResetStaleClaimsTest(unittest.TestCase):
    def rows(self):
        return [{"headword": "care", "pos": "v", "status": "claimed", "note": "votes 2"},
                {"headword": "carry", "pos": "v", "status": "claimed", "note": ""},
                {"headword": "cat", "pos": "n", "status": "pending", "note": ""}]

    def test_unlisted_claim_is_reset_and_listed_one_kept(self):
        rows = self.rows()
        reset = eex_queue.reset_stale_claims(rows, {"carry-v"})
        self.assertEqual(reset, ["care-v"])
        self.assertEqual([r["status"] for r in rows], ["pending", "claimed", "pending"])
        self.assertIn("stale claim reset", rows[0]["note"])

    def test_note_is_not_repeated(self):
        rows = self.rows()
        eex_queue.reset_stale_claims(rows, set())
        rows[0]["status"] = "claimed"
        eex_queue.reset_stale_claims(rows, set())
        self.assertEqual(rows[0]["note"].count("stale claim reset"), 1)


if __name__ == "__main__":
    unittest.main()
