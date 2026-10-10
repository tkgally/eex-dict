#!/usr/bin/env python3
"""pilot.py -- run two decision models over real, unaltered entries and list what they flag.

  exsense: 1,500 examples sampled from entries with 2-6 senses; flagged when both
           models pick a sense other than the one the example is filed under.
  xref:    every see_also link in the dictionary; flagged when both models give
           p(useful) < 0.5.
Writes pilot/<task>.jsonl (all verdicts) and pilot/<task>-flags.jsonl.
"""
import glob, json, random, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from dclient import decide  # noqa: E402
from run import NOUL, CHOICE, spend  # noqa: E402
from build_sets import POSNAME, strip_marks, first_def  # noqa: E402

MODELS = ["microsoft/microsoft-decision-1", "perplexity/pplx-decider-v1.1-27b"]
E = [json.load(open(f)) for f in sorted(glob.glob(str(ROOT / "entries/*/*.json")))]
BY = {e["slug"]: e for e in E}
rng = random.Random(7)
out = HERE / "pilot"; out.mkdir(exist_ok=True)

ex_items = []
for e in E:
    if 2 <= len(e["senses"]) <= 6:
        crit = {f"sense_{i+1}": (f"({s['signpost']}) " if s.get("signpost") else "") + strip_marks(s["definition"])
                for i, s in enumerate(e["senses"])}
        for k, s in enumerate(e["senses"]):
            for x in s["examples"]:
                ex_items.append({"slug": e["slug"], "filed": f"sense_{k+1}", "criteria": crit,
                                 "state": {"word": e["headword"], "part_of_speech": POSNAME[e["pos"]],
                                           "example_sentence": strip_marks(x["text"])}})
rng.shuffle(ex_items)
ex_items = ex_items[:1500]
xr_items = [{"slug": e["slug"], "target": x["slug"],
             "state": {"entry_word": e["headword"], "entry_part_of_speech": POSNAME[e["pos"]], "entry_meaning": first_def(e),
                       "linked_word": BY[x["slug"]]["headword"], "linked_part_of_speech": POSNAME[BY[x["slug"]]["pos"]],
                       "linked_meaning": first_def(BY[x["slug"]])}}
            for e in E for x in (e.get("see_also") or []) if x["slug"] in BY]

cost = {m: 0.0 for m in MODELS}


def ask(args):
    m, task, it = args
    q = ({"q": {"type": "choice", "instructions": CHOICE["exsense"], "criteria": it["criteria"]}} if task == "exsense"
         else {"q": {"type": "noul", "instructions": NOUL["xref"][0], "criteria": NOUL["xref"][1]}})
    r = decide(m, it["state"], q)
    cost[m] += r["cost"]
    a = (r["answers"] or {}).get("q") or {}
    return a.get("choice") if task == "exsense" else a.get("noul"), a.get("confidence")


c = spend("check", "--cost", "0.05"); print(c.stdout.strip())
if c.returncode:
    sys.exit("budget")
for task, items in (("exsense", ex_items), ("xref", xr_items)):
    with ThreadPoolExecutor(12) as ex:
        res = {m: list(ex.map(ask, [(m, task, it) for it in items])) for m in MODELS}
    flags = []
    with open(out / f"{task}.jsonl", "w") as fh:
        for i, it in enumerate(items):
            v = {m.split("/")[0]: res[m][i] for m in MODELS}
            row = {k: it[k] for k in it if k not in ("criteria",)}
            row["verdicts"] = v
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            if task == "exsense":
                picks = [res[m][i][0] for m in MODELS]
                if all(p and p != it["filed"] for p in picks):
                    row["picked"] = picks
                    row["filed_def"] = it["criteria"][it["filed"]]
                    row["picked_def"] = [it["criteria"].get(p) for p in picks]
                    flags.append(row)
            else:
                ps = [res[m][i][0] for m in MODELS]
                if all(p is not None and p < 0.5 for p in ps):
                    flags.append(row)
    with open(out / f"{task}-flags.jsonl", "w") as fh:
        for f in flags:
            fh.write(json.dumps(f, ensure_ascii=False) + "\n")
    print(task, len(items), "items,", len(flags), "flagged")
for m in MODELS:
    print(spend("record", "--cost", f"{cost[m]:.6f}", "--purpose", "experiment:decision-models-v1:pilot", "--model", m).stdout.strip())
