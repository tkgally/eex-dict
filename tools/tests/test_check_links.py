"""Tests for tools/check_links.py: a broken and a good link, plus the ignore rules."""

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import check_links  # noqa: E402


def quiet_main(argv):
    """check_links.main() with its report swallowed, so test output stays readable."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return check_links.main(argv)


class CheckLinksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "wiki" / "notes").mkdir(parents=True)
        (self.root / "wiki" / "good.md").write_text("# Good\n", encoding="utf-8")
        (self.root / "wiki" / "notes" / "note.md").write_text("# Note\n", encoding="utf-8")
        (self.root / "README.md").write_text("# Root\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def test_good_and_broken_links(self):
        page = self.write("wiki/page.md", "\n".join([
            "[good](good.md)",
            "[good with anchor](good.md#some-section)",   # anchors are not validated
            "[note](notes/note.md)",
            "[up to root](../README.md)",
            "[root-relative](/wiki/good.md)",
            "[broken](missing.md)",
            "![broken image](img/pic.png)",
            "[titled broken](also-missing.md \"title\")",
        ]) + "\n")
        broken = check_links.check_page(page, self.root)
        self.assertEqual([(ln, t) for _, ln, t in broken],
                         [(6, "missing.md"), (7, "img/pic.png"), (8, "also-missing.md")])

    def test_ignored_links(self):
        page = self.write("wiki/ignored.md", "\n".join([
            "[external](https://example.org/missing)",
            "[plain http](http://example.org/x.md)",
            "[mail](mailto:someone@example.org)",
            "[anchor only](#section)",
            "inline code `[x](nope-inline.md)` is not a link",
            "```",
            "[in fence](nope-fenced.md)",
            "```",
            "~~~text",
            "[in tilde fence](nope-tilde.md)",
            "~~~",
            "[[bank-n|bank]] is not a markdown link",
            "[empty target]()",
        ]) + "\n")
        self.assertEqual(check_links.check_page(page, self.root), [])

    def test_main_exit_codes_and_output(self):
        self.write("wiki/bad.md", "[broken](nowhere.md)\n")
        self.assertEqual(quiet_main(["--root", str(self.root)]), 1)
        os.unlink(self.root / "wiki" / "bad.md")
        self.assertEqual(quiet_main(["--root", str(self.root)]), 0)
        self.assertEqual(quiet_main(["--root", str(self.root), "does-not-exist.md"]), 2)

    def test_explicit_paths_only(self):
        self.write("wiki/bad.md", "[broken](nowhere.md)\n")
        self.write("journal/2026-09-16.md", "[fine](../README.md)\n")
        # only the journal is named, so the broken wiki page is not visited
        self.assertEqual(quiet_main(["--root", str(self.root), "journal"]), 0)
        self.assertEqual(quiet_main(["--root", str(self.root), "wiki/bad.md"]), 1)

    def test_cli_reports_one_line_per_broken_link(self):
        self.write("wiki/bad.md", "[one](a.md)\n\n[two](b.md)\n")
        proc = subprocess.run([sys.executable, str(TOOLS / "check_links.py"), "--root", str(self.root)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("BROKEN")]
        self.assertEqual(lines, ["BROKEN  wiki/bad.md:1: a.md", "BROKEN  wiki/bad.md:3: b.md"])


if __name__ == "__main__":
    unittest.main()
