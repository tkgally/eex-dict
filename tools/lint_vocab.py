#!/usr/bin/env python3
"""Defining-vocabulary linter (wiki/decisions/defining-vocabulary-rule.md).

    python3 tools/lint_vocab.py [files|slugs]        # check the given entries
    python3 tools/lint_vocab.py --all                # every entry (the default with no files)
    python3 tools/lint_vocab.py --changed --gate     # CI: exit 1 on a definition violation in a changed entry
    python3 tools/lint_vocab.py --all --queue        # queue every out-of-vocabulary definition lemma (closure)
    python3 tools/lint_vocab.py --json ...           # machine-readable summary on stdout

Every word of a definition (core_idea, senses[].definition, subsenses[].definition,
phrases[].definition) is lemmatized and must be in schema/defining-vocabulary.txt
or be the headword of an existing entry; anything else is a VIOLATION.  The same
test on explanations, examples, collocations, notes and adaptation fields gives a
WARN, summarized per entry.  The first sense of a defining-vocabulary word is not
held to the list (style guide section 2): its out-of-vocabulary lemmas are printed
as warnings, still queued by --queue, and never fail --gate.

The form->lemma map is built once from every entry's headword, variants[].form
and inflections.forms, from schema/inflection-exceptions.json when it exists
(tools/inflect.py is used when importable), and last from rules for single
tokens (-s/-es/-ies, -ed/-ied, -ing, -er/-est) whose result counts only when it
is a vocabulary word or a known headword; otherwise the token itself is the lemma.
``Lemmatizer`` is also what tools/link_words.py picks up.  Standard library only.
"""

import argparse
import importlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

NAMES = frozenset("kim mari sam ana lee omar yuki ravi sara".split())
CLITICS = frozenset(["n't", "'s", "'re", "'ve", "'ll", "'d", "'m"])
CONTRACTIONS = {"can't": "can", "won't": "will", "shan't": "shall", "ain't": None}
# The forms of the three grammatical verbs, so the linter reads definitions before the inflection
# tables exist; schema/inflection-exceptions.json and the entries' own forms are consulted first.
BUILTIN_FORMS = {"am": "be", "is": "be", "are": "be", "was": "be", "were": "be", "been": "be", "being": "be",
                 "has": "have", "had": "have", "having": "have", "does": "do", "did": "do", "done": "do",
                 "doing": "do", "cannot": "can"}
LATIN_RE = re.compile(r"^[a-z'-]+$")

DEFINITION_FIELD_RE = re.compile(
    r"^(core_idea|senses\[\d+\]\.definition|senses\[\d+\]\.subsenses\[\d+\]\.definition|phrases\[\d+\]\.definition)$")
# The phrase itself is a headword-like object; an incorrect learner sentence is wrong on purpose.
SKIP_FIELD_RE = re.compile(r"^(phrases\[\d+\]\.text|learner_errors\[\d+\]\.incorrect)$")
FIRST_SENSE = "senses[0].definition"

VERB_KINDS = frozenset(["third_person_singular", "past_tense", "past_participle", "present_participle"])
ADJ_KINDS = frozenset(["comparative", "superlative"])
NOUN_KINDS = frozenset(["plural"])
META_KEYS = frozenset("pos note notes source regular status kind region comment reason slug id band checked".split())
LEMMA_KEYS = ("headword", "lemma", "base", "word")

# A word token: letters/digits with internal apostrophes and hyphens, optionally an affix hyphen at either end.
TOKEN_RE = re.compile(r"-?[^\W_]+(?:['’][^\W_]+)*(?:-[^\W_]+(?:['’][^\W_]+)*)*-?")
OVERRIDE_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]")


def _norm(text):
    """Lowercase, straight apostrophe, accents folded, surrounding space removed."""
    s = str(text).lower().replace("’", "'").replace("‘", "'")
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).strip()


def load_defining_vocabulary(path):
    """The lemmas of a defining-vocabulary file: one per line, ``#`` comments and blanks ignored."""
    out = set()
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for line in lines:
        line = line.split("#", 1)[0] if line.lstrip().startswith("#") or " #" in line else line
        word = _norm(line)
        if word:
            out.add(word)
    return out


# --------------------------------------------------------------------------
# Form tables: entries, schema/inflection-exceptions.json, tools/inflect.py
# --------------------------------------------------------------------------

def _kind_of(key):
    """The inflection kind named by a table key, or None for a key that names no kind."""
    k = str(key).lower()
    if "plural" in k:
        return "plural"
    if "compar" in k:
        return "comparative"
    if "superl" in k:
        return "superlative"
    if "present" in k or "gerund" in k or k.endswith("ing"):
        return "present_participle"
    if "participle" in k:
        return "past_participle"
    if "past" in k or "preterite" in k:
        return "past_tense"
    if "third" in k or "3" in k or "singular" in k:
        return "third_person_singular"
    return None


def _add_form(table, form, lemma, kind):
    form, lemma = _norm(form), _norm(lemma)
    if not form or not lemma or form == lemma:
        return
    entries = table.setdefault(form, [])
    if all(entry[0] != lemma for entry in entries):
        entries.append((lemma, kind))


def _lemma_of_key(key):
    """``go-v`` -> ``go``, ``give-up-phrv`` -> ``give up``, ``mouse`` -> ``mouse``."""
    try:
        return eexlib.parse_slug(str(key))[0].replace("-", " ")
    except ValueError:
        return str(key)


def harvest_forms(obj, lemma, table, depth=0):
    """Read form->lemma pairs out of ``obj`` in any reasonable table shape into ``table``.

    Accepted shapes, mixed freely: ``{"go": {"past_tense": "went"}}``, ``{"went": "go"}``,
    ``{"go": ["went", "gone"]}``, ``{"v": {"go": {...}}}``, ``{"go-v": {...}}``,
    ``[{"headword": "go", "past": "went"}]``, and ``{"forms": {...}}`` under a lemma.
    """
    if depth > 8:
        return
    if isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            if isinstance(item, str):
                if lemma:
                    _add_form(table, item, lemma, None)
            else:
                harvest_forms(item, lemma, table, depth + 1)
        return
    if not isinstance(obj, dict):
        return
    for k in LEMMA_KEYS:
        if isinstance(obj.get(k), str):
            lemma = obj[k]
            break
    for key, val in obj.items():
        key = str(key)
        if key.startswith("_") or key in META_KEYS or key in LEMMA_KEYS:
            continue
        kind = _kind_of(key)
        if kind and lemma and isinstance(val, (str, list, tuple)):
            for form in (val if isinstance(val, (list, tuple)) else [val]):
                if isinstance(form, str):
                    _add_form(table, form, lemma, kind)
        elif isinstance(val, (dict, list, tuple)):
            keep = kind or key in ("forms", "inflections", "exceptions") or key in eexlib.POS_CODES
            harvest_forms(val, lemma if keep else _lemma_of_key(key), table, depth + 1)
        elif isinstance(val, str) and not kind:
            _add_form(table, key, val, None)


def _call_first(fn, arg_lists):
    """``fn(*args)`` for the first argument list that works and returns something, else None."""
    if not callable(fn):
        return None
    for args in arg_lists:
        try:
            result = fn(*args)
        except Exception:  # noqa: BLE001 - an unknown signature or a failing table is not our problem
            continue
        if result is not None:
            return result
    return None


def _import_inflect(root):
    """tools/inflect.py of ``root`` as a module, or None when it is absent or does not import."""
    tools = Path(root) / "tools"
    if not (tools / "inflect.py").is_file():
        return None
    try:
        if str(tools) not in sys.path:
            sys.path.insert(0, str(tools))
        return importlib.import_module("inflect")
    except Exception:  # noqa: BLE001 - a half-written module must not stop the linter
        return None


def headword_index(root=None):
    """slug -> (headword, pos, inflections.forms, [variant forms]) for every non-stub entry."""
    out = {}
    for path in eexlib.iter_entry_paths(root):
        try:
            entry = eexlib.load_json(path)
        except (OSError, ValueError):
            continue
        if not isinstance(entry, dict) or eexlib.is_redirect_stub(entry):
            continue
        headword = entry.get("headword")
        if not isinstance(headword, str) or not headword.strip():
            continue
        forms = (entry.get("inflections") or {}).get("forms") if isinstance(entry.get("inflections"), dict) else {}
        variants = [v.get("form") for v in (entry.get("variants") or []) if isinstance(v, dict) and isinstance(v.get("form"), str)]
        out[entry.get("slug") or path.stem] = (headword, entry.get("pos"), forms if isinstance(forms, dict) else {}, variants)
    return out


def rule_candidates(word):
    """Possible base forms of a single token by suffix rules, most likely first, as (candidate, kind).

    Over-generation is harmless: the caller keeps a candidate only when it is a
    vocabulary word or a known headword.  Adverbs in -ly are separate lemmas.
    """
    out = []

    def add(cand, kind):
        if cand and len(cand) >= 2 and all(cand != c for c, _ in out):
            out.append((cand, kind))

    def stem_variants(stem, kind):
        # A stem ending vowel+consonant usually lost a final e (hoping -> hope, used -> use);
        # otherwise the bare stem is likelier (singing -> sing, being -> be, opened -> open).
        prefer_e = len(stem) >= 2 and stem[-1] not in "aeiouy" and stem[-2] in "aeiou"
        first, second = (stem + "e", stem) if prefer_e else (stem, stem + "e")
        add(first, kind)
        add(second, kind)
        if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            add(stem[:-1], kind)

    n = len(word)
    if word.endswith("ies") and n > 4:
        add(word[:-3] + "y", None)
    if word.endswith("es") and n > 3:
        add(word[:-1], None)
        add(word[:-2], None)
    elif word.endswith("s") and not word.endswith("ss") and n > 2:
        add(word[:-1], None)
    if word.endswith("ied") and n > 4:
        add(word[:-3] + "y", "past_tense")
    if word.endswith("ed") and n > 3:
        stem_variants(word[:-2], "past_tense")
    if word.endswith("ying") and n > 4:
        add(word[:-4] + "ie", "present_participle")
    if word.endswith("ing") and n > 4:
        stem_variants(word[:-3], "present_participle")
    if word.endswith("ier") and n > 4:
        add(word[:-3] + "y", "comparative")
    if word.endswith("er") and n > 3:
        stem_variants(word[:-2], "comparative")
    if word.endswith("iest") and n > 5:
        add(word[:-4] + "y", "superlative")
    if word.endswith("est") and n > 4:
        stem_variants(word[:-3], "superlative")
    return out


class Lemmatizer:
    """form -> lemma over the defining vocabulary, the entries and the exception tables, built once.

    ``headwords`` None means scan the repository's entries; otherwise it is the
    set of known headwords (tools/link_words.py passes its own).  ``root`` and
    ``dv`` override the repository root and the defining-vocabulary file.
    Public: ``known`` (headwords), ``vocabulary``, ``forms``, ``lemmatize``, ``candidates``.
    """

    def __init__(self, headwords=None, root=None, dv=None):
        self.root = Path(root).resolve() if root else eexlib.ROOT
        self.dv_path = Path(dv) if dv else self.root / "schema" / "defining-vocabulary.txt"
        self.vocabulary = load_defining_vocabulary(self.dv_path)
        self.known = set()
        self.forms = {}
        self.index = {}
        if headwords is None:
            self.index = headword_index(self.root)
            for headword, _pos, forms, variants in self.index.values():
                self.known.add(_norm(headword))
                for kind, form in forms.items():
                    if isinstance(form, str):
                        _add_form(self.forms, form, headword, kind if kind in VERB_KINDS | ADJ_KINDS | NOUN_KINDS else None)
                for form in variants:
                    _add_form(self.forms, form, headword, "variant")
        else:
            self.known.update(_norm(h) for h in headwords if isinstance(h, str) and _norm(h))
        self._load_tables()
        for form, lemma in BUILTIN_FORMS.items():
            _add_form(self.forms, form, lemma, None)
        self.phrases = {p for p in (self.vocabulary | self.known | set(self.forms)) if " " in p}
        self.phrase_first = {p.split(" ", 1)[0] for p in self.phrases}
        self.max_phrase = max((p.count(" ") + 1 for p in self.phrases), default=1)

    def _load_tables(self):
        exc_path = self.root / "schema" / "inflection-exceptions.json"
        raw = None
        if exc_path.is_file():
            try:
                raw = eexlib.load_json(exc_path)
            except (OSError, ValueError):
                raw = None
        if raw is not None:
            nouns = raw.get("nouns") if isinstance(raw, dict) else None
            if isinstance(nouns, dict):                  # key = singular, value = plural(s); the generic
                for singular, val in nouns.items():      # harvester would read a string value backwards
                    if singular.startswith("_"):
                        continue
                    plurals = []
                    if isinstance(val, str):
                        plurals = [val]
                    elif isinstance(val, (list, tuple)):
                        plurals = [x for x in val if isinstance(x, str)]
                    elif isinstance(val, dict):
                        plurals = [x for x in [val.get("plural")] + list(val.get("also") or []) if isinstance(x, str)]
                    for form in plurals:
                        _add_form(self.forms, form, singular, "plural")
                for section, kinds in (("verbs", ("third_person_singular", "past_tense", "past_participle", "present_participle")),
                                       ("adjectives", ("comparative", "superlative")), ("adverbs", ("comparative", "superlative"))):
                    sec = raw.get(section)
                    if not isinstance(sec, dict):
                        continue
                    for base, d in sec.items():          # key = base form, value = its irregular forms
                        if base.startswith("_") or not isinstance(d, dict):
                            continue
                        for kind in kinds:
                            form = d.get(kind)
                            if isinstance(form, str) and form:
                                _add_form(self.forms, form, base, kind)
                        for form in d.get("also") or []:
                            if isinstance(form, str):
                                _add_form(self.forms, form, base, None)
                # the spelling lists (doubling, single_l, ...) hold bases, not forms: nothing to harvest
            else:
                harvest_forms(raw, None, self.forms)
        inflect = _import_inflect(self.root)
        if inflect is None:
            return
        loaded = _call_first(getattr(inflect, "load_exceptions", None), [(), (exc_path,), (self.root,)])
        # the table itself was harvested section by section above; inflect's loader returns the same table
        all_forms = getattr(inflect, "all_forms", None)
        failures = 0
        for slug, (headword, pos, forms, _variants) in self.index.items():
            if any(isinstance(f, str) and f for f in forms.values()) or not callable(all_forms) or failures >= 3:
                continue
            result = _call_first(all_forms, [(headword, pos), (headword, pos, loaded), (slug,)])
            if result is None:
                failures += 1
            else:
                harvest_forms(result, headword, self.forms)

    # -- lookups -----------------------------------------------------------

    def is_lemma(self, word):
        """True for a vocabulary word, a known headword (an affix matches with or without its
        hyphen), or a transparent derivative of a vocabulary word (decisions/defining-vocabulary-rule)."""
        return word in self.vocabulary or word in self.known or (
            "-" not in word and (word + "-" in self.vocabulary or "-" + word in self.vocabulary))

    PREFIXES = ("un", "non")
    SUFFIXES = ("ly", "ness", "ful", "less", "able", "ish", "ment", "ed", "ing", "er", "est", "ous")

    def _base_listed(self, base):
        return base in self.vocabulary or base in self.known

    def transparent_derivative(self, word):
        """The listed base of a transparently derived word (politely, unkind, unpleasantness,
        successful, enjoyable, careless, childish), else None. One prefix and up to two
        suffixes; spelling changes reversed (happily, reliable, running, hoped)."""
        if len(word) < 4 or " " in word or "-" in word:
            return None
        stems = [word]
        for pre in self.PREFIXES:
            if word.startswith(pre) and len(word) - len(pre) >= 3:
                stems.append(word[len(pre):])
        for stem in list(stems):
            if self._base_listed(stem) and stem != word:
                return stem
            for suf in self.SUFFIXES:
                if not stem.endswith(suf) or len(stem) - len(suf) < 3:
                    continue
                cut = stem[: -len(suf)]
                bases = [cut, cut + "e"]
                if suf == "ly":
                    bases.append(cut + "le")                 # sensibly, simply, gently
                if suf == "ly" and cut.endswith("i"):
                    bases.append(cut[:-1] + "y")
                elif cut.endswith("i"):
                    bases.append(cut[:-1] + "y")
                if len(cut) >= 3 and cut[-1] == cut[-2] and cut[-1] not in "aeiou":
                    bases.append(cut[:-1])
                if suf == "ly" and cut.endswith("al"):
                    bases.append(cut[:-2])
                for base in bases:
                    if self._base_listed(base):
                        return base
                    # a second suffix: unpleasantness, carelessly, hopefully
                    for suf2 in ("ful", "less", "ness", "able", "ous", "ish", "ing", "ed", "al"):
                        if base.endswith(suf2) and len(base) - len(suf2) >= 2:
                            inner = base[: -len(suf2)]
                            for b2 in (inner, inner + "e", inner[:-1] if len(inner) >= 3 and inner[-1] == inner[-2] else inner):
                                if self._base_listed(b2):
                                    return b2
        return None

    def resolve(self, token):
        """[(lemma, kind), ...] for one normalized token: itself when it is a lemma, then listed
        forms, then rule candidates that are lemmas.  Empty when nothing is known about it."""
        out = []
        if self.is_lemma(token):
            out.append((token, None))
        for lemma, kind in self.forms.get(token, ()):
            if all(lemma != seen for seen, _ in out):
                out.append((lemma, kind))
        for cand, kind in rule_candidates(token):
            if self.is_lemma(cand) and all(cand != seen for seen, _ in out):
                out.append((cand, kind))
        if not out and self.transparent_derivative(token) is not None:
            out.append((token, "derivative"))       # politely, unkind: listed base plus a transparent affix
        return out

    def candidates(self, token):
        """The lemmas ``token`` may be a form of, likeliest first; ``[token]`` when none is known."""
        token = _norm(token)
        return [lemma for lemma, _ in self.resolve(token)] or [token]

    def lemmatize(self, token):
        """The likeliest lemma of ``token`` (the token itself when nothing is known)."""
        return self.candidates(token)[0]

    def parts(self, token):
        """A hyphenated token whole when it is known, else its parts; other tokens as they are."""
        if self.is_lemma(token) or token in self.forms:
            return [token]
        bare = token.strip("-")
        if "-" not in bare:
            return [bare]
        if self.is_lemma(bare) or bare in self.forms or self.resolve(bare):
            return [bare]
        return [p for p in bare.split("-") if p]

    def match_phrase(self, tokens, i):
        """The number of tokens at ``i`` that form a known multi-word lemma or form, else 0."""
        heads = [tokens[i]] + [lemma for lemma, _ in self.resolve(tokens[i])]
        if not any(h in self.phrase_first for h in heads):
            return 0
        for length in range(min(self.max_phrase, len(tokens) - i), 1, -1):
            rest = " ".join(tokens[i + 1:i + length])
            for head in heads:
                gram = head + " " + rest
                if gram in self.phrases or gram in self.forms:
                    return length
        return 0

    def own_tokens(self, entry):
        """The normalized words of an entry's headword, inflected forms and variants (skipped in its prose)."""
        words = [entry.get("headword") or ""]
        forms = (entry.get("inflections") or {}).get("forms") if isinstance(entry.get("inflections"), dict) else None
        words.extend(f for f in (forms or {}).values() if isinstance(f, str))
        words.extend(v.get("form") for v in (entry.get("variants") or []) if isinstance(v, dict) and isinstance(v.get("form"), str))
        return {w for text in words for w in _norm(text).split() if w}


# --------------------------------------------------------------------------
# Tokens and checks
# --------------------------------------------------------------------------

def _override_text(match):
    slug, text = match.group(1).strip(), match.group(2)
    if text is not None and text.strip():
        return text
    try:
        return eexlib.parse_slug(slug)[0].replace("-", " ")
    except ValueError:
        return slug.replace("-", " ")


def tokenize(text):
    """The checkable word tokens of a prose field, normalized: overrides replaced by their visible
    text, possessives and clitics dropped, digits, single letters and example names skipped."""
    text = OVERRIDE_RE.sub(_override_text, eexlib.strip_markup(str(text)))
    out = []
    for tok in TOKEN_RE.findall(text):
        tok = _norm(tok)
        if any(ch.isdigit() for ch in tok):
            continue
        if tok in CONTRACTIONS:
            tok = CONTRACTIONS[tok]
        elif "'" in tok:
            head, clitic = (tok[:-3], "n't") if tok.endswith("n't") else tok.rsplit("'", 1)
            if clitic == "n't" or "'" + clitic in CLITICS:
                tok = head
        if not tok or len(tok.strip("-")) < 2 or tok in NAMES or not LATIN_RE.match(tok):
            continue
        out.append(tok)
    return out


def out_of_vocabulary(lem, text, skip=frozenset()):
    """[(lemma, kind), ...] for every token of ``text`` that is neither a vocabulary word nor a known
    headword, nor a form of one.  ``kind`` says how the lemma was reached (None when unknown)."""
    tokens = tokenize(text)
    out = []
    i = 0
    while i < len(tokens):
        n = lem.match_phrase(tokens, i)
        if n:
            i += n
            continue
        for part in lem.parts(tokens[i]):
            if part in skip or len(part) < 2:
                continue
            found = lem.resolve(part)
            if not found:
                kind = "past_tense" if part.endswith("ed") else "present_participle" if part.endswith("ing") else None
                out.append((part, kind))
            elif not any(lem.is_lemma(lemma) or kind == "derivative" for lemma, kind in found):
                out.append(found[0])
        i += 1
    return out


def check_entry(lem, entry):
    """Check one entry: {"slug", "violations": [...], "relaxed": [...], "warnings": Counter}."""
    slug = entry.get("slug") or entry.get("id") or "?"
    skip = lem.own_tokens(entry)
    basic = (entry.get("frequency") or {}).get("defining_vocabulary") is True or _norm(entry.get("headword") or "") in lem.vocabulary
    result = {"slug": slug, "violations": [], "relaxed": [], "warnings": Counter()}
    for path, text in eexlib.iter_prose(entry):
        if SKIP_FIELD_RE.match(path):
            continue
        oov = out_of_vocabulary(lem, text, skip)
        if not oov:
            continue
        if not DEFINITION_FIELD_RE.match(path):
            result["warnings"].update(lemma for lemma, _ in oov)
            continue
        seen = set()
        for lemma, kind in oov:
            if lemma not in seen:
                seen.add(lemma)
                bucket = "relaxed" if basic and path == FIRST_SENSE else "violations"
                result[bucket].append({"field": path, "lemma": lemma, "kind": kind})
    return result


# --------------------------------------------------------------------------
# Queue, changed files, report
# --------------------------------------------------------------------------

# Suffixes that mark a base-form adjective with no comparative/superlative in play
# (additional, former, sole, active, curious, silent, ...). Checked before the noun
# default so pos_guess does not misclassify these; not exhaustive, only a stronger
# signal than the bare default. See wiki/notes/lint-vocab-pos-guess-gap.md.
ADJ_SUFFIXES = ("al", "ive", "ous", "ent", "ant", "ic", "ful", "less", "able", "ible")


def pos_guess(lem, lemma, kind):
    """``v`` for a lemma reached from a verb form, ``adj`` from a comparative, superlative,
    or a recognized adjective suffix, ``adv`` for a -ly adverb whose base is a lemma, else
    ``n`` (unmarked as a guess: no morphological signal favored any other part of speech)."""
    if kind in VERB_KINDS:
        return "v", False
    if kind in ADJ_KINDS:
        return "adj", False
    stem = lemma[:-2]
    if lemma.endswith("ly") and len(lemma) > 4 and any(
            lem.is_lemma(c) for c in (stem, stem + "e", stem[:-1] + "y", stem + "le", stem[:-2])):
        return "adv", False
    if any(lemma.endswith(suf) and len(lemma) > len(suf) + 2 for suf in ADJ_SUFFIXES):
        return "adj", False
    return "n", True


def queue_lemmas(lem, results, root):
    """Append every out-of-vocabulary definition lemma to the queue as a closure candidate; return the count."""
    rows = {}
    for res in results:
        for item in res["violations"] + res["relaxed"]:
            lemma = item["lemma"].strip("-")
            if len(lemma) < 2 or lemma in lem.known:
                continue
            pos, guessed = pos_guess(lem, lemma, item["kind"])
            row = rows.setdefault((lemma, pos), {"note": "used in %s %s" % (res["slug"], item["field"]),
                                                  "more": set(), "guessed": guessed})
            row["more"].add(res["slug"])
    if not rows:
        return 0
    fd, tmp = tempfile.mkstemp(prefix="lint-vocab-", suffix=".tsv")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write("headword\tpos\tband\tsource\tnote\n")
        for (lemma, pos), row in sorted(rows.items()):
            others = len(row["more"]) - 1
            note = row["note"] + ("; also in %d other entr%s" % (others, "y" if others == 1 else "ies") if others else "")
            if row["guessed"]:
                note += "; pos guessed (no morphological signal), check before claiming"
            fh.write("%s\t%s\t3\tclosure\t%s\n" % (lemma, pos, note))
    try:
        script = Path(root) / "tools" / "queue.py"
        if not script.is_file():
            script = HERE / "queue.py"
        proc = subprocess.run([sys.executable, str(script), "add-batch", tmp], cwd=str(root), capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout).strip())
        print("queue: %s" % (proc.stdout.strip() or "updated"))
    finally:
        os.unlink(tmp)
    return len(rows)


def changed_paths(root, base):
    """Entry files changed since ``base`` plus uncommitted ones (eexlib.changed_entry_paths when it exists)."""
    if hasattr(eexlib, "changed_entry_paths"):
        return eexlib.changed_entry_paths(base, root)
    names = set()
    for cmd in (["git", "diff", "--name-only", "%s...HEAD" % base, "--", "entries/"],
                ["git", "status", "--porcelain", "--", "entries/"]):
        proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
        for line in proc.stdout.splitlines():
            name = line[3:] if cmd[1] == "status" else line
            names.add(name.split(" -> ")[-1].strip().strip('"'))
    return sorted(p for p in (Path(root) / n for n in names if n) if p.is_file() and p.suffix == ".json")


def given_paths(items, root):
    """Entry files named on the command line, by path or by slug."""
    out = []
    for item in items:
        path = Path(item)
        if not path.is_file():
            try:
                path = eexlib.entry_path(item, root)
            except ValueError:
                pass
        if not path.is_file():
            raise SystemExit("error: no entry file %s" % item)
        out.append(path.resolve())
    return out


def print_report(results, gate_slugs, top):
    warn_total = 0
    for res in results:
        for item in res["violations"]:
            print("VIOLATION %s %s: %s" % (res["slug"], item["field"], item["lemma"]))
        for item in res["relaxed"]:
            print("WARN %s %s: %s (first sense of a defining-vocabulary word)" % (res["slug"], item["field"], item["lemma"]))
        if res["warnings"]:
            warn_total += sum(res["warnings"].values())
            shown = ", ".join("%s (%d)" % (w, c) for w, c in res["warnings"].most_common(5))
            print("WARN %s: %d out-of-vocabulary lemma%s in examples and notes: %s" % (
                res["slug"], len(res["warnings"]), "" if len(res["warnings"]) == 1 else "s", shown))
    viol_entries = [r for r in results if r["violations"]]
    warn_entries = [r for r in results if r["warnings"] or r["relaxed"]]
    print("\nentries checked: %d; violations: %d in %d entries; warnings: %d in %d entries%s" % (
        len(results), sum(len(r["violations"]) for r in results), len(viol_entries),
        warn_total + sum(len(r["relaxed"]) for r in results), len(warn_entries),
        "; gate: %d failing" % len(gate_slugs) if gate_slugs is not None else ""))
    for title, table in (("definitions", top["definition"]), ("everything", top["all"])):
        if not table:
            continue
        print("\nmost frequent out-of-vocabulary lemmas (%s): lemma, entries" % title)
        for lemma, n in table:
            print("  %-24s %d" % (lemma, n))


def top_tables(results, limit):
    by_def, by_all = Counter(), Counter()
    for res in results:
        lemmas = {item["lemma"] for item in res["violations"] + res["relaxed"]}
        by_def.update(lemmas)
        by_all.update(lemmas | set(res["warnings"]))
    return {"definition": by_def.most_common(limit), "all": by_all.most_common(limit)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check definition words against the defining vocabulary and the existing entries.")
    parser.add_argument("paths", nargs="*", help="entry files or slugs (default: --all)")
    parser.add_argument("--all", action="store_true", help="check every entry")
    parser.add_argument("--changed", action="store_true", help="check the entries changed since --base plus uncommitted ones")
    parser.add_argument("--base", default="origin/main", help="the base for --changed (default origin/main)")
    parser.add_argument("--gate", action="store_true", help="exit 1 when a checked (with --changed: changed) entry has a definition violation")
    parser.add_argument("--queue", action="store_true", help="queue every out-of-vocabulary definition lemma as a closure candidate")
    parser.add_argument("--json", action="store_true", help="print a machine-readable summary instead of the report")
    parser.add_argument("--root", help="repository root (default: the parent of tools/)")
    parser.add_argument("--dv", help="defining-vocabulary file (default: schema/defining-vocabulary.txt)")
    parser.add_argument("--top", type=int, default=20, help="rows in the summary tables (default 20)")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else eexlib.ROOT

    changed = changed_paths(root, args.base) if args.changed else None
    if args.paths:
        paths = given_paths(args.paths, root)
    elif args.changed and not args.all:
        paths = list(changed)
    else:
        paths = eexlib.iter_entry_paths(root)
    gated = {p.resolve() for p in changed} if changed is not None else {p.resolve() for p in paths}

    lem = Lemmatizer(root=root, dv=args.dv)
    if not lem.vocabulary:
        print("error: no defining vocabulary at %s" % lem.dv_path, file=sys.stderr)
        return 2
    results, failing = [], []
    for path in paths:
        try:
            entry = eexlib.load_json(path)
        except (OSError, ValueError) as exc:
            print("error: %s: %s" % (path, exc), file=sys.stderr)
            return 2
        if not isinstance(entry, dict) or eexlib.is_redirect_stub(entry):
            continue
        res = check_entry(lem, entry)
        res["path"] = str(path)
        results.append(res)
        if res["violations"] and path.resolve() in gated:
            failing.append(res["slug"])
    results.sort(key=lambda r: r["slug"])
    top = top_tables(results, args.top)
    queued = queue_lemmas(lem, results, root) if args.queue else 0
    failed = bool(args.gate and failing)

    if args.json:
        print(json.dumps({
            "entries_checked": len(results),
            "violations": sum(len(r["violations"]) for r in results),
            "relaxed": sum(len(r["relaxed"]) for r in results),
            "warnings": sum(sum(r["warnings"].values()) for r in results),
            "gate": {"enabled": bool(args.gate), "failed": failed, "entries": sorted(failing)},
            "queued": queued,
            "top_definition_lemmas": [list(t) for t in top["definition"]],
            "top_lemmas": [list(t) for t in top["all"]],
            "entries": {r["slug"]: {"path": r["path"], "violations": r["violations"], "relaxed": r["relaxed"],
                                    "warnings": dict(r["warnings"].most_common())} for r in results},
        }, indent=2, ensure_ascii=False))
    else:
        if not results:
            print("no entries to check")
        print_report(results, sorted(failing) if args.gate else None, top)
        if failed:
            print("\nGATE FAILED: definition violations in %s" % ", ".join(sorted(failing)))
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # a report piped into head is not an error
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
