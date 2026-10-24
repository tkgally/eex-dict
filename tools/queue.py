#!/usr/bin/env python3
"""The headword queue: headwords/queue.tsv (see wiki/conventions.md section 3).

    python3 tools/queue.py list [--status S] [--band N] [--source S] [--pos P] [--limit N]
    python3 tools/queue.py add "<headword>" <pos> [--band N] --source S [--note "..."]   # no band: status unbanded
    python3 tools/queue.py set-bands <file.tsv>          # columns slug, band[, note]: the band vote's result (unbanded -> pending)
    python3 tools/queue.py add-batch <file.tsv>          # columns headword, pos, band, source[, note]
    python3 tools/queue.py set "<headword>" <pos> <status> [--note "..."]
    python3 tools/queue.py next [--n 20] [--band N] [--source S] [--pos P]   # pending rows not claimed anywhere
    python3 tools/queue.py sync                           # rows whose entry exists become done; claimed rows no claim file lists go back to pending
    python3 tools/queue.py stamp <slug> [<slug> ...]      # write frequency.band and frequency.defining_vocabulary into entries
    python3 tools/queue.py counts                         # rows by status, band, source
    python3 tools/queue.py repair-forms [--apply]         # rows that lost a hyphen or period (ruling C3): list, or fix

Only this tool edits the queue. Statuses and sources come from schema/vocabularies.json.
A row added without a band is ``unbanded`` with an empty band: it is never handed out until
the next band vote (tools/band_vote.py) gives it one (the owner's ruling A1 of 2026-10-24).
``next`` works milestone 1 first (ruling A2, wiki/decisions/build-order.md): the grammar terms
of GRAMMAR_TERMS, then every other defining-vocabulary word with no entry in any part of
speech, then everything else; each group by band, part of speech, and headword.
A row is one headword plus part of speech; the slug is derived by tools/eexlib.py.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

COLUMNS = ["headword", "pos", "band", "source", "status", "added", "note"]


def queue_path() -> Path:
    return eexlib.ROOT / "headwords" / "queue.tsv"


def load() -> list[dict]:
    p = queue_path()
    if not p.exists():
        return []
    with p.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for r in rows:
        r.setdefault("note", "")
    return rows


def save(rows: list[dict]) -> None:
    p = queue_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        f.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "") or "").replace("\t", " ").replace("\n", " ") for c in COLUMNS) + "\n")


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def key(headword: str, pos: str) -> tuple[str, str]:
    return (headword.strip().lower(), pos.strip())


def check_value(kind: str, value: str) -> None:
    allowed = eexlib.vocab_values(kind)
    if value not in allowed:
        raise SystemExit(f"error: {value!r} is not a {kind} value; allowed: {', '.join(allowed)}")


def _slug_or_none(headword: str, pos: str) -> str | None:
    try:
        return eexlib.slugify(headword, pos)
    except ValueError:
        return None


def add_rows(rows: list[dict], new: list[dict], force_band: bool = False) -> tuple[int, int]:
    """Add rows, or update the existing row with the same headword and part of speech or the same slug
    (so ``brother in law`` never lands beside ``brother-in-law``: ruling C3, wiki/notes/queue-hyphen-loss.md)."""
    index = {key(r["headword"], r["pos"]): r for r in rows}
    by_slug = {}
    for r in rows:
        sl = _slug_or_none(r["headword"], r["pos"])
        if sl and (sl not in by_slug or by_slug[sl]["status"] == "duplicate"):
            by_slug[sl] = r
    added = updated = 0
    for n in new:
        hw, pos = n["headword"].strip(), n["pos"].strip()
        check_value("pos", pos)
        check_value("queue_sources", n["source"])
        raw_band = str(n.get("band") or "").strip()
        band = int(raw_band) if raw_band else None
        if band is not None and not 1 <= band <= 5:
            raise SystemExit(f"error: band {band} for {hw} is not 1 to 5")
        k = key(hw, pos)
        sl = _slug_or_none(hw, pos)
        if k not in index and sl in by_slug:
            k = key(by_slug[sl]["headword"], by_slug[sl]["pos"])
        if k in index:
            r = index[k]
            changed = False
            if force_band and band is not None and str(r["band"]) != str(band):
                r["band"] = str(band); changed = True
                if r["status"] == "unbanded":
                    r["status"] = "pending"
            if n.get("note") and n["note"] not in (r.get("note") or ""):
                r["note"] = ((r.get("note") or "") + "; " + n["note"]).strip("; "); changed = True
            updated += changed
            continue
        rows.append({"headword": hw, "pos": pos, "band": "" if band is None else str(band), "source": n["source"],
                     "status": "unbanded" if band is None else "pending", "added": today(), "note": n.get("note", "") or ""})
        index[k] = rows[-1]
        if sl:
            by_slug.setdefault(sl, rows[-1])
        added += 1
    return added, updated


def taken_slugs() -> set[str]:
    """Slugs claimed in any claim file on origin/main, origin/claude/*, or the working tree."""
    out: set[str] = set()
    try:
        r = subprocess.run([sys.executable, str(HERE / "claim.py"), "--taken", "--quiet"], capture_output=True, text=True, cwd=eexlib.ROOT)
        if r.returncode == 0:
            out |= {s.strip() for s in r.stdout.split() if s.strip()}
    except OSError:
        pass
    return out


def cmd_list(a) -> int:
    rows = load()
    sel = [r for r in rows if (not a.status or r["status"] == a.status) and (not a.band or str(r["band"]) == str(a.band))
           and (not a.source or r["source"] == a.source) and (not a.pos or r["pos"] == a.pos)]
    sel.sort(key=lambda r: (band_of(r), r["headword"], r["pos"]))
    for r in sel[: a.limit or None]:
        print("\t".join(r.get(c, "") for c in COLUMNS))
    print(f"# {len(sel)} rows", file=sys.stderr)
    return 0


def cmd_add(a) -> int:
    rows = load()
    added, updated = add_rows(rows, [{"headword": a.headword, "pos": a.pos, "band": a.band, "source": a.source, "note": a.note or ""}], a.force_band)
    save(rows)
    print(f"added {added}, updated {updated}; slug {eexlib.slugify(a.headword, a.pos)}")
    return 0


def cmd_add_batch(a) -> int:
    rows = load()
    with open(a.file, encoding="utf-8", newline="") as f:
        new = list(csv.DictReader(f, delimiter="\t"))
    added, updated = add_rows(rows, new, a.force_band)
    save(rows)
    print(f"added {added}, updated {updated}, total {len(rows)}")
    return 0


def cmd_set(a) -> int:
    check_value("queue_statuses", a.status)
    rows = load()
    k = key(a.headword, a.pos)
    for r in rows:
        if key(r["headword"], r["pos"]) == k:
            r["status"] = a.status
            if a.note:
                r["note"] = ((r.get("note") or "") + "; " + a.note).strip("; ")
            save(rows)
            print(f"{r['headword']} ({r['pos']}) -> {a.status}")
            return 0
    print(f"error: no queue row for {a.headword} ({a.pos}); add it first", file=sys.stderr)
    return 1


POS_ORDER = ["det", "pron", "prep", "conj", "modal", "aux", "inf", "v", "n", "adj", "adv", "num", "interj", "phrv",
             "phr", "prefix", "suffix", "comb", "abbr"]   # queue order within a band: function words and
                                                            # light verbs first, affixes and abbreviations last


# The grammar terms the dictionary's own notes use: built first (ruling A2 of 2026-10-24).
GRAMMAR_TERMS = ("noun", "plural", "singular", "syllable", "preposition", "pronoun", "countable", "uncountable",
                 "infinitive", "participle", "passive", "tense", "vowel", "consonant")
# The part of speech of each term's grammatical use (*tense* the noun, not *tense* meaning nervous).
GRAMMAR_TERM_POS = {"noun": ("n",), "plural": ("n", "adj"), "singular": ("n", "adj"), "syllable": ("n",),
                    "preposition": ("n",), "pronoun": ("n",), "countable": ("adj",), "uncountable": ("adj",),
                    "infinitive": ("n",), "participle": ("n",), "passive": ("adj", "n"), "tense": ("n",),
                    "vowel": ("n",), "consonant": ("n",)}


def band_of(r: dict) -> int:
    try:
        return int(r.get("band") or 9)
    except ValueError:
        return 9


def defining_vocabulary() -> set[str]:
    p = eexlib.ROOT / "schema" / "defining-vocabulary.txt"
    if not p.exists():
        return set()
    return {w.strip().lower() for w in p.read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")}


def milestone_words(rows: list[dict], entry_headwords: set[str] | None = None, dv: set[str] | None = None) -> set[str]:
    """Defining-vocabulary words with no entry in any part of speech: milestone 1's remaining words."""
    dv = defining_vocabulary() if dv is None else dv
    if entry_headwords is None:
        entry_headwords = {str(e.get("headword", "")).lower() for _p, e in eexlib.iter_entries() if not eexlib.is_redirect_stub(e)}
    return {w for w in dv if w not in entry_headwords}


def order_key(r: dict, milestone: set[str] | None = None) -> tuple:
    """Grammar terms of milestone 1, the rest of milestone 1, everything else; then band, part of speech, headword."""
    pos = r["pos"]
    hw = r["headword"].lower()
    group = 2
    if milestone is not None and hw in milestone:
        group = 0 if pos in GRAMMAR_TERM_POS.get(hw, ()) else 1
    return (group, band_of(r), POS_ORDER.index(pos) if pos in POS_ORDER else len(POS_ORDER), hw)


def cmd_next(a) -> int:
    rows = load()
    taken = taken_slugs()
    existing = {p.stem for p in eexlib.iter_entry_paths()}
    paused = eexlib.closure_paused(rows)
    milestone = milestone_words(rows)
    if a.source in eexlib.CLOSURE_SOURCES and paused:
        print(f"# --source {a.source}: band 2 is unfinished, so only rows at band 1 or 2 (ruling A3, "
              "wiki/decisions/build-order.md)", file=sys.stderr)
    out = []
    for r in sorted(rows, key=lambda r: order_key(r, milestone)):
        if r["status"] != "pending":
            continue
        if a.band and str(r["band"]) != str(a.band):
            continue
        if a.source and r["source"] != a.source:
            continue
        if r["source"] in eexlib.CLOSURE_SOURCES and a.source in eexlib.CLOSURE_SOURCES and not eexlib.closure_row_allowed(r, paused):
            continue
        if a.pos and r["pos"] != a.pos:
            continue
        slug = eexlib.slugify(r["headword"], r["pos"])
        if slug in taken or slug in existing:
            continue
        out.append((slug, r))
        if len(out) >= a.n:
            break
    for slug, r in out:
        print(f"{slug}\t{r['headword']}\t{r['pos']}\t{r['band']}\t{r['source']}")
    return 0


def reset_stale_claims(rows: list[dict], taken: set[str]) -> list[str]:
    """A `claimed` row that no claim file anywhere lists (claim.py --taken) goes back to `pending`
    (wiki/notes/queue-stale-claimed-rows.md). Run after the done pass, so a drafted row is already `done`."""
    reset = []
    for r in rows:
        if r["status"] != "claimed":
            continue
        slug = eexlib.slugify(r["headword"], r["pos"])
        if slug not in taken:
            r["status"] = "pending"
            if "stale claim reset" not in (r.get("note") or ""):
                r["note"] = ((r.get("note") or "") + "; stale claim reset by queue.py sync").strip("; ")
            reset.append(slug)
    return reset


def cmd_sync(a) -> int:
    rows = load()
    index = slug_index(rows)
    done = 0
    missing = []
    for p, e in eexlib.iter_entries():
        if eexlib.is_redirect_stub(e):
            continue
        slug = e["slug"]
        base = slug if e.get("homograph", 1) == 1 else slug.rsplit("-", 1)[0]
        r = index.get(base)
        if r is None:
            missing.append(slug)
        elif r["status"] in ("pending", "claimed"):
            r["status"] = "done"; done += 1
    reset = reset_stale_claims(rows, taken_slugs())
    save(rows)
    print(f"marked done: {done}; stale claims reset to pending: {len(reset)}; entries without a queue row: {len(missing)}")
    for s in reset:
        print("  reset " + s)
    for s in missing:
        print("  " + s)
    return 0


def cmd_stamp(a) -> int:
    rows = load()
    index = slug_index(rows)
    dv_path = eexlib.ROOT / "schema" / "defining-vocabulary.txt"
    dv = {w.strip().lower() for w in dv_path.read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")} if dv_path.exists() else set()
    for slug in a.slugs:
        p = eexlib.entry_path(slug)
        e = eexlib.load_json(p)
        base = slug if e.get("homograph", 1) == 1 else slug.rsplit("-", 1)[0]
        r = index.get(base)
        if r is None or not str(r.get("band") or "").strip():
            print(f"{slug}: no banded queue row; band left as is ({e['frequency']['band']})")
        else:
            e["frequency"]["band"] = int(r["band"])
        e["frequency"]["defining_vocabulary"] = e["headword"].lower() in dv
        e["frequency"]["basis"] = "editorial"
        eexlib.save_json(p, e)
        print(f"{slug}: band {e['frequency']['band']}, defining {e['frequency']['defining_vocabulary']}")
    return 0


def slug_index(rows: list[dict]) -> dict[str, dict]:
    """``slug -> row``; where rows share a slug, a live row beats a duplicate and a row with a
    hyphen or period beats one without (so sync and stamp read the real row, ruling C3)."""
    out: dict[str, dict] = {}
    def score(r):
        return (r["status"] != "duplicate", "-" in r["headword"] or "." in r["headword"])
    for r in rows:
        sl = _slug_or_none(r["headword"], r["pos"])
        if sl and (sl not in out or score(r) > score(out[sl])):
            out[sl] = r
    return out


def repair_forms(rows: list[dict], entries: dict[str, dict]) -> list[str]:
    """Fix rows whose headword lost a hyphen or a period (ruling C3 of 2026-10-24). Returns the changes.

    * Rows that share a slug: the live row with the hyphen or period stays; a pending lossy row
      becomes ``duplicate`` with a note naming the real row.
    * A lone affix row without its hyphen (``ible`` suffix) gets it (``-ible``).
    * A lone row queued by ``crossref`` or ``family`` gets the form the referring entry's prose uses
      (``mother in law`` -> ``mother-in-law`` when that entry writes it so).
    Only the queue's own ``headword``, ``status``, and ``note`` columns change."""
    changes = []
    groups: dict[str, list[dict]] = {}
    for r in rows:
        sl = _slug_or_none(r["headword"], r["pos"])
        if sl:
            groups.setdefault(sl, []).append(r)
    live = ("pending", "claimed", "done", "deferred", "declined", "unbanded")
    for sl, rs in groups.items():
        if len(rs) < 2:
            continue
        best = max(rs, key=lambda r: (r["status"] in live and r["status"] != "duplicate", r["status"] == "done",
                                      "-" in r["headword"] or "." in r["headword"], r["headword"] != r["headword"].lower()))
        for r in rs:
            if r is best or r["status"] not in ("pending", "unbanded"):
                continue
            r["status"] = "duplicate"
            r["note"] = ((r.get("note") or "") + f"; display form lost, the real row is {best['headword']} (queue.py repair-forms)").strip("; ")
            changes.append(f"duplicate {r['headword']} ({r['pos']}): the real row is {best['headword']}")
    for sl, rs in groups.items():
        if len(rs) != 1:
            continue
        r = rs[0]
        if r["status"] not in ("pending", "unbanded"):
            continue
        hw, pos = r["headword"], r["pos"]
        new = hw
        if pos == "suffix" and not hw.startswith("-"):
            new = "-" + hw
        elif pos == "prefix" and not hw.endswith("-"):
            new = hw + "-"
        elif r["source"] in ("crossref", "family") and (" " in hw or pos == "abbr"):
            m = __import__("re").search(r"referenced by ([a-z0-9-]+)", r.get("note") or "")
            ref = entries.get(m.group(1)) if m else None
            if ref is not None:
                guess = eexlib.guess_display_form(sl, eexlib.entry_texts(ref))
                if guess.lower() != hw.lower() and _slug_or_none(guess, pos) == sl:
                    new = guess
        if new != hw:
            r["headword"] = new
            r["note"] = ((r.get("note") or "") + f"; display form repaired from {hw} (queue.py repair-forms)").strip("; ")
            changes.append(f"renamed {hw} ({pos}) -> {new}")
    return changes


def cmd_repair_forms(a) -> int:
    rows = load()
    entries = {e["slug"]: e for _p, e in eexlib.iter_entries() if not eexlib.is_redirect_stub(e)}
    changes = repair_forms(rows, entries)
    for c in changes:
        print(c)
    if a.apply and changes:
        save(rows)
    print(f"{len(changes)} change(s){'' if a.apply else ' (dry run; --apply writes them)'}")
    return 0


def set_bands(rows: list[dict], bands: dict[str, tuple[int, str]]) -> tuple[int, int, list[str]]:
    """Write voted bands into the rows (by slug, the real row of each slug); an ``unbanded`` row becomes
    ``pending``.  Returns (rows changed, rows unbanded -> pending, slugs with no row)."""
    index = slug_index(rows)
    changed = released = 0
    missing = []
    for slug, (band, note) in bands.items():
        if not 1 <= int(band) <= 5:
            raise SystemExit(f"error: band {band} for {slug} is not 1 to 5")
        r = index.get(slug)
        if r is None:
            missing.append(slug)
            continue
        if str(r.get("band")) != str(band):
            r["band"] = str(band); changed += 1
        if r["status"] == "unbanded":
            r["status"] = "pending"; released += 1
        if note and note not in (r.get("note") or ""):
            r["note"] = ((r.get("note") or "") + "; " + note).strip("; ")
    return changed, released, missing


def cmd_set_bands(a) -> int:
    rows = load()
    bands = {}
    with open(a.file, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            bands[r["slug"]] = (int(r["band"]), r.get("note") or "")
    changed, released, missing = set_bands(rows, bands)
    save(rows)
    print(f"bands set: {changed} rows changed, {released} unbanded rows now pending, {len(missing)} slugs with no row")
    for s in missing[:20]:
        print("  no row: " + s)
    return 0


def cmd_counts(a) -> int:
    rows = load()
    for name, fn in (("status", lambda r: r["status"]), ("band", lambda r: r["band"]), ("source", lambda r: r["source"]), ("pos", lambda r: r["pos"])):
        c = Counter(fn(r) for r in rows)
        print(f"{name}: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    print(f"total: {len(rows)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--status"); p.add_argument("--band"); p.add_argument("--source"); p.add_argument("--pos"); p.add_argument("--limit", type=int); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("add"); p.add_argument("headword"); p.add_argument("pos"); p.add_argument("--band", type=int); p.add_argument("--source", required=True); p.add_argument("--note"); p.add_argument("--force-band", action="store_true"); p.set_defaults(fn=cmd_add)
    p = sub.add_parser("add-batch"); p.add_argument("file"); p.add_argument("--force-band", action="store_true"); p.set_defaults(fn=cmd_add_batch)
    p = sub.add_parser("set"); p.add_argument("headword"); p.add_argument("pos"); p.add_argument("status"); p.add_argument("--note"); p.set_defaults(fn=cmd_set)
    p = sub.add_parser("next"); p.add_argument("--n", type=int, default=20); p.add_argument("--band"); p.add_argument("--source"); p.add_argument("--pos"); p.set_defaults(fn=cmd_next)
    p = sub.add_parser("sync"); p.set_defaults(fn=cmd_sync)
    p = sub.add_parser("stamp"); p.add_argument("slugs", nargs="+"); p.set_defaults(fn=cmd_stamp)
    p = sub.add_parser("counts"); p.set_defaults(fn=cmd_counts)
    p = sub.add_parser("set-bands"); p.add_argument("file"); p.set_defaults(fn=cmd_set_bands)
    p = sub.add_parser("repair-forms"); p.add_argument("--apply", action="store_true"); p.set_defaults(fn=cmd_repair_forms)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
