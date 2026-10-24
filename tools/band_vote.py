#!/usr/bin/env python3
"""The band vote (the owner's ruling A1 of 2026-10-24, wiki/decisions/rebanding.md).

    python3 tools/band_vote.py plan [--unbanded]                 # what would be voted on, and the estimated cost
    python3 tools/band_vote.py run [--unbanded] [--limit N] [--workers 6]   # paid: the three-model vote
    python3 tools/band_vote.py settle                             # the splits of more than one band, for the session
    python3 tools/band_vote.py apply [--provisional]              # write the settled bands into the queue

The word-list panel (``wordlist-1`` to ``wordlist-3`` in config/models.md) gives
each item a band from 1 to 5 on the written scale below, sent word for word.
The items are every pending (or claimed) queue row and the row of every built
entry; with ``--unbanded``, only the rows a tool queued as ``unbanded``.  The band
is the lower median of the three votes (with one vote missing, the lower of the
two).  A spread of more than one band is settled by the session: ``settle``
lists them, and the session writes ``<slug>\\t<band>\\t<reason>`` lines to
``settled.tsv`` beside the votes; ``apply`` refuses an unsettled wide split
unless ``--provisional`` (then the lower median stands and the row's note says so).

``apply`` writes the bands through tools/queue.py (``set-bands``), which also
turns ``unbanded`` rows to ``pending``; tools/queue.py stamp then restamps the
built entries (``frequency.band`` is script-owned).  The votes go to
``experiments/band-vote-<date>/votes.tsv``; the raw replies stay in .tmp/.
Costs go through tools/spend.py (``openrouter.call_with_budget``).
"""
from __future__ import annotations

import sys
# tools/queue.py would shadow the standard library's queue, which the thread pool needs:
# import the real one before the tools directory is searched.
_tools_first = sys.path[0] if sys.path else None
if _tools_first is not None:
    sys.path.pop(0)
import queue as _stdlib_queue  # noqa: E402,F401
from concurrent.futures import ThreadPoolExecutor, as_completed  # noqa: E402
if _tools_first is not None:
    sys.path.insert(0, _tools_first)

import argparse  # noqa: E402
import csv  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

ROLES = ["wordlist-1", "wordlist-2", "wordlist-3"]
CHUNK = 120
SCALE = """- 1, very common (about 2,000 headwords): words nearly every learner meets in the first years of study and every speaker uses every day: core everyday vocabulary and the function words (house, eat, good, because, receive).
- 2, common (about 2,500): general everyday words an intermediate learner needs, frequent in conversation, the news, and school (borrow, audience, careful, vacation).
- 3, fairly common (about 2,500): words an educated adult uses regularly, common in newspapers, at work, and in general reading (appetite, reluctant, negotiate).
- 4, less common (about 2,000): words known to most adult native speakers but met mainly in particular topics or more specialized reading (hamper, frugal, ventilate).
- 5, rare (about 1,000): words most native speakers recognize but seldom use: literary, technical, or specialized words a learner's dictionary still includes (quell, serrated, archipelago)."""
SYSTEM = ("You are helping a lexicographer build an original English learner's dictionary. Answer only from your own "
          "judgment of English as it is used today. Do not reproduce, recall, or imitate any published word list, "
          "frequency list, or dictionary. You answer with JSON only.")
USER = """Give each word below a frequency band from 1 to 5 for a learner's dictionary of about 10,000 headwords, on this scale:

{scale}

A word's band is for its most common present-day use in the part of speech shown, in any variety of English. Judge each line on its own; a word with two parts of speech can get two different bands.

Words (one per line, number|word|part of speech):
{words}

Return JSON of the form {{"bands": [[number, band], [number, band], ...]}} with one [number, band] pair per input line, {count} pairs, the number copied from the input, and nothing else."""


def out_dir(date: str | None = None) -> Path:
    date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return eexlib.ROOT / "experiments" / f"band-vote-{date}"


def latest_dir() -> Path | None:
    dirs = sorted((eexlib.ROOT / "experiments").glob("band-vote-*"))
    return dirs[-1] if dirs else None


def items(unbanded: bool = False) -> list[dict]:
    """``[{slug, headword, pos, hint}]``: the rows to vote on, one per slug."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("eex_queue", HERE / "queue.py")
    q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(q)
    rows = q.load()
    best = q.slug_index(rows)
    entries = {e["slug"]: e for _p, e in eexlib.iter_entries() if not eexlib.is_redirect_stub(e)}
    pos_label = {k: (v or {}).get("label", k) for k, v in eexlib.load_vocab()["pos"].items() if not k.startswith("_")}
    out = []
    for slug, r in sorted(best.items()):
        if unbanded:
            if r["status"] != "unbanded":
                continue
        elif not (r["status"] in ("pending", "claimed", "unbanded") or slug in entries):
            continue
        e = entries.get(slug)
        hint = ""
        sib = [s for s in entries if s.startswith(slug + "-") and s[len(slug) + 1:].isdigit()]
        if e is not None and sib:
            hint = " (in the sense: %s)" % ((e.get("senses") or [{}])[0].get("definition", "")[:50])
        out.append({"slug": slug, "headword": (e or {}).get("headword") or r["headword"], "pos": r["pos"],
                    "label": pos_label.get(r["pos"], r["pos"]) + hint})
    return out


def chunks(its: list[dict]) -> list[list[dict]]:
    return [its[i:i + CHUNK] for i in range(0, len(its), CHUNK)]


def estimate(its: list[dict]) -> float:
    import openrouter
    total = 0.0
    for ch in chunks(its):
        tin = 450 + 12 * len(ch)
        tout = 9 * len(ch) + 40
        for role in ROLES:
            total += openrouter.estimate_cost(openrouter.resolve_role(role), tin, tout)
    return total


def lower_median(votes: list[int]) -> int | None:
    v = sorted(x for x in votes if x)
    if not v:
        return None
    return v[(len(v) - 1) // 2]


def ask(chunk_id: int, role: str, ch: list[dict], raw: Path) -> dict:
    import openrouter
    path = raw / f"chunk{chunk_id:03d}.{role}.json"
    if path.exists():
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec.get("pairs"):
            return rec
    words = "\n".join(f"{j + 1}|{it['headword']}|{it['label']}" for j, it in enumerate(ch))
    user = USER.format(scale=SCALE, words=words, count=len(ch))
    model = openrouter.resolve_role(role)
    est = openrouter.estimate_cost(model, 450 + 12 * len(ch), 9 * len(ch) + 40)
    res = openrouter.call_with_budget(model, [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                                      purpose=f"band-vote:chunk{chunk_id:03d}", estimate_usd=est,
                                      max_tokens=12 * len(ch) + 400, temperature=0.1,
                                      response_format={"type": "json_object"},
                                      reasoning=openrouter.reasoning_for(model, "wordlist"))
    pairs = {}
    try:
        reply = openrouter.parse_json_reply(res["text"])
        for n, b in (reply.get("bands") or []):
            n, b = int(n), int(b)
            if 1 <= n <= len(ch) and 1 <= b <= 5:
                pairs[ch[n - 1]["slug"]] = b
    except (ValueError, TypeError, AttributeError):
        pass
    rec = {"chunk": chunk_id, "role": role, "model": res.get("model") or model, "cost_usd": res.get("cost"),
           "pairs": pairs, "asked": len(ch)}
    raw.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return rec


def cmd_plan(a) -> int:
    its = items(a.unbanded)
    print(f"{len(its)} items in {len(chunks(its))} chunks x {len(ROLES)} roles; estimated cost ${estimate(its):.2f}")
    return 0


def cmd_run(a) -> int:
    its = items(a.unbanded)
    if a.limit:
        its = its[: a.limit]
    raw = eexlib.ROOT / ".tmp" / "band-vote" / (("unbanded" if a.unbanded else "all") + (f"-limit{a.limit}" if a.limit else ""))
    jobs = [(i, role, ch) for i, ch in enumerate(chunks(its)) for role in ROLES]
    votes: dict[str, dict[str, int]] = {it["slug"]: {} for it in its}
    cost = 0.0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(ask, i, role, ch, raw): (i, role, len(ch)) for i, role, ch in jobs}
        for f in as_completed(futs):
            i, role, n = futs[f]
            try:
                rec = f.result()
            except Exception as e:  # noqa: BLE001 - one failed chunk is reported, not fatal
                print(f"FAILED chunk{i:03d} {role}: {e}", flush=True)
                continue
            cost += float(rec.get("cost_usd") or 0)
            for slug, b in rec["pairs"].items():
                votes[slug][role] = b
            print(f"chunk{i:03d} {role:11s} {len(rec['pairs']):4d}/{n} ${float(rec.get('cost_usd') or 0):.4f}", flush=True)
    d = out_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = d / (("votes-unbanded" if a.unbanded else "votes") + (f"-limit{a.limit}" if a.limit else "") + ".tsv")
    with path.open("w", encoding="utf-8") as f:
        f.write("slug\theadword\tpos\t" + "\t".join(ROLES) + "\tlower_median\tspread\n")
        for it in its:
            v = [votes[it["slug"]].get(r) for r in ROLES]
            got = [x for x in v if x]
            med = lower_median(got)
            spread = (max(got) - min(got)) if got else ""
            f.write(f"{it['slug']}\t{it['headword']}\t{it['pos']}\t" + "\t".join(str(x or "") for x in v)
                    + f"\t{med or ''}\t{spread}\n")
    missing = sum(1 for it in its if len(votes[it["slug"]]) < 2)
    print(f"wrote {path.relative_to(eexlib.ROOT)}: {len(its)} items, billed this invocation ${cost:.4f}; "
          f"{missing} with fewer than two votes (re-run to retry the failed chunks)")
    return 0


def read_votes(d: Path, name: str = "votes.tsv") -> list[dict]:
    with (d / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_settled(d: Path) -> dict[str, tuple[int, str]]:
    p = d / "settled.tsv"
    out = {}
    if p.is_file():
        for ln in p.read_text(encoding="utf-8").splitlines():
            parts = ln.split("\t")
            if len(parts) >= 2 and parts[0] != "slug" and parts[1].strip().isdigit():
                out[parts[0]] = (int(parts[1]), parts[2] if len(parts) > 2 else "")
    return out


def cmd_settle(a) -> int:
    d = Path(a.dir) if a.dir else latest_dir()
    rows = read_votes(d, a.votes)
    settled = read_settled(d)
    wide = [r for r in rows if r["spread"] and int(r["spread"]) > 1]
    for r in wide:
        mark = "settled %d" % settled[r["slug"]][0] if r["slug"] in settled else "OPEN"
        print(f"{mark:10s} {r['slug']:32s} votes {r['wordlist-1'] or '-'} {r['wordlist-2'] or '-'} {r['wordlist-3'] or '-'}"
              f"  lower median {r['lower_median']}")
    print(f"{len(wide)} splits of more than one band; {sum(1 for r in wide if r['slug'] in settled)} settled")
    return 0


def final_bands(rows: list[dict], settled: dict[str, tuple[int, str]], provisional: bool) -> tuple[dict, list[str]]:
    out, unsettled = {}, []
    for r in rows:
        if not r["lower_median"]:
            continue
        if r["slug"] in settled:
            out[r["slug"]] = (settled[r["slug"]][0], "band vote 2026-10-24, settled: " + settled[r["slug"]][1])
        elif r["spread"] and int(r["spread"]) > 1:
            unsettled.append(r["slug"])
            if provisional:
                out[r["slug"]] = (int(r["lower_median"]), "band vote, lower median provisional (wide split)")
        else:
            out[r["slug"]] = (int(r["lower_median"]), "")
    return out, unsettled


def cmd_apply(a) -> int:
    d = Path(a.dir) if a.dir else latest_dir()
    rows = read_votes(d, a.votes)
    bands, unsettled = final_bands(rows, read_settled(d), a.provisional)
    if unsettled and not a.provisional:
        print(f"refused: {len(unsettled)} wide splits are not settled (band_vote.py settle; or --provisional)")
        return 1
    tmp = eexlib.ROOT / ".tmp" / "band-vote-apply.tsv"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with tmp.open("w", encoding="utf-8") as f:
        f.write("slug\tband\tnote\n")
        for slug, (band, note) in sorted(bands.items()):
            f.write(f"{slug}\t{band}\t{note}\n")
    r = subprocess.run([sys.executable, str(HERE / "queue.py"), "set-bands", str(tmp)], capture_output=True, text=True,
                       cwd=eexlib.ROOT)
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.add_argument("--unbanded", action="store_true"); p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("run"); p.add_argument("--unbanded", action="store_true"); p.add_argument("--limit", type=int)
    p.add_argument("--workers", type=int, default=6); p.set_defaults(fn=cmd_run)
    for name, fn in (("settle", cmd_settle), ("apply", cmd_apply)):
        p = sub.add_parser(name); p.add_argument("--dir"); p.add_argument("--votes", default="votes.tsv")
        if name == "apply":
            p.add_argument("--provisional", action="store_true")
        p.set_defaults(fn=fn)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
