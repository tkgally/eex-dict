#!/usr/bin/env python3
"""Claude-subagent reviewers against the OpenRouter reviewers, on identical prompts (design in README.md).

    python3 harness.py prompts                      # prompts/system.txt and prompts/<slug>.user.txt from inputs/
    python3 harness.py openrouter --role reviewer-a [--slugs ...] [--workers 4]
                                                    # one paid call per entry, raw reply to outputs/<role>/<slug>.json
    python3 harness.py ingest --arm sonnet          # outputs/<arm>/<slug>.raw.json (written by a subagent) -> normalized
    python3 harness.py pool                         # judge/<slug>.pool.json: every issue of every arm, shuffled, unlabelled
    python3 harness.py score                        # results.json and a printed table

The prompts are exactly tools/review_panel.py's (system prompt with the house rules, user prompt with the
checklist); the replies are normalized by its normalize_verdicts with no role, so the production
DISABLED_FAMILIES filter is not applied here; `score` reports the filtered view separately.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import eexlib  # noqa: E402
import review_panel as rp  # noqa: E402

ARMS = ["reviewer-a", "reviewer-b", "sonnet", "haiku"]
RUN_ID = "20261025T014638Z-ysf43k"


def inputs(slugs=None):
    out = []
    for p in sorted((HERE / "inputs").glob("*.json")):
        if slugs and p.stem not in slugs:
            continue
        out.append((p.stem, json.loads(p.read_text())))
    return out


def cmd_prompts(a):
    (HERE / "prompts").mkdir(exist_ok=True)
    (HERE / "prompts" / "system.txt").write_text(rp.system_prompt() + "\n")
    for slug, e in inputs():
        (HERE / "prompts" / f"{slug}.user.txt").write_text(rp.user_prompt(e) + "\n")
        (HERE / "prompts" / f"{slug}.fields.json").write_text(json.dumps(rp.checklist(e)) + "\n")
    print("prompts written for", len(inputs()), "entries")


def one_openrouter(role, slug, e):
    import openrouter
    model = openrouter.resolve_role(role)
    system, prompt, fields = rp.system_prompt(), rp.user_prompt(e), rp.checklist(e)
    est = openrouter.estimate_cost(model, len(system) // 4 + len(prompt) // 4, 40 * len(fields) + 200)
    t0 = time.time()
    rec = {"arm": role, "model": model, "slug": slug}
    try:
        res = openrouter.call_with_budget(model, [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                                          purpose=f"experiment:claude-reviewers-v1:{slug}:{role}", estimate_usd=est,
                                          run_id=RUN_ID, max_tokens=120 * len(fields) + 3000, temperature=0.1,
                                          response_format={"type": "json_object"}, reasoning=openrouter.reasoning_for(model))
        rec.update({"seconds": round(time.time() - t0, 1), "cost_usd": res.get("cost"), "tokens_in": res.get("tokens_in"),
                    "tokens_out": res.get("tokens_out"), "finish": res.get("finish_reason"), "text": res.get("text")})
    except Exception as ex:  # noqa: BLE001
        rec.update({"seconds": round(time.time() - t0, 1), "error": f"{type(ex).__name__}: {str(ex)[:300]}"})
    return rec


def cmd_openrouter(a):
    outdir = HERE / "outputs" / a.role
    outdir.mkdir(parents=True, exist_ok=True)
    todo = [(s, e) for s, e in inputs(a.slugs) if a.force or not (outdir / f"{s}.json").exists()]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for rec in pool.map(lambda se: one_openrouter(a.role, *se), todo):
            normalize_into(rec)
            (outdir / f"{rec['slug']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
            print(rec["slug"], rec.get("seconds"), rec.get("cost_usd"), rec.get("error") or rec.get("parse_error") or
                  f"{sum(v['verdict'] == 'issue' for v in rec['verdicts'])} issues")


def normalize_into(rec):
    import openrouter
    fields = json.loads((HERE / "prompts" / f"{rec['slug']}.fields.json").read_text())
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


def cmd_ingest(a):
    outdir = HERE / "outputs" / a.arm
    meta = json.loads((outdir / "meta.json").read_text()) if (outdir / "meta.json").exists() else {}
    for raw in sorted(outdir.glob("*.raw.json")):
        slug = raw.name[: -len(".raw.json")]
        rec = {"arm": a.arm, "model": a.arm, "slug": slug, "text": raw.read_text(), **meta.get(slug, {})}
        normalize_into(rec)
        (outdir / f"{slug}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
        print(slug, rec.get("parse_error") or f"{sum(v['verdict'] == 'issue' for v in rec['verdicts'])} issues")


def load_outputs(arm):
    out = {}
    for p in (HERE / "outputs" / arm).glob("*.json"):
        if p.name.endswith(".raw.json") or p.name == "meta.json":
            continue
        out[p.stem] = json.loads(p.read_text())
    return out


def cmd_pool(a):
    (HERE / "judge").mkdir(exist_ok=True)
    rng = random.Random(20261025)
    allout = {arm: load_outputs(arm) for arm in ARMS}
    for slug, _e in inputs():
        if (HERE / "judge" / f"{slug}.verdicts.json").exists():
            continue                                   # already judged: its ids must not change
        items = []
        for arm in ARMS:
            rec = allout[arm].get(slug)
            for v in (rec or {}).get("verdicts", []):
                if v["verdict"] == "issue":
                    items.append({"arm": arm, **{k: v[k] for k in ("field", "quote", "severity", "family", "reason")}})
        rng.shuffle(items)
        key, pool = [], []
        for i, it in enumerate(items, 1):
            key.append({"id": i, "arm": it["arm"]})
            pool.append({"id": i, **{k: it[k] for k in ("field", "quote", "severity", "family", "reason")}})
        (HERE / "judge" / f"{slug}.pool.json").write_text(json.dumps(pool, ensure_ascii=False, indent=1) + "\n")
        (HERE / "judge" / f"{slug}.key.json").write_text(json.dumps(key) + "\n")
        print(slug, len(pool), "issues pooled")


def cmd_score(a):
    planted = json.loads((HERE / "planted.json").read_text())
    planted_slugs = {p["slug"] for p in planted}
    allout = {arm: load_outputs(arm) for arm in ARMS}
    stats = {arm: {"issues": 0, "blocking": 0, "valid": 0, "valid_blocking": 0, "invalid": 0, "partly": 0, "findings": set(),
                   "planted_hit": 0, "parse_fail": 0, "missing_fields": 0, "filtered_out": 0, "filtered_valid": 0,
                   "seconds": [], "cost": 0.0, "tok_in": 0, "tok_out": 0, "entries": 0} for arm in ARMS}
    union = {"all": set(), "planted_set": set(), "natural_set": set()}
    planted_hits = {p["id"]: set() for p in planted}
    for slug, _e in inputs():
        jf = HERE / "judge" / f"{slug}.verdicts.json"
        if not jf.exists():
            print("no judge verdicts for", slug); continue
        jv = {j["id"]: j for j in json.loads(jf.read_text())["issues"]}
        key = {k["id"]: k["arm"] for k in json.loads((HERE / "judge" / f"{slug}.key.json").read_text())}
        pool = {p["id"]: p for p in json.loads((HERE / "judge" / f"{slug}.pool.json").read_text())}
        for i, arm in key.items():
            j, it, s = jv[i], pool[i], stats[arm]
            s["issues"] += 1
            s["blocking"] += it["severity"] == "blocking"
            ok = j["valid"] == "yes"
            s["valid"] += ok
            s["partly"] += j["valid"] == "partly"
            s["invalid"] += j["valid"] == "no"
            s["valid_blocking"] += ok and it["severity"] == "blocking"
            if role_filtered(arm, it["family"]):
                s["filtered_out"] += 1
                s["filtered_valid"] += ok
            if ok and j.get("finding"):
                fid = f"{slug}:{j['finding']}"
                s["findings"].add(fid)
                union["all"].add(fid)
                union["planted_set" if slug in planted_slugs else "natural_set"].add(fid)
            for pid in j.get("planted") or []:
                pid = str(pid)
                pid = pid if "#" in pid else f"{slug}#{pid}"
                pid = pid if pid.startswith(slug) else f"{slug}{pid[pid.index('#'):]}"
                if ok or j["valid"] == "partly":
                    planted_hits.setdefault(pid, set()).add(arm)
        for arm in ARMS:
            rec = allout[arm].get(slug)
            if not rec:
                continue
            s = stats[arm]
            s["entries"] += 1
            s["parse_fail"] += bool(rec.get("parse_error") and not rec.get("verdicts"))
            s["missing_fields"] += bool(rec.get("parse_error") and rec.get("verdicts"))
            if rec.get("seconds") is not None:
                s["seconds"].append(rec["seconds"])
            s["cost"] += float(rec.get("cost_usd") or 0)
            s["tok_in"] += int(rec.get("tokens_in") or 0)
            s["tok_out"] += int(rec.get("tokens_out") or 0)
    for pid, arms in planted_hits.items():
        for arm in arms:
            stats[arm]["planted_hit"] += 1
    res = {"planted_total": len(planted), "union_findings": {k: len(v) for k, v in union.items()}, "arms": {},
           "planted_by_defect": {pid: sorted(a) for pid, a in planted_hits.items()}}
    for arm, s in stats.items():
        f = s["findings"]
        res["arms"][arm] = {
            "entries": s["entries"], "issues": s["issues"], "blocking": s["blocking"], "valid": s["valid"], "partly": s["partly"],
            "invalid": s["invalid"], "precision": round(s["valid"] / s["issues"], 3) if s["issues"] else None,
            "valid_blocking": s["valid_blocking"],
            "findings": len(f), "recall_all": round(len(f) / len(union["all"]), 3) if union["all"] else None,
            "recall_natural": round(len(f & union["natural_set"]) / len(union["natural_set"]), 3) if union["natural_set"] else None,
            "recall_planted_set": round(len(f & union["planted_set"]) / len(union["planted_set"]), 3) if union["planted_set"] else None,
            "unique_findings": len(f - set().union(*(stats[o]["findings"] for o in ARMS if o != arm))),
            "planted_hit": s["planted_hit"], "parse_fail": s["parse_fail"], "missing_fields": s["missing_fields"],
            "production_filter_drops": s["filtered_out"], "production_filter_drops_valid": s["filtered_valid"],
            "median_seconds": sorted(s["seconds"])[len(s["seconds"]) // 2] if s["seconds"] else None,
            "cost_usd": round(s["cost"], 4), "tokens_in": s["tok_in"], "tokens_out": s["tok_out"]}
    # panels: the union of two arms' findings
    for name, pair in {"openrouter-panel": ("reviewer-a", "reviewer-b"), "claude-panel": ("sonnet", "haiku"),
                       "sonnet+reviewer-a": ("sonnet", "reviewer-a"), "sonnet+reviewer-b": ("sonnet", "reviewer-b")}.items():
        f = stats[pair[0]]["findings"] | stats[pair[1]]["findings"]
        res.setdefault("panels", {})[name] = {
            "findings": len(f), "recall_all": round(len(f) / len(union["all"]), 3) if union["all"] else None,
            "recall_natural": round(len(f & union["natural_set"]) / len(union["natural_set"]), 3) if union["natural_set"] else None,
            "planted_hit": sum(1 for arms in planted_hits.values() if set(pair) & arms),
            "issues_to_adjudicate": stats[pair[0]]["issues"] + stats[pair[1]]["issues"]}
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


XJUDGE = """You are the adjudicator for one entry of an English-English learner's dictionary. Several reviewers checked the entry field by
field; their issues were pooled, shuffled, and stripped of reviewer identity. Judge each issue only on whether it is right, using the house
rules below (including the list of house conventions that are NOT issues) and your own expert knowledge of English. Answer with JSON only.

For every issue decide "valid": "yes" (the reviewer is right and a fix is warranted), "partly" (a real point but the reason or direction is
wrong, or a matter of taste with a small real point), or "no" (wrong, objects to a stated house convention, or mere taste). Be strict both ways.
Return {"issues": [{"id": <id>, "valid": "yes"|"partly"|"no", "note": "<at most fifteen words>"}]} with every id exactly once.

HOUSE RULES GIVEN TO THE REVIEWERS:
"""


def cmd_xjudge(a):
    """A second, non-Claude judge on the same blind pools (a check on the Claude judge's bias)."""
    import openrouter
    out = HERE / "judge" / f"x-{a.role}"
    out.mkdir(parents=True, exist_ok=True)
    model = openrouter.resolve_role(a.role)
    todo = [(s, e) for s, e in inputs(a.slugs) if (HERE / "judge" / f"{s}.pool.json").exists() and not (out / f"{s}.json").exists()]

    def one(se):
        slug, e = se
        pool = json.loads((HERE / "judge" / f"{slug}.pool.json").read_text())
        system = XJUDGE + rp.system_prompt()
        user = ("ENTRY (JSON):\n" + json.dumps(rp.strip_for_review(e), ensure_ascii=False, indent=1) +
                "\n\nPOOLED ISSUES (JSON):\n" + json.dumps(pool, ensure_ascii=False, indent=1))
        est = openrouter.estimate_cost(model, (len(system) + len(user)) // 4, 60 * len(pool) + 300)
        t0 = time.time()
        try:
            res = openrouter.call_with_budget(model, [{"role": "system", "content": system}, {"role": "user", "content": user}],
                                              purpose=f"experiment:claude-reviewers-v1:{slug}:xjudge", estimate_usd=est, run_id=RUN_ID,
                                              max_tokens=80 * len(pool) + 2000, temperature=0.1,
                                              response_format={"type": "json_object"}, reasoning=openrouter.reasoning_for(model))
            rec = {"slug": slug, "model": model, "seconds": round(time.time() - t0, 1), "cost_usd": res.get("cost"),
                   "raw": openrouter.parse_json_reply(res["text"])}
        except Exception as ex:  # noqa: BLE001
            rec = {"slug": slug, "model": model, "error": f"{type(ex).__name__}: {str(ex)[:300]}"}
        (out / f"{slug}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
        return slug, rec.get("cost_usd"), rec.get("error")

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for r in pool.map(one, todo):
            print(*r)


def cmd_xscore(a):
    """Precision by arm under the Claude judge and under the second (OpenRouter) judge, and their agreement."""
    planted = {p["slug"]: p.get("set") for p in json.loads((HERE / "planted.json").read_text())}
    tab, agree, n = {}, 0, 0
    for slug, _e in inputs():
        jf, xf = HERE / "judge" / f"{slug}.verdicts.json", HERE / "judge" / f"x-{a.role}" / f"{slug}.json"
        if not (jf.exists() and xf.exists()):
            continue
        group = planted.get(slug, "natural")
        jv = {j["id"]: j["valid"] for j in json.loads(jf.read_text())["issues"]}
        xv = {int(j["id"]): j["valid"] for j in (json.loads(xf.read_text()).get("raw") or {}).get("issues", [])}
        for k in json.loads((HERE / "judge" / f"{slug}.key.json").read_text()):
            i, arm = k["id"], k["arm"]
            for g in (group, "all"):
                t = tab.setdefault((g, arm), [0, 0, 0])
                t[0] += 1; t[1] += jv.get(i) == "yes"; t[2] += xv.get(i) == "yes"
            if i in xv:
                n += 1; agree += (jv.get(i) == "yes") == (xv.get(i) == "yes")
    print(f"agreement on yes/not-yes: {agree}/{n} = {agree / max(n, 1):.2f}")
    print(f"{'set':8s} {'arm':11s} {'issues':>6s} {'claude-judge':>12s} {a.role + '-judge':>17s}")
    for (g, arm), (t, c, x) in sorted(tab.items()):
        print(f"{g:8s} {arm:11s} {t:6d} {c / t:12.2f} {x / t:17.2f}")


def claude_cli(model, system, user, effort=None):
    """One headless Claude Code call with no tools and our own system prompt; returns (text, result record)."""
    import subprocess
    cmd = ["claude", "-p", "--model", model, "--tools", "", "--system-prompt", system, "--output-format", "json",
           "--no-session-persistence"] + (["--effort", effort] if effort else [])
    t0 = time.time()
    p = subprocess.run(cmd, input=user, capture_output=True, text=True, timeout=900)
    try:
        res = json.loads(p.stdout)
    except ValueError:
        return None, {"error": f"exit {p.returncode}: {p.stderr[-300:]}", "seconds": round(time.time() - t0, 1)}
    u = res.get("usage") or {}
    meta = {"seconds": round(time.time() - t0, 1), "api_equiv_usd": res.get("total_cost_usd"),
            "tokens_in": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
            "cache_read": u.get("cache_read_input_tokens", 0), "tokens_out": u.get("output_tokens", 0),
            "thinking": (u.get("output_tokens_details") or {}).get("thinking_tokens", 0),
            "model_used": ",".join((res.get("modelUsage") or {}).keys()), "is_error": res.get("is_error")}
    return res.get("result"), meta


def cmd_cli(a):
    """The reviewer prompt through headless `claude -p` (no subagent harness): outputs/<arm>/<slug>.json."""
    outdir = HERE / "outputs" / a.arm
    outdir.mkdir(parents=True, exist_ok=True)
    system = rp.system_prompt()
    todo = [(s, e) for s, e in inputs(a.slugs) if not (outdir / f"{s}.json").exists()]

    def one(se):
        slug, e = se
        text, meta = claude_cli(a.model, system, rp.user_prompt(e), a.effort)
        rec = {"arm": a.arm, "model": meta.get("model_used") or a.model, "slug": slug, "text": text, **meta,
               "cost_usd": 0.0}
        normalize_into(rec)
        (outdir / f"{slug}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
        return slug, rec.get("seconds"), rec.get("api_equiv_usd"), rec.get("error") or rec.get("parse_error") or \
            f"{sum(v['verdict'] == 'issue' for v in rec['verdicts'])} issues"

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for r in pool.map(one, todo):
            print(*r, flush=True)


def cmd_clijudge(a):
    """Judge the headless arms' issues blind with a headless Opus call (same rules as judge/INSTRUCTIONS.md):
    judge-cli/<slug>.pool.json, .key.json, .verdicts.json."""
    arms = a.arms.split(",")
    jd = HERE / a.dir
    jd.mkdir(exist_ok=True)
    planted = json.loads((HERE / "planted.json").read_text())
    instructions = (HERE / "judge" / "INSTRUCTIONS.md").read_text()
    style = (ROOT / "wiki" / "style-guide.md").read_text()
    system = ("You are a blind adjudicator in an experiment. Follow these instructions; the files they name are given to you inline "
              "below instead, and your output is the JSON object they describe, printed as your whole reply (no file, no code fence).\n\n"
              + instructions + "\n\nprompts/system.txt (the house rules the reviewers were given):\n" + rp.system_prompt()
              + "\n\nwiki/style-guide.md:\n" + style)
    rng = random.Random(20261026)
    todo = []
    for slug, e in inputs(a.slugs):
        if (jd / f"{slug}.verdicts.json").exists():
            continue
        items = []
        for arm in arms:
            for v in (load_outputs(arm).get(slug) or {}).get("verdicts", []):
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
        import openrouter
        try:
            out = openrouter.parse_json_reply(text or "")
        except ValueError as ex:
            out = {"error": str(ex), "raw": (text or "")[:500]}
        out["_meta"] = meta
        (jd / f"{slug}.verdicts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
        return slug, len(pool), meta.get("seconds"), meta.get("api_equiv_usd"), out.get("error")

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for r in ex.map(one, todo):
            print(*r, flush=True)


def cmd_cliscore(a):
    jd = HERE / a.dir
    planted = json.loads((HERE / "planted.json").read_text())
    pset = {p["slug"]: p["set"] for p in planted}
    st, hits = {}, {}
    for slug, _e in inputs():
        vf = jd / f"{slug}.verdicts.json"
        if not vf.exists():
            continue
        jv = {int(j["id"]): j for j in json.loads(vf.read_text()).get("issues", [])}
        pool = {p["id"]: p for p in json.loads((jd / f"{slug}.pool.json").read_text())}
        for k in json.loads((jd / f"{slug}.key.json").read_text()):
            j, it = jv.get(k["id"], {"valid": "missing"}), pool[k["id"]]
            for g in (pset.get(slug, "natural"), "all"):
                s = st.setdefault((k["arm"], g), {"n": 0, "yes": 0, "blocking": 0, "b_yes": 0, "missing": 0})
                s["n"] += 1; s["yes"] += j["valid"] == "yes"; s["missing"] += j["valid"] == "missing"
                s["blocking"] += it["severity"] == "blocking"; s["b_yes"] += it["severity"] == "blocking" and j["valid"] == "yes"
            for pid in j.get("planted") or []:
                pid = str(pid); pid = pid if "#" in pid else f"{slug}#{pid}"
                if j["valid"] in ("yes", "partly"):
                    hits.setdefault(k["arm"], set()).add(pid)
    for (arm, g), s in sorted(st.items()):
        print(f"{arm:11s} {g:8s} issues {s['n']:4d} precision {s['yes'] / s['n']:.2f}  blocking {s['blocking']:3d} "
              f"blocking-precision {s['b_yes'] / max(s['blocking'], 1):.2f}  unjudged {s['missing']}")
    for arm, h in hits.items():
        print(arm, "planted defects found:", len(h), "of", len(planted), "missed:", sorted({p["id"] for p in planted} - h))


def role_filtered(arm, family):
    return (arm, family) in rp.DISABLED_FAMILIES


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prompts")
    o = sub.add_parser("openrouter"); o.add_argument("--role", required=True); o.add_argument("--slugs", nargs="*")
    o.add_argument("--workers", type=int, default=4); o.add_argument("--force", action="store_true")
    i = sub.add_parser("ingest"); i.add_argument("--arm", required=True)
    sub.add_parser("pool"); sub.add_parser("score")
    x = sub.add_parser("xjudge"); x.add_argument("--role", default="reviewer-a"); x.add_argument("--slugs", nargs="*")
    x.add_argument("--workers", type=int, default=4)
    c = sub.add_parser("cli"); c.add_argument("--arm", required=True); c.add_argument("--model", required=True)
    c.add_argument("--effort"); c.add_argument("--slugs", nargs="*"); c.add_argument("--workers", type=int, default=6)
    cj = sub.add_parser("clijudge"); cj.add_argument("--arms", default="sonnet-cli,haiku-cli"); cj.add_argument("--model", default="opus")
    cj.add_argument("--effort"); cj.add_argument("--slugs", nargs="*"); cj.add_argument("--workers", type=int, default=6)
    cj.add_argument("--dir", default="judge-cli")
    cs = sub.add_parser("cliscore"); cs.add_argument("--dir", default="judge-cli")
    xs = sub.add_parser("xscore"); xs.add_argument("--role", default="reviewer-a")
    a = ap.parse_args()
    {"prompts": cmd_prompts, "openrouter": cmd_openrouter, "ingest": cmd_ingest, "pool": cmd_pool, "score": cmd_score, "xjudge": cmd_xjudge, "xscore": cmd_xscore, "cli": cmd_cli, "clijudge": cmd_clijudge, "cliscore": cmd_cliscore}[a.cmd](a)


if __name__ == "__main__":
    main()
