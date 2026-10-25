#!/usr/bin/env python3
"""Newer or cheaper OpenRouter models against the ones in config/models.md (design in README.md).

Reviewer test (reuses ../claude-reviewers-v1: its 28 inputs, planted-defect key, prompts and baseline outputs):

    python3 harness.py review --model google/gemini-3.8-flash --arm flash [--slugs ...] [--workers 4]
                                    # production review_panel.py call, raw + normalized reply to outputs/<arm>/<slug>.json
    python3 harness.py judge --arms reviewer-b,sonnet-cli-xhigh,flash,argon
                                    # blind pools judged by a headless Opus call: judge/<slug>.{pool,key,verdicts}.json
    python3 harness.py score        # results-review.json and a printed table

Pronunciation test (reuses ../pronunciation-model-test-v1: its 500 words and the 2026-09-16 panel outputs):

    python3 harness.py pron --model openai/gpt-6.1-sol --arm gpt-6.1-sol
    python3 harness.py pronscore    # agreement with CMU (American, fetched to .tmp/) and with the drafter (British)

Arms that existed before this experiment are read from the older folders: reviewer-b (Gemini 3.1 Pro) and
sonnet-cli-xhigh (headless Sonnet, the model behind today's reviewer-a) from claude-reviewers-v1/outputs;
pronunciation-1..3 and drafter from pronunciation-model-test-v1/outputs.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1 = ROOT / "experiments" / "claude-reviewers-v1"
PRON = ROOT / "experiments" / "pronunciation-model-test-v1"
sys.path.insert(0, str(ROOT / "tools"))
import openrouter  # noqa: E402
import pronounce_check as pc  # noqa: E402
import review_panel as rp  # noqa: E402

RUN_ID = "20261025T140734Z-mrefv1"
REASONING = None                     # --reasoning '{"effort": "low"}' for a model that refuses to switch it off
OLD_ARMS = {"reviewer-b", "sonnet-cli-xhigh", "reviewer-a", "sonnet-cli", "haiku-cli"}


def inputs(slugs=None):
    return [(p.stem, json.loads(p.read_text())) for p in sorted((V1 / "inputs").glob("*.json"))
            if not slugs or p.stem in slugs]


def outdir(arm):
    return (V1 if arm in OLD_ARMS else HERE) / "outputs" / arm


def load_outputs(arm):
    return {p.stem: json.loads(p.read_text()) for p in outdir(arm).glob("*.json") if not p.name.endswith((".raw.json", "meta.json"))}


def normalize_into(rec):
    fields = json.loads((V1 / "prompts" / f"{rec['slug']}.fields.json").read_text())
    rec["verdicts"], rec["parse_error"] = [], None
    if rec.get("error"):
        return
    try:
        raw = openrouter.parse_json_reply(rec.get("text") or "")
    except ValueError as ex:
        rec["parse_error"] = str(ex)
        return
    rec["verdicts"], rec["parse_error"] = rp.normalize_verdicts(raw, fields, None)
    rec["summary"] = raw.get("summary") if isinstance(raw, dict) else None


def one_review(model, arm, slug, e):
    system, prompt, fields = rp.system_prompt(), rp.user_prompt(e), rp.checklist(e)
    est = round((len(system) // 4 + len(prompt) // 4) * 2e-6 + (120 * len(fields) + 3000) * 12e-6, 6)
    t0 = time.time()
    rec = {"arm": arm, "model": model, "slug": slug}
    try:
        res = openrouter.call_with_budget(model, [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                                          purpose=f"experiment:model-refresh-v1:{slug}:{arm}", estimate_usd=est, run_id=RUN_ID,
                                          max_tokens=120 * len(fields) + 3000, temperature=0.1,
                                          response_format={"type": "json_object"}, json_schema=rp.REPLY_SCHEMA,
                                          reasoning=REASONING or openrouter.reasoning_for(model))
        rec.update({"seconds": round(time.time() - t0, 1), "cost_usd": res.get("cost"), "tokens_in": res.get("tokens_in"),
                    "tokens_out": res.get("tokens_out"), "finish": res.get("finish_reason"), "text": res.get("text"),
                    "model_used": res.get("model")})
    except Exception as ex:  # noqa: BLE001
        rec.update({"seconds": round(time.time() - t0, 1), "error": f"{type(ex).__name__}: {str(ex)[:300]}"})
    normalize_into(rec)
    return rec


def cmd_review(a):
    od = outdir(a.arm)
    od.mkdir(parents=True, exist_ok=True)
    todo = [(s, e) for s, e in inputs(a.slugs) if a.force or not (od / f"{s}.json").exists()]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for rec in pool.map(lambda se: one_review(a.model, a.arm, *se), todo):
            (od / f"{rec['slug']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
            print(rec["slug"], rec.get("seconds"), rec.get("cost_usd"), rec.get("error") or rec.get("parse_error") or
                  f"{sum(v['verdict'] == 'issue' for v in rec['verdicts'])} issues", flush=True)


def claude_cli(model, system, user, effort=None):
    sys.path.insert(0, str(V1))
    import harness as v1h  # the same headless call the earlier experiment used
    return v1h.claude_cli(model, system, user, effort)


def cmd_judge(a):
    """Blind adjudication with the earlier experiment's instructions, all arms pooled per entry."""
    arms = a.arms.split(",")
    jd = HERE / a.dir
    jd.mkdir(exist_ok=True)
    planted = json.loads((V1 / "planted.json").read_text())
    instructions = (V1 / "judge" / "INSTRUCTIONS.md").read_text()
    style = (ROOT / "wiki" / "style-guide.md").read_text()
    system = ("You are a blind adjudicator in an experiment. Follow these instructions; the files they name are given to you inline "
              "below instead, and your output is the JSON object they describe, printed as your whole reply (no file, no code fence).\n\n"
              + instructions + "\n\nprompts/system.txt (the house rules the reviewers were given):\n" + rp.system_prompt()
              + "\n\nwiki/style-guide.md:\n" + style)
    rng = random.Random(20261025)
    outs = {arm: load_outputs(arm) for arm in arms}
    todo = []
    for slug, e in inputs(a.slugs):
        if (jd / f"{slug}.verdicts.json").exists() and "error" not in json.loads((jd / f"{slug}.verdicts.json").read_text()):
            continue
        items = []
        for arm in arms:
            for v in (outs[arm].get(slug) or {}).get("verdicts", []):
                if v["verdict"] == "issue":
                    items.append({"arm": arm, **{k: v[k] for k in ("field", "quote", "severity", "family", "reason")}})
        rng.shuffle(items)
        key = [{"id": i, "arm": it["arm"]} for i, it in enumerate(items, 1)]
        pool = [{"id": i, **{k: it[k] for k in ("field", "quote", "severity", "family", "reason")}} for i, it in enumerate(items, 1)]
        (jd / f"{slug}.pool.json").write_text(json.dumps(pool, ensure_ascii=False, indent=1) + "\n")
        (jd / f"{slug}.key.json").write_text(json.dumps(key) + "\n")
        todo.append((slug, e, pool))

    def one(t):
        slug, e, pool = t
        pl = [p for p in planted if p["slug"] == slug]
        plant_txt = ("Planted defects for this entry (deliberately damaged to test the reviewers): " +
                     "; ".join(f"{p['id']} ({p['field']}): {p['defect']}" for p in pl) + ". Other real problems may also exist."
                     ) if pl else "This entry is a fresh draft with no planted defects: use [] for every planted field."
        user = (f"Entry slug: {slug}. {plant_txt}\n\ninputs/{slug}.json:\n" + json.dumps(e, ensure_ascii=False, indent=1) +
                f"\n\njudge/{slug}.pool.json:\n" + json.dumps(pool, ensure_ascii=False, indent=1))
        text, meta = claude_cli(a.model, system, user, a.effort)
        try:
            out = openrouter.parse_json_reply(text or "")
        except ValueError as ex:
            out = {"error": str(ex), "raw": (text or "")[:500]}
        out["_meta"] = meta
        (jd / f"{slug}.verdicts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
        return slug, len(pool), meta.get("seconds"), out.get("error")

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for r in ex.map(one, todo):
            print(*r, flush=True)


def cmd_score(a):
    jd = HERE / a.dir
    planted = json.loads((V1 / "planted.json").read_text())
    pset = {p["slug"]: p["set"] for p in planted}
    st, hits, finds, falseb = {}, {}, {}, {}
    all_blocking_findings = set()
    for slug, _e in inputs():
        vf = jd / f"{slug}.verdicts.json"
        if not vf.exists():
            continue
        jv = {int(j["id"]): j for j in json.loads(vf.read_text()).get("issues", [])}
        pool = {p["id"]: p for p in json.loads((jd / f"{slug}.pool.json").read_text())}
        for k in json.loads((jd / f"{slug}.key.json").read_text()):
            j, it, arm = jv.get(k["id"], {"valid": "missing"}), pool[k["id"]], k["arm"]
            for g in (pset.get(slug, "natural"), "all"):
                s = st.setdefault((arm, g), {"n": 0, "yes": 0, "blocking": 0, "b_yes": 0, "b_no": 0, "missing": 0})
                s["n"] += 1; s["yes"] += j["valid"] == "yes"; s["missing"] += j["valid"] == "missing"
                if it["severity"] == "blocking":
                    s["blocking"] += 1; s["b_yes"] += j["valid"] == "yes"; s["b_no"] += j["valid"] in ("no", "partly")
            if it["severity"] == "blocking" and j["valid"] in ("no", "partly"):
                falseb[arm] = falseb.get(arm, 0) + 1
            if j["valid"] == "yes" and j.get("finding"):
                f = f"{slug}#{j['finding']}"
                finds.setdefault(arm, set()).add(f)
                if it["severity"] == "blocking":
                    all_blocking_findings.add(f)
            for pid in j.get("planted") or []:
                pid = str(pid); pid = pid if "#" in pid else f"{slug}#{pid}"
                if j["valid"] in ("yes", "partly"):
                    hits.setdefault(arm, set()).add(pid)
    arms = sorted({arm for arm, _ in st})
    cost = {}
    for arm in arms:
        recs = load_outputs(arm).values()
        c = [r.get("cost_usd") for r in recs if r.get("cost_usd") is not None]
        secs = sorted(r.get("seconds") or 0 for r in recs)
        cost[arm] = {"usd_per_entry": round(sum(c) / max(len(c), 1), 4), "median_seconds": secs[len(secs) // 2] if secs else None,
                     "errors": sum(bool(r.get("error") or r.get("parse_error")) for r in recs)}
    res = {"arms": {}, "panels": {}, "blocking_findings_total": len(all_blocking_findings), "planted_total": len(planted)}
    print(f"real blocking-level findings in the union of all arms: {len(all_blocking_findings)}")
    for arm in arms:
        s = st[(arm, "all")]
        bf = finds.get(arm, set()) & all_blocking_findings
        r = {"issues": s["n"], "precision": round(s["yes"] / max(s["n"], 1), 2), "blocking": s["blocking"],
             "blocking_precision": round(s["b_yes"] / max(s["blocking"], 1), 2), "false_blocking": s["b_no"],
             "planted_found": len(hits.get(arm, set())), "blocking_findings": len(bf), "unjudged": s["missing"],
             "by_set": {g: {"issues": st[(arm, g)]["n"], "precision": round(st[(arm, g)]["yes"] / max(st[(arm, g)]["n"], 1), 2)}
                        for g in ("obvious", "subtle", "natural") if (arm, g) in st},
             "missed_planted": sorted({p["id"] for p in planted} - hits.get(arm, set())), **cost[arm]}
        res["arms"][arm] = r
        print(f"{arm:17s} issues {r['issues']:4d} prec {r['precision']:.2f} blocking {r['blocking']:3d} "
              f"b-prec {r['blocking_precision']:.2f} false-b {r['false_blocking']:3d} planted {r['planted_found']:2d}/{len(planted)} "
              f"blocking-findings {r['blocking_findings']:3d} ${r['usd_per_entry']:.4f}/entry {r['median_seconds']}s err {r['errors']}")
    partner = "sonnet-cli-xhigh"
    for arm in arms:
        if arm == partner:
            continue
        u = (finds.get(partner, set()) | finds.get(arm, set())) & all_blocking_findings
        res["panels"][f"{partner}+{arm}"] = {"blocking_findings": len(u), "false_blocking": falseb.get(partner, 0) + falseb.get(arm, 0)}
        print(f"panel {partner}+{arm}: blocking findings {len(u)}, false blocking {falseb.get(partner, 0) + falseb.get(arm, 0)}")
    (HERE / ("results-review.json" if a.dir == "judge" else f"results-{a.dir}.json")).write_text(json.dumps(res, indent=1) + "\n")


# --- pronunciation --------------------------------------------------------------

def pron_items():
    with (PRON / "words.tsv").open(encoding="utf-8") as f:
        return [(r["word"], r["pos"], r["stratum"]) for r in csv.DictReader(f, delimiter="\t")]


def cmd_pron(a):
    """The production pronunciation call (prompt, chunk, temperature, no reasoning) with a model slug in place of a role."""
    out = HERE / "outputs" / "pron" / f"{a.arm}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    have = {}
    if out.exists():
        have = {(it["w"].lower(), it["pos"]): it for it in json.loads(out.read_text())["items"]}
    items = [(w, p) for w, p, _ in pron_items()]
    cost = 0.0
    for chunk in (50, 25, 10):
        missing = [(w, p) for w, p in items if (w.lower(), p) not in have]
        if not missing:
            break
        print(f"{a.arm}: asking for {len(missing)} item(s), chunk {chunk}", flush=True)
        for i in range(0, len(missing), chunk):
            batch = missing[i:i + chunk]
            user = pc.PROMPT + "\n".join(f"{w}|{p}" for w, p in batch)
            try:
                res = openrouter.call_with_budget(a.model, [{"role": "user", "content": user}],
                                                  purpose=f"experiment:model-refresh-v1:pron:{a.arm}",
                                                  estimate_usd=round((500 + 8 * len(batch)) * 2e-6 + 60 * len(batch) * 12e-6, 6),
                                                  run_id=RUN_ID, max_tokens=60 * len(batch) + 600, temperature=0.1,
                                                  response_format={"type": "json_object"},
                                                  reasoning=REASONING or openrouter.reasoning_for(a.model, "pronunciation"))
                cost += res.get("cost") or 0
                data = openrouter.parse_json_reply(res["text"])
            except Exception as e:  # noqa: BLE001
                print(f"  chunk of {len(batch)} failed: {str(e)[:160]}", flush=True)
                continue
            for it in data.get("items", []) if isinstance(data, dict) else []:
                if isinstance(it, dict) and (it.get("american") or it.get("british")):
                    k = (str(it.get("w", "")).strip().lower(), str(it.get("pos", "")).strip().lower())
                    have[k] = {"w": k[0], "pos": k[1], "american": str(it.get("american", "")), "british": str(it.get("british", ""))}
    rec = {"role": a.arm, "model": a.model, "n_items": len(have), "cost_usd": round(cost, 6),
           "items": [have[(w.lower(), p)] for w, p in items if (w.lower(), p) in have]}
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
    print(f"{a.arm}: {len(have)} of {len(items)} answered, ${cost:.4f}")


def cmd_pronscore(a):
    cmu = pc.fetch_cmudict()
    if cmu is None:
        print("cmudict unreachable: American scores need it"); return
    arms = {}
    for p in sorted((PRON / "outputs").glob("*.json")):
        arms[p.stem + " (2026-09-16)"] = json.loads(p.read_text())
    for p in sorted((HERE / "outputs" / "pron").glob("*.json")):
        arms[p.stem] = json.loads(p.read_text())
    words = pron_items()
    ref = {(it["w"].lower(), it["pos"]): it for it in json.loads((PRON / "outputs" / "drafter.json").read_text())["items"]}
    res = {}
    strata = sorted({s for _, _, s in words})
    print(f"{'arm':34s} {'answered':>8s} {'CMU agree (US)':>15s} " + " ".join(f"{s[:9]:>9s}" for s in strata) + f" {'drafter UK':>10s}")
    for name, d in arms.items():
        got = {(it["w"].lower(), it["pos"]): it for it in d["items"]}
        tot = {"all": [0, 0]}
        uk = [0, 0]
        for w, p, stratum in words:
            it = got.get((w.lower(), p))
            forms = cmu.get(w.lower())
            if forms:
                ok = bool(it and it.get("american") and pc.agree(pc.cmu_votes(w, cmu, it["american"]), it["american"], "american"))
                for g in ("all", stratum):
                    t = tot.setdefault(g, [0, 0]); t[0] += ok; t[1] += 1
            r = ref.get((w.lower(), p))
            if r and r.get("british") and not name.startswith("drafter"):
                uk[1] += 1
                uk[0] += bool(it and it.get("british") and pc.agree(r["british"], it["british"], "british"))
        f = lambda g: f"{100 * tot[g][0] / tot[g][1]:.1f}" if g in tot and tot[g][1] else "-"
        res[name] = {"answered": len(got), "cmu_agree_pct": f("all"), "by_stratum": {g: f(g) for g in tot if g != "all"},
                     "drafter_british_agree_pct": f"{100 * uk[0] / uk[1]:.1f}" if uk[1] else "-", "cost_usd": d.get("cost_usd")}
        print(f"{name:34s} {len(got):8d} {f('all'):>15s} " + " ".join(f"{f(s):>9s}" for s in strata) +
              f" {res[name]['drafter_british_agree_pct']:>10s}")
    (HERE / "results-pron.json").write_text(json.dumps(res, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review"); r.add_argument("--model", required=True); r.add_argument("--arm", required=True)
    r.add_argument("--slugs", nargs="*"); r.add_argument("--workers", type=int, default=4); r.add_argument("--force", action="store_true")
    j = sub.add_parser("judge"); j.add_argument("--arms", required=True); j.add_argument("--model", default="opus")
    j.add_argument("--effort", default="high"); j.add_argument("--slugs", nargs="*"); j.add_argument("--workers", type=int, default=6)
    j.add_argument("--dir", default="judge", help="judge folder; a new arm judged on its own goes in its own folder")
    sc = sub.add_parser("score"); sc.add_argument("--dir", default="judge")
    p = sub.add_parser("pron"); p.add_argument("--model", required=True); p.add_argument("--arm", required=True)
    sub.add_parser("pronscore")
    for sp in (r, p):
        sp.add_argument("--reasoning", help="JSON reasoning setting overriding openrouter.reasoning_for")
    a = ap.parse_args()
    global REASONING
    REASONING = json.loads(a.reasoning) if getattr(a, "reasoning", None) else None
    {"review": cmd_review, "judge": cmd_judge, "score": cmd_score, "pron": cmd_pron, "pronscore": cmd_pronscore}[a.cmd](a)


if __name__ == "__main__":
    main()
