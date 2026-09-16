#!/usr/bin/env python3
"""check_caps.py -- enforce the word and line caps from wiki/conventions.md section 1.

Caps checked (words = whitespace-separated tokens; lines = every line, blank
lines included):

    CLAUDE.md                 <= 1,500 words
    resume-prompt.md          <=   800 words
    routine-prompt.md         <= 2,500 words
    NEXT.md                   <=    60 lines
    wiki/style-guide.md       <= 3,500 words
    wiki/ total               <= 30,000 words, excluding wiki/index.md,
                                 wiki/log.md and everything under wiki/decisions/
    each entry of wiki/log.md <=   200 words (an entry starts at a line that
                                 begins with "## [" and includes that header
                                 line; text before the first header is a
                                 preamble, not an entry)

A file that does not exist yet is reported as "absent" and skipped
(routine-prompt.md and wiki/style-guide.md arrive in later stages).

Usage:
    python3 tools/check_caps.py [--root DIR] [--verbose]

Prints a table (file, count, cap, status) and exits 1 if any cap is breached,
0 otherwise. --root defaults to the repository root (the parent of tools/).
--verbose adds one row per log entry instead of only the longest one.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (relative path, cap, unit)
FILE_CAPS = [
    ("CLAUDE.md", 1500, "words"),
    ("resume-prompt.md", 800, "words"),
    ("routine-prompt.md", 2500, "words"),
    ("NEXT.md", 60, "lines"),
    ("wiki/style-guide.md", 3500, "words"),
]
WIKI_TOTAL_CAP = 30000
WIKI_EXCLUDED_FILES = ("index.md", "log.md")
WIKI_EXCLUDED_DIRS = ("decisions",)
LOG_ENTRY_CAP = 200
LOG_HEADER_PREFIX = "## ["


def count_words(text: str) -> int:
    """Whitespace-separated tokens."""
    return len(text.split())


def count_lines(text: str) -> int:
    """Every line, blank ones included; a trailing newline does not add a line."""
    return len(text.splitlines())


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def wiki_pages(root: Path):
    """Every wiki/*.md page that counts toward the 30,000-word total."""
    wiki = root / "wiki"
    if not wiki.is_dir():
        return None
    pages = []
    for page in sorted(wiki.rglob("*.md")):
        rel = page.relative_to(wiki)
        if rel.parts[0] in WIKI_EXCLUDED_DIRS:
            continue
        if len(rel.parts) == 1 and rel.name in WIKI_EXCLUDED_FILES:
            continue
        pages.append(page)
    return pages


def log_entries(text: str):
    """Split wiki/log.md into (header, word_count) tuples, one per entry.

    An entry starts at a line beginning with "## [" and runs to the next such
    line; the header line is part of the entry. Text before the first header
    is a preamble and is not an entry.
    """
    entries = []
    header = None
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith(LOG_HEADER_PREFIX):
            if header is not None:
                entries.append((header, count_words("\n".join(buf))))
            header = line.strip()
            buf = [line]
        elif header is not None:
            buf.append(line)
    if header is not None:
        entries.append((header, count_words("\n".join(buf))))
    return entries


def check(root: Path, verbose: bool = False):
    """Return (rows, breached). Each row is (label, count, cap_text, status)."""
    rows = []
    breached = False

    def add(label, count, cap, unit, absent=False):
        nonlocal breached
        cap_text = f"{cap} {unit}"
        if absent:
            rows.append((label, "absent", cap_text, "skipped"))
            return
        if count > cap:
            breached = True
            rows.append((label, str(count), cap_text, "BREACH"))
        else:
            rows.append((label, str(count), cap_text, "OK"))

    for rel, cap, unit in FILE_CAPS:
        path = root / rel
        if not path.is_file():
            add(rel, 0, cap, unit, absent=True)
            continue
        text = read(path)
        count = count_lines(text) if unit == "lines" else count_words(text)
        add(rel, count, cap, unit)

    pages = wiki_pages(root)
    label = "wiki/ (excluding index.md, log.md, decisions/)"
    if pages is None:
        add(label, 0, WIKI_TOTAL_CAP, "words", absent=True)
    else:
        total = sum(count_words(read(p)) for p in pages)
        add(f"{label} [{len(pages)} pages]", total, WIKI_TOTAL_CAP, "words")

    log_path = root / "wiki" / "log.md"
    if not log_path.is_file():
        add("wiki/log.md entries", 0, LOG_ENTRY_CAP, "words", absent=True)
    else:
        entries = log_entries(read(log_path))
        if not entries:
            rows.append(("wiki/log.md entries [0 entries]", "0", f"{LOG_ENTRY_CAP} words", "OK"))
        else:
            longest = max(entries, key=lambda e: e[1])
            add(f"wiki/log.md entries [{len(entries)} entries, longest]", longest[1],
                LOG_ENTRY_CAP, "words")
            for header, words in entries:
                if verbose or words > LOG_ENTRY_CAP:
                    add(f"  {header[:60]}", words, LOG_ENTRY_CAP, "words")
    return rows, breached


def format_table(rows) -> str:
    header = ("file", "count", "cap", "status")
    widths = [max(len(str(r[i])) for r in rows + [header]) for i in range(4)]
    lines = []
    fmt = "{:<%d}  {:>%d}  {:>%d}  {:<%d}" % tuple(widths)
    lines.append(fmt.format(*header))
    lines.append("  ".join("-" * w for w in widths))
    for r in rows:
        lines.append(fmt.format(*r))
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the word and line caps from wiki/conventions.md section 1 "
                    "(CLAUDE.md, resume-prompt.md, routine-prompt.md, NEXT.md, "
                    "wiki/style-guide.md, the wiki total, and each wiki/log.md entry). "
                    "Absent files are skipped. Exit 1 on any breach.")
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="repository root (default: parent of tools/)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="list every wiki/log.md entry, not only the longest")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: root {root} is not a directory", file=sys.stderr)
        return 2

    rows, breached = check(root, verbose=args.verbose)
    print(format_table(rows))
    if breached:
        n = sum(1 for r in rows if r[3] == "BREACH")
        print(f"\n{n} cap breach(es). Trim the files marked BREACH.")
        return 1
    print("\nAll caps respected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
