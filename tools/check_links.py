#!/usr/bin/env python3
"""check_links.py -- verify that every relative markdown link in the repository resolves.

Port of the knowledge-base framework's starter checker (framework.md section 6),
extended for this repository's layout.

Usage:
    python3 tools/check_links.py                    # default targets (below)
    python3 tools/check_links.py wiki/ journal/x.md # explicit files and/or directories
    python3 tools/check_links.py --root DIR ...

Default targets, each skipped quietly when it does not exist yet:
    wiki/  journal/  inbox/  reviews/  experiments/  config/  sources/
    README.md  PROJECT.md  CLAUDE.md  resume-prompt.md  routine-prompt.md
    NEXT.md  framework.md

Explicit paths are taken relative to the current directory when they exist
there, otherwise relative to --root; a missing explicit path is an error.
Directories are searched recursively for *.md files.

What is checked: every inline link or image, [text](target), whose target is a
relative path. The target must exist on disk relative to the linking page
(a target that starts with "/" is taken relative to the repository root, as
GitHub renders it). Ignored: external links (any URL scheme such as http,
https, mailto), pure anchors (#section), and links inside fenced code blocks
(``` or ~~~) or inline code spans.

Known limit, disclosed rather than silently assumed away: a link's #anchor
fragment (page.md#section-name) is NOT validated -- only that page.md itself
exists. A link to an existing page but a wrong or renamed section is not
caught; check those by hand for anything load-bearing.

Exit code 0 when every relative link target exists; 1 otherwise, with one line
per broken link (BROKEN  file: target); 2 on a usage error. Run before every
commit (wiki/conventions.md section 1).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_DIRS = ["wiki", "journal", "inbox", "reviews", "experiments", "config", "sources"]
DEFAULT_FILES = ["README.md", "PROJECT.md", "CLAUDE.md", "resume-prompt.md",
                 "routine-prompt.md", "NEXT.md", "framework.md"]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
CODE_SPAN_RE = re.compile(r"`+[^`]*`+")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def iter_links(text: str):
    """Yield (line_number, target) for every inline link outside code."""
    fence = None
    for lineno, line in enumerate(text.splitlines(), start=1):
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker[0]
            elif marker[0] == fence:
                fence = None
            continue
        if fence is not None:
            continue
        line = CODE_SPAN_RE.sub("", line)
        for m in LINK_RE.finditer(line):
            yield lineno, m.group(1)


def is_external(target: str) -> bool:
    return bool(SCHEME_RE.match(target))


def check_page(page: Path, root: Path):
    """Return a list of (page, lineno, target) for the broken links on one page."""
    broken = []
    text = page.read_text(encoding="utf-8")
    for lineno, target in iter_links(text):
        if is_external(target) or target.startswith("#"):
            continue
        path_part = unquote(target.split("#", 1)[0])
        if not path_part:
            continue
        if path_part.startswith("/"):
            resolved = root / path_part.lstrip("/")
        else:
            resolved = page.parent / path_part
        if not resolved.exists():
            broken.append((page, lineno, target))
    return broken


def collect_pages(targets, root: Path):
    pages = []
    for t in targets:
        if t.is_dir():
            pages.extend(sorted(p for p in t.rglob("*.md") if p.is_file()))
        elif t.is_file():
            pages.append(t)
    # de-duplicate while keeping order
    seen = set()
    unique = []
    for p in pages:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            unique.append(p)
    return unique


def default_targets(root: Path):
    targets = [root / d for d in DEFAULT_DIRS] + [root / f for f in DEFAULT_FILES]
    return [t for t in targets if t.exists()]


def resolve_explicit(paths, root: Path):
    """Resolve user-given paths: cwd first, then --root. Missing is an error."""
    targets, missing = [], []
    for p in paths:
        cand = Path(p)
        if not cand.exists():
            cand = root / p
        if cand.exists():
            targets.append(cand)
        else:
            missing.append(p)
    return targets, missing


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that every relative markdown link resolves to an existing file. "
                    "External links (http, https, mailto), pure #anchors and links inside "
                    "fenced code blocks are ignored. Anchors (#section) are NOT validated, "
                    "only that the target file exists. Exit 1 with one line per broken link.",
        epilog="Default targets: " + ", ".join(DEFAULT_DIRS + DEFAULT_FILES))
    parser.add_argument("paths", nargs="*",
                        help="files or directories to check (default: the repository's "
                             "knowledge-base directories and root markdown files)")
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="repository root (default: parent of tools/)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print only broken links")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: root {root} is not a directory", file=sys.stderr)
        return 2

    if args.paths:
        targets, missing = resolve_explicit(args.paths, root)
        if missing:
            for m in missing:
                print(f"error: {m} does not exist (looked in the current directory and {root})",
                      file=sys.stderr)
            return 2
    else:
        targets = default_targets(root)

    pages = collect_pages(targets, root)
    broken = []
    for page in pages:
        broken.extend(check_page(page, root))

    if broken:
        for page, lineno, target in broken:
            print(f"BROKEN  {rel(page, root)}:{lineno}: {target}")
        print(f"\n{len(broken)} broken link(s) in {len(pages)} page(s).")
        return 1
    if not args.quiet:
        print(f"All relative links resolve ({len(pages)} page(s) checked; "
              f"anchors not validated).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
