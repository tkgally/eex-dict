#!/usr/bin/env python3
"""Harvest the defining vocabulary and the band-2/3 candidates from model judgment.

No external word list or frequency list is consulted at any step. Three models
from different labs (roles wordlist-1, wordlist-2, wordlist-3 in
config/models.md) are asked independently, chunk by chunk (fields.json), and
their raw replies are kept in raw/<pass>/<chunk>.<role>.json as the record.

    python3 experiments/defining-vocabulary-v1/harvest.py propose   # the defining-vocabulary pass
    python3 experiments/defining-vocabulary-v1/harvest.py expand    # the band-2/3 candidate pass
    python3 experiments/defining-vocabulary-v1/harvest.py band      # each model bands every candidate
    python3 experiments/defining-vocabulary-v1/harvest.py merge     # tallies -> proposals.tsv, candidates.tsv, bands.tsv

Every request goes through tools/openrouter.py with a budget pre-flight and the
billed cost recorded in config/budget-ledger.json. Re-running a pass skips
chunks whose raw file already exists, so an interrupted pass resumes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import openrouter  # noqa: E402

ROLES = ["wordlist-1", "wordlist-2", "wordlist-3"]
BAND_CHUNK_SIZE = 150
# Reasoning settings per role: DeepSeek spends the whole output budget on hidden
# reasoning unless it is switched off (probe of 2026-09-16); the others answer at low effort.
REASONING = {"wordlist-3": {"enabled": False}}
DEFAULT_REASONING = {"effort": "low"}
POS_CODES = ["n", "v", "adj", "adv", "prep", "conj", "pron", "det", "num", "modal", "aux",
             "interj", "phrv", "phr", "prefix", "suffix", "comb", "abbr"]

SYSTEM = (
    "You are helping a lexicographer build an original English learner's dictionary. "
    "Answer only from your own judgment of English as it is used today. Do not reproduce, "
    "recall, or imitate any published word list, frequency list, or dictionary's defining "
    "vocabulary; the project is deliberately building its own list. Reply with JSON only."
)

PROPOSE_USER = """The dictionary's defining vocabulary is a closed set of about 2,500 lemmas that will be used to write every definition, so it must contain the most basic, general, and indispensable words of English: the words needed to define other words.

Field: {field}.
Parts of speech wanted: {pos}.

List the lemmas this field contributes to the defining vocabulary: up to {max} words, the most basic first. Rules: lemmas only (no inflected forms); lowercase; phrasal verbs written with a space ("give up"); prefixes with a trailing hyphen ("un-") and suffixes with a leading hyphen ("-ness"); no proper nouns; a word with two common parts of speech appears once per part of speech.

Return JSON of the form {{"words": [{{"w": "lemma", "pos": "code"}}]}} where code is one of: {codes}."""

EXPAND_USER = """The dictionary already covers the most basic 2,500 words of English (its defining vocabulary). It will now grow to about 10,000 headwords chosen for intermediate and advanced learners.

Field: {field}.
Parts of speech wanted: {pos}.

List the next most useful words in this field for such learners, beyond the basic 2,500: up to {max} words, the most useful first. Rules: lemmas only; lowercase; phrasal verbs with a space; no proper nouns; no rare or technical words that a general learner would not meet; a word with two common parts of speech appears once per part of speech.

Return JSON of the form {{"words": [{{"w": "lemma", "pos": "code"}}]}} where code is one of: {codes}."""

BAND_USER = """Estimate the frequency band of each word below in general present-day English, from your own sense of how often the word is used across speech and writing. Bands: 1 = very common (among the most basic 2,500 words); 2 = common (roughly the next 3,000); 3 = fairly common (roughly the next 4,500); 4 = less common (met in wide reading); 5 = rare, technical, or literary. Judge the word as the part of speech shown.

Words (one per line, number|word|pos):
{words}

Return JSON of the form {{"bands": [[number, band], [number, band], ...]}} with one [number, band] pair per input line, {count} pairs, the number copied from the input, and nothing else."""


def load_chunks() -> list[dict]:
    return json.loads((HERE / "fields.json").read_text(encoding="utf-8"))["chunks"]


def raw_path(pass_name: str, chunk_id: str, role: str) -> Path:
    return HERE / "raw" / pass_name / f"{chunk_id}.{role}.json"


def ask(pass_name: str, chunk_id: str, role: str, user: str, est_out_tokens: int) -> dict:
    """One request; the raw reply is written to raw/<pass>/<chunk>.<role>.json."""
    out = raw_path(pass_name, chunk_id, role)
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))
    model = openrouter.resolve_role(role)
    est = openrouter.estimate_cost(model, 700, est_out_tokens)
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    res = openrouter.call_with_budget(model, messages, purpose=f"wordlist:{pass_name}:{chunk_id}",
                                      estimate_usd=est, max_tokens=est_out_tokens + 400,
                                      temperature=0.2, response_format={"type": "json_object"},
                                      reasoning=openrouter.reasoning_for(model, "wordlist"))
    try:
        parsed = openrouter.parse_json_reply(res["text"])
    except ValueError as e:
        parsed = {"_parse_error": str(e)}
    record = {"pass": pass_name, "chunk": chunk_id, "role": role, "model": res.get("model") or model,
              "cost_usd": res.get("cost"), "tokens_in": res.get("tokens_in"),
              "tokens_out": res.get("tokens_out"), "reply": parsed}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return record


def run_pass(pass_name: str, roles: list[str], workers: int, only: list[str] | None) -> None:
    chunks = load_chunks()
    if only:
        chunks = [c for c in chunks if c["id"] in only]
    jobs = []
    for c in chunks:
        if pass_name == "propose":
            user = PROPOSE_USER.format(field=c["field"], pos=", ".join(c["pos"]), max=c["max"],
                                       codes=", ".join(POS_CODES))
            est_out = c["max"] * 12 + 200
        else:
            user = EXPAND_USER.format(field=c["field"], pos=", ".join(c["pos"]), max=c["max_expand"],
                                      codes=", ".join(POS_CODES))
            est_out = c["max_expand"] * 12 + 200
        for role in roles:
            jobs.append((c["id"], role, user, est_out))
    total_cost = 0.0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(ask, pass_name, cid, role, user, est_out): (cid, role) for cid, role, user, est_out in jobs}
        for f in as_completed(futs):
            cid, role = futs[f]
            try:
                rec = f.result()
            except Exception as e:  # noqa: BLE001
                print(f"FAILED {cid} {role}: {e}", flush=True)
                continue
            n = len(rec["reply"].get("words", [])) if isinstance(rec["reply"], dict) else 0
            total_cost += float(rec.get("cost_usd") or 0)
            print(f"{cid:28s} {role:11s} {n:4d} words  ${float(rec.get('cost_usd') or 0):.4f}", flush=True)
    print(f"pass {pass_name}: billed this invocation ${total_cost:.4f}")


def norm_word(w: str) -> str:
    w = w.strip().lower()
    w = re.sub(r"\s+", " ", w)
    w = w.replace("’", "'")
    return w


def collect(pass_name: str) -> dict[tuple[str, str], set[str]]:
    """(word, pos) -> set of roles that proposed it."""
    votes: dict[tuple[str, str], set[str]] = {}
    for p in sorted((HERE / "raw" / pass_name).glob("*.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        reply = rec.get("reply") or {}
        for item in reply.get("words", []) if isinstance(reply, dict) else []:
            if not isinstance(item, dict):
                continue
            w, pos = norm_word(str(item.get("w", ""))), str(item.get("pos", "")).strip().lower()
            if not w or pos not in POS_CODES:
                continue
            votes.setdefault((w, pos), set()).add(rec["role"])
    return votes


def write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


def candidates_for_banding() -> list[tuple[str, str]]:
    """Words from the expand pass proposed by at least two roles, plus every
    propose-pass word not taken into the defining vocabulary (settled later)."""
    exp = collect("expand")
    prop = collect("propose")
    cands = {k for k, roles in exp.items() if len(roles) >= 2}
    cands |= {k for k, roles in prop.items() if len(roles) >= 1}
    return sorted(cands)


def run_band(roles: list[str], workers: int, chunk_size: int) -> None:
    cands = candidates_for_banding()
    chunks = [cands[i:i + chunk_size] for i in range(0, len(cands), chunk_size)]
    print(f"banding {len(cands)} candidates in {len(chunks)} chunks x {len(roles)} roles")
    jobs = []
    for i, ch in enumerate(chunks):
        words = "\n".join(f"{j + 1}|{w}|{pos}" for j, (w, pos) in enumerate(ch))
        user = BAND_USER.format(words=words, count=len(ch))
        for role in roles:
            jobs.append((f"chunk{i:03d}", role, user, len(ch) * 8 + 600))
    total = 0.0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(ask, "band", cid, role, user, est): (cid, role) for cid, role, user, est in jobs}
        for f in as_completed(futs):
            cid, role = futs[f]
            try:
                rec = f.result()
            except Exception as e:  # noqa: BLE001
                print(f"FAILED {cid} {role}: {e}", flush=True)
                continue
            n = len(rec["reply"].get("bands", [])) if isinstance(rec["reply"], dict) else 0
            total += float(rec.get("cost_usd") or 0)
            print(f"{cid:10s} {role:11s} {n:4d} bands  ${float(rec.get('cost_usd') or 0):.4f}", flush=True)
    print(f"pass band: billed this invocation ${total:.4f}")


def merge() -> None:
    prop = collect("propose")
    rows = [[w, pos, len(r), ",".join(sorted(r))] for (w, pos), r in sorted(prop.items())]
    write_tsv(HERE / "proposals.tsv", ["word", "pos", "votes", "roles"], rows)
    exp = collect("expand")
    rows = [[w, pos, len(r), ",".join(sorted(r))] for (w, pos), r in sorted(exp.items())]
    write_tsv(HERE / "candidates.tsv", ["word", "pos", "votes", "roles"], rows)
    bands: dict[tuple[str, str], dict[str, int]] = {}
    cands = candidates_for_banding()
    size = BAND_CHUNK_SIZE
    chunks = [cands[i:i + size] for i in range(0, len(cands), size)]
    misaligned = []
    for p in sorted((HERE / "raw" / "band").glob("*.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        reply = rec.get("reply") or {}
        idx = int(rec["chunk"].replace("chunk", ""))
        vals = reply.get("bands", []) if isinstance(reply, dict) else []
        if idx >= len(chunks):
            misaligned.append((rec["chunk"], rec["role"], len(vals), None)); continue
        pairs = []
        if vals and all(isinstance(v, (list, tuple)) and len(v) == 2 for v in vals):
            for n, b in vals:                       # numbered pairs: alignment by number
                try:
                    n, b = int(n), int(b)
                except (TypeError, ValueError):
                    continue
                if 1 <= n <= len(chunks[idx]) and 1 <= b <= 5:
                    pairs.append((chunks[idx][n - 1], b))
            if len(pairs) < 0.9 * len(chunks[idx]):
                misaligned.append((rec["chunk"], rec["role"], len(pairs), len(chunks[idx]))); continue
        else:                                       # plain ordered integers: alignment by position
            if len(vals) != len(chunks[idx]):
                misaligned.append((rec["chunk"], rec["role"], len(vals), len(chunks[idx]))); continue
            for (w, pos), b in zip(chunks[idx], vals):
                try:
                    b = int(b)
                except (TypeError, ValueError):
                    continue
                if 1 <= b <= 5:
                    pairs.append(((w, pos), b))
        for (w, pos), b in pairs:
            bands.setdefault((w, pos), {})[rec["role"]] = b
    if misaligned:
        print("misaligned band replies (delete the raw file and rerun the chunk):", misaligned)
    rows = []
    for (w, pos), by_role in sorted(bands.items()):
        vals = sorted(by_role.values())
        median = vals[len(vals) // 2] if len(vals) % 2 else vals[len(vals) // 2 - 1]  # lower median on ties
        rows.append([w, pos, median, len(vals), ",".join(f"{r}={b}" for r, b in sorted(by_role.items()))])
    write_tsv(HERE / "bands.tsv", ["word", "pos", "band_median", "votes", "by_role"], rows)
    print(f"proposals {len(prop)}  candidates {len(exp)}  banded {len(bands)}")
    print("votes in propose pass:", {k: sum(1 for r in prop.values() if len(r) == k) for k in (1, 2, 3)})
    print("votes in expand pass:", {k: sum(1 for r in exp.values() if len(r) == k) for k in (1, 2, 3)})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pass_name", choices=["propose", "expand", "band", "merge"])
    ap.add_argument("--roles", default=",".join(ROLES))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only", help="comma-separated chunk ids")
    ap.add_argument("--chunk-size", type=int, default=BAND_CHUNK_SIZE, help="words per banding request (merge assumes the default)")
    a = ap.parse_args()
    roles = a.roles.split(",")
    if a.pass_name in ("propose", "expand"):
        run_pass(a.pass_name, roles, a.workers, a.only.split(",") if a.only else None)
    elif a.pass_name == "band":
        run_band(roles, a.workers, a.chunk_size)
    else:
        merge()
    return 0


if __name__ == "__main__":
    sys.exit(main())
