#!/usr/bin/env python3
"""Totals for usage.json: Claude subagents (tokens, wall time, API-equivalent dollars) and OpenRouter calls (billed dollars)."""
import glob
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
# US dollars per million tokens: input, cache write (1-hour), cache read, output (first-party list prices, 2026-10)
PRICE = {"claude-sonnet-5-5": (2, 4, 0.2, 10), "claude-haiku-5-5": (0.1, 0.2, 0.01, 0.5), "opus": (4, 8, 0.2, 20)}


def claude(d):
    t = {"tasks": 0, "input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "thinking": 0, "api_equiv_usd": 0.0}
    secs = []
    for u in d.values():
        t["tasks"] += 1
        for f in ("input", "cache_write", "cache_read", "output", "thinking"):
            t[f] += u[f]
        secs.append(u["seconds"] or 0)
        p = PRICE[u["model"]]
        t["api_equiv_usd"] += (u["input"] * p[0] + u["cache_write"] * p[1] + u["cache_read"] * p[2] + u["output"] * p[3]) / 1e6
    secs.sort()
    t["model"] = sorted({u["model"] for u in d.values()})
    t["api_equiv_usd"] = round(t["api_equiv_usd"], 3)
    t["median_seconds"], t["total_seconds"] = secs[len(secs) // 2], round(sum(secs))
    t["tokens_per_task"] = round((t["input"] + t["cache_write"] + t["cache_read"] + t["output"]) / t["tasks"])
    return t


out = {}
for arm in ("sonnet", "haiku"):
    out[arm] = claude(json.loads((HERE / "outputs" / arm / "meta.json").read_text()))
out["judge"] = claude(json.loads((HERE / "judge" / "meta.json").read_text()))
out["drafter"] = claude(json.loads((HERE / "outputs" / "drafter-meta.json").read_text()))
for arm in ("reviewer-a", "reviewer-b"):
    recs = [json.loads(Path(f).read_text()) for f in glob.glob(str(HERE / "outputs" / arm / "*.json"))]
    s = sorted(r["seconds"] for r in recs)
    out[arm] = {"tasks": len(recs), "billed_usd": round(sum(r["cost_usd"] for r in recs), 4),
                "tokens_in": sum(r["tokens_in"] for r in recs), "tokens_out": sum(r["tokens_out"] for r in recs),
                "median_seconds": s[len(s) // 2], "model": recs[0]["model"]}
for role in ("reviewer-a", "reviewer-b"):
    recs = [json.loads(Path(f).read_text()) for f in glob.glob(str(HERE / "judge" / f"x-{role}" / "*.json"))]
    out[f"xjudge-{role}"] = {"tasks": len(recs), "billed_usd": round(sum(r.get("cost_usd") or 0 for r in recs), 4)}
(HERE / "usage.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
