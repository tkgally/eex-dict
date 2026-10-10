#!/usr/bin/env python3
"""export.py -- compact verdicts.tsv from results/ (results/ itself is not committed).

Columns: phase, model, item id, answer (p(yes) for yes-no tasks, the chosen option for
choice tasks), confidence, billed cost in USD, latency in seconds.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
with open(HERE / "verdicts.tsv", "w") as out:
    out.write("phase\tmodel\tid\tanswer\tconfidence\tcost_usd\tlatency_s\terror\n")
    for phase in ("screen", "full"):
        for d in sorted((HERE / "results" / phase).iterdir()):
            if d.name.startswith("ensemble"):
                continue
            for f in sorted(d.glob("*.jsonl")):
                for l in open(f):
                    r = json.loads(l)
                    ans = r.get("p") if "p" in r else r.get("choice")
                    if isinstance(ans, float):
                        ans = round(ans, 4)
                    conf = r.get("conf")
                    conf = round(conf, 4) if isinstance(conf, (int, float)) else ""
                    out.write(f"{phase}\t{d.name}\t{r['id']}\t{'' if ans is None else ans}\t{conf}\t"
                              f"{round(r.get('cost') or 0, 8)}\t{r.get('lat')}\t{'1' if r.get('err') else ''}\n")
