#!/usr/bin/env python3
"""Run the pronunciation model test: ask every role in design.md section 2 for the
American and British IPA of every word in words.tsv, and save the raw replies.

    python3 experiments/pronunciation-model-test-v1/run.py [--roles drafter,pronunciation-1,...]

Replies go to outputs/<role>.json (the models' own output, committed as the
record). A role whose output file exists is skipped, so an interrupted run
resumes. The prompt, chunking, and temperature are those fixed in
tools/pronounce_check.py, which the pipeline uses too.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pronounce_check as pc  # noqa: E402

ROLES = ["drafter", "pronunciation-1", "pronunciation-2", "pronunciation-3"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roles", default=",".join(ROLES))
    a = ap.parse_args()
    with (HERE / "words.tsv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    items = [(r["word"], r["pos"]) for r in rows]
    (HERE / "outputs").mkdir(exist_ok=True)
    for role in a.roles.split(","):
        out = HERE / "outputs" / f"{role}.json"
        have: dict[tuple[str, str], dict] = {}
        model = None
        if out.exists():
            d = json.loads(out.read_text(encoding="utf-8"))
            model = d.get("model")
            have = {(it["w"].lower(), it["pos"]): it for it in d["items"]}
        # first pass, then up to two top-ups for items a chunk lost (truncated or unparsable reply)
        for attempt, chunk in ((0, 50), (1, 25), (2, 10)):
            missing = [(w, p) for (w, p) in items if (w.lower(), p) not in have]
            if not missing:
                break
            if attempt == 0 and have:
                continue
            print(f"{role}: asking for {len(missing)} item(s), chunk {chunk}", flush=True)
            res = pc.ask_panel(missing, [role], purpose="pron-test-v1", chunk=chunk)[role]
            for (w, p), v in res.items():
                if v.get("american") or v.get("british"):
                    have[(w, p)] = {"w": w, "pos": p, "american": v["american"], "british": v["british"]}
                    model = model or v.get("model")
        record = {"role": role, "model": model, "n_items": len(have),
                  "items": [have[(w.lower(), p)] for (w, p) in items if (w.lower(), p) in have]}
        out.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{role}: {len(have)} of {len(items)} items answered (costs are in config/budget-ledger.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
