"""Tests for tools/spend.py against a temporary ledger: check, record, rollover, CLI."""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import spend  # noqa: E402

TODAY = "2026-09-16"
YESTERDAY = "2026-09-15"


class SpendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "config" / "budget-ledger.json"
        # spend.py reports ledger creation and rollovers on stderr; keep the test run quiet
        self._quiet = contextlib.redirect_stderr(io.StringIO())
        self._quiet.__enter__()

    def tearDown(self):
        self._quiet.__exit__(None, None, None)
        self.tmp.cleanup()

    def read(self):
        return json.loads(self.ledger.read_text(encoding="utf-8"))

    def test_fresh_ledger_shape(self):
        ledger, changed = spend.load_ledger(self.ledger, today=TODAY)
        self.assertTrue(changed)
        self.assertTrue(self.ledger.is_file())
        data = self.read()
        self.assertEqual(list(data), ["_doc", "daily_cap_usd", "date", "spent_usd", "calls", "history"])
        self.assertEqual(data["daily_cap_usd"], 5.0)
        self.assertEqual(data["date"], TODAY)
        self.assertEqual(data["spent_usd"], 0.0)
        self.assertEqual(data["calls"], [])
        self.assertEqual(data["history"], {})

    def test_check_within_and_over_cap(self):
        ok, left, _ = spend.check(self.ledger, 1.0, today=TODAY)
        self.assertTrue(ok)
        self.assertEqual(left, 4.0)
        ok, left, _ = spend.check(self.ledger, 5.0, today=TODAY)   # exactly the cap is allowed
        self.assertTrue(ok)
        self.assertEqual(left, 0.0)
        ok, left, _ = spend.check(self.ledger, 5.000001, today=TODAY)
        self.assertFalse(ok)
        self.assertEqual(left, -0.000001)
        with self.assertRaises(ValueError):
            spend.check(self.ledger, -1, today=TODAY)

    def test_record_appends_and_sums_rounded(self):
        spend.record(self.ledger, 0.0012345678, "review", "openai/x", 100, 20,
                     run_id="r1", today=TODAY, ts="2026-09-16T10:00:00Z")
        ledger = spend.record(self.ledger, 0.0000004, "review", "google/y", 5, 1,
                              run_id="r1", today=TODAY)
        self.assertEqual(len(ledger["calls"]), 2)
        first = ledger["calls"][0]
        self.assertEqual(first, {"ts": "2026-09-16T10:00:00Z", "run_id": "r1", "purpose": "review",
                                 "model": "openai/x", "cost_usd": 0.001235, "tokens_in": 100,
                                 "tokens_out": 20})
        self.assertEqual(ledger["spent_usd"], 0.001235)          # 6-decimal rounding
        self.assertEqual(self.read()["spent_usd"], 0.001235)
        ok, left, _ = spend.check(self.ledger, 4.998765, today=TODAY)
        self.assertTrue(ok)
        ok, _, _ = spend.check(self.ledger, 4.998766, today=TODAY)
        self.assertFalse(ok)

    def test_rollover_moves_total_into_history(self):
        self.ledger.parent.mkdir(parents=True)
        self.ledger.write_text(json.dumps({
            "_doc": "x", "daily_cap_usd": 5.0, "date": YESTERDAY, "spent_usd": 1.25,
            "calls": [{"ts": "t", "run_id": "r", "purpose": "p", "model": "m",
                       "cost_usd": 1.25, "tokens_in": 1, "tokens_out": 1}],
            "history": {"2026-09-10": 0.5}}), encoding="utf-8")
        ok, left, ledger = spend.check(self.ledger, 4.9, today=TODAY)
        self.assertTrue(ok)                                     # yesterday's spend no longer counts
        self.assertEqual(ledger["date"], TODAY)
        self.assertEqual(ledger["spent_usd"], 0.0)
        self.assertEqual(ledger["calls"], [])
        self.assertEqual(ledger["history"], {"2026-09-10": 0.5, YESTERDAY: 1.25})
        self.assertEqual(self.read()["history"][YESTERDAY], 1.25)   # persisted
        # a same-day load does not roll over again
        ledger, changed = spend.load_ledger(self.ledger, today=TODAY)
        self.assertFalse(changed)
        self.assertEqual(ledger["history"], {"2026-09-10": 0.5, YESTERDAY: 1.25})

    def test_default_run_id_reads_tmp_file(self):
        root = Path(self.tmp.name)
        (root / ".tmp").mkdir()
        (root / ".tmp" / "run-id").write_text("20260916T130600Z-1yir52\n", encoding="utf-8")
        self.assertEqual(spend.default_run_id(root), "20260916T130600Z-1yir52")

    def test_status_text(self):
        spend.record(self.ledger, 0.5, "p", "m", run_id="r", today=TODAY)
        ledger, _ = spend.load_ledger(self.ledger, today=TODAY)
        ledger["history"] = {f"2026-09-{d:02d}": d / 100 for d in range(1, 11)}
        text = spend.status_text(ledger)
        self.assertIn(f"date:      {TODAY}", text)
        self.assertIn("spent:     $0.500000", text)
        self.assertIn("remaining: $4.500000", text)
        self.assertIn("calls:     1", text)
        history_lines = [ln for ln in text.splitlines() if ln.startswith("  2026-")]
        self.assertEqual(len(history_lines), 7)
        self.assertTrue(history_lines[0].startswith("  2026-09-10"))

    def test_cli(self):
        def run(*args):
            return subprocess.run([sys.executable, str(TOOLS / "spend.py"), "--ledger", str(self.ledger), *args],
                                  capture_output=True, text=True)
        p = run("check", "--cost", "0.25")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("remaining", p.stdout)
        p = run("record", "--cost", "0.25", "--purpose", "smoke", "--model", "a/b",
                "--tokens-in", "10", "--tokens-out", "2", "--run-id", "test")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("today's total $0.250000", p.stdout)
        p = run("check", "--cost", "4.75")
        self.assertEqual(p.returncode, 0, p.stderr)
        p = run("check", "--cost", "4.750001")
        self.assertEqual(p.returncode, 1)
        self.assertIn("refused", p.stdout)
        p = run("status")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("calls:     1", p.stdout)
        data = self.read()
        self.assertEqual(data["calls"][0]["run_id"], "test")
        self.assertEqual(data["calls"][0]["tokens_in"], 10)


if __name__ == "__main__":
    unittest.main()
