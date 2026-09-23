#!/usr/bin/env python3
"""Pick the mode for this Routine run (routine-prompt.md section 1).

    python3 tools/next_mode.py            # JSON: mode, params, reason, signals, budget
    python3 tools/next_mode.py --explain  # the same, human-readable
    python3 tools/next_mode.py --simulate 60

Deterministic and stateless: a smooth weighted round robin whose "debt" per mode
is replayed from the mode history in metrics/history.jsonl (append-only, so
overlapping runs never conflict over a state file). Rules from
config/routine-config.json: lint is forced after N runs without one; originality
every Nth run; site when the last site build failed; build is blocked when the
draft ceiling is reached or the day's remaining budget cannot pay for the panel
(then review or a free mode runs); closure needs closure candidates in the
queue; review needs entries that have had only one reading, or drafts.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402


def load_config() -> dict:
    return eexlib.load_json(eexlib.ROOT / "config" / "routine-config.json")


def history() -> list[dict]:
    p = eexlib.ROOT / "metrics" / "history.jsonl"
    rows = []
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln:
                try:
                    rows.append(json.loads(ln))
                except json.JSONDecodeError:
                    continue
    rows.sort(key=lambda r: r.get("ts", ""))
    return dedupe_runs(rows)


def dedupe_runs(rows: list[dict]) -> list[dict]:
    """One row per run: a run that called metrics.py twice counts once, at its first row's place, with its
    last row's content (wiki/notes/metrics-duplicate-calls.md). Rows without a run_id are kept as they are."""
    last = {r["run_id"]: r for r in rows if r.get("run_id")}
    out, seen = [], set()
    for r in rows:
        rid = r.get("run_id")
        if not rid:
            out.append(r)
        elif rid not in seen:
            seen.add(rid); out.append(last[rid])
    return out


def budget_remaining() -> tuple[float, float, float]:
    r = subprocess.run([sys.executable, str(HERE / "spend.py"), "status"], capture_output=True, text=True, cwd=eexlib.ROOT)
    spent = cap = remaining = 0.0
    for ln in r.stdout.splitlines():
        k, _, v = ln.partition(":")
        v = v.strip().lstrip("$")
        try:
            if k.strip() == "spent":
                spent = float(v)
            elif k.strip() == "cap":
                cap = float(v)
            elif k.strip() == "remaining":
                remaining = float(v)
        except ValueError:
            pass
    return spent, cap, remaining


def signals(cfg: dict) -> dict:
    drafts = reviewed = once_reviewed = 0
    for _p, e in eexlib.iter_entries():
        if eexlib.is_redirect_stub(e):
            continue
        st = e.get("provenance", {}).get("status")
        if st == "draft":
            drafts += 1
        elif st == "reviewed":
            reviewed += 1
            runs = {r.get("run_id") for r in e.get("provenance", {}).get("reviews", [])}
            if len(runs) <= 1:
                once_reviewed += 1
    q = eexlib.ROOT / "headwords" / "queue.tsv"
    pending = closure = 0
    if q.exists():
        with q.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if r.get("status") == "pending":
                    pending += 1
                    if r.get("source") in ("closure", "family", "crossref"):
                        closure += 1
    hist = history()
    runs_since_lint = 0
    for r in reversed(hist):
        if r.get("mode") == "lint":
            break
        runs_since_lint += 1
    last_site = next((r.get("site_build") for r in reversed(hist) if r.get("site_build") not in (None, "unknown")), None)
    spent, cap, remaining = budget_remaining()
    return {"entries_draft": drafts, "entries_reviewed": reviewed, "reviewed_once_only": once_reviewed,
            "queue_pending": pending, "queue_closure": closure, "runs_total": len(hist),
            "runs_since_lint": runs_since_lint, "last_site_build": last_site,
            "budget_spent_usd": round(spent, 4), "budget_cap_usd": cap, "budget_remaining_usd": round(remaining, 4),
            "last_mode": hist[-1].get("mode") if hist else None}


def eligibility(cfg: dict, sig: dict) -> tuple[dict, dict, str | None]:
    """(eligible flags, reasons, forced mode or None)."""
    elig = {m: True for m in cfg["modes"]}
    why = {m: [] for m in cfg["modes"]}
    per_run = float(cfg.get("per_run_cap_usd", 1.0))
    panel_cost = float(cfg["panel_cost_per_entry_usd"]) + float(cfg["pronunciation_cost_per_entry_usd"])
    forced = None
    if sig["entries_draft"] >= int(cfg["draft_ceiling"]):
        elig["build"] = elig["closure"] = False
        why["build"].append(f"draft ceiling reached ({sig['entries_draft']} drafts)")
        why["closure"].append("draft ceiling reached")
    min_budget = panel_cost * 5  # at least five entries' worth of review
    if sig["budget_remaining_usd"] < min_budget:
        for m in ("build", "closure", "review"):
            elig[m] = False
            why[m].append(f"remaining budget ${sig['budget_remaining_usd']:.2f} below ${min_budget:.2f}")
    if sig["queue_closure"] == 0:
        elig["closure"] = False
        why["closure"].append("no closure candidates in the queue")
    if sig["reviewed_once_only"] == 0 and sig["entries_draft"] == 0:
        elig["review"] = False
        why["review"].append("nothing needs a second reading")
    if sig["queue_pending"] == 0:
        elig["build"] = False
        why["build"].append("queue empty")
    if sig["runs_since_lint"] >= int(cfg["lint_every_runs"]) and sig["runs_total"] > 0:
        forced = "lint"
        why["lint"].append(f"forced: {sig['runs_since_lint']} runs since the last lint")
    n = int(cfg["originality_every_runs"])
    if n and sig["runs_total"] > 0 and (sig["runs_total"] + 1) % n == 0 and forced is None:
        forced = "originality"
        why["originality"].append(f"forced: run {sig['runs_total'] + 1} is a multiple of {n}")
    if sig["last_site_build"] == "failed" and forced is None:
        forced = "site"
        why["site"].append("forced: the last site build failed")
    return elig, why, forced


def debts(cfg: dict, hist: list[dict]) -> dict:
    w = {m: float(cfg["weights"].get(m, 0.0)) for m in cfg["modes"]}
    total = sum(w.values()) or 1.0
    d = {m: 0.0 for m in cfg["modes"]}
    for r in hist:
        for m in d:
            d[m] += w[m] / total
        m = r.get("mode")
        if m in d:
            d[m] -= 1.0
    return d


def choose(cfg: dict, sig: dict, hist: list[dict]) -> tuple[str, str]:
    elig, why, forced = eligibility(cfg, sig)
    if forced:
        return forced, "; ".join(why[forced])
    d = debts(cfg, hist)
    w = cfg["weights"]
    anti = set(cfg.get("anti_repeat_modes", []))
    cands = [m for m in cfg["modes"] if elig[m] and float(w.get(m, 0)) > 0 and not (m in anti and sig.get("last_mode") == m)]
    if not cands:
        cands = [m for m in cfg["modes"] if elig[m]] or ["lint"]
    best = max(cands, key=lambda m: (d[m] + float(w.get(m, 0)) / (sum(float(x) for x in w.values()) or 1.0), float(w.get(m, 0))))
    reason = f"highest scheduler debt among eligible modes ({', '.join(cands)})"
    blocked = [f"{m}: {'; '.join(why[m])}" for m in cfg["modes"] if not elig[m] and why[m]]
    if blocked:
        reason += " | blocked: " + " / ".join(blocked)
    return best, reason


def params_for(mode: str, cfg: dict, sig: dict) -> dict:
    per_run = float(cfg.get("per_run_cap_usd", 1.0))
    budget = round(min(per_run, sig["budget_remaining_usd"]), 2)
    unit = float(cfg["panel_cost_per_entry_usd"]) + float(cfg["pronunciation_cost_per_entry_usd"])
    affordable = int(budget // unit) if unit else 0
    if mode == "build":
        n = min(int(cfg["entries_per_run"]), max(0, int(cfg["draft_ceiling"]) - sig["entries_draft"]), affordable)
        return {"max_new_entries": n, "run_budget_usd": budget, "source": "defining or band, queue order"}
    if mode == "closure":
        n = min(int(cfg["entries_per_run"]), max(0, int(cfg["draft_ceiling"]) - sig["entries_draft"]), affordable, sig["queue_closure"])
        return {"max_new_entries": n, "run_budget_usd": budget, "source": "closure, family, crossref"}
    if mode == "review":
        return {"block_size": min(int(cfg["review_block_size"]), affordable), "run_budget_usd": budget,
                "take": "all draft entries first, then reviewed entries read only once"}
    if mode == "originality":
        return {"sample": 10, "run_budget_usd": round(min(0.10, sig["budget_remaining_usd"]), 2)}
    return {"run_budget_usd": 0.0}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--simulate", type=int, metavar="N")
    ap.add_argument("--force", choices=["build", "review", "closure", "site", "lint", "originality"])
    a = ap.parse_args()
    cfg = load_config()
    sig = signals(cfg)
    hist = history()
    if a.simulate:
        sim = list(hist)
        tally = {m: 0 for m in cfg["modes"]}
        s2 = dict(sig)
        for _ in range(a.simulate):
            s2["runs_total"] = len(sim)
            s2["runs_since_lint"] = 0
            for r in reversed(sim):
                if r.get("mode") == "lint":
                    break
                s2["runs_since_lint"] += 1
            s2["last_mode"] = sim[-1]["mode"] if sim else None
            m, _ = choose(cfg, s2, sim)
            tally[m] += 1
            sim.append({"ts": f"sim{len(sim):05d}", "mode": m})
        for m, c in tally.items():
            print(f"{m:12s} {c:5d} {100 * c / a.simulate:5.1f}%  (weight {100 * float(cfg['weights'][m]):.0f}%)")
        return 0
    mode, reason = (a.force, "forced from the command line") if a.force else choose(cfg, sig, hist)
    out = {"mode": mode, "params": params_for(mode, cfg, sig), "reason": reason, "signals": sig}
    if a.explain:
        d = debts(cfg, hist)
        print(f"mode: {mode}\nreason: {reason}\nsignals:")
        for k, v in sig.items():
            print(f"  {k:24s} {v}")
        print("debts: " + ", ".join(f"{m}={d[m]:.2f}" for m in cfg["modes"]))
        print("params: " + json.dumps(out["params"]))
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
