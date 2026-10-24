#!/usr/bin/env python3
"""Check and complete cross-references between entries.

    python3 tools/crossref.py [<slug> ...] [--all] [--gate] [--apply] [--queue]
    python3 tools/crossref.py --missing-senses [<slug> ...]   # report: incoming synonyms/antonyms with no matching sense

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

A sense-level back-link is written only where one sense of the target clearly
matches (the owner's ruling C1 of 2026-10-24, wiki/decisions/cross-reference-display.md):
the target has one sense; or exactly one sense already names the source under
another relation; or exactly one sense uses the source headword in its
definition or explanation.  Otherwise nothing is written and a NO-SENSE line
reports the pair (with the closest sense by shared words, as a hint only) for a
review cycle to place by hand.  The old fallback (the sense with the most shared
words, else the first sense) is gone.  The back-link's note is null. Each
back-link is printed as a BACKLINK line. When the target already names the
source under another sense relation (a synonym one way, a compare the other),
nothing is written and a TYPE-MISMATCH line is printed: the type is a semantic
choice for the session.

A target that a fence rules out or whose queue row is ``duplicate``
(eexlib.ruled_out_targets) is refused: it is never queued, and a reference to
it is a RULED-OUT line, an ERROR in an entry changed since origin/main (so no
new one lands) and a warning in the others (the review cycles remove those).
--gate exits 1 on ERRORs only (missing targets are the closure queue's job,
not a gate failure).

--missing-senses lists the incoming synonyms and antonyms for which no sense of
the target clearly matches the source sense: evidence of a sense the target may
lack (ruling B1; *sharp* "clever" lists *dull*). It writes nothing.
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


def _mentions(sense: dict, headword: str) -> bool:
    """True when the sense's definition or explanation uses ``headword`` (or a simple form of it)."""
    if not headword:
        return False
    text = f"{sense.get('definition') or ''} {sense.get('explanation') or ''}".lower()
    words = {_stem(w) for w in re.findall(r"[a-z]+", text)}
    hw = headword.lower()
    if " " in hw:
        return hw in text
    return _stem(hw) in words or hw in words


def clear_sense(target: dict, source_slug: str, source_headword: str = "") -> int | None:
    """The index of the one target sense that clearly matches the source, or None (ruling C1)."""
    senses = target.get("senses", [])
    if len(senses) == 1:
        return 0
    named = [i for i, s in enumerate(senses) if any(x["slug"] == source_slug for r in SENSE_RELATIONS for x in s.get(r, []))]
    if len(named) == 1:
        return named[0]
    if named:
        return None
    used = [i for i, s in enumerate(senses) if _mentions(s, source_headword)]
    return used[0] if len(used) == 1 else None


def best_sense(target: dict, source_sense: dict | None, source_headword: str = "") -> int:
    """Index of the target sense that shares the most words with the source sense (0 when nothing scores
    MIN_OVERLAP).  Since ruling C1 a hint printed on a NO-SENSE line only, never a placement."""
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
                 source_sense_index: int | None = None) -> str | None:
    """Write the mirror link and return where it went, or None when no sense clearly matches (nothing written)."""
    if rel == "word_family":
        target.setdefault("word_family", []).append({"slug": source_slug, "form": None, "note": None})
        return "word_family"
    idx = clear_sense(target, source_slug, (source or {}).get("headword", ""))
    if idx is None:
        return None
    target["senses"][idx].setdefault(rel, []).append({"slug": source_slug, "note": None})
    return f"senses[{idx}].{rel}"


def changed_slugs() -> set[str]:
    try:
        return {p.stem for p in eexlib.changed_entry_paths()}
    except Exception:  # noqa: BLE001 - no git, no ratchet
        return set()


def missing_senses(entries: dict, slugs) -> list[str]:
    """Incoming synonyms/antonyms that no sense of the target matches (ruling B1's free signal).

    A pair is listed when the target names the source on no sense, or names it only through a
    note-less mirror on a sense that shares no content word with the source sense and does not use
    the source headword (the old fallback's placements).  The answer is a judgment for a review cycle."""
    out = []
    for slug in slugs:
        _p, e = entries[slug]
        for i, s in enumerate(e.get("senses", [])):
            sw = _content_words(s)
            for rel in ("synonyms", "antonyms"):
                for x in s.get(rel, []):
                    t = x["slug"]
                    if t not in entries or t == slug:
                        continue
                    te = entries[t][1]
                    if len(te.get("senses", [])) < 2:
                        continue
                    homes = [(j, y) for j, ts in enumerate(te["senses"]) for y in ts.get(rel, []) if y["slug"] == slug]
                    if homes and (any(y.get("note") for _j, y in homes)
                                  or any(sw & _content_words(te["senses"][j]) or _mentions(te["senses"][j], e.get("headword", ""))
                                         for j, _y in homes)):
                        continue
                    where = "names it nowhere" if not homes else "names it only on sense %s" % ", ".join(str(j + 1) for j, _y in homes)
                    out.append(f"MISSING-SENSE? {t} ({where}) for {slug} sense {s.get('n', i + 1)} "
                               f"({rel[:-1]}: \"{(s.get('definition') or '')[:60]}\")")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--gate", action="store_true", help="exit 1 on errors (self-reference, malformed slug)")
    ap.add_argument("--apply", action="store_true", help="write missing back-links into target entries")
    ap.add_argument("--queue", action="store_true", help="queue missing targets as crossref/family candidates")
    ap.add_argument("--missing-senses", action="store_true", help="report incoming synonyms/antonyms with no matching sense; writes nothing")
    a = ap.parse_args()
    entries = load_all()
    slugs = a.slugs or (sorted(entries) if (a.all or a.gate or not a.slugs) else [])
    if a.missing_senses:
        lines = missing_senses(entries, slugs)
        for ln in lines:
            print(ln)
        print(f"crossref --missing-senses: {len(slugs)} entries, {len(lines)} pairs to check by hand")
        return 0
    ruled = {k: v for k, v in eexlib.ruled_out_targets().items() if k not in entries}
    changed = changed_slugs()
    no_sense = 0
    errors = warns = 0
    missing: dict[str, tuple[str, str]] = {}
    written: set[str] = set()
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
            if target in ruled:
                level = "ERROR" if slug in changed else "WARN"
                print(f"RULED-OUT {level} {where}: {target} ({ruled[target]})")
                if level == "ERROR":
                    errors += 1
                else:
                    warns += 1
                continue
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
                        if loc is None:
                            hint = best_sense(te, e.get("senses", [])[sense_i] if sense_i is not None else None, e.get("headword", ""))
                            print(f"NO-SENSE {target} <- {slug} senses[{sense_i}].{rel}: no sense clearly matches; "
                                  f"nothing written (closest by shared words: senses[{hint}])"); warns += 1; no_sense += 1
                            continue
                        te["provenance"]["modified"] = eexlib.utcnow_iso()
                        written.add(target)
                        print(f"BACKLINK {target} {loc} <- {slug}")
                    else:
                        print(f"ASYMMETRY {target} lacks {rel} back-link to {slug} (use --apply)"); warns += 1
    for t in written:
        tp, te = entries[t]
        eexlib.save_json(tp, te)
    if a.queue and missing:
        rows = ["headword\tpos\tband\tsource\tnote"]
        known = eexlib.queue_display_map(eexlib.load_queue_rows())
        for target, (src, from_slug) in sorted(missing.items()):
            _hw, pos, _h = eexlib.parse_slug(target)
            # the display form keeps its hyphens and periods (ruling C3): a queue row's, else the referring entry's prose
            hw = known.get(target) or eexlib.guess_display_form(target, eexlib.entry_texts(entries[from_slug][1]))
            rows.append(f"{hw}\t{pos}\t3\t{src}\treferenced by {from_slug}")
        with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False, encoding="utf-8") as tf:
            tf.write("\n".join(rows) + "\n")
        r = subprocess.run([sys.executable, str(HERE / "queue.py"), "add-batch", tf.name], capture_output=True, text=True, cwd=eexlib.ROOT)
        print("queue:", r.stdout.strip() or r.stderr.strip())
        Path(tf.name).unlink(missing_ok=True)
    print(f"crossref: {len(slugs)} entries, {errors} errors, {warns} warnings, {len(missing)} missing targets, "
          f"{len(written)} entries updated, {no_sense} back-links left for a person (NO-SENSE)")
    return 1 if (errors and a.gate) or (errors and not a.gate and False) else (1 if errors else 0)


if __name__ == "__main__":
    sys.exit(main())
