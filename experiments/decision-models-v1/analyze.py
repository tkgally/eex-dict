#!/usr/bin/env python3
"""analyze.py -- score results/<phase>/<model>/<task>.jsonl against the sets.

  python3 analyze.py --phase screen            table of accuracy per model and task
  python3 analyze.py --phase full --json out   full metrics (accuracy, AUC, cascade
                                               coverage at 95% precision, cost, latency)
"""
from __future__ import annotations
import argparse, json, statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOUL = {"pron", "defs", "exok", "xref", "triage"}
COUNT_KEYS = {k: None for k in ["countable", "uncountable", "countable or uncountable", "singular only", "plural only"]}
TASKS = ["pron", "defs", "exsense", "exok", "xref", "link", "triage", "count"]


def items(task):
    return {it["id"]: it for it in (json.loads(l) for l in open(HERE / "sets" / f"{task}.jsonl"))}


def auc(pairs):
    """pairs: (score, gold bool). Mann-Whitney AUC with ties counted half."""
    pos = [s for s, g in pairs if g]
    neg = [s for s, g in pairs if not g]
    if not pos or not neg:
        return None
    wins = 0.0
    for p in pos:
        for n in neg:
            wins += 1 if p > n else 0.5 if p == n else 0
    return wins / (len(pos) * len(neg))


def cascade(pairs, target=0.95):
    """Two thresholds: auto-accept p >= hi, auto-flag p <= lo, the rest go to the LLM.
    Pick the widest band that keeps precision >= target on each automatic side.
    Returns (coverage, accept_precision, flag_precision, hi, lo)."""
    n = len(pairs)
    srt = sorted(pairs, key=lambda x: -x[0])
    best_hi, acc_n = 1.01, 0
    good = 0
    for i, (s, g) in enumerate(srt):
        good += g
        if (i + 1 < n and srt[i + 1][0] == s):
            continue
        if good / (i + 1) >= target:
            best_hi, acc_n = s, i + 1
    srt2 = sorted(pairs, key=lambda x: x[0])
    best_lo, flag_n, bad = -0.01, 0, 0
    for i, (s, g) in enumerate(srt2):
        bad += (not g)
        if (i + 1 < n and srt2[i + 1][0] == s):
            continue
        if bad / (i + 1) >= target:
            best_lo, flag_n = s, i + 1
    if best_lo >= best_hi:  # overlapping bands: keep accept side only
        flag_n, best_lo = 0, -0.01
    acc_prec = (sum(g for s, g in pairs if s >= best_hi) / acc_n) if acc_n else None
    flag_prec = (sum(not g for s, g in pairs if s <= best_lo) / flag_n) if flag_n else None
    return (acc_n + flag_n) / n, acc_prec, flag_prec, best_hi, best_lo


def cv_cascade(rows, target=0.95):
    """2-fold cross-validation: thresholds tuned on even-numbered items are applied to
    odd-numbered ones and vice versa. Returns the share decided automatically and the
    error rate among those automatic decisions, pooled over both folds."""
    folds = [[r for r in rows if int(r[0][-3:]) % 2 == k] for k in (0, 1)]
    auto = wrong = 0
    for k in (0, 1):
        tune = [(p, g) for _, p, g in folds[k]]
        _, _, _, hi, lo = cascade(tune, target)
        for _, p, g in folds[1 - k]:
            if p >= hi:
                auto += 1; wrong += (not g)
            elif p <= lo:
                auto += 1; wrong += g
    n = len(rows)
    return {"auto_share": auto / n, "auto_error": (wrong / auto) if auto else None}


def score(phase, model_dir, task, subset=None):
    f = model_dir / f"{task}.jsonl"
    if not f.exists():
        return None
    gold = items(task)
    rows = [json.loads(l) for l in open(f)]
    if subset:
        rows = [r for r in rows if gold[r["id"]]["kind"] in subset]
    ok = [r for r in rows if not r.get("err")]
    res = {"n": len(rows), "errors": len(rows) - len(ok)}
    if not ok:
        res["unsupported"] = True
        return res
    res["cost"] = sum(r["cost"] or 0 for r in rows)
    res["cost_per_item"] = res["cost"] / len(ok)
    lats = sorted(r["lat"] for r in ok)
    res["lat_median"] = statistics.median(lats)
    res["tok_in_mean"] = statistics.mean(r["tok"] or 0 for r in ok)
    if task in NOUL:
        pairs = [((r["p"] if r.get("p") is not None else 0.5), gold[r["id"]]["gold"]) for r in ok]
        res["acc"] = sum((p >= 0.5) == g for p, g in pairs) / len(pairs)
        res["auc"] = auc(pairs)
        cov, ap, fp, hi, lo = cascade(pairs)
        res["cv"] = cv_cascade([(r["id"], (r["p"] if r.get("p") is not None else 0.5), gold[r["id"]]["gold"]) for r in ok])
        res.update(cascade_cov=cov, cascade_acc_prec=ap, cascade_flag_prec=fp, hi=hi, lo=lo)
        # recall of bad items at the 0.5 cut (how many errors would be caught)
        negs = [(p, g) for p, g in pairs if not g]
        res["bad_recall"] = sum(p < 0.5 for p, g in negs) / len(negs) if negs else None
        bykind = {}
        for r in ok:
            k = gold[r["id"]]["kind"]
            p = r["p"] if r.get("p") is not None else 0.5
            bykind.setdefault(k, []).append((p >= 0.5) == gold[r["id"]]["gold"])
        res["by_kind"] = {k: sum(v) / len(v) for k, v in bykind.items()}
    else:
        keys = list((gold[ok[0]["id"]].get("criteria") or COUNT_KEYS).keys()) if task != "count" else list(COUNT_KEYS)
        for r in ok:  # an LLM that echoes "key: description" is credited with the key
            c = r.get("choice")
            if isinstance(c, str) and c not in gold[r["id"]].get("criteria", COUNT_KEYS):
                ks = gold[r["id"]].get("criteria") or COUNT_KEYS
                m = [k for k in ks if c.strip().lower().startswith(k.lower())]
                r["choice"] = max(m, key=len) if m else c
        right = [r.get("choice") == gold[r["id"]]["gold"] for r in ok]
        res["acc"] = sum(right) / len(right)
        confs = [((r.get("conf") or 0), r.get("choice") == gold[r["id"]]["gold"]) for r in ok]
        # coverage at which accuracy of the most confident answers stays >= 95%
        srt = sorted(confs, key=lambda x: -float(x[0] or 0))
        cov, good = 0, 0
        for i, (c, g) in enumerate(srt):
            good += g
            if good / (i + 1) >= 0.95:
                cov = (i + 1) / len(srt)
        res["cascade_cov"] = cov
        bykind = {}
        for r in ok:
            k = gold[r["id"]]["kind"]
            bykind.setdefault(k, []).append(r.get("choice") == gold[r["id"]]["gold"])
        res["by_kind"] = {k: sum(v) / len(v) for k, v in bykind.items()}
    return res


def ensemble(phase, models, task, name):
    """Average the probabilities of several decision models (noul) or their option probabilities (choice)."""
    gold = items(task)
    per = []
    for m in models:
        f = HERE / "results" / phase / m / f"{task}.jsonl"
        if not f.exists():
            return None
        per.append({r["id"]: r for r in (json.loads(l) for l in open(f)) if not r.get("err")})
    ids = set.intersection(*(set(p) for p in per))
    out = HERE / "results" / phase / name
    out.mkdir(parents=True, exist_ok=True)
    with open(out / f"{task}.jsonl", "w") as fh:
        for i in sorted(ids):
            rs = [p[i] for p in per]
            row = {"id": i, "cost": sum(r["cost"] or 0 for r in rs), "lat": max(r["lat"] for r in rs),
                   "tok": sum(r["tok"] or 0 for r in rs), "err": None}
            if task in NOUL:
                ps = [r["p"] for r in rs if r.get("p") is not None]
                row["p"] = sum(ps) / len(ps) if ps else None
            else:
                acc = {}
                for r in rs:
                    for k, v in (r.get("probs") or {}).items():
                        acc[k] = acc.get(k, 0) + v / len(rs)
                if acc:
                    best = max(acc, key=acc.get)
                    row.update(choice=best, conf=acc[best], probs=acc)
            fh.write(json.dumps(row) + "\n")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="screen")
    ap.add_argument("--json")
    ap.add_argument("--ensemble", action="append", default=[], help="name=m1,m2,... (dir names)")
    a = ap.parse_args()
    base = HERE / "results" / a.phase
    for spec in a.ensemble:
        name, ms = spec.split("=")
        for t in TASKS:
            ensemble(a.phase, ms.split(","), t, name)
    allres = {}
    for md in sorted(p for p in base.iterdir() if p.is_dir()):
        allres[md.name] = {t: score(a.phase, md, t) for t in TASKS}
    # table
    hdr = f"{'model':42s}" + "".join(f"{t:>9s}" for t in TASKS) + f"{'mean':>8s}{'$/item':>11s}{'lat':>6s}"
    print(hdr)
    for m, rs in allres.items():
        accs = [r["acc"] for r in rs.values() if r and "acc" in r]
        cells = "".join(f"{(r['acc'] if r and 'acc' in r else float('nan')):9.2f}" if r and 'acc' in r else f"{'—' if r else '':>9s}" for r in rs.values())
        costs = [r["cost_per_item"] for r in rs.values() if r and "cost_per_item" in r]
        lats = [r["lat_median"] for r in rs.values() if r and "lat_median" in r]
        print(f"{m:42s}{cells}{(sum(accs)/len(accs) if accs else 0):8.2f}{(sum(costs)/len(costs) if costs else 0):11.7f}{(statistics.median(lats) if lats else 0):6.2f}")
    if a.json:
        Path(a.json).write_text(json.dumps(allres, indent=1))
