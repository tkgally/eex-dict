#!/usr/bin/env python3
"""Shared library for the eex-dict tools.

Everything the command-line tools have in common lives here: the repository
root, JSON loading and saving in the house format, the vocabularies, the slug
rules of wiki/conventions.md section 2 (slugify, parse_slug, shard,
entry_path, phrase_sub_id), iteration over entry files, the list of prose
fields and the inline marks they may carry, the headword's own forms, key
ordering derived from the schema, and two small git helpers.

Standard library only.  Import it from a sibling tool with::

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import eexlib

Run ``python3 tools/eexlib.py --help`` for a short self-description.
"""

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# Repository root
# --------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REDIRECT_STUB_KEYS = ["schema_version", "slug", "redirect_to", "renamed", "reason"]

_CACHE = {}


def set_root(path):
    """Point every root-relative helper at another repository layout.

    The tests use this to run the tools against a temporary copy of the
    repository.  POS_CODES is reloaded from the new root's vocabularies.
    """
    global ROOT, POS_CODES
    ROOT = Path(path).resolve()
    _CACHE.clear()
    POS_CODES = _load_pos_codes()


def get_root():
    """The current repository root as a Path."""
    return ROOT


def _root(root):
    return Path(root).resolve() if root is not None else ROOT


# --------------------------------------------------------------------------
# JSON in the house format
# --------------------------------------------------------------------------

def load_json(path):
    """Read a UTF-8 JSON file and return the parsed value."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, obj):
    """Write ``obj`` as UTF-8 JSON, two-space indent, no ASCII escaping, trailing newline."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def dumps_json(obj):
    """The exact text save_json would write for ``obj``."""
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def load_schema(root=None):
    """Load schema/entry.schema.json (cached per root)."""
    key = ("schema", _root(root))
    if key not in _CACHE:
        _CACHE[key] = load_json(_root(root) / "schema" / "entry.schema.json")
    return _CACHE[key]


def load_vocab(root=None):
    """Load schema/vocabularies.json (cached per root)."""
    key = ("vocab", _root(root))
    if key not in _CACHE:
        _CACHE[key] = load_json(_root(root) / "schema" / "vocabularies.json")
    return _CACHE[key]


def vocab_values(name, vocab=None):
    """The allowed values of the closed vocabulary ``name``: its keys minus the ``_``-prefixed ones."""
    vocab = load_vocab() if vocab is None else vocab
    table = vocab.get(name)
    if not isinstance(table, dict):
        raise KeyError("no vocabulary named %r in schema/vocabularies.json" % name)
    return [k for k in table if not k.startswith("_")]


def _load_pos_codes():
    try:
        return tuple(vocab_values("pos"))
    except (OSError, KeyError, ValueError):
        return ()


POS_CODES = _load_pos_codes()


# --------------------------------------------------------------------------
# Slugs, shards, paths (wiki/conventions.md section 2)
# --------------------------------------------------------------------------

def _slug_text(text):
    """Slugify free text: the headword part of a slug or a phrase sub_id."""
    s = str(text).lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("'", "").replace("’", "").replace("‘", "").replace(".", "")
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def slugify(headword, pos, homograph=1):
    """The slug of ``headword`` with part-of-speech code ``pos`` and homograph number.

    ``bank``/``n`` -> ``bank-n``; ``give up``/``phrv`` -> ``give-up-phrv``;
    ``o'clock``/``adv`` -> ``oclock-adv``; ``café``/``n`` -> ``cafe-n``;
    ``bat``/``n``/2 -> ``bat-n-2``.  Raises ValueError for an unknown
    part-of-speech code, a headword that leaves nothing after slugification,
    or a homograph below 1.
    """
    if pos not in POS_CODES:
        raise ValueError("unknown part-of-speech code %r (known: %s)" % (pos, ", ".join(POS_CODES)))
    head = _slug_text(headword)
    if not head:
        raise ValueError("headword %r leaves nothing to slugify" % (headword,))
    try:
        homograph = int(homograph)
    except (TypeError, ValueError):
        raise ValueError("homograph must be an integer, got %r" % (homograph,))
    if homograph < 1:
        raise ValueError("homograph must be 1 or more, got %d" % homograph)
    slug = "%s-%s" % (head, pos)
    if homograph > 1:
        slug += "-%d" % homograph
    return slug


def phrase_sub_id(text):
    """The sub_id of a phrase: its text slugified, no part-of-speech suffix.

    ``give someone a hand`` -> ``give-someone-a-hand``.
    """
    sub_id = _slug_text(text)
    if not sub_id:
        raise ValueError("phrase text %r leaves nothing to slugify" % (text,))
    return sub_id


def parse_slug(slug):
    """Split a slug into (headword_part, pos, homograph).

    A trailing ``-<digits>`` is the homograph number (2 or more); the last
    remaining segment must be a part-of-speech code.  Raises ValueError for
    anything else.
    """
    if not isinstance(slug, str) or not SLUG_RE.match(slug):
        raise ValueError("%r is not a well-formed slug" % (slug,))
    parts = slug.split("-")
    homograph = 1
    if len(parts) >= 3 and parts[-1].isdigit() and parts[-2] in POS_CODES:
        homograph = int(parts.pop())
        if homograph < 2:
            raise ValueError("%r: a homograph suffix must be -2 or higher" % (slug,))
    if len(parts) < 2 or parts[-1] not in POS_CODES:
        raise ValueError("%r does not end in a part-of-speech code" % (slug,))
    pos = parts.pop()
    return "-".join(parts), pos, homograph


def shard(slug):
    """The shard directory of a slug: first two leading ASCII letters, one letter, or ``0-9``."""
    m = re.match(r"[a-z]+", slug)
    if m:
        return m.group(0)[:2]
    if slug[:1].isdigit():
        return "0-9"
    raise ValueError("%r does not start with a letter or digit" % (slug,))


def entry_path(slug, root=None):
    """The absolute path of the entry file for ``slug``: ROOT/entries/<shard>/<slug>.json."""
    return _root(root) / "entries" / shard(slug) / (slug + ".json")


def relative_entry_path(slug):
    """The repository-relative path of an entry as a string: entries/<shard>/<slug>.json."""
    return "entries/%s/%s.json" % (shard(slug), slug)


def iter_entry_paths(root=None):
    """Every ``*.json`` file under entries/, sorted."""
    entries = _root(root) / "entries"
    if not entries.is_dir():
        return []
    return sorted(p for p in entries.rglob("*.json") if p.is_file())


def iter_entries(root=None):
    """Yield (path, dict) for every entry file (redirect stubs included)."""
    for path in iter_entry_paths(root):
        yield path, load_json(path)


def is_redirect_stub(d):
    """True for the stub left behind by a rename (it has a ``redirect_to`` key)."""
    return isinstance(d, dict) and "redirect_to" in d


def utcnow_iso():
    """The current UTC time as ``YYYY-MM-DDTHH:MM:SSZ``."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def word_count(text):
    """The number of whitespace-separated tokens in ``text``."""
    return len(str(text).split())


# --------------------------------------------------------------------------
# Prose fields
# --------------------------------------------------------------------------

ADAPTATION_KINDS = ["semantic", "grammar", "culture", "false_friends", "pronunciation"]

# Every prose field of an entry.  ``[]`` expands over a list, ``*`` over the
# keys of an object.
PROSE_PATHS = [
    "core_idea",
    "usage_note",
    "inflections.note",
    "pronunciation.notes",
    "variants[].note",
    "pronunciation.variants[].note",
    "senses[].definition",
    "senses[].explanation",
    "senses[].examples[].text",
    "senses[].examples[].note",
    "senses[].collocations[].items[]",
    "senses[].synonyms[].note",
    "senses[].antonyms[].note",
    "senses[].compare[].note",
    "senses[].subsenses[].definition",
    "senses[].subsenses[].explanation",
    "senses[].subsenses[].examples[].text",
    "senses[].subsenses[].examples[].note",
    "senses[].subsenses[].collocations[].items[]",
    "senses[].adaptation.*",
    "phrases[].text",
    "phrases[].definition",
    "phrases[].explanation",
    "phrases[].examples[].text",
    "phrases[].examples[].note",
    "phrases[].adaptation.*",
    "synonym_discrimination.note",
    "learner_errors[].incorrect",
    "learner_errors[].correct",
    "learner_errors[].note",
    "etymology.text",
    "see_also[].note",
    "word_family[].note",
    "adaptation.*",
]


def _split_path(spec):
    """``senses[].examples[].text`` -> ['senses', '[]', 'examples', '[]', 'text']."""
    out = []
    for piece in spec.split("."):
        name = piece.rstrip("[]")
        if name:
            out.append(name)
        out.extend(["[]"] * ((len(piece) - len(name)) // 2))
    return out


def _walk(value, segments, prefix):
    """Yield (path, value) for every string reached by following ``segments``."""
    if not segments:
        if isinstance(value, str):
            yield prefix, value
        return
    seg, rest = segments[0], segments[1:]
    if seg == "[]":
        if isinstance(value, list):
            for i, item in enumerate(value):
                yield from _walk(item, rest, "%s[%d]" % (prefix, i))
    elif seg == "*":
        if isinstance(value, dict):
            for key, item in value.items():
                yield from _walk(item, rest, "%s.%s" % (prefix, key) if prefix else key)
    elif isinstance(value, dict) and seg in value:
        yield from _walk(value[seg], rest, "%s.%s" % (prefix, seg) if prefix else seg)


def iter_prose(entry):
    """Yield (json_path, text) for every non-null prose field of ``entry``.

    Paths look like ``senses[0].examples[1].text``.
    """
    for spec in PROSE_PATHS:
        yield from _walk(entry, _split_path(spec), "")


# --------------------------------------------------------------------------
# Inline marks in prose (wiki/decisions/inline-markup.md)
# --------------------------------------------------------------------------

# ``**word**`` names a word as a word (in an example: the headword itself);
# ``*phrase*`` quotes language as an illustration.  A mark never spans a line,
# never starts or ends with a space, and never nests.  Anything else that
# contains an asterisk is malformed (tools/validate.py reports it).
MARK_RE = re.compile(r"\*\*(?![\s*])(.+?)(?<![\s*])\*\*|\*(?![\s*])(.+?)(?<![\s*])\*")

# Prose fields that carry no marks at all: they are quoted language as a whole.
NO_MARKUP_FIELDS = re.compile(r"(?:^|\.)(?:collocations\[\d+\]\.items\[\d+\]|phrases\[\d+\]\.text|learner_errors\[\d+\]\.(?:incorrect|correct))$")
EXAMPLE_TEXT_FIELD = re.compile(r"examples\[\d+\]\.text$")


def iter_markup(text):
    """Yield ``(kind, inner, start, end)`` for every well-formed mark in ``text``: kind ``"b"`` or ``"i"``."""
    for m in MARK_RE.finditer(str(text or "")):
        if m.group(1) is not None:
            yield "b", m.group(1), m.start(), m.end()
        else:
            yield "i", m.group(2), m.start(), m.end()


def strip_markup(text):
    """``text`` with its marks removed and their inner text kept (malformed asterisks are left alone)."""
    return MARK_RE.sub(lambda m: m.group(1) if m.group(1) is not None else m.group(2), str(text or ""))


def markup_errors(text, field=""):
    """One message per fault in the marks of a prose field, judged by the field's path (empty for a prose field
    that allows both marks): an asterisk outside a mark, a nested mark, a single-asterisk mark in an example,
    any mark in a field that carries none.  (A mark inside a link override is the validator's check.)"""
    text = str(text or "")
    out = []
    if "*" not in text:
        return out
    if field and NO_MARKUP_FIELDS.search(field):
        out.append("marks are not used in this field (it is quoted language as a whole)")
        return out
    example = bool(field) and bool(EXAMPLE_TEXT_FIELD.search(field))
    rest = []
    pos = 0
    for kind, inner, start, end in iter_markup(text):
        rest.append(text[pos:start])
        pos = end
        if "*" in inner:
            out.append("marks do not nest: %r" % text[start:end])
        if example and kind == "i":
            out.append("an example carries no single-asterisk mark (the sentence is the illustration): %r" % text[start:end])
    rest.append(text[pos:])
    leftover = "".join(rest)
    if "*" in leftover:
        out.append("an asterisk that is not a well-formed mark (**word** or *phrase*, no space inside, same line)")
    return out


def own_forms(entry):
    """The headword, its listed inflected forms, and its variant forms, as display strings (duplicates removed)."""
    forms = []
    hw = entry.get("headword") if isinstance(entry, dict) else None
    if isinstance(hw, str) and hw.strip():
        forms.append(hw.strip())
    infl = entry.get("inflections") if isinstance(entry, dict) else None
    table = infl.get("forms") if isinstance(infl, dict) else None
    for value in (table or {}).values():
        if isinstance(value, str):
            for piece in re.split(r"[/,;]| or ", value):
                if piece.strip():
                    forms.append(piece.strip())
    for v in (entry.get("variants") or []) if isinstance(entry, dict) else []:
        if isinstance(v, dict) and isinstance(v.get("form"), str) and v["form"].strip():
            forms.append(v["form"].strip())
    seen, out = set(), []
    for f in forms:
        if f.lower() not in seen:
            seen.add(f.lower())
            out.append(f)
    return out


_WORD_TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*")
_CLITIC_RE = re.compile(r"^(.+?)(n't|'(?:s|ve|re|ll|d|m))$")
AFFIX_POS = {"prefix", "suffix", "comb"}


def split_clitic(word):
    """``(base, clitic)`` for a lowercase token with a contracted ending: ``doesn't`` -> ``('does', "n't")``,
    ``bank's`` -> ``('bank', "'s")``, ``can't`` -> ``('can', "'t")``, ``cannot`` -> ``('can', 'not')``; else ``(word, '')``."""
    if word == "cannot":
        return "can", "not"
    if word == "can't":
        return "can", "'t"
    m = _CLITIC_RE.match(word)
    if m and len(m.group(1)) >= 1:
        return m.group(1), m.group(2)
    return word, ""


def _norm_word(token):
    s = token.lower().replace("’", "'")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return split_clitic(s)[0]


def contains_form(text, forms):
    """True when ``text`` contains one of ``forms`` as whole words (a multi-word form as adjacent words).

    Case, accents, and a contracted ending (``'s``, ``n't``, ``'ve``) are ignored.  Used by the validator's
    "does the example contain the headword" check; the site's own marking is
    done by tools/link_words.py from the same forms.
    """
    tokens = [_norm_word(t) for t in _WORD_TOKEN_RE.findall(strip_markup(text))]
    for form in forms:
        want = [_norm_word(t) for t in _WORD_TOKEN_RE.findall(str(form))]
        if not want:
            continue
        n = len(want)
        for i in range(len(tokens) - n + 1):
            if tokens[i:i + n] == want:
                return True
    return False


# --------------------------------------------------------------------------
# Key order from the schema
# --------------------------------------------------------------------------

def resolve_ref(ref, root_schema):
    """Resolve a local ``#/$defs/...`` (or ``#/definitions/...``) reference."""
    if not ref.startswith("#/"):
        raise ValueError("only local references are supported, got %r" % ref)
    node = root_schema
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            node = node[int(token)]
        else:
            node = node[token]
    return node


def _order_node(fragment, root_schema, depth=0):
    """The ordering node of a schema fragment: {key: child node}; ``*`` is additionalProperties."""
    node = {}
    if not isinstance(fragment, dict) or depth > 40:
        return node
    if "$ref" in fragment:
        _merge_order(node, _order_node(resolve_ref(fragment["$ref"], root_schema), root_schema, depth + 1))
    props = fragment.get("properties")
    if isinstance(props, dict):
        for key, sub in props.items():
            _merge_order(node.setdefault(key, {}), _order_node(sub, root_schema, depth + 1))
    extra = fragment.get("additionalProperties")
    if isinstance(extra, dict):
        _merge_order(node.setdefault("*", {}), _order_node(extra, root_schema, depth + 1))
    items = fragment.get("items")
    if isinstance(items, dict):
        _merge_order(node, _order_node(items, root_schema, depth + 1))
    for keyword in ("oneOf", "anyOf", "allOf"):
        for branch in fragment.get(keyword) or []:
            _merge_order(node, _order_node(branch, root_schema, depth + 1))
    return node


def _merge_order(target, extra):
    for key, sub in extra.items():
        _merge_order(target.setdefault(key, {}), sub)


def schema_key_order(schema=None):
    """Nested key ordering derived from the schema's ``properties`` order.

    Returns a dict whose insertion order is the key order; each value is the
    ordering node of that property (for arrays, of their items).  The special
    key ``*`` holds the node used for keys admitted by ``additionalProperties``.
    """
    schema = load_schema() if schema is None else schema
    return _order_node(schema, schema)


def reorder_entry(entry, schema=None):
    """Return ``entry`` with keys in schema order at every level (unknown keys last)."""
    return _reorder(entry, schema_key_order(schema))


def _reorder(value, node):
    if isinstance(value, dict):
        known = [k for k in node if k != "*" and k in value]
        unknown = [k for k in value if k not in node or k == "*"]
        out = {}
        for key in known + unknown:
            child = node.get(key) if key in node and key != "*" else node.get("*", {})
            out[key] = _reorder(value[key], child or {})
        return out
    if isinstance(value, list):
        return [_reorder(item, node) for item in value]
    return value


# --------------------------------------------------------------------------
# Git helpers
# --------------------------------------------------------------------------

def _git(args, root=None):
    proc = subprocess.run(["git"] + list(args), cwd=str(_root(root)), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), proc.stderr.strip()))
    return proc.stdout


def changed_entry_paths(base="origin/main", root=None):
    """Entry files added or changed since ``base``, plus uncommitted changes under entries/.

    Uses ``git diff --name-only --diff-filter=ACMR <base>...HEAD -- entries/``
    and ``git status --porcelain --untracked-files=all -- entries/`` (without
    ``--untracked-files=all`` a new, untracked shard directory is listed as the
    directory alone and its files are missed).  Returns sorted absolute Paths
    of files that still exist.
    """
    root = _root(root)
    names = set()
    try:
        out = _git(["diff", "--name-only", "--diff-filter=ACMR", "%s...HEAD" % base, "--", "entries/"], root)
    except RuntimeError as exc:
        print("warning: %s" % exc, file=sys.stderr)
        out = ""
    names.update(line.strip() for line in out.splitlines() if line.strip())
    for line in _git(["status", "--porcelain", "--untracked-files=all", "--", "entries/"], root).splitlines():
        if len(line) < 4:
            continue
        name = line[3:].strip()
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        names.add(name.strip('"'))
    paths = [root / n for n in names]
    return sorted(p for p in paths if p.is_file() and p.suffix == ".json")


# --------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="Shared library for the eex-dict tools; import it, do not run it.")
    parser.add_argument("--root", help="print the repository root and exit", action="store_true")
    args = parser.parse_args(argv)
    if args.root:
        print(ROOT)
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
