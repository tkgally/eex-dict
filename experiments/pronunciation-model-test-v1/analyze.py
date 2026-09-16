#!/usr/bin/env python3
"""Score the pronunciation model test (design.md sections 4 to 6) and write
verdicts.tsv and results.md. The CMU Pronouncing Dictionary is fetched to .tmp/
for the comparison and nothing from it is written out: verdicts.tsv holds only
yes/no agreement flags and the rule's verdict per word.

    python3 experiments/pronunciation-model-test-v1/analyze.py [--threshold 2] [--offline]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pronounce_check as pc  # noqa: E402

PANEL = ["pronunciation-1", "pronunciation-2", "pronunciation-3"]


def normalize_n2_v0(ipa: str, variety: str) -> str:
    """The N2 of the frozen design before amendment 4a, kept here only so that
    results.md can report both (see design.md section 4a)."""
    import re as _re
    s = pc.normalize_n1(ipa)
    s = _re.sub(r"a(?![ɪʊ])", "æ", s)
    s = _re.sub(r"ɪ$", "i", s)
    s = _re.sub(r"(?<![ˈˌeaɔ])ɪ", "ə", s)
    if variety == "american":
        s = s.replace("ɛ", "e").replace("ɒ", "ɑ")
        s = _re.sub(r"ɔ(?![ɪr])", "ɑ", s)
        s = s.replace("ɚ", "ər").replace("ɝ", "ɜr").replace("ʌr", "ɜr").replace("ɜːr", "ɜr")
        s = s.replace("əʊ", "o").replace("oʊ", "o")
    else:
        s = s.replace("ɛ", "e").replace("oʊ", "əʊ").replace("ɝ", "ɜ").replace("ɚ", "ə")
        s = s.replace("eə", "ɛə").replace("ɛə", "eə")
    s = s.replace("ˌ", "")
    return s


def load_outputs() -> dict[str, dict[tuple[str, str], dict]]:
    out = {}
    for p in sorted((HERE / "outputs").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        out[d["role"]] = {(it["w"].lower(), it["pos"]): it for it in d["items"]}
    return out


def pct(n: int, d: int) -> str:
    return f"{100.0 * n / d:.1f}%" if d else "n/a"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--threshold", type=int, default=pc.THRESHOLD)
    ap.add_argument("--offline", action="store_true", help="do not fetch cmudict; use .tmp copy if present")
    ap.add_argument("--n2", choices=["v1", "v0"], default="v1", help="v0 = the normalization before amendment 4a")
    ap.add_argument("--out", default="results.md")
    a = ap.parse_args()
    if a.n2 == "v0":
        pc.normalize_n2 = normalize_n2_v0
    with (HERE / "words.tsv").open(encoding="utf-8") as f:
        words = list(csv.DictReader(f, delimiter="\t"))
    outs = load_outputs()
    roles = [r for r in ["drafter"] + PANEL if r in outs]
    cmu = pc.fetch_cmudict(offline=a.offline)
    wikt = {}
    wpath = HERE / "wiktionary-check.tsv"
    if wpath.exists():
        with wpath.open(encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if r["verdict"] in ("agree", "disagree"):      # not-fetched and no-line rows are not checks
                    wikt[(r["word"], r["pos"], r["role"])] = r["verdict"]

    # per-role agreement with CMU (American), by stratum
    cmu_n1 = defaultdict(lambda: defaultdict(int)); cmu_n2 = defaultdict(lambda: defaultdict(int)); cmu_have = defaultdict(int)
    pair_n2 = {v: defaultdict(int) for v in ("american", "british")}
    pair_den = {v: defaultdict(int) for v in ("american", "british")}
    verdict_rows = []
    ver_stats = {"verified": 0, "verified_cmu_agree": 0, "drafter_wrong": 0, "drafter_wrong_caught": 0,
                 "disputed": 0, "unverified": 0, "british_verified": 0, "british_disputed": 0, "british_unverified": 0}
    for row in words:
        key = (row["word"].lower(), row["pos"])
        stratum = row["stratum"]
        got = {r: outs[r].get(key, {}) for r in roles}
        cmu_forms = (cmu or {}).get(key[0]) if (cmu and " " not in key[0] and stratum != "heteronym") else None
        if cmu_forms:
            cmu_have[stratum] += 1
        flags = {}
        for r in roles:
            am = got[r].get("american", "")
            if cmu_forms:
                n1 = any(pc.normalize_n1(am) == pc.normalize_n1(f) for f in cmu_forms)
                n2 = any(pc.agree(am, f, "american") for f in cmu_forms)
                cmu_n1[r][stratum] += n1; cmu_n2[r][stratum] += n2
                flags[f"{r}:cmu"] = "yes" if n2 else "no"
            else:
                flags[f"{r}:cmu"] = "-"
        for v in ("american", "british"):
            for i, r1 in enumerate(roles):
                for r2 in roles[i + 1:]:
                    x, y = got[r1].get(v, ""), got[r2].get(v, "")
                    if x and y:
                        pair_den[v][(r1, r2)] += 1
                        pair_n2[v][(r1, r2)] += pc.agree(x, y, v)
        # the rule, drafter as source
        if "drafter" in outs:
            d_am, d_br = got["drafter"].get("american", ""), got["drafter"].get("british", "")
            votes_am = {r: got[r].get("american", "") for r in PANEL if r in outs}
            if cmu is not None and " " not in key[0] and stratum != "heteronym":
                votes_am["cmudict"] = pc.cmu_votes(key[0], cmu, d_am)
            st_am, cb_am = pc.verdict(d_am, votes_am, "american", a.threshold) if d_am else ("unverified", "no drafter output")
            votes_br = {r: got[r].get("british", "") for r in PANEL if r in outs}
            st_br, cb_br = pc.verdict(d_br, votes_br, "british", a.threshold) if d_br else ("unverified", "no drafter output")
            ver_stats[st_am] += 1
            ver_stats["british_" + st_br] += 1
            cmu_ok = None
            if cmu_forms and d_am:
                cmu_ok = any(pc.agree(d_am, f, "american") for f in cmu_forms)
                if st_am == "verified":
                    ver_stats["verified_cmu_agree"] += cmu_ok
                if not cmu_ok:
                    ver_stats["drafter_wrong"] += 1
                    ver_stats["drafter_wrong_caught"] += (st_am != "verified")
            for r in PANEL:
                flags[f"{r}:drafter_am"] = "yes" if (got.get(r, {}).get("american") and pc.agree(d_am, got[r]["american"], "american")) else "no"
                flags[f"{r}:drafter_br"] = "yes" if (got.get(r, {}).get("british") and pc.agree(d_br, got[r]["british"], "british")) else "no"
            verdict_rows.append({"word": row["word"], "pos": row["pos"], "stratum": stratum, "american_verdict": st_am,
                                 "american_checked_by": cb_am, "british_verdict": st_br, "british_checked_by": cb_br,
                                 "drafter_cmu": "-" if cmu_ok is None else ("yes" if cmu_ok else "no"), **flags})

    if verdict_rows and a.n2 == "v1":
        cols = list(verdict_rows[0].keys())
        with (HERE / "verdicts.tsv").open("w", encoding="utf-8") as f:
            f.write("\t".join(cols) + "\n")
            for r in verdict_rows:
                f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")

    strata = ["defining", "mid", "rare", "heteronym", "loan"]
    lines = ["# Results of pronunciation model test v1", "",
             f"Scored {len(words)} words; roles present: {', '.join(roles)}; threshold {a.threshold}; "
             f"CMU {'reachable' if cmu else 'not reachable'}.", "",
             "## 1. Agreement with the CMU Pronouncing Dictionary (American), phoneme level N2 (exact N1 in parentheses)", "",
             "| role | " + " | ".join(strata[:3] + ["loan"]) + " | all |", "|---|" + "---|" * 5]
    for r in roles:
        cells = []
        tot_n2 = tot_n1 = tot_d = 0
        for s in ["defining", "mid", "rare", "loan"]:
            d = cmu_have[s]; n2 = cmu_n2[r][s]; n1 = cmu_n1[r][s]
            tot_n2 += n2; tot_n1 += n1; tot_d += d
            cells.append(f"{pct(n2, d)} ({pct(n1, d)}) n={d}")
        cells.append(f"{pct(tot_n2, tot_d)} ({pct(tot_n1, tot_d)}) n={tot_d}")
        lines.append(f"| {r} | " + " | ".join(cells) + " |")
    lines += ["", "Heteronyms are excluded from the CMU comparison (CMU does not mark the part of speech).", "",
              "## 2. Pairwise inter-model agreement (N2)", ""]
    for v in ("american", "british"):
        lines.append(f"**{v}**: " + "; ".join(f"{r1} vs {r2} {pct(pair_n2[v][(r1, r2)], pair_den[v][(r1, r2)])}"
                                             for (r1, r2) in pair_den[v]))
    if verdict_rows:
        lines += ["", "## 3. The pre-registered rule applied to the drafter's transcriptions", "",
                  f"- American: verified {ver_stats['verified']}, disputed {ver_stats['disputed']}, unverified {ver_stats['unverified']}.",
                  f"- **Verified precision** (verified and agrees with CMU, over verified words CMU has): "
                  f"{pct(ver_stats['verified_cmu_agree'], sum(1 for r in verdict_rows if r['american_verdict'] == 'verified' and r['drafter_cmu'] != '-'))}.",
                  f"- **Disputed recall** (drafter disagrees with CMU and the rule did not mark it verified): "
                  f"{pct(ver_stats['drafter_wrong_caught'], ver_stats['drafter_wrong'])} of {ver_stats['drafter_wrong']} drafter errors.",
                  f"- British (panel only): verified {ver_stats['british_verified']}, disputed {ver_stats['british_disputed']}, unverified {ver_stats['british_unverified']}."]
        by_stratum = defaultdict(lambda: defaultdict(int))
        for r in verdict_rows:
            by_stratum[r["stratum"]][r["american_verdict"]] += 1
            by_stratum[r["stratum"]]["british_" + r["british_verdict"]] += 1
            by_stratum[r["stratum"]]["n"] += 1
        lines += ["", "| stratum | n | American verified | disputed | unverified | British verified | disputed | unverified |", "|---|---|---|---|---|---|---|---|"]
        for s in strata:
            b = by_stratum[s]
            lines.append(f"| {s} | {b['n']} | {b['verified']} | {b['disputed']} | {b['unverified']} | {b['british_verified']} | {b['british_disputed']} | {b['british_unverified']} |")
    if wikt:
        lines += ["", "## 4. Hand check against Wiktionary (British), agree rate by role", ""]
        by_role = defaultdict(lambda: [0, 0])
        for (w, p, r), v in wikt.items():
            by_role[r][1] += 1; by_role[r][0] += (v == "agree")
        for r, (ag, n) in sorted(by_role.items()):
            lines.append(f"- {r}: {pct(ag, n)} of {n}")
    lines.insert(2, f"Normalization: N2 {a.n2} ({'amended, design section 4a' if a.n2 == 'v1' else 'as frozen in section 4, before the amendment'}).")
    (HERE / a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
