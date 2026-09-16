#!/usr/bin/env python3
"""Write an entry's ``inflections`` from the spelling rules and schema/inflection-exceptions.json.

    python3 tools/inflect.py <slug> [<slug> ...] [--dry-run]     # write (or show) the forms of entries
    python3 tools/inflect.py --word "<headword>" --pos <pos> [--code "not gradable"] [--code "comparative with more"]
                             [--countability uncountable]        # print JSON, touch nothing
    python3 tools/inflect.py --confirm <slug> [<slug> ...]       # set inflections.status to verified, change nothing else
    python3 tools/inflect.py ... --root DIR | --entries DIR | --exceptions FILE   # other locations (tests)

American forms are primary.  Nouns get ``plural``; verbs and phrasal verbs get ``third_person_singular``,
``past_tense``, ``past_participle`` and ``present_participle``; adjectives and adverbs get ``comparative`` and
``superlative``; every other part of speech gets no forms (``source: none``).  A form found in the table's verbs,
nouns, adjectives or adverbs sections makes the entry ``regular: false`` with ``source: exceptions``; the table's
spelling lists (doubling, single_l, keep_e, ie_to_y, o_es, f_to_ves, c_ck, suffix_regular) only steer the rules.

What the entry itself decides: a noun whose every sense is uncountable, singular only or plural only has
``plural: null``; an adjective or adverb whose every sense carries a gradability code (``not gradable`` or
``comparative with more``) has null comparison forms with that code as the note.  A comparison the rules cannot
decide (most words of two or more syllables) is left null with ``status: unverified`` and a note asking for a
grammar code or a table line.  Everything the rules or the table decide is ``verified``.

Only ``inflections`` and ``provenance.modified`` are written.  The previous note is printed and then replaced.

Library: ``inflect(headword, pos, codes=(), countability=None, exceptions=None)`` returns
``(forms, regular, source, status, note)``; ``all_forms(...)`` returns the set of every form including the
headword and the table's alternative plurals; ``load_exceptions(path=None)`` loads the table.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

EXCEPTIONS_FILE = HERE.parent / "schema" / "inflection-exceptions.json"
VOWELS = "aeiou"
NO_PLURAL = ("uncountable", "plural only", "singular only")
GRADABILITY_CODES = ("not gradable", "comparative with more")
NON_INFLECTING = ("prep", "conj", "pron", "det", "num", "interj", "phr", "prefix", "suffix", "comb")
NO_FORM_VERBS = ("modal", "aux")
LIST_SECTIONS = ("doubling", "single_l", "keep_e", "ie_to_y", "o_es", "f_to_ves", "c_ck", "suffix_regular")
DOUBLING_PREFIXES = ("re", "un", "de", "dis", "mis", "over", "under", "out", "pre", "sub", "trans", "inter", "co", "fore", "up")
IRREGULAR_SUFFIX_KEYS = ("woman", "child", "tooth", "goose", "mouse", "louse", "foot", "man")
UNDECIDED_NOTE = ("comparative undecided: add a grammar code (comparative with more / not gradable) "
                  "or a line in schema/inflection-exceptions.json")
FORM_ORDER = ("plural", "third_person_singular", "past_tense", "past_participle", "present_participle",
              "comparative", "superlative")

_EXC_CACHE = {}


# --------------------------------------------------------------------------
# The table
# --------------------------------------------------------------------------

def load_exceptions(path=None):
    """Load the exceptions table (cached per path); the spelling lists become sets."""
    path = Path(path) if path else EXCEPTIONS_FILE
    key = str(path.resolve())
    if key not in _EXC_CACHE:
        table = eexlib.load_json(path)
        for section in ("verbs", "nouns", "adjectives", "adverbs"):
            table.setdefault(section, {})
        for section in LIST_SECTIONS:
            table[section] = set(table.get(section) or [])
        _EXC_CACHE[key] = table
    return _EXC_CACHE[key]


def _listed(exc, section, word):
    return word.lower() in (exc.get(section) or ())


# --------------------------------------------------------------------------
# Spelling helpers
# --------------------------------------------------------------------------

def _cap_like(model, form):
    """Give ``form`` the capitalization of ``model`` (Child -> Children, TV -> TVs)."""
    if form and model[:1].isupper() and form[:1].islower():
        return form[0].upper() + form[1:]
    return form


def syllables(word):
    """A syllable estimate: vowel groups, with a final silent e not counted (simple, table: the -le is counted)."""
    w = re.sub(r"[^a-z]", "", word.lower()).replace("qu", "q")
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if n > 1 and w.endswith("e") and w[-2] not in "aeiouy":
        if not (w.endswith("le") and w[-3] not in "aeiouy"):
            n -= 1
    elif n > 2 and w.endswith("ely") and w[-4] not in "aeiouy":   # lonely, likely: the medial e is silent
        n -= 1
    return max(n, 1)


def _cvc(word):
    """True when the word ends consonant + single vowel letter + consonant other than w, x or y."""
    w = word.lower().replace("qu", "q")
    if len(w) < 3 or not w[-1].isalpha():
        return False
    last, mid, before = w[-1], w[-2], w[-3]
    if last in VOWELS or last in "wxy" or mid not in VOWELS:
        return False
    if before in VOWELS:          # digraph: rain -> rained, seat -> seated
        return False
    return before.isalpha()


def _in_doubling(exc, word):
    w = word.lower()
    if w in exc["doubling"]:
        return True
    for prefix in DOUBLING_PREFIXES:
        if w.startswith(prefix) and w[len(prefix):] in exc["doubling"]:
            return True
    return False


def _doubles(word, exc):
    """Should the final consonant double before -ed, -ing, -er, -est?"""
    if not _cvc(word):
        return False
    if syllables(word) == 1:
        return True
    return _in_doubling(exc, word)


def _consonant_y(word):
    w = word.lower().replace("qu", "q")
    return len(w) >= 2 and w.endswith("y") and w[-2] not in VOWELS


# --------------------------------------------------------------------------
# Nouns
# --------------------------------------------------------------------------

def _table_plural(headword, value):
    """Resolve a nouns-section value to (plural, alternatives, note)."""
    if value is None:
        return None, [], "no plural"
    if isinstance(value, str):
        return _cap_like(headword, value), [], None
    if isinstance(value, list):
        alts = [_cap_like(headword, v) for v in value[1:]]
        return _cap_like(headword, value[0]), alts, ("also " + ", ".join(alts)) if alts else None
    plural = value.get("plural")
    plural = _cap_like(headword, plural) if plural else None
    alts = [_cap_like(headword, v) for v in value.get("also") or []]
    note = value.get("note")
    if note is None:
        note = ("also " + ", ".join(alts)) if alts else ("no plural" if plural is None else None)
    return plural, alts, note


def _plural_rules(word, exc):
    """The regular plural of a single word (no table lookup for the word itself)."""
    w = word.lower()
    for key in IRREGULAR_SUFFIX_KEYS:          # policeman -> policemen, grandchild -> grandchildren
        if w.endswith(key) and len(w) > len(key) and key in exc["nouns"] and w not in exc["suffix_regular"]:
            plural = _table_plural(word[-len(key):], exc["nouns"][key])[0]
            return word[:-len(key)] + plural
    for key in exc["f_to_ves"]:                # penknife -> penknives, bookshelf -> bookshelves
        if w.endswith(key) and len(w) > len(key) and len(key) >= 4:
            return word[:-1] + "ves" if w.endswith("f") else word[:-2] + "ves"
    if w.endswith("sis") and len(w) > 4:       # synopsis -> synopses
        return word[:-2] + "es"
    if w.endswith(("ch", "sh", "s", "x", "z")):
        if w.endswith("z") and _cvc(w) and syllables(w) == 1:   # quiz -> quizzes
            return word + "zes"
        return word + "es"
    if _consonant_y(w):
        return word[:-1] + "ies"
    if w.endswith("o"):
        return word + ("es" if w in exc["o_es"] else "s")
    if w in exc["f_to_ves"]:
        return (word[:-1] if w.endswith("f") else word[:-2]) + "ves"
    return word + "s"


def plural_noun(headword, exc, abbreviation=False):
    """(plural, alternatives, note, from_table) for a noun or abbreviation headword."""
    key = headword.lower()
    if key in exc["nouns"]:
        plural, alts, note = _table_plural(headword, exc["nouns"][key])
        return plural, alts, note, True
    if abbreviation:
        return headword + "s", [], None, False
    for sep in (" ", "-"):
        if sep in headword.strip(sep):
            head, _, last = headword.rpartition(sep)
            plural, alts, note, from_table = plural_noun(last, exc)
            if plural is None:
                return None, [], note, from_table
            return head + sep + plural, [head + sep + alt for alt in alts], note, from_table
    return _plural_rules(headword, exc), [], None, False


def _noun_forms(headword, pos, countability, exc):
    if countability in NO_PLURAL:
        note = "plural only" if countability == "plural only" else "no plural"
        return {"plural": None}, True, "rules", "verified", note
    if pos == "abbr" and countability is None:
        return {}, True, "none", "verified", None
    plural, _alts, note, from_table = plural_noun(headword, exc, abbreviation=(pos == "abbr"))
    return {"plural": plural}, not from_table, "exceptions" if from_table else "rules", "verified", note


# --------------------------------------------------------------------------
# Verbs
# --------------------------------------------------------------------------

def _third_person(word, exc):
    w = word.lower()
    if _consonant_y(w):
        return word[:-1] + "ies"
    if w.endswith(("ch", "sh", "s", "x", "z")):
        if w.endswith("z") and _cvc(w) and syllables(w) == 1:   # quiz -> quizzes
            return word + "zes"
        return word + "es"
    if w.endswith("o") and (w in exc["o_es"] or w in ("go", "do")):
        return word + "es"
    return word + "s"


def _past(word, exc):
    w = word.lower()
    if w.endswith("e"):
        return word + "d"
    if _consonant_y(w):
        return word[:-1] + "ied"
    if w.endswith("c") and (w in exc["c_ck"] or (len(w) > 1 and w[-2] in VOWELS)):
        return word + "ked"
    if _doubles(word, exc):
        return word + word[-1] + "ed"
    return word + "ed"


def _present_participle(word, exc):
    w = word.lower()
    if w.endswith("ie"):
        return word[:-2] + "ying"
    if w.endswith("e"):
        if w in exc["keep_e"] or w.endswith(("ee", "oe", "ye")):
            return word + "ing"
        return word[:-1] + "ing"
    if w.endswith("c") and (w in exc["c_ck"] or (len(w) > 1 and w[-2] in VOWELS)):
        return word + "king"
    if _doubles(word, exc):
        return word + word[-1] + "ing"
    return word + "ing"


def verb_forms(headword, exc):
    """(forms, note, from_table) for a verb; a phrasal verb inflects its first word, a hyphenated verb its last."""
    key = headword.lower()
    prefix, word, suffix = "", headword, ""
    if key not in exc["verbs"]:
        if " " in headword.strip():
            word, _, rest = headword.partition(" ")
            suffix = " " + rest
        elif "-" in headword.strip("-"):
            head, _, word = headword.rpartition("-")
            prefix = head + "-"
    key = word.lower()
    table = exc["verbs"].get(key) or {}
    forms = {
        "third_person_singular": table.get("third_person_singular") or _third_person(word, exc),
        "past_tense": table.get("past_tense") or _past(word, exc),
        "past_participle": table.get("past_participle") or _past(word, exc),
        "present_participle": table.get("present_participle") or _present_participle(word, exc),
    }
    forms = {k: prefix + _cap_like(word, v) + suffix for k, v in forms.items()}
    note = table.get("note")
    if not table and key in exc["single_l"]:
        note = "British spelling doubles the l: %s, %s" % (word + "led", word + "ling")
    return forms, note, bool(table)


# --------------------------------------------------------------------------
# Adjectives and adverbs
# --------------------------------------------------------------------------

def _er_est(word, exc):
    w = word.lower()
    if w.endswith("e"):
        return word + "r", word + "st"
    if _consonant_y(w):
        return word[:-1] + "ier", word[:-1] + "iest"
    if _doubles(word, exc):
        return word + word[-1] + "er", word + word[-1] + "est"
    return word + "er", word + "est"


def compare_forms(headword, pos, codes, exc):
    """(forms, regular, source, status, note) for an adjective or adverb."""
    null = {"comparative": None, "superlative": None}
    codes = tuple(codes or ())
    if "not gradable" in codes:
        return null, True, "rules", "verified", "not gradable"
    if "comparative with more" in codes:
        return null, True, "rules", "verified", "comparative with more"
    table = exc["adjectives" if pos == "adj" else "adverbs"].get(headword.lower())
    if table:
        forms = {k: _cap_like(headword, table.get(k)) if table.get(k) else None for k in ("comparative", "superlative")}
        return forms, False, "exceptions", "verified", table.get("note")
    w = headword.lower()
    n = syllables(headword)
    if pos == "adv" and n > 1 and w.endswith("ly"):
        return null, True, "rules", "verified", "comparative with more"
    if n == 1 or (n == 2 and (w.endswith(("ow", "le", "er", "et")) or _consonant_y(w))):
        comp, sup = _er_est(headword, exc)
        note = None
        if w in exc["single_l"]:
            note = "British spelling doubles the l: %s, %s" % (w + "ler", w + "lest")
        return {"comparative": comp, "superlative": sup}, True, "rules", "verified", note
    return null, True, "rules", "unverified", UNDECIDED_NOTE


# --------------------------------------------------------------------------
# The library entry points
# --------------------------------------------------------------------------

def inflect(headword, pos, codes=(), countability=None, exceptions=None):
    """Return ``(forms, regular, source, status, note)`` for a headword of part of speech ``pos``.

    ``codes`` are the grammar codes that bear on gradability; ``countability`` is a value of the countability
    vocabulary (for a noun, None means countable; for an abbreviation, None means not used as a noun).
    ``exceptions`` is a loaded table (``load_exceptions``) or None for the repository's own.
    """
    headword = str(headword).strip()
    if not headword:
        raise ValueError("empty headword")
    exc = exceptions if exceptions is not None else load_exceptions()
    if pos in NON_INFLECTING or pos in NO_FORM_VERBS:
        return {}, True, "none", "verified", None
    if pos in ("n", "abbr"):
        return _noun_forms(headword, pos, countability, exc)
    if pos in ("v", "phrv"):
        forms, note, from_table = verb_forms(headword, exc)
        return forms, not from_table, "exceptions" if from_table else "rules", "verified", note
    if pos in ("adj", "adv"):
        return compare_forms(headword, pos, codes, exc)
    raise ValueError("unknown part of speech %r" % (pos,))


def all_forms(headword, pos, codes=(), countability=None, exceptions=None):
    """Every form of the headword as a set: the headword, the generated forms, and the table's alternatives."""
    exc = exceptions if exceptions is not None else load_exceptions()
    forms, _regular, _source, _status, _note = inflect(headword, pos, codes, countability, exc)
    out = {headword.strip()}
    out.update(v for v in forms.values() if v)
    if pos in ("n", "abbr") and forms.get("plural"):
        _plural, alts, _note, _from_table = plural_noun(headword.strip(), exc, abbreviation=(pos == "abbr"))
        out.update(alts)
    return out


def inflections_record(headword, pos, codes=(), countability=None, exceptions=None):
    """The ``inflections`` object of an entry, keys in schema order."""
    forms, regular, source, status, note = inflect(headword, pos, codes, countability, exceptions)
    ordered = {k: forms[k] for k in FORM_ORDER if k in forms}
    return {"forms": ordered, "regular": regular, "source": source, "status": status, "note": note}


# --------------------------------------------------------------------------
# Reading an entry: the codes and countability its senses agree on
# --------------------------------------------------------------------------

def entry_codes(entry):
    """The gradability codes to apply: a code counts only when every sense carries one.

    A sense with no gradability code makes the word gradable as a whole (happy has a sense marked not gradable
    but is still happier, happiest).  When every sense is restricted and at least one compares with more,
    that code wins over not gradable, because a form exists for it.
    """
    senses = entry.get("senses") or []
    per_sense = []
    for sense in senses:
        codes = set(((sense.get("grammar") or {}).get("codes")) or [])
        per_sense.append(codes & set(GRADABILITY_CODES))
    if not senses or not all(per_sense):
        return ()
    union = set().union(*per_sense)
    return ("comparative with more",) if "comparative with more" in union else ("not gradable",)


def entry_countability(entry):
    """The countability to apply: no plural only when every sense says so; None when no sense has a value."""
    senses = entry.get("senses") or []
    values = [((sense.get("grammar") or {}).get("countability")) for sense in senses]
    if not values or not any(values):
        return None
    if all(v in NO_PLURAL for v in values):
        return "plural only" if all(v == "plural only" for v in values) else "uncountable"
    return "countable"


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

def _entry_file(slug, entries_dir):
    eexlib.parse_slug(slug)                       # raises ValueError for a malformed slug
    return Path(entries_dir) / eexlib.shard(slug) / (slug + ".json")


def _forms_text(forms):
    if not forms:
        return "-"
    return "; ".join("%s=%s" % (k, "null" if v is None else v) for k, v in forms.items())


def _print_table(rows):
    """rows: (slug, forms, source, status, note)."""
    widths = [max(len(str(r[i])) for r in rows + [("slug", "forms", "source", "status", "note")]) for i in range(4)]
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(("slug", "forms", "source", "status"))) + "  note"
    print(line)
    print("-" * len(line))
    for r in rows:
        print("  ".join(str(r[i]).ljust(widths[i]) for i in range(4)) + "  " + ("-" if r[4] is None else str(r[4])))


def process_entry(entry, exc):
    """Compute and install the inflections of an entry; return (record, previous_note)."""
    codes = entry_codes(entry)
    countability = entry_countability(entry)
    record = inflections_record(entry["headword"], entry["pos"], codes, countability, exc)
    previous = (entry.get("inflections") or {}).get("note")
    entry["inflections"] = record
    entry.setdefault("provenance", {})["modified"] = eexlib.utcnow_iso()
    return record, previous


def run_slugs(slugs, entries_dir, exc, dry_run=False, confirm=False):
    rows, failures = [], 0
    for slug in slugs:
        try:
            path = _entry_file(slug, entries_dir)
            entry = eexlib.load_json(path)
        except (ValueError, OSError) as err:
            print("error: %s: %s" % (slug, err), file=sys.stderr)
            failures += 1
            continue
        if eexlib.is_redirect_stub(entry):
            print("error: %s is a redirect stub" % slug, file=sys.stderr)
            failures += 1
            continue
        if confirm:
            record = entry.setdefault("inflections", {"forms": {}, "regular": True, "source": "none", "note": None})
            record["status"] = "verified"
            entry.setdefault("provenance", {})["modified"] = eexlib.utcnow_iso()
            previous = None
        else:
            record, previous = process_entry(entry, exc)
            if previous:
                print("%s: previous note replaced: %s" % (slug, previous))
        if not dry_run:
            eexlib.save_json(path, entry)
        rows.append((slug, _forms_text(record["forms"]), record["source"], record["status"], record["note"]))
    if rows:
        _print_table(rows)
        print("%d entr%s %s" % (len(rows), "y" if len(rows) == 1 else "ies", "shown (dry run)" if dry_run else "written"))
    return 1 if failures else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*", help="entries to inflect (or to confirm with --confirm)")
    ap.add_argument("--dry-run", action="store_true", help="print the table; write nothing")
    ap.add_argument("--confirm", action="store_true", help="set inflections.status to verified for the slugs; change nothing else")
    ap.add_argument("--word", help="a headword to inflect without touching any file (with --pos)")
    ap.add_argument("--pos", help="the part-of-speech code for --word")
    ap.add_argument("--code", action="append", default=[], help="a grammar code for --word (repeatable)")
    ap.add_argument("--countability", help="the countability of the noun given with --word")
    ap.add_argument("--root", help="another repository root (entries and table under it)")
    ap.add_argument("--entries", help="another entries directory")
    ap.add_argument("--exceptions", help="another exceptions table")
    args = ap.parse_args(argv)

    if args.root:
        eexlib.set_root(args.root)
    root = eexlib.get_root()
    entries_dir = Path(args.entries) if args.entries else root / "entries"
    table_path = Path(args.exceptions) if args.exceptions else root / "schema" / "inflection-exceptions.json"
    if not table_path.is_file():
        table_path = EXCEPTIONS_FILE
    exc = load_exceptions(table_path)

    if args.word is not None:
        if not args.pos:
            ap.error("--word needs --pos")
        if args.pos not in eexlib.POS_CODES:
            ap.error("unknown part-of-speech code %r (known: %s)" % (args.pos, ", ".join(eexlib.POS_CODES)))
        record = inflections_record(args.word, args.pos, tuple(args.code), args.countability, exc)
        record["all_forms"] = sorted(all_forms(args.word, args.pos, tuple(args.code), args.countability, exc))
        print(json.dumps(record, indent=2, ensure_ascii=False))
        return 0
    if not args.slugs:
        ap.error("give at least one slug, or --word with --pos")
    return run_slugs(args.slugs, entries_dir, exc, dry_run=args.dry_run, confirm=args.confirm)


if __name__ == "__main__":
    sys.exit(main())
