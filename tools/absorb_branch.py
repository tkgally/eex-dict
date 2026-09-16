#!/usr/bin/env python3
"""Absorb a stranded ``claude/*`` branch (a run that ended red or unmerged) into the current branch.

    python3 tools/absorb_branch.py --residue <branch>      # read-only: durable files the branch changed that HEAD lacks
    python3 tools/absorb_branch.py <branch> [--pr N] [--no-commit]

Merges origin/<branch> into HEAD with a per-file policy so that a Sonnet-class
model can do it mechanically (ported from the owner's earlier dictionary project
and simplified for this one):

* append-only ledgers take the union: reviews/decisions.jsonl, metrics/history.jsonl,
  reviews/needs_curator.txt, wiki/log.md (their new entries are inserted after the
  header), config/budget-ledger.json (union of calls, spent recomputed);
* the headword queue is merged row by row (a row missing on our side is added; a
  status further along wins: done > declined > claimed > pending);
* per-session state keeps ours: NEXT.md, wiki/index.md (their new lines are
  printed for a hand check), .github/ and tools/ conflicts abort;
* entries, wiki pages, journal, reviews/<run-id>/ files, claim files merge as git
  merges them; a conflict in an entry or a code file aborts the whole merge and
  lists the files.

Every absorb is recorded in headwords/absorbed-branches.jsonl (branch tip and
target), so a branch is never absorbed twice. After a successful absorb run the
local gate (validate --gate, check_caps, check_links, tests) and fix what it reports.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import io
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

ROOT = eexlib.ROOT
UNION = ("reviews/decisions.jsonl", "metrics/history.jsonl", "reviews/needs_curator.txt")
KEEP_OURS = ("NEXT.md", "wiki/index.md", "config/routine-config.json")
LEDGER = "headwords/absorbed-branches.jsonl"
QUEUE = "headwords/queue.tsv"
LOG = "wiki/log.md"
BUDGET = "config/budget-ledger.json"
STATUS_RANK = {"pending": 0, "claimed": 1, "declined": 2, "deferred": 2, "duplicate": 2, "done": 3}


def git(*args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=check)


def out(*args: str) -> str:
    return git(*args).stdout.strip()


def show(ref: str, path: str) -> str | None:
    r = git("show", f"{ref}:{path}")
    return r.stdout if r.returncode == 0 else None


def union_lines(base: str | None, ours: str, theirs: str) -> str:
    base_l, ours_l, theirs_l = (base or "").splitlines(), ours.splitlines(), theirs.splitlines()
    added = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(a=base_l, b=theirs_l, autojunk=False).get_opcodes():
        if tag in ("insert", "replace"):
            added.extend(theirs_l[j1:j2])
    present = {ln for ln in ours_l if ln.strip()}
    new = [ln for ln in added if ln.strip() and ln not in present]
    return "\n".join(ours_l + new) + "\n" if new else (ours if ours.endswith("\n") else ours + "\n")


def merge_log(base: str | None, ours: str, theirs: str) -> str:
    """Insert the branch's new log entries (blocks starting '## [') after ours' header."""
    def blocks(text: str) -> list[str]:
        parts, cur = [], []
        for ln in text.splitlines():
            if ln.startswith("## [") and cur:
                parts.append("\n".join(cur)); cur = []
            cur.append(ln)
        if cur:
            parts.append("\n".join(cur))
        return parts
    ob, tb, bb = blocks(ours), blocks(theirs), blocks(base or "")
    known = {b.splitlines()[0] for b in ob} | {b.splitlines()[0] for b in bb}
    new = [b for b in tb if b.startswith("## [") and b.splitlines()[0] not in known]
    if not new:
        return ours
    head = ob[0] if ob and not ob[0].startswith("## [") else ""
    rest = ob[1:] if head else ob
    return "\n\n".join([head.rstrip()] + [b.rstrip() for b in new] + [b.rstrip() for b in rest]).strip() + "\n"


def merge_queue(ours: str, theirs: str) -> str:
    def rows(text: str) -> list[dict]:
        return list(csv.DictReader(io.StringIO(text), delimiter="\t"))
    o, t = rows(ours), rows(theirs)
    cols = ["headword", "pos", "band", "source", "status", "added", "note"]
    index = {(r["headword"].lower(), r["pos"]): r for r in o}
    for r in t:
        k = (r["headword"].lower(), r["pos"])
        if k not in index:
            o.append(r); index[k] = r
        else:
            mine = index[k]
            if STATUS_RANK.get(r.get("status", ""), 0) > STATUS_RANK.get(mine.get("status", ""), 0):
                mine["status"] = r["status"]
            if r.get("note") and r["note"] not in (mine.get("note") or ""):
                mine["note"] = ((mine.get("note") or "") + "; " + r["note"]).strip("; ")
    buf = io.StringIO()
    buf.write("\t".join(cols) + "\n")
    for r in o:
        buf.write("\t".join(str(r.get(c, "") or "") for c in cols) + "\n")
    return buf.getvalue()


def merge_budget(ours: str, theirs: str) -> str:
    o, t = json.loads(ours), json.loads(theirs)
    if o.get("date") != t.get("date"):
        return ours if o.get("date", "") >= t.get("date", "") else theirs
    seen = {json.dumps(c, sort_keys=True) for c in o.get("calls", [])}
    for c in t.get("calls", []):
        if json.dumps(c, sort_keys=True) not in seen:
            o["calls"].append(c)
    o["calls"].sort(key=lambda c: c.get("ts", ""))
    o["spent_usd"] = round(sum(float(c.get("cost_usd") or 0) for c in o["calls"]), 6)
    for d, v in (t.get("history") or {}).items():
        o.setdefault("history", {}).setdefault(d, v)
    return json.dumps(o, ensure_ascii=False, indent=2) + "\n"


def residue(theirs: str) -> list[str]:
    base = out("merge-base", "HEAD", theirs)
    res = []
    for path in out("diff", "--name-only", base, theirs).splitlines():
        if not path or git("diff", "--quiet", "HEAD", theirs, "--", path).returncode == 0:
            continue
        if path in KEEP_OURS or path == BUDGET:
            continue
        o, t, b = show("HEAD", path), show(theirs, path), show(base, path)
        if o is not None and t is not None and path in UNION and union_lines(b, o, t) == (o if o.endswith("\n") else o + "\n"):
            continue
        if o is not None and t is not None and path == LOG and merge_log(b, o, t) == o:
            continue
        if o is not None and t is not None and path == QUEUE and merge_queue(o, t) == o:
            continue
        res.append(path)
    return res


def already(branch: str, tip: str) -> dict | None:
    p = ROOT / LEDGER
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(ln)
            except json.JSONDecodeError:
                continue
            if row.get("branch") == branch and row.get("tip") == tip:
                return row
    return None


def absorb(branch: str, pr: int | None, commit: bool) -> int:
    theirs = f"origin/{branch}"
    if out("status", "--porcelain"):
        print("ERROR: working tree is not clean; commit or stash first."); return 1
    if git("fetch", "origin", branch).returncode != 0:
        print(f"{branch}: not on origin; nothing to do."); return 0
    tip = out("rev-parse", theirs)
    row = already(branch, tip)
    if row:
        print(f"{branch}: already absorbed on {row['ts'][:10]} into {row.get('into')}; nothing to do."); return 0
    res = residue(theirs)
    if not res:
        print(f"{branch}: no residue against HEAD; nothing to absorb (the branch can be pruned)."); return 0
    print(f"Absorbing {branch} ({len(res)} durable files differ):")
    for p in res:
        print("  " + p)
    base = out("merge-base", "HEAD", theirs)
    git("merge", "--no-commit", "--no-ff", theirs)
    conflicted = [ln for ln in out("diff", "--name-only", "--diff-filter=U").splitlines() if ln]
    unresolvable = []
    for path in conflicted:
        o, t, b = show("HEAD", path), show(theirs, path), show(base, path)
        if path in KEEP_OURS:
            git("checkout", "--ours", "--", path); git("add", "--", path)
            if path == "wiki/index.md" and t:
                new_lines = [ln for ln in t.splitlines() if ln.startswith("- ") and ln not in (o or "")]
                for ln in new_lines:
                    print(f"index line from the branch to place by hand: {ln}")
        elif path in UNION and o is not None and t is not None:
            (ROOT / path).write_text(union_lines(b, o, t), encoding="utf-8"); git("add", "--", path)
        elif path == LOG and o is not None and t is not None:
            (ROOT / path).write_text(merge_log(b, o, t), encoding="utf-8"); git("add", "--", path)
        elif path == QUEUE and o is not None and t is not None:
            (ROOT / path).write_text(merge_queue(o, t), encoding="utf-8"); git("add", "--", path)
        elif path == BUDGET and o is not None and t is not None:
            (ROOT / path).write_text(merge_budget(o, t), encoding="utf-8"); git("add", "--", path)
        else:
            unresolvable.append(path)
    if unresolvable:
        git("merge", "--abort")
        print("\nABORTED: these conflicts need a person (the merge was undone):")
        for p in unresolvable:
            print("  " + p)
        return 2
    with (ROOT / LEDGER).open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "branch": branch, "tip": tip,
                            "pr": pr, "into": out("rev-parse", "--abbrev-ref", "HEAD")}) + "\n")
    git("add", "--", LEDGER)
    if commit:
        subject = out("log", "-1", "--format=%s", theirs).splitlines()[0]
        git("commit", "--no-verify", "-m", f"absorb {branch}" + (f" (PR #{pr})" if pr else "") + f": {subject}")
        print(f"\nCommitted the absorb of {branch}.")
    else:
        print("\nMerge staged, not committed.")
    entries = [p for p in res if p.startswith("entries/")]
    if entries:
        print(f"Entries the branch brings ({len(entries)}): " + " ".join(Path(p).stem for p in entries))
    print("Next: run the local gate (validate --gate, check_caps, check_links, unit tests) and fix what it reports.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("branch")
    ap.add_argument("--residue", action="store_true")
    ap.add_argument("--pr", type=int)
    ap.add_argument("--no-commit", action="store_true")
    a = ap.parse_args()
    branch = a.branch.removeprefix("origin/")
    if a.residue:
        if git("fetch", "origin", branch).returncode != 0:
            print(f"{branch}: not on origin."); return 0
        tip = out("rev-parse", f"origin/{branch}")
        row = already(branch, tip)
        if row:
            print(f"{branch}: absorbed on {row['ts'][:10]} into {row.get('into')}; no residue."); return 0
        res = residue(f"origin/{branch}")
        print(f"{branch}: " + ("no residue (fully absorbed)." if not res else f"{len(res)} durable file(s) differ from HEAD:"))
        for p in res:
            print("  " + p)
        return 0
    return absorb(branch, a.pr, not a.no_commit)


if __name__ == "__main__":
    sys.exit(main())
