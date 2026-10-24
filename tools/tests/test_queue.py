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


def row(hw, pos, status="pending", source="crossref", note="", band="3"):
    return {"headword": hw, "pos": pos, "band": band, "source": source, "status": status, "added": "2026-10-01", "note": note}


class DisplayFormsTest(unittest.TestCase):
    """The owner's ruling C3 of 2026-10-24: queue rows keep their hyphens and periods."""

    def test_add_rows_matches_an_existing_row_by_slug(self):
        rows = [row("brother-in-law", "n", source="defining")]
        added, _updated = eex_queue.add_rows(rows, [{"headword": "brother in law", "pos": "n", "band": "3",
                                                     "source": "crossref", "note": "referenced by brother-n"}])
        self.assertEqual(added, 0)
        self.assertEqual(len(rows), 1)
        self.assertIn("referenced by brother-n", rows[0]["note"])

    def test_repair_marks_the_lossy_twin_duplicate(self):
        rows = [row("mother-in-law", "n"), row("mother in law", "n")]
        changes = eex_queue.repair_forms(rows, {})
        self.assertEqual([r["status"] for r in rows], ["pending", "duplicate"])
        self.assertIn("the real row is mother-in-law", rows[1]["note"])
        self.assertEqual(len(changes), 1)

    def test_repair_restores_affix_hyphens_and_prose_forms(self):
        ref = {"slug": "shirt-n", "senses": [{"definition": "a piece of clothing", "examples": [{"text": "a white T-shirt"}]}]}
        rows = [row("ible", "suffix", note="referenced by able-suffix"), row("dis", "prefix"),
                row("t shirt", "n", note="referenced by shirt-n"), row("ice cream", "n", note="referenced by shirt-n")]
        eex_queue.repair_forms(rows, {"shirt-n": ref})
        self.assertEqual([r["headword"] for r in rows], ["-ible", "dis-", "T-shirt", "ice cream"])
        self.assertIn("repaired from t shirt", rows[2]["note"])

    def test_slug_index_prefers_the_real_row(self):
        rows = [row("-less", "suffix", status="done", band="1"), row("less", "suffix", status="duplicate")]
        self.assertEqual(eex_queue.slug_index(rows)["less-suffix"]["headword"], "-less")
        rows.reverse()
        self.assertEqual(eex_queue.slug_index(rows)["less-suffix"]["headword"], "-less")

    def test_guess_display_form(self):
        import eexlib
        self.assertEqual(eexlib.guess_display_form("am-abbr", ["at 9 a.m. today"]), "a.m.")
        self.assertEqual(eexlib.guess_display_form("look-forward-to-phrv"), "look forward to")
        self.assertEqual(eexlib.guess_display_form("x-ray-n", ["an X-ray of the chest"]), "X-ray")
        self.assertEqual(eexlib.guess_display_form("ee-suffix"), "-ee")
        self.assertEqual(eexlib.guess_display_form("us-pron", ["the U.S. and us"]), "us")


class ClosurePauseTest(unittest.TestCase):
    """The owner's ruling A3 of 2026-10-24: closure sources draw only bands 1 and 2 until band 2 is finished."""

    def test_pause_holds_while_band_2_has_pending_rows(self):
        import eexlib
        rows = [row("cat", "n", band="1", status="done"), row("vane", "n", band="4"), row("borrow", "v", band="2")]
        self.assertTrue(eexlib.closure_paused(rows))
        self.assertFalse(eexlib.closure_row_allowed(rows[1], True))
        self.assertTrue(eexlib.closure_row_allowed(rows[2], True))
        rows[2]["status"] = "done"
        self.assertFalse(eexlib.closure_paused(rows))
        self.assertTrue(eexlib.closure_row_allowed(rows[1], False))


if __name__ == "__main__":
    unittest.main()
