#!/usr/bin/env python3
"""run.py -- run decision models (and LLM baselines) over the test sets.

  python3 run.py --phase screen --models M1,M2 [--tasks t1,t2]
  python3 run.py --phase full   --models M1,M2 [--tasks ...]
  python3 run.py --phase full   --llm openai/gpt-5.6-terra [--tasks ...]

Each answer goes to results/<phase>/<model>/<task>.jsonl (resumable: items
already answered are skipped). Before a batch, tools/spend.py check is run on
an estimate; after it, one aggregated tools/spend.py record line per model and
phase carries the summed billed usage.cost. OPENROUTER_API_KEY is read by
dclient.py and never printed.
"""
from __future__ import annotations
import argparse, json, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from dclient import decide, chat  # noqa: E402

TASKS = ["pron", "defs", "exsense", "exok", "xref", "link", "triage", "count"]

NOUL = {
    "pron": ("Is this IPA transcription a correct standard General American pronunciation of the word, "
             "with the right sounds and the main stress (ˈ) on the right syllable?",
             {"true": "Every sound and the main stress match how the word is normally pronounced in General American English.",
              "false": "At least one sound is wrong, or the main stress is on the wrong syllable."}),
    "defs": ("Is this a correct definition of the given word, used as the given part of speech, in one of its real meanings?",
             {"true": "The definition describes a real meaning of this word.",
              "false": "The definition describes a different word, or a meaning this word does not have."}),
    "exok": ("Is this a good example sentence for this sense in a learner's dictionary: grammatical, natural English "
             "that uses the word with the stated meaning?",
             {"true": "The sentence is grammatical and natural, and it uses the word with the stated meaning.",
              "false": "The sentence has a grammar or word-order error or a wrong word form, or it does not use the word with the stated meaning."}),
    "xref": ("Would a learner who looks up the entry word be helped by a 'see also' link to the linked word, "
             "because the two words are closely related in meaning or use?",
             {"true": "The words are closely related: similar or opposite meanings, the same narrow topic, or often confused.",
              "false": "The words have no close relation in meaning or use."}),
    "triage": ("A reviewer objected to part of a learner's dictionary entry. Is the objection correct, so that the entry should be changed?",
               {"true": "The objection identifies a real error, or a real problem for learners, in the quoted text.",
                "false": "The objection is mistaken, exaggerated, or a matter of taste; the quoted text can stay as it is."}),
}
CHOICE = {
    "exsense": "Which sense of the word does the example sentence illustrate?",
    "link": "Which dictionary entry does the word belong to as it is used in this sentence?",
    "count": "How is this noun used in this meaning?",
}
COUNT_CRIT = {
    "countable": "It has a plural and is used with a or an, as in a chair, two chairs.",
    "uncountable": "It has no plural and is not used with a or an, as in some advice.",
    "countable or uncountable": "In this meaning it is used both ways, as in a coffee and some coffee.",
    "singular only": "It is used only in the singular, usually with the or a, as in the future or a shame.",
    "plural only": "It is used only in a plural form and takes a plural verb, as in scissors or clothes.",
}


def load(task, phase):
    items = [json.loads(l) for l in open(HERE / "sets" / f"{task}.jsonl")]
    return [it for it in items if it["screen"]] if phase == "screen" else items


def question(task, it):
    if task in NOUL:
        ins, crit = NOUL[task]
        return {"q": {"type": "noul", "instructions": ins, "criteria": crit}}
    crit = COUNT_CRIT if task == "count" else it["criteria"]
    return {"q": {"type": "choice", "instructions": CHOICE[task], "criteria": crit}}


def safe(m):
    return m.replace("/", "__").replace(":", "_")


def state_for(model, st):
    # Respan's models accept only a string state (or a chat transcript)
    return json.dumps(st, ensure_ascii=False) if model.startswith("respan/") else st


def ask_decision(model, task, it):
    r = decide(model, state_for(model, it["state"]), question(task, it))
    a = (r["answers"] or {}).get("q") or {}
    out = {"id": it["id"], "cost": r["cost"], "lat": round(r["latency"], 3), "tok": r["tokens_in"], "err": r["error"]}
    if task in NOUL:
        out["p"] = a.get("noul")
    else:
        out["choice"] = a.get("choice"); out["conf"] = a.get("confidence"); out["probs"] = a.get("probabilities")
    return out


def llm_prompt(task, it):
    q = question(task, it)["q"]
    lines = [f"Item (JSON): {json.dumps(it['state'], ensure_ascii=False)}", f"Question: {q['instructions']}"]
    if q["type"] == "noul":
        lines += [f"- yes: {q['criteria']['true']}", f"- no: {q['criteria']['false']}",
                  'Reply with JSON only: {"answer": "yes" or "no", "p_yes": probability from 0 to 1 that yes is correct}']
    else:
        lines += ["Options:"] + [f"- {k}: {v}" for k, v in q["criteria"].items()]
        lines += ['Reply with JSON only: {"answer": "<option key exactly as written>", "confidence": 0 to 1}']
    return [{"role": "system", "content": "You answer one classification question about an item from an English learner's dictionary. Reply with JSON only, no explanation."},
            {"role": "user", "content": "\n".join(lines)}]


def parse_json(text):
    if not text:
        return None
    s, e = text.find("{"), text.rfind("}")
    try:
        return json.loads(text[s:e + 1])
    except Exception:
        return None


def ask_llm(model, task, it):
    if model.startswith("stepfun/"):
        kw = {"reasoning": {"effort": "low"}, "max_tokens": 3000}
    elif model.startswith(("openai/", "anthropic/")):
        kw = {"reasoning": {"enabled": False}, "max_tokens": 80}
    else:
        kw = {"max_tokens": 80}
    r = chat(model, llm_prompt(task, it), **kw)
    j = parse_json(r["text"]) or {}
    out = {"id": it["id"], "cost": r["cost"], "lat": round(r["latency"], 3), "tok": r["tokens_in"],
           "tok_out": r.get("tokens_out"), "err": r["error"] or (None if j else f"unparsed: {str(r['text'])[:80]}")}
    if task in NOUL:
        p = j.get("p_yes")
        try:
            p = float(p)
        except (TypeError, ValueError):
            p = None
        if p is None and j.get("answer") in ("yes", "no"):
            p = 1.0 if j["answer"] == "yes" else 0.0
        # keep p consistent with the stated answer when the model contradicts itself
        if p is not None and j.get("answer") == "yes" and p < 0.5:
            p = 1 - p
        if p is not None and j.get("answer") == "no" and p > 0.5:
            p = 1 - p
        out["p"] = p
    else:
        out["choice"] = j.get("answer"); out["conf"] = j.get("confidence")
    return out


def spend(cmd, *args):
    return subprocess.run([sys.executable, str(ROOT / "tools/spend.py"), cmd, *args],
                          capture_output=True, text=True)


def run_model(model, tasks, phase, llm, workers):
    total = 0.0
    lock = threading.Lock()
    for task in tasks:
        items = load(task, phase)
        d = HERE / "results" / phase / safe(model)
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"{task}.jsonl"
        done = set()
        if f.exists():
            done = {json.loads(l)["id"] for l in open(f) if not json.loads(l).get("err")}
            keep = [l for l in open(f) if not json.loads(l).get("err")]
            f.write_text("".join(keep))
        todo = [it for it in items if it["id"] not in done]
        if not todo:
            continue
        fn = ask_llm if llm else ask_decision
        t0 = time.time()
        with ThreadPoolExecutor(workers) as ex, open(f, "a") as fh:
            for out in ex.map(lambda it: fn(model, task, it), todo):
                with lock:
                    fh.write(json.dumps(out, ensure_ascii=False) + "\n")
                    total += out["cost"] or 0
        errs = sum(1 for l in open(f) if json.loads(l).get("err"))
        print(f"{model:40s} {task:8s} n={len(todo):4d} {time.time()-t0:6.1f}s errors={errs} cost_so_far=${total:.5f}", flush=True)
    return total


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["screen", "full"], required=True)
    ap.add_argument("--models", default="")
    ap.add_argument("--llm", default="", help="comma-separated chat models (baselines)")
    ap.add_argument("--tasks", default=",".join(TASKS))
    ap.add_argument("--estimate", type=float, default=0.10, help="USD estimate passed to spend.py check")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    tasks = [t for t in a.tasks.split(",") if t]
    jobs = [(m, False) for m in a.models.split(",") if m] + [(m, True) for m in a.llm.split(",") if m]
    c = spend("check", "--cost", str(a.estimate))
    print(c.stdout.strip() or c.stderr.strip())
    if c.returncode != 0:
        sys.exit("budget check refused")
    with ThreadPoolExecutor(max(1, len(jobs))) as ex:
        costs = list(ex.map(lambda j: (j[0], run_model(j[0], tasks, a.phase, j[1], a.workers)), jobs))
    for m, cost in costs:
        if cost > 0:
            r = spend("record", "--cost", f"{cost:.6f}", "--purpose",
                      f"experiment:decision-models-v1:{a.phase}", "--model", m)
            print(r.stdout.strip() or r.stderr.strip())
