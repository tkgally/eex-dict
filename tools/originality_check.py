#!/usr/bin/env python3
"""Sample definitions for the periodic originality check and record the result.

    python3 tools/originality_check.py sample [--n 10] [--seed N]     # writes .tmp/originality-<date>.md, a checklist for the session
    python3 tools/originality_check.py record <date> --file <path>     # copies a completed checklist into reviews/originality/<date>.md

The session runs an exact-phrase web search for each sampled definition (the
checklist lists the query to use) and puts the reviewer question to one
reviewer role ("does this read as copied from a published dictionary?"), then
fills in the verdict column and records the file. Nothing is copied from any
dictionary; only whether a match was found. Runs about every tenth Routine run
(config/routine-config.json: originality_every_runs).
"""
from __future__ import annotations

import argparse
import random
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402


def sample(n: int, seed: int | None) -> list[tuple[str, str, str]]:
    pool = []
    for _p, e in eexlib.iter_entries():
        if eexlib.is_redirect_stub(e) or e["provenance"]["status"] != "reviewed":
            continue
        for i, s in enumerate(e["senses"]):
            pool.append((e["slug"], f"senses[{i}].definition", eexlib.strip_markup(s["definition"])))
        for i, ph in enumerate(e.get("phrases", [])):
            pool.append((e["slug"], f"phrases[{i}].definition", eexlib.strip_markup(ph["definition"])))
        if e.get("usage_note"):
            pool.append((e["slug"], "usage_note", eexlib.strip_markup(e["usage_note"])))
    rng = random.Random(seed if seed is not None else int(datetime.now(timezone.utc).strftime("%Y%m%d")))
    rng.shuffle(pool)
    return pool[:n]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample"); s.add_argument("--n", type=int, default=10); s.add_argument("--seed", type=int)
    r = sub.add_parser("record"); r.add_argument("date"); r.add_argument("--file", required=True)
    a = ap.parse_args()
    if a.cmd == "record":
        dst = eexlib.ROOT / "reviews" / "originality" / f"{a.date}.md"
        shutil.copyfile(a.file, dst)
        print(f"recorded {dst.relative_to(eexlib.ROOT)}")
        return 0
    items = sample(a.n, a.seed)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = eexlib.ROOT / ".tmp" / f"originality-{date}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Originality check {date}", "",
             "For each row: run the exact-phrase query in a web search (WebSearch), look only at whether a published dictionary "
             "or word list shows the same wording; ask one reviewer role the question below; fill the last two columns; "
             "then `python3 tools/originality_check.py record <date> --file <this file>`. Verdict values: original, "
             "generic-overlap (a short plain definition that any dictionary would write the same way), rewrite (matches a "
             "published dictionary's distinctive wording; rewrite the field in a build or review run and log it).", "",
             "Reviewer question: \"Does this definition read as copied from a published dictionary, or as an original plain-English "
             "definition? Answer copied / original / cannot tell, with one line of reason. If you answer copied, name the source and "
             "quote the matching published wording exactly; if you cannot quote it, do not answer copied.\"", "",
             "| slug | field | text | query | search result | reviewer | verdict |", "|---|---|---|---|---|---|---|"]
    for slug, field, text in items:
        q = '"' + text.replace('"', "'")[:120] + '"'
        lines.append(f"| {slug} | {field} | {text.replace('|', '/')} | {q.replace('|', '/')} |  |  |  |")
    lines += ["", "Summary: (original N, generic-overlap N, rewrite N; what was rewritten)"]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out} with {len(items)} sampled fields")
    return 0


if __name__ == "__main__":
    sys.exit(main())
