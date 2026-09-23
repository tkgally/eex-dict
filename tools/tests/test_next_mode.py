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
