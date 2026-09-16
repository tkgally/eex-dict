#!/usr/bin/env python3
"""Build-time linker: turn the prose of an entry into HTML in which every word
that has an entry links to the page of its headword.

    python3 tools/link_words.py --text "Mari opened an account at the bank." [--self bank-n]
    python3 tools/link_words.py --text "..." --html          # the HTML instead of the link list
    python3 tools/link_words.py --text "..." --entries DIR   # index another entries directory
    python3 tools/link_words.py --text "..." --drafts        # index draft entries too

Library use (what tools/build_site.py does)::

    import link_words
    index = link_words.build_index(entries)        # entry dicts; redirect stubs are skipped
    html = link_words.link_text(text, "bank-n", "../", index=index)

The rules
---------
* Every word token is looked up in a map built from the entries' own headwords,
  ``inflections.forms``, and ``variants[].form``.  A token links only when it
  resolves to exactly one headword.  A headword with several entries (bank-n,
  bank-v) links to the headword page ``w/<headword>.html`` with no anchor, so
  the reader sees all of them; a form that belongs to one entry only links to
  that entry's anchor ``#<slug>``.
* Multi-word headwords ("give up", "in spite of", and their forms "gave up" ...)
  are matched greedily, longest first, before single words.  A hyphenated word
  is tried as a whole ("x-ray") before its parts.
* ``[[slug|visible text]]`` in the source forces the target: the link goes to
  that slug's anchor and shows the text.  ``[[slug]]`` shows the target's
  headword.  A slug with no published entry shows the text unlinked.
* The entry's own headword and its forms are never linked (``self_slug``).
  Ambiguity is judged before that exclusion: a form shared by the entry's own
  headword and another headword is left unlinked rather than sent to the other.
* A single-word token with no listed form is lemmatized.  When tools/lint_vocab.py
  exists and exposes a lemmatizer class or function it is used; otherwise a
  small rule set applies (strip -s/-es/-ies, -ed/-ied, -ing with e-restoration
  and undoubling, -er/-est).  Either way a candidate counts only when it is a
  known headword, and the one-headword rule still applies.
* FUNCTION_WORDS (about forty) are never lemmatized: they link only through an
  entry of their own or a listed inflected form, so "is" never becomes "I" and
  "as" never becomes "a".  They are linked like any other word once their entry
  exists.
* A possessive ending ("bank's") is split off and left unlinked.
* Everything else is HTML-escaped and left as it is.

Output: ``<a class="w" href="<base_rel>w/<headword>.html#<slug>" data-hw="<headword>">word</a>``,
where ``base_rel`` is the path from the current page's directory to the site
root ("../" for a page under w/, "" for the home page) and ``<headword>`` in the
URL is the slug without its part-of-speech suffix (``in-spite-of``, ``oclock``).

Standard library only.
"""

import argparse
import html
import inspect
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

# Function words that the fallback lemmatizer never touches.  They are linked
# only when an entry of their own (or a listed inflected form) exists.  The
# list guards against "is" -> "i", "as" -> "a", "his" -> "hi", "its" -> "it",
# "does" -> "do", "has" -> "ha" and the like; harmless words are on it too so
# the list reads as what it is: the closed class of the commonest function words.
FUNCTION_WORDS = frozenset("""
a an the and of to in at on by for with from as
that this these those it its is are was were be am
he she we they you i his her their us
does has had did not so if
""".split())

WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*")
OVERRIDE_RE = re.compile(r"\[\[([a-z0-9]+(?:-[a-z0-9]+)*)(?:\|([^\]]*))?\]\]")
SOFT_SEP_RE = re.compile(r"^(?:[\s\-–]+|\.)$")
POSSESSIVE_RE = re.compile(r"^(.+)(['’]s)$")
LINK_RE = re.compile(r'<a class="w" href="([^"]*)" data-hw="([^"]*)">([^<]*)</a>')


# --------------------------------------------------------------------------
# Keys
# --------------------------------------------------------------------------

def _norm_token(token):
    """The lookup key of one word token: lowercase, straight apostrophe, accents folded."""
    s = token.lower().replace("’", "'")
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def form_key(text):
    """The lookup key of a headword or inflected form: its tokens, normalized, space-joined.

    ``"Give up"`` -> ``"give up"``; ``"x-ray"`` -> ``"x ray"``; ``"a.m."`` -> ``"a m"``.
    """
    return " ".join(_norm_token(t) for t in WORD_RE.findall(str(text)))


def page_name(slug):
    """The headword-page name of a slug: the slug without its part-of-speech suffix."""
    try:
        return eexlib.parse_slug(slug)[0]
    except ValueError:
        return slug


def headword_from_slug(slug):
    """A display form for a slug whose entry does not exist: ``building-society-n`` -> ``building society``."""
    return page_name(slug).replace("-", " ")


# --------------------------------------------------------------------------
# Lemmatizers
# --------------------------------------------------------------------------

def rule_lemmas(word):
    """Candidate base forms of ``word`` by the minimal rules (no dictionary knowledge).

    The caller accepts a candidate only when it is a known headword, so
    over-generation is harmless; under-generation would lose links.
    """
    out = []

    def add(c):
        if c and len(c) >= 2 and c not in out:
            out.append(c)

    def undouble(stem):
        if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            add(stem[:-1])

    n = len(word)
    if word.endswith("ies") and n > 4:
        add(word[:-3] + "y")
    if word.endswith("es") and n > 3:
        add(word[:-2])
        add(word[:-1])
    elif word.endswith("s") and not word.endswith("ss") and n > 2:
        add(word[:-1])
    if word.endswith("ied") and n > 4:
        add(word[:-3] + "y")
    if word.endswith("ed") and n > 3:
        stem = word[:-2]
        add(stem)
        add(stem + "e")
        undouble(stem)
    if word.endswith("ing") and n > 4:
        stem = word[:-3]
        add(stem)
        add(stem + "e")
        undouble(stem)
    if word.endswith("ier") and n > 4:
        add(word[:-3] + "y")
    if word.endswith("er") and n > 3:
        stem = word[:-2]
        add(stem)
        add(stem + "e")
        undouble(stem)
    if word.endswith("iest") and n > 5:
        add(word[:-4] + "y")
    if word.endswith("est") and n > 4:
        stem = word[:-3]
        add(stem)
        add(stem + "e")
        undouble(stem)
    return out


def _instantiate(cls, known):
    for args in ((), (known,), (sorted(known),)):
        try:
            return cls(*args)
        except Exception:  # noqa: BLE001 - any failure means "not this way"
            continue
    return None


def _wrap_lemmatizer(fn, known):
    """Adapt an external callable to ``word -> [candidates]``, or return None when it does not work."""
    for extra in ((), (known,)):
        try:
            fn("running", *extra)
        except Exception:  # noqa: BLE001
            continue

        def call(word, _fn=fn, _extra=extra):
            try:
                r = _fn(word, *_extra)
            except Exception:  # noqa: BLE001
                return []
            if r is None:
                return []
            if isinstance(r, str):
                return [r]
            try:
                return [x for x in r if isinstance(x, str)]
            except TypeError:
                return []

        return call
    return None


def external_lemmatizer(known):
    """The lemmatizer of tools/lint_vocab.py as ``word -> [candidates]``, or None.

    Looks for a class or function whose name contains "lemma" (a class is
    instantiated with no arguments or with the set of known headwords and must
    offer ``lemmatize``, ``lemmas``, ``candidates`` or ``__call__``).  Anything
    that raises is skipped; the rules are the fallback.
    """
    if not (HERE / "lint_vocab.py").is_file():
        return None
    try:
        import importlib
        mod = importlib.import_module("lint_vocab")
    except Exception:  # noqa: BLE001 - a half-written or failing module is not a linker problem
        return None
    names = [n for n in dir(mod) if "lemma" in n.lower() and not n.startswith("_")]
    names.sort(key=lambda n: (not n.lower().startswith("lemmatizer"), not n.lower().startswith("lemmatize"), n))
    for name in names:
        obj = getattr(mod, name, None)
        fn = None
        if inspect.isclass(obj):
            inst = _instantiate(obj, known)
            if inst is None:
                continue
            for meth in ("lemmatize", "lemmas", "candidates", "__call__"):
                cand = getattr(inst, meth, None)
                if callable(cand):
                    fn = cand
                    break
        elif callable(obj):
            fn = obj
        if fn is None:
            continue
        wrapped = _wrap_lemmatizer(fn, known)
        if wrapped is not None:
            return wrapped
    return None


# --------------------------------------------------------------------------
# The index
# --------------------------------------------------------------------------

class Index:
    """Every inflected form of every indexed entry, mapped to its headword and slugs.

    ``lemmatizer``: None (use lint_vocab's when available, else the rules),
    ``"rules"`` (always the built-in rules), or a callable ``word -> [candidates]``.
    """

    def __init__(self, lemmatizer=None):
        self.headwords = {}    # hw_key -> {"display": str, "page": str, "slugs": [slug, ...]}
        self.forms = {}        # form_key -> {hw_key: set(slugs)}
        self.slug_hw = {}      # slug -> hw_key
        self.multi_first = set()
        self.max_tokens = 1
        self._lemmatizer_spec = lemmatizer
        self._lemmatizer = None
        self._cache = {}

    # -- building ---------------------------------------------------------

    def add_entry(self, entry):
        """Index one entry dict (a redirect stub or anything without slug and headword is ignored)."""
        if not isinstance(entry, dict) or eexlib.is_redirect_stub(entry):
            return
        slug = entry.get("slug")
        headword = entry.get("headword")
        if not slug or not headword:
            return
        hw_key = form_key(headword)
        if not hw_key:
            return
        info = self.headwords.get(hw_key)
        if info is None:
            info = {"display": str(headword), "page": page_name(slug), "slugs": []}
            self.headwords[hw_key] = info
        if slug not in info["slugs"]:
            info["slugs"].append(slug)
            info["slugs"].sort()
        self.slug_hw[slug] = hw_key
        self._add_form(hw_key, hw_key, slug)
        forms = (entry.get("inflections") or {}).get("forms") or {}
        for value in forms.values():
            for piece in _split_forms(value):
                self._add_form(form_key(piece), hw_key, slug)
        for variant in entry.get("variants") or []:
            if isinstance(variant, dict) and variant.get("form"):
                self._add_form(form_key(variant["form"]), hw_key, slug)
        self._cache.clear()

    def _add_form(self, key, hw_key, slug):
        if not key:
            return
        self.forms.setdefault(key, {}).setdefault(hw_key, set()).add(slug)
        if " " in key:
            self.multi_first.add(key.split(" ", 1)[0])
            self.max_tokens = max(self.max_tokens, key.count(" ") + 1)

    # -- lookups ----------------------------------------------------------

    @property
    def lemmatizer(self):
        if self._lemmatizer is None:
            spec = self._lemmatizer_spec
            if callable(spec):
                self._lemmatizer = spec
            elif spec == "rules":
                self._lemmatizer = rule_lemmas
            else:
                self._lemmatizer = external_lemmatizer(set(self.headwords)) or rule_lemmas
        return self._lemmatizer

    def headword_of(self, slug):
        """The headword key an indexed slug belongs to, or None."""
        return self.slug_hw.get(slug)

    def resolve_exact(self, key):
        """``(hw_key, slug or None)`` when ``key`` is a listed form of exactly one headword, else None."""
        hit = self.forms.get(key)
        return self._single(hit)

    def resolve(self, key):
        """Like resolve_exact, but a single word with no listed form is lemmatized first."""
        try:
            return self._cache[key]
        except KeyError:
            pass
        hit = self.forms.get(key)
        if hit is None and key and " " not in key and "'" not in key and key not in FUNCTION_WORDS:
            found = {}
            for cand in self.lemmatizer(key):
                ck = form_key(cand)
                info = self.headwords.get(ck)
                if info is not None and ck != key:
                    found.setdefault(ck, set(info["slugs"]))
            hit = found or None
        result = self._single(hit)
        self._cache[key] = result
        return result

    @staticmethod
    def _single(hit):
        if not hit or len(hit) != 1:
            return None
        hw_key, slugs = next(iter(hit.items()))
        return hw_key, (next(iter(slugs)) if len(slugs) == 1 else None)

    # -- linking ----------------------------------------------------------

    def _self_key(self, self_slug):
        if not self_slug:
            return None
        key = self.slug_hw.get(self_slug)
        if key is None:
            key = form_key(headword_from_slug(self_slug))
        return key

    def anchor(self, hit, visible, base_rel):
        """The ``<a class="w">`` element for a resolved hit around ``visible`` (unescaped text)."""
        hw_key, slug = hit
        info = self.headwords[hw_key]
        href = "%sw/%s.html" % (base_rel, info["page"])
        if slug:
            href += "#" + slug
        return '<a class="w" href="%s" data-hw="%s">%s</a>' % (
            html.escape(href, quote=True), html.escape(info["display"], quote=True), html.escape(visible, quote=False))

    def link(self, text, self_slug=None, base_rel=""):
        """The HTML of ``text`` with links placed; ``[[slug|text]]`` overrides honoured."""
        text = "" if text is None else str(text)
        self_key = self._self_key(self_slug)
        out = []
        pos = 0
        for m in OVERRIDE_RE.finditer(text):
            out.append(self._link_plain(text[pos:m.start()], self_key, base_rel))
            out.append(self._override(m.group(1), m.group(2), base_rel))
            pos = m.end()
        out.append(self._link_plain(text[pos:], self_key, base_rel))
        return "".join(out)

    def _override(self, slug, visible, base_rel):
        hw_key = self.slug_hw.get(slug)
        if hw_key is None:
            return html.escape(visible if visible else headword_from_slug(slug), quote=False)
        info = self.headwords[hw_key]
        return self.anchor((hw_key, slug), visible if visible else info["display"], base_rel)

    def _link_plain(self, seg, self_key, base_rel):
        if not seg:
            return ""
        tokens = list(WORD_RE.finditer(seg))
        if not tokens:
            return html.escape(seg, quote=False)
        out = []
        pos = 0
        i = 0
        n = len(tokens)
        while i < n:
            m = tokens[i]
            out.append(html.escape(seg[pos:m.start()], quote=False))
            tok = m.group(0)
            key = _norm_token(tok)
            if key in self.multi_first and self.max_tokens > 1:
                hit_span = self._match_multi(seg, tokens, i, self_key)
                if hit_span is not None:
                    hit, span = hit_span
                    last = tokens[i + span - 1]
                    out.append(self.anchor(hit, seg[m.start():last.end()], base_rel))
                    pos = last.end()
                    i += span
                    continue
            base, suffix = key, ""
            pm = POSSESSIVE_RE.match(key)
            if pm:
                base, suffix = pm.group(1), pm.group(2)
            hit = self.resolve(base)
            if hit is not None and hit[0] != self_key:
                cut = len(tok) - len(suffix)
                out.append(self.anchor(hit, tok[:cut], base_rel) + html.escape(tok[cut:], quote=False))
            else:
                out.append(html.escape(tok, quote=False))
            pos = m.end()
            i += 1
        out.append(html.escape(seg[pos:], quote=False))
        return "".join(out)

    def _match_multi(self, seg, tokens, i, self_key):
        n = len(tokens)
        for span in range(min(self.max_tokens, n - i), 1, -1):
            ok = True
            for j in range(i, i + span - 1):
                if not SOFT_SEP_RE.match(seg[tokens[j].end():tokens[j + 1].start()]):
                    ok = False
                    break
            if not ok:
                continue
            mkey = " ".join(_norm_token(t.group(0)) for t in tokens[i:i + span])
            hit = self.resolve_exact(mkey)
            if hit is not None and hit[0] != self_key:
                return hit, span
        return None

    def links(self, text, self_slug=None, base_rel=""):
        """``[(visible text, headword, href)]`` for every link ``link`` would place."""
        return [(html.unescape(m.group(3)), html.unescape(m.group(2)), html.unescape(m.group(1)))
                for m in LINK_RE.finditer(self.link(text, self_slug, base_rel))]


def _split_forms(value):
    """An inflected-form value as a list: ``"burned / burnt"`` -> both; null -> nothing."""
    if not value or not isinstance(value, str):
        return []
    return [p.strip() for p in re.split(r"[/,;]| or ", value) if p.strip()]


# --------------------------------------------------------------------------
# Module-level API
# --------------------------------------------------------------------------

_DEFAULT = None


def build_index(entries, lemmatizer=None):
    """The form map for ``entries``: an iterable of entry dicts or of ``(path, dict)`` pairs.

    Redirect stubs are skipped.  The caller decides which entries to index
    (the site indexes reviewed entries only).
    """
    index = Index(lemmatizer=lemmatizer)
    for item in entries:
        entry = item[1] if isinstance(item, tuple) else item
        index.add_entry(entry)
    return index


def published_entries(entries_dir=None, drafts=False):
    """Entry dicts under ``entries_dir`` (default ROOT/entries): reviewed ones, or all with ``drafts``."""
    entries_dir = Path(entries_dir) if entries_dir else eexlib.ROOT / "entries"
    out = []
    if not entries_dir.is_dir():
        return out
    for path in sorted(p for p in entries_dir.rglob("*.json") if p.is_file()):
        try:
            d = eexlib.load_json(path)
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict) or eexlib.is_redirect_stub(d):
            continue
        if drafts or (d.get("provenance") or {}).get("status") == "reviewed":
            out.append(d)
    return out


def default_index(entries_dir=None, drafts=False, rebuild=False):
    """The module's shared index over the repository's published entries (built once)."""
    global _DEFAULT
    if _DEFAULT is None or rebuild:
        _DEFAULT = build_index(published_entries(entries_dir, drafts))
    return _DEFAULT


def set_default_index(index):
    """Make ``index`` the one ``link_text`` uses when none is passed."""
    global _DEFAULT
    _DEFAULT = index


def link_text(text, self_slug, base_rel, index=None):
    """The HTML of ``text`` with every resolvable word linked (see the module docstring)."""
    index = index if index is not None else default_index()
    return index.link(text, self_slug, base_rel)


# --------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="Show the links the build-time linker would place in a text.")
    parser.add_argument("--text", required=True, help="the text to link")
    parser.add_argument("--self", dest="self_slug", default=None, help="the slug of the entry the text belongs to (never linked)")
    parser.add_argument("--base-rel", default="../", help="path from the page to the site root (default ../)")
    parser.add_argument("--entries", default=None, help="entries directory to index (default entries/)")
    parser.add_argument("--drafts", action="store_true", help="index draft entries as well as reviewed ones")
    parser.add_argument("--html", action="store_true", help="print the HTML instead of the list of links")
    args = parser.parse_args(argv)
    index = build_index(published_entries(args.entries, args.drafts))
    if args.html:
        print(index.link(args.text, args.self_slug, args.base_rel))
        return 0
    links = index.links(args.text, args.self_slug, args.base_rel)
    if not links:
        print("(no links; %d headwords indexed)" % len(index.headwords))
        return 0
    for visible, headword, href in links:
        print("%s -> %s  %s" % (visible, headword, href))
    return 0


if __name__ == "__main__":
    sys.exit(main())
