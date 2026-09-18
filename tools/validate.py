#!/usr/bin/env python3
"""Validate dictionary entries against the schema and the rules of wiki/conventions.md.

    tools/validate.py                      every entry under entries/
    tools/validate.py entries/ba/bank-n.json ...   the named files (or directories)
    tools/validate.py --changed            entries changed since origin/main plus uncommitted ones
    tools/validate.py --all                every entry, plus the duplicate-slug check
    tools/validate.py --gate               --all plus the draft ceiling and cross-reference slug checks
    tools/validate.py --fix-format FILES   rewrite error-free files in the house format
    tools/validate.py --root DIR           validate another repository layout (used by the tests)

Every finding is one line, ``ERROR <path>: <message>`` or ``WARN <path>: <message>``,
followed by ``validate: N files, E errors, W warnings``.  Exit status 1 when
there is at least one error.  ``--quiet`` hides the WARN lines.

The checks, in the order they run for each file: redirect stubs; JSON and
schema (with x-vocabulary); id, slug, path, shard, homograph; sense numbers,
subsense letters, phrase sub_ids, example counts, adaptation word caps,
core_idea; prose (the abbreviation deny list, the inline marks of
wiki/decisions/inline-markup.md, [[slug|text]] link overrides, example
punctuation, an example that does not contain the headword, technical terms
in pronunciation notes); pronunciation; frequency against the defining
vocabulary and the queue; provenance (dates, and the ``reviewed`` rules).
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eexlib  # noqa: E402
import schema_check  # noqa: E402

DENY_LIST = ["sb", "sth", "e.g.", "i.e.", "etc.", "approx.", "vs.", "cf.", "esp.", "usu.", "NB"]
DENY_RE = re.compile(r"(?<![A-Za-z0-9])(?:%s)(?![A-Za-z0-9])" % "|".join(re.escape(t) for t in DENY_LIST), re.IGNORECASE)
LINK_RE = re.compile(r"\[\[([^\]]*)\]\]")
NO_PRONUNCIATION_POS = {"prefix", "suffix", "comb", "abbr"}
ADAPTATION_WORD_CAP = 60
DRAFT_CEILING = 40
EXAMPLE_LIMITS = {"sense": (2, 4), "subsense": (1, 4), "phrase": (1, 3)}
EXAMPLE_ENDINGS = (".", "?", "!", '"', "'", "”", "’")
IPA_FORBIDDEN = "/[]"
# Words a B1 reader cannot follow in a pronunciation note (style guide section 11); the note says the sound in plain words.
PRONUNCIATION_JARGON = ["schwa", "rhotic", "non-rhotic", "diphthong", "monophthong", "fricative", "plosive", "affricate",
                        "glottal", "alveolar", "velar", "bilabial", "labiodental", "aspirated", "unaspirated", "voiced",
                        "voiceless", "unvoiced", "sibilant", "approximant", "allophone", "phoneme"]
JARGON_RE = re.compile(r"(?<![A-Za-z-])(?:%s)(?![A-Za-z])" % "|".join(re.escape(t) for t in PRONUNCIATION_JARGON), re.IGNORECASE)
PRONUNCIATION_PROSE_RE = re.compile(r"^pronunciation\.|\.pronunciation$|^adaptation\.pronunciation$")


def L(value):
    """``value`` if it is a list, else an empty list (schema errors are reported separately)."""
    return value if isinstance(value, list) else []


def D(value):
    """``value`` if it is a dict, else an empty dict."""
    return value if isinstance(value, dict) else {}


class Report:
    """Prints findings and keeps the counts."""

    def __init__(self, quiet=False):
        self.quiet = quiet
        self.errors = 0
        self.warnings = 0

    def error(self, path, message):
        self.errors += 1
        print("ERROR %s: %s" % (path, message))

    def warn(self, path, message):
        self.warnings += 1
        if not self.quiet:
            print("WARN %s: %s" % (path, message))


class Context:
    """Everything loaded once per run: schema, vocabularies, ledgers, and the slugs on disk."""

    def __init__(self, root, report, gate=False):
        self.root = Path(root).resolve()
        self.report = report
        self.gate = gate
        self.schema = eexlib.load_schema(self.root)
        self.vocab = eexlib.load_vocab(self.root)
        self.existing_slugs = {p.stem for p in eexlib.iter_entry_paths(self.root)}
        self.redirects = self._load_redirects()
        self.decisions = self._load_decisions()
        self.defining = self._load_defining_vocabulary()
        self.queue_bands = self._load_queue()
        self.slug_files = {}   # slug field -> [relative paths], for the duplicate check
        self.draft_count = 0

    def rel(self, path):
        try:
            return Path(path).resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def _load_redirects(self):
        path = self.root / "headwords" / "redirects.json"
        if not path.is_file():
            return {}
        try:
            data = eexlib.load_json(path)
        except ValueError as exc:
            self.report.error(self.rel(path), "cannot parse: %s" % exc)
            return {}
        return data if isinstance(data, dict) else {}

    def _load_decisions(self):
        """Counter of (slug, run_id) over the lines of reviews/decisions.jsonl."""
        counts = Counter()
        path = self.root / "reviews" / "decisions.jsonl"
        if not path.is_file():
            return counts
        with open(path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    self.report.warn(self.rel(path), "line %d is not valid JSON" % n)
                    continue
                if isinstance(rec, dict) and rec.get("slug"):
                    counts[(rec.get("slug"), rec.get("run_id"))] += 1
        return counts

    def _load_defining_vocabulary(self):
        path = self.root / "schema" / "defining-vocabulary.txt"
        if not path.is_file():
            return None
        words = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            word = line.split("#", 1)[0].strip().lower()
            if word:
                words.add(word)
        return words

    def _load_queue(self):
        """(headword, pos) -> band from headwords/queue.tsv, if it exists."""
        path = self.root / "headwords" / "queue.tsv"
        bands = {}
        if not path.is_file():
            return bands
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return bands
        header = lines[0].split("\t")
        try:
            hw, pos, band = header.index("headword"), header.index("pos"), header.index("band")
        except ValueError:
            return bands
        for line in lines[1:]:
            cols = line.split("\t")
            if len(cols) > max(hw, pos, band):
                bands[(cols[hw].strip().lower(), cols[pos].strip())] = cols[band].strip()
        return bands


# --------------------------------------------------------------------------
# Redirect stubs
# --------------------------------------------------------------------------

def check_stub(ctx, rel, path, stub):
    err = ctx.report.error
    keys = list(stub.keys())
    if sorted(keys) != sorted(eexlib.REDIRECT_STUB_KEYS):
        err(rel, "a redirect stub must have exactly the keys %s" % ", ".join(eexlib.REDIRECT_STUB_KEYS))
    slug, target = stub.get("slug"), stub.get("redirect_to")
    if slug != path.stem:
        err(rel, "stub slug %r does not equal the file name %r" % (slug, path.stem))
    if not isinstance(target, str) or target not in ctx.existing_slugs:
        err(rel, "redirect_to %r is not an existing entry" % (target,))
    elif not eexlib.entry_path(target, ctx.root).is_file():
        err(rel, "redirect_to %r is not at its expected path" % target)
    if ctx.redirects.get(slug) != target:
        err(rel, "headwords/redirects.json does not map %r to %r" % (slug, target))


# --------------------------------------------------------------------------
# Identity: id, slug, path, shard, homograph
# --------------------------------------------------------------------------

def check_identity(ctx, rel, path, e):
    err, warn = ctx.report.error, ctx.report.warn
    slug, headword, pos, homograph = e.get("slug"), e.get("headword"), e.get("pos"), e.get("homograph")
    if e.get("id") != slug:
        err(rel, "id %r does not equal slug %r" % (e.get("id"), slug))
    if not isinstance(slug, str) or not eexlib.SLUG_RE.match(slug):
        return
    if pos in eexlib.POS_CODES and isinstance(headword, str) and isinstance(homograph, int) and homograph >= 1:
        try:
            expected = eexlib.slugify(headword, pos, homograph)
        except ValueError as exc:
            err(rel, "cannot derive a slug: %s" % exc)
            expected = None
        if expected and expected != slug:
            err(rel, "slug %r should be %r (from headword %r, pos %r, homograph %s)" % (slug, expected, headword, pos, homograph))

    # File path and shard.
    resolved = path.resolve()
    entries_dir = ctx.root / "entries"
    if entries_dir in resolved.parents:
        if resolved != eexlib.entry_path(slug, ctx.root):
            err(rel, "file should be at %s" % eexlib.relative_entry_path(slug))
            if resolved.parent.name != eexlib.shard(slug):
                err(rel, "shard directory should be %r, not %r" % (eexlib.shard(slug), resolved.parent.name))
    else:
        warn(rel, "not under entries/, so the path and shard checks were skipped")

    # Homograph number against the slug and the earlier homographs.
    if isinstance(homograph, int) and homograph >= 1:
        try:
            head, slug_pos, slug_homograph = eexlib.parse_slug(slug)
        except ValueError:
            return
        if homograph > 1 and not slug.endswith("-%d" % homograph):
            err(rel, "homograph %d but the slug does not end in -%d" % (homograph, homograph))
        if homograph == 1 and slug_homograph != 1:
            err(rel, "homograph 1 but the slug ends in a numeric suffix")
        if homograph > 1:
            missing = [s for s in [eexlib.slugify(head, slug_pos, k) for k in range(1, homograph)] if s not in ctx.existing_slugs]
            if missing:
                warn(rel, "earlier homograph entries do not exist: %s" % ", ".join(missing))


# --------------------------------------------------------------------------
# Structure: numbering, sub_ids, example counts, adaptation caps, core_idea
# --------------------------------------------------------------------------

def check_examples(ctx, rel, where, kind, examples):
    low, high = EXAMPLE_LIMITS[kind]
    n = len(L(examples))
    if not low <= n <= high:
        ctx.report.error(rel, "%s has %d example%s; a %s needs %d to %d" % (where, n, "" if n == 1 else "s", kind, low, high))


def check_adaptation(ctx, rel, where, adaptation):
    for kind, text in D(adaptation).items():
        if isinstance(text, str) and eexlib.word_count(text) > ADAPTATION_WORD_CAP:
            ctx.report.error(rel, "%s.%s has %d words; the cap is %d" % (where, kind, eexlib.word_count(text), ADAPTATION_WORD_CAP))


def check_structure(ctx, rel, e):
    err, warn = ctx.report.error, ctx.report.warn
    senses = L(e.get("senses"))
    for i, sense in enumerate(senses):
        sense = D(sense)
        where = "senses[%d]" % i
        if sense.get("n") != i + 1:
            err(rel, "%s.n is %r; senses are numbered 1, 2, 3 in order" % (where, sense.get("n")))
        check_examples(ctx, rel, where, "sense", sense.get("examples"))
        check_adaptation(ctx, rel, where + ".adaptation", sense.get("adaptation"))
        for j, sub in enumerate(L(sense.get("subsenses"))):
            sub = D(sub)
            sub_where = "%s.subsenses[%d]" % (where, j)
            expected = chr(ord("a") + j) if j < 26 else None
            if sub.get("letter") != expected:
                err(rel, "%s.letter is %r; subsenses are lettered a, b, c in order" % (sub_where, sub.get("letter")))
            check_examples(ctx, rel, sub_where, "subsense", sub.get("examples"))

    seen = {}
    for i, phrase in enumerate(L(e.get("phrases"))):
        phrase = D(phrase)
        where = "phrases[%d]" % i
        sub_id, text = phrase.get("sub_id"), phrase.get("text")
        if isinstance(text, str) and text.strip():
            try:
                expected = eexlib.phrase_sub_id(text)
            except ValueError:
                expected = None
            if expected != sub_id:
                err(rel, "%s.sub_id is %r; the text %r gives %r" % (where, sub_id, text, expected))
        if sub_id in seen:
            err(rel, "%s.sub_id %r is also used by phrases[%d]" % (where, sub_id, seen[sub_id]))
        seen.setdefault(sub_id, i)
        check_examples(ctx, rel, where, "phrase", phrase.get("examples"))
        check_adaptation(ctx, rel, where + ".adaptation", phrase.get("adaptation"))

    check_adaptation(ctx, rel, "adaptation", e.get("adaptation"))

    core = e.get("core_idea")
    if core is None and len(senses) >= 3:
        warn(rel, "core_idea is null but the entry has %d senses" % len(senses))
    if isinstance(core, str) and len(senses) == 1:
        err(rel, "core_idea is set but the entry has only one sense")


# --------------------------------------------------------------------------
# Prose: deny list, link overrides, example punctuation
# --------------------------------------------------------------------------

def check_prose(ctx, rel, e):
    err, warn = ctx.report.error, ctx.report.warn
    forms = [] if e.get("pos") in eexlib.AFFIX_POS else eexlib.own_forms(e)
    for field, text in eexlib.iter_prose(e):
        reported = set()
        for m in DENY_RE.finditer(text):
            token = m.group(0)
            if token.lower() not in reported:
                reported.add(token.lower())
                err(rel, "%s: abbreviation %r is not allowed in prose" % (field, token))
        for message in eexlib.markup_errors(text, field):
            err(rel, "%s: %s" % (field, message))
        for m in LINK_RE.finditer(text):
            inner = m.group(1)
            if "|" not in inner:
                err(rel, "%s: link override %r must have the form [[slug|visible text]]" % (field, m.group(0)))
                continue
            slug, visible = inner.split("|", 1)
            if not eexlib.SLUG_RE.match(slug):
                err(rel, "%s: link override target %r is not a well-formed slug" % (field, slug))
            elif slug not in ctx.existing_slugs:
                warn(rel, "%s: link override target %r has no entry" % (field, slug))
            if "*" in visible:
                err(rel, "%s: a link override carries no mark inside it: %r" % (field, m.group(0)))
        if eexlib.EXAMPLE_TEXT_FIELD.search(field):
            if not text.rstrip().endswith(EXAMPLE_ENDINGS):
                warn(rel, "%s: example does not end in . ? ! or a closing quote" % field)
            explicit = any(kind == "b" for kind, _i, _s, _e in eexlib.iter_markup(text))
            if forms and not explicit and not eexlib.contains_form(text, forms):
                warn(rel, "%s: example contains neither the headword nor a listed form (mark an irregular or separated form with **...**)" % field)
        if PRONUNCIATION_PROSE_RE.search(field):
            for m in JARGON_RE.finditer(text):
                token = m.group(0)
                if token.lower() not in reported:
                    reported.add(token.lower())
                    err(rel, "%s: %r is a technical term; say the sound in plain words (style guide section 11)" % (field, token))


# --------------------------------------------------------------------------
# Pronunciation
# --------------------------------------------------------------------------

def iter_ipa(e):
    """Yield (field, ipa) for every transcription in the entry."""
    pron = D(e.get("pronunciation"))
    for side in ("american", "british"):
        if isinstance(pron.get(side), dict):
            yield "pronunciation.%s.ipa" % side, pron[side].get("ipa")
    for i, v in enumerate(L(pron.get("variants"))):
        yield "pronunciation.variants[%d].ipa" % i, D(v).get("ipa")
    for i, sense in enumerate(L(e.get("senses"))):
        sp = D(D(sense).get("pronunciation"))
        for side in ("american", "british"):
            if isinstance(sp.get(side), dict):
                yield "senses[%d].pronunciation.%s.ipa" % (i, side), sp[side].get("ipa")


def check_pronunciation(ctx, rel, e):
    err, warn = ctx.report.error, ctx.report.warn
    pron = D(e.get("pronunciation"))
    if e.get("pos") not in NO_PRONUNCIATION_POS:
        for side in ("american", "british"):
            if pron.get(side) is None:
                err(rel, "pronunciation.%s is null; only prefix, suffix, comb, and abbr may omit it" % side)
    for field, ipa in iter_ipa(e):
        if not isinstance(ipa, str):
            continue
        bad = sorted(set(ch for ch in ipa if ch in IPA_FORBIDDEN))
        if bad:
            err(rel, "%s: must not contain %s" % (field, " ".join(bad)))
        if "." in ipa and "ˈ" not in ipa:
            warn(rel, "%s: has syllable breaks but no primary stress mark ˈ" % field)


# --------------------------------------------------------------------------
# Frequency
# --------------------------------------------------------------------------

def check_frequency(ctx, rel, e):
    warn = ctx.report.warn
    freq = D(e.get("frequency"))
    headword = e.get("headword") if isinstance(e.get("headword"), str) else ""
    if freq.get("defining_vocabulary") is True and ctx.defining is not None and headword.lower() not in ctx.defining:
        warn(rel, "frequency.defining_vocabulary is true but %r is not in schema/defining-vocabulary.txt" % headword)
    queued = ctx.queue_bands.get((headword.lower(), e.get("pos")))
    if queued is not None and str(freq.get("band")) != queued:
        warn(rel, "frequency.band %r differs from the queue band %r" % (freq.get("band"), queued))


# --------------------------------------------------------------------------
# Provenance
# --------------------------------------------------------------------------

def count_blocking(review_file):
    """The number of blocking issues in a review file (None if it cannot be read)."""
    try:
        data = eexlib.load_json(review_file)
    except (OSError, ValueError):
        return None
    n = 0
    for reviewer in L(D(data).get("reviewers")):
        for verdict in L(D(reviewer).get("verdicts")):
            if D(verdict).get("verdict") == "issue" and D(verdict).get("severity") == "blocking":
                n += 1
    return n


def check_provenance(ctx, rel, e):
    err = ctx.report.error
    prov = D(e.get("provenance"))
    created, modified = prov.get("created"), prov.get("modified")
    if isinstance(created, str) and isinstance(modified, str) and modified < created:
        err(rel, "provenance.modified %s is earlier than created %s" % (modified, created))
    if prov.get("status") == "draft":
        ctx.draft_count += 1
    if prov.get("status") != "reviewed":
        return

    flags = set(f for f in L(prov.get("flags")) if isinstance(f, str))
    pron = D(e.get("pronunciation"))
    for side in ("american", "british"):
        tr = pron.get(side)
        if isinstance(tr, dict) and tr.get("status") != "verified" and "pronunciation-%s" % tr.get("status") not in flags:
            err(rel, "reviewed entry: pronunciation.%s.status is %r and provenance.flags has no matching pronunciation flag" % (side, tr.get("status")))
    infl = D(e.get("inflections"))
    if infl.get("status") != "verified" and "inflection-%s" % infl.get("status") not in flags:
        err(rel, "reviewed entry: inflections.status is %r and provenance.flags has no matching inflection flag" % infl.get("status"))

    reviews = [D(r) for r in L(prov.get("reviews"))]
    roles = set(r.get("role") for r in reviews)
    if len(reviews) < 2 or len(roles) < 2:
        err(rel, "reviewed entry: provenance.reviews needs at least two records with distinct roles")
    for i, rec in enumerate(reviews):
        file = rec.get("file")
        review_path = ctx.root / file if isinstance(file, str) else None
        if review_path is None or not review_path.is_file():
            err(rel, "provenance.reviews[%d].file %r does not exist" % (i, file))
            continue
        blocking = count_blocking(review_path)
        if blocking is None:
            err(rel, "provenance.reviews[%d].file %r cannot be read as JSON" % (i, file))
            continue
        decided = ctx.decisions.get((e.get("slug"), rec.get("run_id")), 0)
        if decided < blocking:
            err(rel, "provenance.reviews[%d]: %d blocking issue%s but only %d decision line%s for run %r in reviews/decisions.jsonl"
                % (i, blocking, "" if blocking == 1 else "s", decided, "" if decided == 1 else "s", rec.get("run_id")))


# --------------------------------------------------------------------------
# Cross-reference slugs (--gate)
# --------------------------------------------------------------------------

def iter_crossref_slugs(e):
    for i, item in enumerate(L(e.get("word_family"))):
        yield "word_family[%d].slug" % i, D(item).get("slug")
    for i, item in enumerate(L(e.get("see_also"))):
        yield "see_also[%d].slug" % i, D(item).get("slug")
    for i, sense in enumerate(L(e.get("senses"))):
        for kind in ("synonyms", "antonyms", "compare"):
            for j, item in enumerate(L(D(sense).get(kind))):
                yield "senses[%d].%s[%d].slug" % (i, kind, j), D(item).get("slug")
    for i, slug in enumerate(L(D(e.get("synonym_discrimination")).get("words"))):
        yield "synonym_discrimination.words[%d]" % i, slug


def check_crossref_slugs(ctx, rel, e):
    for field, slug in iter_crossref_slugs(e):
        try:
            eexlib.parse_slug(slug)
        except ValueError as exc:
            ctx.report.error(rel, "%s: %s" % (field, exc))


# --------------------------------------------------------------------------
# One file
# --------------------------------------------------------------------------

def check_file(ctx, path, fix_format=False):
    """Run every check on one file; format it afterwards if asked and error-free."""
    rel = ctx.rel(path)
    before = ctx.report.errors
    try:
        data = eexlib.load_json(path)
    except (OSError, ValueError) as exc:
        ctx.report.error(rel, "cannot parse JSON: %s" % exc)
        return
    if not isinstance(data, dict):
        ctx.report.error(rel, "the top level must be a JSON object")
        return

    if eexlib.is_redirect_stub(data):
        check_stub(ctx, rel, path, data)
        order = {k: {} for k in eexlib.REDIRECT_STUB_KEYS}
    else:
        for field, message in schema_check.validate(data, ctx.schema, ctx.vocab):
            ctx.report.error(rel, "schema: %s: %s" % (field, message))
        if isinstance(data.get("slug"), str):
            ctx.slug_files.setdefault(data["slug"], []).append(rel)
        check_identity(ctx, rel, path, data)
        check_structure(ctx, rel, data)
        check_prose(ctx, rel, data)
        check_pronunciation(ctx, rel, data)
        check_frequency(ctx, rel, data)
        check_provenance(ctx, rel, data)
        if ctx.gate:
            check_crossref_slugs(ctx, rel, data)
        order = eexlib.schema_key_order(ctx.schema)

    if fix_format:
        if ctx.report.errors > before:
            print("skipped %s: not formatted because it has errors" % rel)
            return
        text = eexlib.dumps_json(eexlib._reorder(data, order))
        if text != path.read_text(encoding="utf-8"):
            path.write_text(text, encoding="utf-8")
            print("formatted %s" % rel)


# --------------------------------------------------------------------------

def collect_paths(ctx, args):
    if args.gate or args.all or (not args.paths and not args.changed):
        return eexlib.iter_entry_paths(ctx.root)
    paths = []
    if args.changed:
        try:
            paths.extend(eexlib.changed_entry_paths(root=ctx.root))
        except RuntimeError as exc:
            ctx.report.error("entries/", "--changed needs a git checkout: %s" % exc)
    for p in args.paths:
        p = Path(p)
        if not p.is_absolute() and (ctx.root / p).exists():
            p = ctx.root / p  # a relative path names a place under --root
        if p.is_dir():
            paths.extend(sorted(q for q in p.rglob("*.json") if q.is_file()))
        else:
            paths.append(p)
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate dictionary entries (schema, vocabularies, and the rules of wiki/conventions.md).")
    parser.add_argument("paths", nargs="*", help="entry files or directories (default: every entry under entries/)")
    parser.add_argument("--all", action="store_true", help="every entry under entries/, plus the duplicate-slug check")
    parser.add_argument("--changed", action="store_true", help="entries changed since origin/main plus uncommitted changes")
    parser.add_argument("--gate", action="store_true", help="--all plus the draft ceiling and cross-reference slug checks")
    parser.add_argument("--fix-format", action="store_true", help="rewrite error-free files with keys in schema order")
    parser.add_argument("--quiet", action="store_true", help="hide WARN lines (they are still counted)")
    parser.add_argument("--root", default=None, help="repository root (default: the parent of tools/)")
    args = parser.parse_args(argv)

    if args.root:
        eexlib.set_root(args.root)
    report = Report(quiet=args.quiet)
    ctx = Context(eexlib.get_root(), report, gate=args.gate)

    paths = collect_paths(ctx, args)
    for path in paths:
        if not path.is_file():
            report.error(ctx.rel(path), "no such file")
            continue
        check_file(ctx, path, fix_format=args.fix_format)

    if args.all or args.gate:
        for slug, files in sorted(ctx.slug_files.items()):
            if len(files) > 1:
                report.error("entries/", "slug %r appears in %d files: %s" % (slug, len(files), ", ".join(files)))
    if args.gate and ctx.draft_count > DRAFT_CEILING:
        report.error("entries/", "%d entries have status draft; the ceiling is %d" % (ctx.draft_count, DRAFT_CEILING))

    print("validate: %d files, %d errors, %d warnings" % (len(paths), report.errors, report.warnings))
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
