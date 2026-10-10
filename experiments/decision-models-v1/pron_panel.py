#!/usr/bin/env python3
"""pron_panel.py -- the production pronunciation check as a baseline for the pron set.

The three panel roles (config/models.md) transcribe each word through
tools/pronounce_check.ask_panel (budget-checked and recorded by call_with_budget);
a shown transcription counts as accepted when at least two panel members agree with
it under N2, the production rule without the run-time CMU vote. Writes
results/full/panel__pronunciation-3/pron.jsonl with p = agreeing / 3.
"""
import json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pronounce_check as pc  # noqa: E402

items = [json.loads(l) for l in open(HERE / "sets/pron.jsonl")]
POS = {"noun": "n", "verb": "v", "adjective": "adj", "adverb": "adv"}
words = sorted({(it["state"]["word"].lower(), POS[it["state"]["part_of_speech"]]) for it in items})
roles = ["pronunciation-1", "pronunciation-2", "pronunciation-3"]
t0 = time.time()
votes = pc.ask_panel(words, roles, purpose="experiment:decision-models-v1:pron-panel")
elapsed = time.time() - t0
cost = sum(v.get("cost_usd") or 0 for r in votes.values() for v in r.values())
out = HERE / "results/full/panel__pronunciation-3"
out.mkdir(parents=True, exist_ok=True)
with open(out / "pron.jsonl", "w") as fh:
    for it in items:
        key = (it["state"]["word"].lower(), POS[it["state"]["part_of_speech"]])
        shown = it["state"]["ipa_general_american"]
        got = [votes[r].get(key, {}).get("american", "") for r in roles]
        agreeing = sum(1 for g in got if g and pc.agree(shown, g, "american"))
        fh.write(json.dumps({"id": it["id"], "p": agreeing / 3, "votes": got, "cost": 0, "lat": elapsed / len(words),
                             "tok": 0, "err": None}, ensure_ascii=False) + "\n")
print(f"panel: {len(words)} words, {elapsed:.0f}s, chunk costs as recorded in the ledger")
