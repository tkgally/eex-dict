#!/usr/bin/env python3
"""Check and complete cross-references between entries.

    python3 tools/crossref.py [<slug> ...] [--all] [--gate] [--apply] [--queue]

For every reference an entry makes (senses[].synonyms / antonyms / compare,
see_also, word_family, synonym_discrimination.words, phrases are not references):

* the slug must parse (a malformed slug is an ERROR; validate.py checks this too);
* a reference to the entry itself is an ERROR;
* a target with no entry file is reported (WARN) and, with --queue, added to the
  queue as a ``crossref`` or ``family`` candidate so that closure can create it;
* symmetric relations (synonym, antonym, compare at sense level; word family at
  entry level) get their back-link when the target exists: with --apply the
  back-link is written into the target entry (a script-owned operation per
  CLAUDE.md: adding a back-link that mirrors an existing forward link, never
  more), otherwise it is listed as an asymmetry.

A sense-level back-link is added to the target's sense that already lists the
source; else to the target sense whose definition and explanation share the most
content words with the source sense's (the source headword in the target sense
counts two), provided the best sense scores at least 2; else to the first sense.
The back-link's note is null. Each back-link is printed as a BACKLINK line; a
session should check that the sense fits. When the target already names the
source under another sense relation (a synonym one way, a compare the other),
nothing is written and a TYPE-MISMATCH line is printed: the type is a semantic
choice for the session. --gate exits 1 on ERRORs only
(missing targets are the closure queue's job, not a gate failure).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

SENSE_RELATIONS = ["synonyms", "antonyms", "compare"]

# Words too common to say which sense a back-link belongs on.
_STOP = set("""a an the of to or and in on for with by at from as is are be been being it its
this that these those something someone somebody somewhere things thing people person you your
they them their he she his her we our not no so if when which who what how very more most usually
especially often another other such some any than into out up about over used using use one way
make makes made have has had do does done get gets got""".split())
MIN_OVERLAP = 2   # chosen on the 585 symmetric pairs in the dictionary, 2026-09-25


def _stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "s", "ly"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def _content_words(sense: dict) -> set[str]:
    text = f"{sense.get('definition') or ''} {sense.get('explanation') or ''}".lower()
    return {_stem(w) for w in re.findall(r"[a-z]+", text) if w not in _STOP and len(w) > 2}


def best_sense(target: dict, source_sense: dict | None, source_headword: str = "") -> int:
    """Index of the target sense that best matches the source sense (0 when nothing scores MIN_OVERLAP)."""
    if not source_sense:
        return 0
    sw = _content_words(source_sense)
    hw = _stem(source_headword.lower())
    best, best_score = 0, -1
    for j, s in enumerate(target.get("senses", [])):
        tw = _content_words(s)
        score = len(sw & tw) + (2 if hw and hw in tw else 0)
        if score > best_score and (j == 0 or score >= MIN_OVERLAP):
            best, best_score = j, score
    return best


def load_all() -> dict[str, tuple[Path, dict]]:
    out = {}
    for p, e in eexlib.iter_entries():
        if eexlib.is_redirect_stub(e):
            continue
        out[e["slug"]] = (p, e)
    return out


def refs_of(entry: dict):
    """Yield (kind, slug, sense_index_or_None)."""
    for i, s in enumerate(entry.get("senses", [])):
        for rel in SENSE_RELATIONS:
            for x in s.get(rel, []):
                yield rel, x["slug"], i
    for x in entry.get("see_also", []):
        yield "see_also", x["slug"], None
    for x in entry.get("word_family", []):
        yield "word_family", x["slug"], None
    sd = entry.get("synonym_discrimination")
    if sd:
        for slug in sd.get("words", []):
            yield "synonym_discrimination", slug, None


def has_backlink(target: dict, rel: str, source_slug: str) -> bool:
    if rel == "word_family":
        return any(x["slug"] == source_slug for x in target.get("word_family", []))
    return any(x["slug"] == source_slug for s in target.get("senses", []) for x in s.get(rel, []))


def other_type_link(target: dict, rel: str, source_slug: str) -> str | None:
    """The other sense relation under which the target already names the source, if any."""
    for s in target.get("senses", []):
        for r in SENSE_RELATIONS:
            if r != rel and any(x["slug"] == source_slug for x in s.get(r, [])):
                return r
    return None


def add_backlink(target: dict, rel: str, source_slug: str, source: dict | None = None,
                 source_sense_index: int | None = None) -> str:
    if rel == "word_family":
        target.setdefault("word_family", []).append({"slug": source_slug, "form": None, "note": None})
        return "word_family"
    # prefer a sense that already mentions the source in another relation; else the closest sense
    idx = None
    for i, s in enumerate(target.get("senses", [])):
        if any(x["slug"] == source_slug for r in SENSE_RELATIONS for x in s.get(r, [])):
            idx = i
            break
    if idx is None:
        src_sense = None
        if source is not None and source_sense_index is not None:
            src_sense = source.get("senses", [])[source_sense_index]
        idx = best_sense(target, src_sense, (source or {}).get("headword", ""))
    target["senses"][idx].setdefault(rel, []).append({"slug": source_slug, "note": None})
    return f"senses[{idx}].{rel}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--gate", action="store_true", help="exit 1 on errors (self-reference, malformed slug)")
    ap.add_argument("--apply", action="store_true", help="write missing back-links into target entries")
    ap.add_argument("--queue", action="store_true", help="queue missing targets as crossref/family candidates")
    a = ap.parse_args()
    entries = load_all()
    slugs = a.slugs or (sorted(entries) if (a.all or a.gate or not a.slugs) else [])
    errors = warns = 0
    missing: dict[str, tuple[str, str]] = {}
    changed: set[str] = set()
    for slug in slugs:
        if slug not in entries:
            print(f"ERROR {slug}: no such entry"); errors += 1; continue
        _p, e = entries[slug]
        for rel, target, sense_i in refs_of(e):
            where = f"{slug}" + (f" senses[{sense_i}].{rel}" if sense_i is not None else f" {rel}")
            try:
                eexlib.parse_slug(target)
            except ValueError:
                print(f"ERROR {where}: malformed slug {target!r}"); errors += 1; continue
            if target == slug:
                if rel == "synonym_discrimination":      # the note compares the headword with the others
                    continue
                print(f"ERROR {where}: refers to itself"); errors += 1; continue
            if target not in entries:
                print(f"WARN {where}: no entry for {target} yet"); warns += 1
                missing.setdefault(target, ("family" if rel == "word_family" else "crossref", slug))
                continue
            if rel in SENSE_RELATIONS or rel == "word_family":
                tp, te = entries[target]
                if not has_backlink(te, rel, slug):
                    other = other_type_link(te, rel, slug) if rel in SENSE_RELATIONS else None
                    if other:
                        # the pair's type is a semantic choice: report it, never write a second type
                        print(f"TYPE-MISMATCH {target} names {slug} under {other}, {slug} names {target} under {rel}"); warns += 1
                    elif a.apply:
                        loc = add_backlink(te, rel, slug, e, sense_i)
                        te["provenance"]["modified"] = eexlib.utcnow_iso()
                        changed.add(target)
                        print(f"BACKLINK {target} {loc} <- {slug}")
                    else:
                        print(f"ASYMMETRY {target} lacks {rel} back-link to {slug} (use --apply)"); warns += 1
    for t in changed:
        tp, te = entries[t]
        eexlib.save_json(tp, te)
    if a.queue and missing:
        rows = ["headword\tpos\tband\tsource\tnote"]
        for target, (src, from_slug) in sorted(missing.items()):
            hw, pos, _h = eexlib.parse_slug(target)
            rows.append(f"{hw.replace('-', ' ')}\t{pos}\t3\t{src}\treferenced by {from_slug}")
        with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False, encoding="utf-8") as tf:
            tf.write("\n".join(rows) + "\n")
        r = subprocess.run([sys.executable, str(HERE / "queue.py"), "add-batch", tf.name], capture_output=True, text=True, cwd=eexlib.ROOT)
        print("queue:", r.stdout.strip() or r.stderr.strip())
        Path(tf.name).unlink(missing_ok=True)
    print(f"crossref: {len(slugs)} entries, {errors} errors, {warns} warnings, {len(missing)} missing targets, {len(changed)} entries updated")
    return 1 if (errors and a.gate) or (errors and not a.gate and False) else (1 if errors else 0)


if __name__ == "__main__":
    sys.exit(main())
