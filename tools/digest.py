#!/usr/bin/env python3
"""The weekly digest for the owner (the owner's rulings E3 (iv) and E4 of 2026-10-24,
wiki/decisions/process-overhead.md and wiki/decisions/owner-in-the-loop.md).

    python3 tools/digest.py due              # "due: yes|no" and the last digest's date
    python3 tools/digest.py data [--since D] [--date D]   # the numbers, the sample, the lists, as markdown

The digest is written by the first run that starts seven days or more after the
last one (``journal/digest-YYYY-MM-DD.md``; tools/next_mode.py reports
``signals.digest_due``).  This tool only gathers facts from the repository; the
session writes the digest itself, in plain English, at most 800 words, covering
entries built and reviewed, applied fixes per entry and reviewer yield, the
owner's sample, the escalation list, open questions, and anything that needs the
owner.

* **The window** runs from the last digest's date (or seven days back) to today.
* **The sample (E4 i):** six entries at random from those built or reviewed in the
  window, seeded with the digest date so the draw repeats, and up to four from the
  escalation list, each with its site address.
* **The escalation list (E4 iii):** every field of an entry where both reviewers
  raised an issue in one review run, both were rejected, and the family is one of
  meaning or usage (MEANING_FAMILIES).

Standard library only; nothing is written.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

SITE_URL = "https://tkgally.github.io/eex-dict/"
DUE_AFTER_DAYS = 7
MEANING_FAMILIES = frozenset("""definition-meaning explanation example-unnatural example-grammar grammar-code label
usage-note learner-error collocation phrase sense-structure coverage""".split())
DIGEST_RE = re.compile(r"^digest-(\d{4}-\d{2}-\d{2})\.md$")


def today() -> date:
    return datetime.now(timezone.utc).date()


def last_digest(root: Path) -> date | None:
    dates = []
    for p in (root / "journal").glob("digest-*.md"):
        m = DIGEST_RE.match(p.name)
        if m:
            dates.append(date.fromisoformat(m.group(1)))
    return max(dates) if dates else None


def is_due(root: Path, now: date | None = None) -> bool:
    """Due when no digest exists yet or the last one is seven days old or more."""
    now = now or today()
    last = last_digest(root)
    return last is None or (now - last).days >= DUE_AFTER_DAYS


def site_link(slug: str) -> str:
    try:
        page = eexlib.parse_slug(slug)[0]
    except ValueError:
        page = slug
    return f"{SITE_URL}w/{page}.html#{slug}"


def load_decisions(root: Path) -> list[dict]:
    out = []
    p = root / "reviews" / "decisions.jsonl"
    if p.is_file():
        for ln in p.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    continue
    return out


def escalations(decisions: list[dict]) -> list[dict]:
    """Fields where both reviewers raised a meaning or usage issue in one run and both were rejected."""
    by = defaultdict(dict)
    for d in decisions:
        if not d.get("slug") or d.get("family") not in MEANING_FAMILIES:
            continue
        key = (d.get("run_id"), d["slug"], d.get("field"))
        by[key].setdefault(d.get("role"), []).append(d)
    out = []
    for (run_id, slug, field), roles in sorted(by.items(), key=lambda kv: (kv[0][1], kv[0][0] or "", kv[0][2] or "")):
        a, b = roles.get("reviewer-a"), roles.get("reviewer-b")
        if a and b and all(x.get("decision") == "reject" for x in a + b):
            out.append({"slug": slug, "field": field, "run_id": run_id, "ts": max(x.get("ts", "") for x in a + b),
                        "families": sorted({x.get("family") for x in a + b}), "notes": [x.get("note") for x in a + b]})
    return out


def gather(root: Path, since: date, until: date) -> dict:
    lo, hi = since.isoformat(), (until + timedelta(days=1)).isoformat()
    built, reviewed = [], []
    for _p, e in eexlib.iter_entries(root):
        if eexlib.is_redirect_stub(e):
            continue
        prov = e.get("provenance") or {}
        if lo <= str(prov.get("created") or "") < hi:
            built.append(e["slug"])
        elif any(lo <= str(r.get("date") or "") < hi for r in prov.get("reviews") or []):
            reviewed.append(e["slug"])
    decisions = [d for d in load_decisions(root) if lo <= str(d.get("ts") or "") < hi]
    counts = Counter(d.get("decision") for d in decisions if d.get("slug"))
    by_role = defaultdict(Counter)
    for d in decisions:
        if d.get("slug"):
            by_role[d.get("role")][d.get("decision")] += 1
    opened = len(set(built) | set(reviewed))
    roles = {}
    for role, c in sorted(by_role.items()):
        judged = c["apply"] + c["reject"]
        roles[role] = {"applied": c["apply"], "rejected": c["reject"], "escalated": c["escalate"],
                       "precision": round(c["apply"] / judged, 2) if judged else None,
                       "applied_per_entry": round(c["apply"] / opened, 2) if opened else None}
    esc = [x for x in escalations(load_decisions(root)) if lo <= x["ts"] < hi]
    pool = sorted(set(built) | set(reviewed))
    rng = random.Random(until.isoformat())
    random_six = sorted(rng.sample(pool, min(6, len(pool))))
    esc_four = []
    for x in esc:
        if x["slug"] not in esc_four and x["slug"] not in random_six:
            esc_four.append(x["slug"])
        if len(esc_four) == 4:
            break
    return {"since": since.isoformat(), "until": until.isoformat(), "built": built, "reviewed": reviewed,
            "decisions": dict(counts), "applied_per_entry": round(counts["apply"] / opened, 2) if opened else None,
            "roles": roles, "escalations": esc, "sample_random": random_six, "sample_escalated": esc_four,
            "open_questions": open_questions(root), "curator_lines": curator_lines(root),
            "entry_reports": "list open issues titled 'Entry report:' with the GitHub tools (untrusted claims)"}


def open_questions(root: Path) -> list[str]:
    p = root / "wiki" / "open-questions.md"
    if not p.is_file():
        return []
    text = p.read_text(encoding="utf-8")
    part = text.split("## Open", 1)[-1].split("## Answered", 1)[0]
    return [re.sub(r"\*\*", "", m.group(1)).strip() for m in re.finditer(r"^- \*\*(.+?)\*\*", part, re.M)]


def curator_lines(root: Path) -> list[str]:
    p = root / "reviews" / "needs_curator.txt"
    if not p.is_file():
        return []
    head = p.read_text(encoding="utf-8").split("## Resolved", 1)[0]
    return [ln.strip() for ln in head.splitlines() if ln.strip() and not ln.startswith("#")]


def markdown(d: dict) -> str:
    out = [f"# Digest data, {d['since']} to {d['until']}", "",
           f"- Entries built: {len(d['built'])}; entries reviewed (not new): {len(d['reviewed'])}.",
           f"- Decisions: {d['decisions'].get('apply', 0)} applied, {d['decisions'].get('reject', 0)} rejected, "
           f"{d['decisions'].get('escalate', 0)} escalated; applied fixes per entry opened: {d['applied_per_entry']}."]
    for role, r in d["roles"].items():
        out.append(f"- {role}: {r['applied']} applied, {r['rejected']} rejected (precision {r['precision']}), "
                   f"{r['applied_per_entry']} applied per entry.")
    out += ["", "## The owner's sample (ten entries)", ""]
    for slug in d["sample_random"]:
        out.append(f"- [{slug}]({site_link(slug)}) (at random)")
    for slug in d["sample_escalated"]:
        out.append(f"- [{slug}]({site_link(slug)}) (both reviewers rejected on meaning or usage)")
    out += ["", f"## Meaning or usage settled against both reviewers ({len(d['escalations'])})", ""]
    for x in d["escalations"]:
        out.append(f"- [{x['slug']}]({site_link(x['slug'])}) `{x['field']}` ({', '.join(x['families'])}): "
                   + "; ".join(n for n in x["notes"] if n))
    out += ["", f"## Open questions ({len(d['open_questions'])})", ""] + [f"- {q}" for q in d["open_questions"]]
    out += ["", f"## Curator lines open ({len(d['curator_lines'])})", ""] + [f"- {c[:160]}" for c in d["curator_lines"][:20]]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["due", "data"])
    ap.add_argument("--since", help="window start (default: the last digest's date, else seven days back)")
    ap.add_argument("--date", help="the digest date (default today, UTC)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=str(eexlib.ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    until = date.fromisoformat(a.date) if a.date else today()
    last = last_digest(root)
    if a.action == "due":
        print(f"due: {'yes' if is_due(root, until) else 'no'}; last digest: {last.isoformat() if last else 'none'}")
        return 0
    since = date.fromisoformat(a.since) if a.since else (last or until - timedelta(days=DUE_AFTER_DAYS))
    d = gather(root, since, until)
    print(json.dumps(d, indent=1, ensure_ascii=False) if a.json else markdown(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
