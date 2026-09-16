#!/usr/bin/env python3
"""The headword queue: headwords/queue.tsv (see wiki/conventions.md section 3).

    python3 tools/queue.py list [--status S] [--band N] [--source S] [--pos P] [--limit N]
    python3 tools/queue.py add "<headword>" <pos> --band N --source S [--note "..."]
    python3 tools/queue.py add-batch <file.tsv>          # columns headword, pos, band, source[, note]
    python3 tools/queue.py set "<headword>" <pos> <status> [--note "..."]
    python3 tools/queue.py next [--n 20] [--band N] [--source S] [--pos P]   # pending rows not claimed anywhere
    python3 tools/queue.py sync                           # rows whose entry exists become done; entries without a row are reported
    python3 tools/queue.py stamp <slug> [<slug> ...]      # write frequency.band and frequency.defining_vocabulary into entries
    python3 tools/queue.py counts                         # rows by status, band, source

Only this tool edits the queue. Statuses and sources come from schema/vocabularies.json.
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


def add_rows(rows: list[dict], new: list[dict], force_band: bool = False) -> tuple[int, int]:
    index = {key(r["headword"], r["pos"]): r for r in rows}
    added = updated = 0
    for n in new:
        hw, pos = n["headword"].strip(), n["pos"].strip()
        check_value("pos", pos)
        check_value("queue_sources", n["source"])
        band = int(n["band"])
        if not 1 <= band <= 5:
            raise SystemExit(f"error: band {band} for {hw} is not 1 to 5")
        k = key(hw, pos)
        if k in index:
            r = index[k]
            changed = False
            if force_band and str(r["band"]) != str(band):
                r["band"] = str(band); changed = True
            if n.get("note") and n["note"] not in (r.get("note") or ""):
                r["note"] = ((r.get("note") or "") + "; " + n["note"]).strip("; "); changed = True
            updated += changed
            continue
        rows.append({"headword": hw, "pos": pos, "band": str(band), "source": n["source"], "status": "pending",
                     "added": today(), "note": n.get("note", "") or ""})
        index[k] = rows[-1]
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
    sel.sort(key=lambda r: (int(r["band"]), r["headword"], r["pos"]))
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


def cmd_next(a) -> int:
    rows = load()
    taken = taken_slugs()
    existing = {p.stem for p in eexlib.iter_entry_paths()}
    out = []
    for r in sorted(rows, key=lambda r: (int(r["band"]), r["headword"], r["pos"])):
        if r["status"] != "pending":
            continue
        if a.band and str(r["band"]) != str(a.band):
            continue
        if a.source and r["source"] != a.source:
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


def cmd_sync(a) -> int:
    rows = load()
    index = {eexlib.slugify(r["headword"], r["pos"]): r for r in rows}
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
    save(rows)
    print(f"marked done: {done}; entries without a queue row: {len(missing)}")
    for s in missing:
        print("  " + s)
    return 0


def cmd_stamp(a) -> int:
    rows = load()
    index = {eexlib.slugify(r["headword"], r["pos"]): r for r in rows}
    dv_path = eexlib.ROOT / "schema" / "defining-vocabulary.txt"
    dv = {w.strip().lower() for w in dv_path.read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")} if dv_path.exists() else set()
    for slug in a.slugs:
        p = eexlib.entry_path(slug)
        e = eexlib.load_json(p)
        base = slug if e.get("homograph", 1) == 1 else slug.rsplit("-", 1)[0]
        r = index.get(base)
        if r is None:
            print(f"{slug}: no queue row; band left as is ({e['frequency']['band']})")
        else:
            e["frequency"]["band"] = int(r["band"])
        e["frequency"]["defining_vocabulary"] = e["headword"].lower() in dv
        e["frequency"]["basis"] = "editorial"
        eexlib.save_json(p, e)
        print(f"{slug}: band {e['frequency']['band']}, defining {e['frequency']['defining_vocabulary']}")
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
    p = sub.add_parser("add"); p.add_argument("headword"); p.add_argument("pos"); p.add_argument("--band", type=int, required=True); p.add_argument("--source", required=True); p.add_argument("--note"); p.add_argument("--force-band", action="store_true"); p.set_defaults(fn=cmd_add)
    p = sub.add_parser("add-batch"); p.add_argument("file"); p.add_argument("--force-band", action="store_true"); p.set_defaults(fn=cmd_add_batch)
    p = sub.add_parser("set"); p.add_argument("headword"); p.add_argument("pos"); p.add_argument("status"); p.add_argument("--note"); p.set_defaults(fn=cmd_set)
    p = sub.add_parser("next"); p.add_argument("--n", type=int, default=20); p.add_argument("--band"); p.add_argument("--source"); p.add_argument("--pos"); p.set_defaults(fn=cmd_next)
    p = sub.add_parser("sync"); p.set_defaults(fn=cmd_sync)
    p = sub.add_parser("stamp"); p.add_argument("slugs", nargs="+"); p.set_defaults(fn=cmd_stamp)
    p = sub.add_parser("counts"); p.set_defaults(fn=cmd_counts)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
