#!/usr/bin/env python3
"""Append one JSON line per run to metrics/history.jsonl, and report on it.

    python3 tools/metrics.py --mode build [--changed N] [--site-build ok|failed|unknown] [--dry-run]
    python3 tools/metrics.py --summary        # the latest row, readable
    python3 tools/metrics.py --precision      # reviewer precision by role and family, all time

A row holds: entries by status and band, defining-vocabulary coverage, the
closure gap, queue counts, review counts and precision (from the decision ledger
lines logged since the previous row), spend (today and this run), and the site
build status the run observed. tools/next_mode.py replays the "mode" column, so
every run must append a row, even a run that changed nothing.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

HISTORY = eexlib.ROOT / "metrics" / "history.jsonl"


def read_jsonl(path: Path):
    if not path.exists():
        return
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln:
            try:
                yield json.loads(ln)
            except json.JSONDecodeError:
                continue


def run_id() -> str:
    p = eexlib.ROOT / ".tmp" / "run-id"
    return p.read_text(encoding="utf-8").strip() if p.exists() else "local"


def entry_stats() -> dict:
    total = 0
    status = Counter()
    band = Counter()
    headwords = set()
    for _p, e in eexlib.iter_entries():
        if eexlib.is_redirect_stub(e):
            continue
        total += 1
        status[e["provenance"]["status"]] += 1
        band[str(e["frequency"]["band"])] += 1
        headwords.add(e["headword"].lower())
    dv_path = eexlib.ROOT / "schema" / "defining-vocabulary.txt"
    dv = {w.strip().lower() for w in dv_path.read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")} if dv_path.exists() else set()
    with_entry = len(dv & headwords)
    return {"entries_total": total, "entries_reviewed": status.get("reviewed", 0), "entries_draft": status.get("draft", 0),
            "by_band": {b: band.get(b, 0) for b in "12345"},
            "defining_vocabulary": {"size": len(dv), "with_entry": with_entry,
                                    "coverage": round(with_entry / len(dv), 4) if dv else None}}


def queue_stats() -> dict:
    q = eexlib.ROOT / "headwords" / "queue.tsv"
    st = Counter()
    closure_gap = 0
    if q.exists():
        with q.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                st[r.get("status", "")] += 1
                if r.get("status") == "pending" and r.get("source") in ("closure", "family", "crossref"):
                    closure_gap += 1
    return {"queue": {k: st.get(k, 0) for k in ("pending", "claimed", "done", "declined", "deferred", "duplicate")},
            "closure_gap": closure_gap}


def review_stats(since_ts: str) -> dict:
    dec = Counter()
    by_role = defaultdict(Counter)
    for d in read_jsonl(eexlib.ROOT / "reviews" / "decisions.jsonl"):
        if since_ts and str(d.get("ts", "")) <= since_ts:
            continue
        n = int(d.get("n", 1) or 1)
        dec[d.get("decision", "")] += n
        by_role[d.get("role", "?")][d.get("decision", "")] += n
    precision = {}
    for role, c in by_role.items():
        denom = c["apply"] + c["reject"]
        precision[role] = round(c["apply"] / denom, 3) if denom else None
    issues = blocking = 0
    for p in (eexlib.ROOT / "reviews").glob("*/*.json"):
        try:
            rec = eexlib.load_json(p)
        except (ValueError, OSError):
            continue
        if since_ts and any(str(r.get("requested_at", "")) <= since_ts for r in rec.get("reviewers", [])):
            continue
        for r in rec.get("reviewers", []):
            for v in r.get("verdicts", []):
                if v.get("verdict") == "issue":
                    issues += 1
                    blocking += v.get("severity") == "blocking"
    return {"reviews": {"issues": issues, "blocking": blocking, "applied": dec["apply"], "rejected": dec["reject"],
                        "escalated": dec["escalate"], "precision_by_role": precision}}


def spend_stats(rid: str) -> dict:
    led = eexlib.load_json(eexlib.ROOT / "config" / "budget-ledger.json") if (eexlib.ROOT / "config" / "budget-ledger.json").exists() else {}
    run = sum(float(c.get("cost_usd") or 0) for c in led.get("calls", []) if c.get("run_id") == rid)
    return {"spend_today_usd": round(float(led.get("spent_usd", 0.0)), 4), "spend_run_usd": round(run, 4)}


def precision_report() -> None:
    by = defaultdict(Counter)
    for d in read_jsonl(eexlib.ROOT / "reviews" / "decisions.jsonl"):
        n = int(d.get("n", 1) or 1)
        by[(d.get("role", "?"), d.get("family", "?"))][d.get("decision", "")] += n
        by[(d.get("role", "?"), "ALL")][d.get("decision", "")] += n
    print(f"{'role':12s} {'family':24s} {'apply':>6s} {'reject':>7s} {'escal':>6s} {'precision':>10s}")
    for (role, fam), c in sorted(by.items()):
        denom = c["apply"] + c["reject"]
        prec = f"{c['apply'] / denom:.2f}" if denom else "-"
        print(f"{role:12s} {fam:24s} {c['apply']:6d} {c['reject']:7d} {c['escalate']:6d} {prec:>10s}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["build", "review", "closure", "site", "lint", "originality", "setup"])
    ap.add_argument("--changed", type=int, default=0, help="entries created or modified this run")
    ap.add_argument("--site-build", choices=["ok", "failed", "unknown"], default="unknown")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--precision", action="store_true")
    a = ap.parse_args()
    if a.precision:
        precision_report(); return 0
    rows = list(read_jsonl(HISTORY))
    if a.summary:
        if not rows:
            print("no metrics rows yet"); return 0
        print(json.dumps(rows[-1], ensure_ascii=False, indent=2)); return 0
    if not a.mode:
        ap.error("--mode is required to append a row")
    since = max((str(r.get("ts", "")) for r in rows), default="")
    rid = run_id()
    row = {"ts": eexlib.utcnow_iso(), "run_id": rid, "mode": a.mode, "entries_changed": a.changed}
    row.update(entry_stats()); row.update(queue_stats()); row.update(review_stats(since)); row.update(spend_stats(rid))
    row["site_build"] = a.site_build
    if a.dry_run:
        print("dry-run " + json.dumps(row, ensure_ascii=False)); return 0
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("metrics: " + json.dumps(row, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
