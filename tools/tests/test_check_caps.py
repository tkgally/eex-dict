"""Tests for tools/check_caps.py: an over-cap file, a compliant one, absent files, log entries."""

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import check_caps  # noqa: E402


def quiet_main(argv):
    """check_caps.main() with its table swallowed, so test output stays readable."""
    with contextlib.redirect_stdout(io.StringIO()):
        return check_caps.main(argv)


def words(n: int, word: str = "w") -> str:
    return " ".join(f"{word}{i}" for i in range(n)) + "\n"


class CheckCapsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "wiki" / "decisions").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def rows_by_label(self, rows):
        return {r[0]: r for r in rows}

    def test_over_cap_and_compliant_files(self):
        (self.root / "CLAUDE.md").write_text(words(1600), encoding="utf-8")       # over 1,500
        (self.root / "resume-prompt.md").write_text(words(100), encoding="utf-8")  # under 800
        (self.root / "NEXT.md").write_text("\n".join(f"line {i}" for i in range(61)) + "\n",
                                           encoding="utf-8")                      # 61 lines
        rows, breached = check_caps.check(self.root)
        by = self.rows_by_label(rows)
        self.assertTrue(breached)
        self.assertEqual(by["CLAUDE.md"][1:], ("1600", "1500 words", "BREACH"))
        self.assertEqual(by["resume-prompt.md"][1:], ("100", "800 words", "OK"))
        self.assertEqual(by["NEXT.md"][1:], ("61", "60 lines", "BREACH"))
        self.assertEqual(quiet_main(["--root", str(self.root)]), 1)

    def test_absent_files_are_skipped_and_compliant_root_passes(self):
        (self.root / "NEXT.md").write_text("\n".join(f"line {i}" for i in range(60)) + "\n",
                                           encoding="utf-8")                      # exactly 60
        (self.root / "wiki" / "conventions.md").write_text(words(500), encoding="utf-8")
        rows, breached = check_caps.check(self.root)
        by = self.rows_by_label(rows)
        self.assertFalse(breached)
        self.assertEqual(by["NEXT.md"][1:], ("60", "60 lines", "OK"))
        for absent in ("CLAUDE.md", "resume-prompt.md", "routine-prompt.md", "wiki/style-guide.md"):
            self.assertEqual(by[absent][1:], ("absent", by[absent][2], "skipped"))
        self.assertEqual(by["wiki/log.md entries"][3], "skipped")
        self.assertEqual(quiet_main(["--root", str(self.root)]), 0)

    def test_wiki_total_excludes_index_log_and_decisions(self):
        wiki = self.root / "wiki"
        (wiki / "conventions.md").write_text(words(300), encoding="utf-8")
        (wiki / "notes").mkdir()
        (wiki / "notes" / "a.md").write_text(words(200), encoding="utf-8")
        (wiki / "index.md").write_text(words(1000), encoding="utf-8")
        (wiki / "log.md").write_text("# Log\n\n## [2026-09-16] setup | x\n" + words(10), encoding="utf-8")
        (wiki / "decisions" / "d.md").write_text(words(5000), encoding="utf-8")
        rows, breached = check_caps.check(self.root)
        total_row = next(r for r in rows if r[0].startswith("wiki/ (excluding"))
        self.assertIn("[2 pages]", total_row[0])
        self.assertEqual(total_row[1], "500")
        self.assertFalse(breached)

    def test_wiki_total_breach(self):
        (self.root / "wiki" / "big.md").write_text(words(30001), encoding="utf-8")
        rows, breached = check_caps.check(self.root)
        total_row = next(r for r in rows if r[0].startswith("wiki/ (excluding"))
        self.assertEqual(total_row[3], "BREACH")
        self.assertTrue(breached)

    def test_log_entries_split_at_headers_and_capped_at_200(self):
        log = ("# Log\n\npreamble that is not an entry " + words(300) +
               "## [2026-09-16] setup | short\n" + words(50) +
               "## [2026-09-15] ingest | long\n" + words(250))
        (self.root / "wiki" / "log.md").write_text(log, encoding="utf-8")
        entries = check_caps.log_entries(log)
        self.assertEqual([e[0] for e in entries],
                         ["## [2026-09-16] setup | short", "## [2026-09-15] ingest | long"])
        self.assertEqual(entries[0][1], 50 + 5)     # header words count toward the entry
        self.assertEqual(entries[1][1], 250 + 5)
        rows, breached = check_caps.check(self.root)
        self.assertTrue(breached)
        breaching = [r for r in rows if r[3] == "BREACH"]
        self.assertEqual(len(breaching), 2)          # the "longest" summary row and the entry itself
        self.assertTrue(any("ingest | long" in r[0] for r in breaching))
        self.assertFalse(any("setup | short" in r[0] for r in breaching))

    def test_cli_exit_codes(self):
        (self.root / "resume-prompt.md").write_text(words(801), encoding="utf-8")
        proc = subprocess.run([sys.executable, str(TOOLS / "check_caps.py"), "--root", str(self.root)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("BREACH", proc.stdout)
        (self.root / "resume-prompt.md").write_text(words(800), encoding="utf-8")
        proc = subprocess.run([sys.executable, str(TOOLS / "check_caps.py"), "--root", str(self.root)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("All caps respected", proc.stdout)


if __name__ == "__main__":
    unittest.main()
