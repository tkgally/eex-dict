#!/usr/bin/env python3
"""Render the whole static site from entries/, journal/, metrics/, and sources/.

    python3 tools/build_site.py [--out docs] [--root DIR] [--entries DIR] [--quiet]

Only entries with ``provenance.status == "reviewed"`` are published; drafts are
never written anywhere.  A redirect stub (a renamed entry) and every line of
headwords/redirects.json become redirect pages.  ``--entries`` points the build
at another entries directory (the tests and site_check use a scratch copy of
the fixture); ``--root`` at another repository layout.

Pages written (every link relative, so the site works at any base URL):

    index.html                 home: search, description, counts, links
    w/<headword>.html          one page per headword with every entry of it;
                               anchors #<slug> and #<slug>-<sub_id>
    browse/index.html          A to Z and the frequency bands
    browse/<letter>.html       the headwords of one letter (0-9 for digits)
    browse/band-<n>.html       the headwords of one frequency band
    random.html                picks a random headword client-side
    recent.html                the 100 most recently created entries
    journal/index.html         the owner reports (journal/*.md rendered)
    journal/<name>.html
    about.html                 authorship disclosure, licences, counts, sources
    grammar-key.html           every grammar code with label and description
    labels-key.html            every usage label with its description
    pronunciation-key.html     the IPA symbols with key words
    redirect/<old-slug>.html   meta refresh to the new headword page
    search-index.json          the compact client-side index (forms, gloss)
    p/<headword>.json          the preview payload of one headword
    site.css, site.js          from tools/site/

The HTML shell is tools/site/page.html.  Two consecutive builds produce
identical output except for the build date on the about page.  Standard
library only.
"""

import argparse
import html
import json
import os
import posixpath
import re
import shutil
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402
import link_words  # noqa: E402

SITE_NAME = "TKG English Learner's Dictionary"
GITHUB_URL = "https://github.com/tkgally/eex-dict"
DISCLOSURE = ("Every entry was written by language models and reviewed by other language models; "
              "no human has checked most entries.")
BAND_TITLE = "Frequency bands are this dictionary's own editorial estimates, not counts from a corpus."
DV_TITLE = "One of the about 2,500 words the definitions are written with"
TEMPLATE_DIR = HERE / "site"
RECENT_COUNT = 100
GLOSS_LIMIT = 80

FORM_NAMES = OrderedDict([
    ("plural", "plural"),
    ("third_person_singular", "third-person singular"),
    ("past_tense", "past tense"),
    ("past_participle", "past participle"),
    ("present_participle", "present participle"),
    ("comparative", "comparative"),
    ("superlative", "superlative"),
])
ADAPTATION_LABELS = OrderedDict([
    ("semantic", "Meaning across languages"),
    ("grammar", "Grammar trap"),
    ("culture", "Cultural background"),
    ("false_friends", "False friends"),
    ("pronunciation", "Pronunciation trap"),
])
LABEL_GROUPS = ["register", "region", "domain", "currency", "attitude"]
STATUS_MARKS = {
    "disputed": ("?", "Disputed: the pronunciation checks disagreed about this transcription"),
    "unverified": ("*", "Unverified: this transcription has not been checked yet"),
}
PRON_KEY = {
    "consonants": [("p", "pen"), ("b", "bad"), ("t", "tea"), ("d", "did"), ("k", "cat"), ("ɡ", "get"),
                   ("tʃ", "chin"), ("dʒ", "jam"), ("f", "fall"), ("v", "van"), ("θ", "thin"), ("ð", "this"),
                   ("s", "see"), ("z", "zoo"), ("ʃ", "she"), ("ʒ", "vision"), ("h", "hat"), ("m", "man"),
                   ("n", "no"), ("ŋ", "sing"), ("l", "leg"), ("r", "red"), ("w", "wet"), ("j", "yes")],
    "american": [("i", "see"), ("ɪ", "sit"), ("ɛ", "bed"), ("æ", "cat"), ("ɑ", "father, hot"),
                 ("ɔ", "law (for speakers who keep it apart from the vowel of hot)"), ("ʊ", "put"), ("u", "too"),
                 ("ʌ", "cup"), ("ə", "about (the first sound)"), ("ɚ", "letter (the last sound)"), ("ɝ", "bird"),
                 ("eɪ", "day"), ("oʊ", "go"), ("aɪ", "my"), ("aʊ", "now"), ("ɔɪ", "boy")],
    "british": [("iː", "see"), ("i", "happy (the last sound)"), ("ɪ", "sit"), ("e", "bed"), ("æ", "cat"),
                ("ɑː", "father"), ("ɒ", "hot"), ("ɔː", "law"), ("ʊ", "put"), ("uː", "too"), ("ʌ", "cup"),
                ("ə", "about (the first sound)"), ("ɜː", "bird"), ("eɪ", "day"), ("əʊ", "go"), ("aɪ", "my"),
                ("aʊ", "now"), ("ɔɪ", "boy"), ("ɪə", "near"), ("eə", "hair"), ("ʊə", "pure")],
    "marks": [("ˈ", "primary stress: the syllable that follows is the strongest"),
              ("ˌ", "secondary stress"), (".", "a syllable break")],
}


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def slug_text(text):
    return eexlib._slug_text(text)


def anchor_id(table, value):
    return "%s-%s" % (table.replace("_", "-"), slug_text(value) or "x")


def build_date():
    """The UTC build date; SOURCE_DATE_EPOCH makes it reproducible."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch and epoch.isdigit():
        return datetime.fromtimestamp(int(epoch), tz=timezone.utc).strftime("%Y-%m-%d")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def plain_prose(text):
    """Prose with its inline marks removed and ``[[slug|text]]`` overrides reduced to their visible text."""
    return link_words.plain_text(str(text or ""))


def gloss(text, limit=GLOSS_LIMIT):
    text = " ".join(plain_prose(text).split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


# --------------------------------------------------------------------------
# A minimal markdown converter (headings, paragraphs, lists, bold, italic,
# links, code spans, fenced code, block quotes, rules, pipe tables)
# --------------------------------------------------------------------------

_MD_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_MD_UL = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_MD_OL = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
_MD_HR = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_MD_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")


def md_inline(text, link=None):
    codes = []

    def stash(m):
        codes.append(html.escape(m.group(2), quote=False))
        return "\x00%d\x00" % (len(codes) - 1)

    text = re.sub(r"(`+)(.+?)\1", stash, text)
    text = html.escape(text, quote=False)

    def make_link(m):
        url = html.unescape(m.group(2))
        if link:
            url = link(url)
        return '<a href="%s">%s</a>' % (html.escape(url, quote=True), m.group(1))

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+&quot;[^&]*&quot;)?\)", make_link, text)
    text = re.sub(r"&lt;(https?://[^\s&]+)&gt;", r'<a href="\1">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)__(.+?)__(?!\w)", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: "<code>%s</code>" % codes[int(m.group(1))], text)
    return text


def _md_render_list(items, link):
    def render(start, end):
        parts = []
        open_tag = None
        k = start
        while k < end:
            indent, ordered, text = items[k]
            tag = "ol" if ordered else "ul"
            if tag != open_tag:
                if open_tag:
                    parts.append("</%s>" % open_tag)
                parts.append("<%s>" % tag)
                open_tag = tag
            j = k + 1
            while j < end and items[j][0] > indent:
                j += 1
            inner = md_inline(text, link)
            if j > k + 1:
                inner += render(k + 1, j)
            parts.append("<li>%s</li>" % inner)
            k = j
        if open_tag:
            parts.append("</%s>" % open_tag)
        return "".join(parts)
    return render(0, len(items))


def _md_list(lines, i, out, link):
    items = []
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            j = i
            while j < n and not lines[j].strip():
                j += 1
            if j < n and (_MD_UL.match(lines[j]) or _MD_OL.match(lines[j])):
                i = j
                continue
            break
        m = _MD_UL.match(line)
        ordered = False
        if not m:
            m = _MD_OL.match(line)
            ordered = True
        if m:
            items.append([len(m.group(1).expandtabs(4)), ordered, m.group(2)])
        elif items and line[:1] in (" ", "\t"):
            items[-1][2] += " " + line.strip()
        else:
            break
        i += 1
    if items:
        out.append(_md_render_list(items, link))
    return i


def _md_cells(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip() for c in row.split("|")]


def _md_table(lines, i, out, link):
    header = _md_cells(lines[i])
    i += 2
    body = []
    while i < len(lines) and lines[i].strip() and "|" in lines[i]:
        body.append(_md_cells(lines[i]))
        i += 1
    head = "".join("<th>%s</th>" % md_inline(c, link) for c in header)
    rows = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % md_inline(c, link) for c in r) for r in body)
    out.append('<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (head, rows))
    return i


def md_to_html(text, link=None):
    """Convert markdown to HTML.  ``link`` rewrites every link target (a callable url -> url)."""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    out = []
    para = []
    n = len(lines)
    i = 0

    def flush():
        if para:
            out.append("<p>%s</p>" % md_inline(" ".join(s.strip() for s in para), link))
            del para[:]

    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            lang = stripped[3:].strip()
            j = i + 1
            buf = []
            while j < n and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            cls = ' class="lang-%s"' % esc(lang) if lang else ""
            out.append("<pre><code%s>%s</code></pre>" % (cls, html.escape("\n".join(buf), quote=False)))
            i = j + 1
            continue
        if not stripped:
            flush()
            i += 1
            continue
        m = _MD_HEADING.match(line)
        if m:
            flush()
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, md_inline(m.group(2), link), level))
            i += 1
            continue
        if _MD_HR.match(line):
            flush()
            out.append("<hr>")
            i += 1
            continue
        if stripped.startswith(">"):
            flush()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote>%s</blockquote>" % md_to_html("\n".join(buf), link))
            continue
        if "|" in stripped and i + 1 < n and _MD_TABLE_SEP.match(lines[i + 1]) and "|" in lines[i + 1]:
            flush()
            i = _md_table(lines, i, out, link)
            continue
        if _MD_UL.match(line) or _MD_OL.match(line):
            flush()
            i = _md_list(lines, i, out, link)
            continue
        para.append(line)
        i += 1
    flush()
    return "\n".join(out)


def md_title(text, fallback):
    for line in (text or "").splitlines():
        m = _MD_HEADING.match(line)
        if m:
            return re.sub(r"[*_`]", "", m.group(2)).strip() or fallback
    return fallback


def repo_link_rewriter(from_dir):
    """Relative links in a repository markdown file point at the file on GitHub."""
    def rewrite(url):
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) or url.startswith("#") or url.startswith("/"):
            return url
        target, _, fragment = url.partition("#")
        path = posixpath.normpath(posixpath.join(from_dir, target)) if target else from_dir
        if path.startswith(".."):
            return url
        kind = "tree" if target.endswith("/") or not target else "blob"
        return "%s/%s/main/%s%s" % (GITHUB_URL, kind, path, ("#" + fragment) if fragment else "")
    return rewrite


def journal_link_rewriter(url):
    """A journal report's link to another report opens the rendered page."""
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) or url.startswith("#") or url.startswith("/"):
        return url
    if url.endswith(".md") and "/" not in url:
        return url[:-3] + ".html"
    return url


# --------------------------------------------------------------------------
# The builder
# --------------------------------------------------------------------------

class Builder:
    def __init__(self, root=None, entries_dir=None, out=None, quiet=False):
        self.root = Path(root).resolve() if root else eexlib.ROOT
        self.entries_dir = Path(entries_dir).resolve() if entries_dir else self.root / "entries"
        self.out = Path(out).resolve() if out else self.root / "docs"
        self.quiet = quiet
        self.vocab = eexlib.load_vocab(self.root)
        self.pos_order = {code: i for i, code in enumerate(eexlib.vocab_values("pos", self.vocab))}
        self.template = (TEMPLATE_DIR / "page.html").read_text(encoding="utf-8")
        self.date = build_date()
        self.entries = []
        self.stubs = []
        self.drafts = 0
        self.by_slug = {}
        self.pages = OrderedDict()   # page name -> {"display": headword, "entries": [entry, ...]}
        self.redirects = OrderedDict()
        self.index = None
        self.files_written = 0

    # -- loading ----------------------------------------------------------

    def log(self, msg):
        if not self.quiet:
            print(msg)

    def load(self):
        entries = []
        if self.entries_dir.is_dir():
            for path in sorted(p for p in self.entries_dir.rglob("*.json") if p.is_file()):
                try:
                    d = eexlib.load_json(path)
                except (OSError, ValueError) as exc:
                    self.log("warning: skipping %s (%s)" % (path, exc))
                    continue
                if not isinstance(d, dict):
                    continue
                if eexlib.is_redirect_stub(d):
                    self.stubs.append(d)
                    continue
                if not d.get("slug") or not d.get("headword"):
                    continue
                if (d.get("provenance") or {}).get("status") != "reviewed":
                    self.drafts += 1
                    continue
                entries.append(d)
        entries.sort(key=self.entry_sort_key)
        self.entries = entries
        self.by_slug = {e["slug"]: e for e in entries}
        for e in entries:
            page = self.page_of(e)
            group = self.pages.setdefault(page, {"display": e["headword"], "entries": []})
            group["entries"].append(e)
        self.pages = OrderedDict(sorted(self.pages.items(), key=lambda kv: (kv[0], kv[1]["display"])))
        redirects_path = self.root / "headwords" / "redirects.json"
        if redirects_path.is_file():
            try:
                data = eexlib.load_json(redirects_path)
            except (OSError, ValueError):
                data = {}
            if isinstance(data, dict):
                for old, new in sorted(data.items()):
                    if isinstance(old, str) and isinstance(new, str):
                        self.redirects[old] = new
        for stub in self.stubs:
            old, new = stub.get("slug"), stub.get("redirect_to")
            if isinstance(old, str) and isinstance(new, str) and old not in self.redirects:
                self.redirects[old] = new
        self.index = link_words.build_index(entries)

    def entry_sort_key(self, e):
        return (self.page_of(e), self.pos_order.get(e.get("pos"), 99), int(e.get("homograph") or 1), e["slug"])

    @staticmethod
    def page_of(entry):
        return link_words.page_name(entry["slug"])

    # -- output -----------------------------------------------------------

    def prepare_out(self):
        out = self.out
        if out == self.root or out in self.root.parents:
            raise SystemExit("refusing to build into %s" % out)
        if out.exists():
            if any(out.iterdir()) and not (out / "site.css").exists():
                raise SystemExit("refusing to overwrite %s: it is not empty and not a previous build (no site.css)" % out)
            shutil.rmtree(out)
        out.mkdir(parents=True)

    def write(self, relpath, text):
        path = self.out / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self.files_written += 1

    @staticmethod
    def base_for(relpath):
        depth = relpath.count("/")
        return "../" * depth

    def page(self, relpath, title, content, kind="page", description="", head=""):
        base = self.base_for(relpath)
        full_title = SITE_NAME if relpath == "index.html" else "%s | %s" % (title, SITE_NAME)
        page = self.template
        for key, value in (("{{base}}", base), ("{{title}}", esc(full_title)), ("{{description}}", esc(description)),
                           ("{{head}}", head), ("{{kind}}", esc(kind)), ("{{site_name}}", esc(SITE_NAME)),
                           ("{{search_id}}", "site-search"), ("{{disclosure}}", esc(DISCLOSURE)), ("{{content}}", content)):
            page = page.replace(key, value)
        self.write(relpath, page)

    # -- prose and small renderers ------------------------------------------

    def prose(self, text, slug, base):
        return self.index.link(text, slug, base)

    def example_prose(self, text, slug, base):
        """An example sentence: linked like prose, with the entry's own headword marked (wiki/decisions/inline-markup.md)."""
        return self.index.link(text, slug, base, mark_self=True)

    def pos_label(self, code):
        return (self.vocab.get("pos", {}).get(code) or {}).get("label") or code

    def band_label(self, band):
        return (self.vocab.get("frequency_bands", {}).get(str(band)) or {}).get("label") or ("band %s" % band)

    def vocab_info(self, table, value):
        return self.vocab.get(table, {}).get(value) or {}

    def gram_link(self, table, value, base):
        info = self.vocab_info(table, value)
        code = info.get("code") or value
        label = info.get("label") or value
        return ('<a class="gram" href="%sgrammar-key.html#%s" title="%s">%s <span class="code">[%s]</span></a>'
                % (base, anchor_id(table, value), esc(info.get("description", "")), esc(label), esc(code)))

    def render_grammar(self, g, base):
        if not g:
            return ""
        items = []
        if g.get("countability"):
            items.append(self.gram_link("countability", g["countability"], base))
        if g.get("transitivity"):
            items.append(self.gram_link("transitivity", g["transitivity"], base))
        for code in g.get("codes") or []:
            items.append(self.gram_link("grammar_codes", code, base))
        for pattern in g.get("patterns") or []:
            items.append(self.gram_link("verb_patterns", pattern, base))
        return " ".join(items)

    def render_labels(self, labels, base):
        if not labels:
            return ""
        chips = []
        for group in LABEL_GROUPS:
            for value in labels.get(group) or []:
                desc = self.vocab_info(group, value).get("description", "")
                chips.append('<a class="chip chip-%s" href="%slabels-key.html#%s" title="%s">%s</a>'
                             % (esc(group), base, anchor_id(group, value), esc(desc), esc(value)))
        return "".join(chips)

    def render_transcription(self, label, t):
        if not t or not t.get("ipa"):
            return ""
        mark = ""
        status = t.get("status")
        if status in STATUS_MARKS:
            sym, title = STATUS_MARKS[status]
            if t.get("checked_by"):
                title += " (" + str(t["checked_by"]) + ")"
            mark = '<sup class="mark %s" title="%s">%s</sup>' % (esc(status), esc(title), sym)
        return '<span class="pron"><span class="pron-label">%s</span> /<span class="ipa">%s</span>/%s</span>' % (
            esc(label), esc(t["ipa"]), mark)

    def render_pronunciation(self, p, slug, base, cls="pron-line"):
        if not p:
            return ""
        parts = [self.render_transcription("American", p.get("american")),
                 self.render_transcription("British", p.get("british"))]
        for v in p.get("variants") or []:
            if not v or not v.get("ipa"):
                continue
            label = "also"
            if v.get("region"):
                label = "also (%s)" % v["region"]
            extra = self.render_transcription(label, {"ipa": v["ipa"], "status": "verified"})
            if v.get("note"):
                extra += ' <span class="muted small">%s</span>' % self.prose(v["note"], slug, base)
            parts.append(extra)
        if p.get("notes"):
            parts.append('<span class="muted small">%s</span>' % self.prose(p["notes"], slug, base))
        parts = [x for x in parts if x]
        if not parts:
            return ""
        return '<div class="%s">%s</div>' % (cls, " ".join(parts))

    def render_variants(self, variants, slug, base):
        rows = []
        for v in variants or []:
            if not v or not v.get("form"):
                continue
            kind = v.get("kind") or "form"
            region = v.get("region")
            if region:
                lead = "%s %s" % (region, kind)
            else:
                lead = "Also spelled" if kind == "spelling" else "Also"
            text = "%s: <b>%s</b>" % (esc(lead), esc(v["form"]))
            if v.get("note"):
                text += ' <span class="muted">(%s)</span>' % self.prose(v["note"], slug, base)
            rows.append('<div class="variants">%s</div>' % text)
        return "".join(rows)

    def render_inflections(self, inflections, slug, base):
        if not inflections:
            return ""
        forms = inflections.get("forms") or {}
        parts = []
        for key, name in FORM_NAMES.items():
            value = forms.get(key)
            if value:
                parts.append('<span class="form"><span class="form-name">%s</span> <b>%s</b></span>' % (esc(name), esc(value)))
        for key, value in forms.items():
            if key not in FORM_NAMES and value:
                parts.append('<span class="form"><span class="form-name">%s</span> <b>%s</b></span>' % (esc(key.replace("_", " ")), esc(value)))
        if inflections.get("note"):
            parts.append('<span class="note">%s</span>' % self.prose(inflections["note"], slug, base))
        if not parts:
            return ""
        return '<div class="inflections">%s</div>' % " ".join(parts)

    def render_frequency(self, freq, base):
        if not freq:
            return ""
        band = freq.get("band")
        parts = []
        if band:
            parts.append('<a class="band band-%s" href="%sbrowse/band-%s.html" title="%s">%s</a>'
                         % (esc(band), base, esc(band), esc(BAND_TITLE), esc(self.band_label(band))))
        if freq.get("defining_vocabulary"):
            parts.append('<span class="chip dv" title="%s">defining vocabulary</span>' % esc(DV_TITLE))
        return "".join(parts)

    def xref(self, slug, base, form=None):
        """A link to an entry that is published, else its headword as plain text."""
        e = self.by_slug.get(slug)
        if e is not None:
            text = form or e["headword"]
            return '<a class="xref" href="%sw/%s.html#%s">%s</a>' % (base, esc(self.page_of(e)), esc(slug), esc(text))
        text = form or link_words.headword_from_slug(slug)
        return '<span class="xref-missing" title="no entry yet: %s">%s</span>' % (esc(slug), esc(text))

    def render_xref_list(self, label, refs, slug, base, cls="xrefs"):
        if not refs:
            return ""
        items = []
        for r in refs:
            if not r or not r.get("slug"):
                continue
            item = self.xref(r["slug"], base)
            if r.get("note"):
                item += ' <span class="xref-note">(%s)</span>' % self.prose(r["note"], slug, base)
            items.append(item)
        if not items:
            return ""
        return '<p class="%s"><span class="xref-type">%s</span> %s</p>' % (cls, esc(label), "; ".join(items))

    def render_examples(self, examples, slug, base):
        if not examples:
            return ""
        items = []
        for ex in examples:
            if not ex or not ex.get("text"):
                continue
            text = '<span class="ex">%s</span>' % self.example_prose(ex["text"], slug, base)
            if ex.get("pattern"):
                info = self.vocab_info("verb_patterns", ex["pattern"])
                text += ' <a class="pattern" href="%sgrammar-key.html#%s" title="%s">%s</a>' % (
                    base, anchor_id("verb_patterns", ex["pattern"]), esc(info.get("label") or ex["pattern"]),
                    esc(info.get("code") or ex["pattern"]))
            if ex.get("note"):
                text += ' <span class="ex-note">(%s)</span>' % self.prose(ex["note"], slug, base)
            items.append("<li>%s</li>" % text)
        return '<ul class="examples">%s</ul>' % "".join(items) if items else ""

    def render_collocations(self, collocations, slug, base):
        if not collocations:
            return ""
        rows = []
        for c in collocations:
            if not c or not c.get("items"):
                continue
            desc = self.vocab_info("collocation_types", c.get("type", "")).get("description", "")
            items = ", ".join(self.prose(x, slug, base) for x in c["items"])
            rows.append('<div class="colloc"><span class="colloc-type" title="%s">%s</span> %s</div>'
                        % (esc(desc), esc(c.get("type", "")), items))
        if not rows:
            return ""
        return '<div class="box collocations"><h3>Collocations</h3>%s</div>' % "".join(rows)

    def render_adaptation(self, adaptation, l1, slug, base, title):
        rows = []
        for kind, label in ADAPTATION_LABELS.items():
            value = (adaptation or {}).get(kind)
            if value:
                rows.append('<div class="adapt"><span class="adapt-kind">%s</span> %s</div>' % (esc(label), self.prose(value, slug, base)))
        for code, value in sorted((l1 or {}).items()):
            if not isinstance(value, dict):
                continue
            eq = ", ".join(esc(x) for x in value.get("equivalents") or [])
            text = eq or '<span class="muted">(no equivalents yet)</span>'
            if value.get("note"):
                text += " — " + self.prose(value["note"], slug, base)
            if value.get("status"):
                text += ' <span class="l1-status">(%s)</span>' % esc(value["status"])
            rows.append('<div class="l1"><span class="adapt-kind" title="language code">%s</span> %s</div>' % (esc(code), text))
        if not rows:
            return ""
        return '<div class="translator box"><h3>%s</h3>%s</div>' % (esc(title), "".join(rows))

    # -- senses --------------------------------------------------------------

    def render_sense_body(self, s, slug, base):
        parts = []
        gram = self.render_grammar(s.get("grammar"), base)
        labels = self.render_labels(s.get("labels"), base)
        if s.get("explanation"):
            parts.append('<p class="expl">%s</p>' % self.prose(s["explanation"], slug, base))
        if gram or labels:
            parts.append('<p class="gram-line">%s</p>' % " ".join(x for x in (gram, labels) if x))
        if s.get("pronunciation"):
            parts.append(self.render_pronunciation(s["pronunciation"], slug, base, cls="pron-line sense-pron"))
        parts.append(self.render_examples(s.get("examples"), slug, base))
        parts.append(self.render_collocations(s.get("collocations"), slug, base))
        parts.append(self.render_xref_list("Synonyms", s.get("synonyms"), slug, base))
        parts.append(self.render_xref_list("Antonyms", s.get("antonyms"), slug, base))
        parts.append(self.render_xref_list("Compare", s.get("compare"), slug, base))
        return "".join(parts)

    def render_sense(self, s, e, base):
        slug = e["slug"]
        n = s.get("n")
        sense_id = "%s-s%s" % (slug, n) if n else None
        head = ""
        if s.get("signpost"):
            head += '<span class="signpost">%s</span>' % esc(s["signpost"])
        head += '<span class="def">%s</span>' % self.prose(s.get("definition", ""), slug, base)
        body = ['<p class="def-line">%s</p>' % head, self.render_sense_body(s, slug, base)]
        subs = []
        for sub in s.get("subsenses") or []:
            letter = sub.get("letter") or ""
            sub_head = '<span class="subsense-letter">%s</span><span class="def">%s</span>' % (
                esc(letter), self.prose(sub.get("definition", ""), slug, base))
            subs.append('<li class="subsense"><p class="def-line">%s</p>%s</li>' % (sub_head, self.render_sense_body(sub, slug, base)))
        if subs:
            body.append('<ol class="subsenses">%s</ol>' % "".join(subs))
        title = "For translators (sense %s)" % n if n else "For translators"
        body.append(self.render_adaptation(s.get("adaptation"), s.get("l1"), slug, base, title))
        attr = ' id="%s"' % esc(sense_id) if sense_id else ""
        value = ' value="%d"' % int(n) if isinstance(n, int) else ""
        return '<li class="sense"%s%s>%s</li>' % (attr, value, "".join(body))

    def render_phrase(self, ph, e, base):
        slug = e["slug"]
        pid = "%s-%s" % (slug, ph.get("sub_id") or slug_text(ph.get("text", "")))
        parts = ['<div class="phrase" id="%s">' % esc(pid)]
        labels = self.render_labels(ph.get("labels"), base)
        parts.append('<p class="phrase-head">%s %s</p>' % (esc(ph.get("text", "")), labels))
        parts.append('<p class="def-line"><span class="def">%s</span></p>' % self.prose(ph.get("definition", ""), slug, base))
        if ph.get("explanation"):
            parts.append('<p class="expl">%s</p>' % self.prose(ph["explanation"], slug, base))
        parts.append(self.render_examples(ph.get("examples"), slug, base))
        parts.append(self.render_adaptation(ph.get("adaptation"), ph.get("l1"), slug, base, "For translators (phrase)"))
        parts.append("</div>")
        return "".join(parts)

    # -- the entry ------------------------------------------------------------

    def render_entry(self, e, base):
        slug = e["slug"]
        parts = ['<article class="entry" id="%s">' % esc(slug)]
        homograph = int(e.get("homograph") or 1)
        title = '<span class="hw">%s</span>' % esc(e["headword"])
        if homograph > 1:
            title += '<span class="homograph" title="homograph %d">%d</span>' % (homograph, homograph)
        title += '<span class="pos">%s</span>' % esc(self.pos_label(e.get("pos")))
        parts.append('<h2 class="entry-title">%s</h2>' % title)
        parts.append(self.render_pronunciation(e.get("pronunciation"), slug, base))
        parts.append(self.render_variants(e.get("variants"), slug, base))
        parts.append(self.render_inflections(e.get("inflections"), slug, base))
        meta = self.render_frequency(e.get("frequency"), base) + self.render_labels(e.get("labels"), base)
        if meta:
            parts.append('<div class="entry-meta">%s</div>' % meta)
        if e.get("core_idea"):
            parts.append('<p class="core-idea">%s</p>' % self.prose(e["core_idea"], slug, base))
        senses = [self.render_sense(s, e, base) for s in e.get("senses") or []]
        if senses:
            parts.append('<ol class="senses">%s</ol>' % "".join(senses))
        phrases = [self.render_phrase(ph, e, base) for ph in e.get("phrases") or []]
        if phrases:
            parts.append('<section class="phrases"><h3>Phrases</h3>%s</section>' % "".join(phrases))
        parts.append(self.render_word_family(e, base))
        parts.append(self.render_synonym_discrimination(e, base))
        if e.get("usage_note"):
            parts.append('<div class="box usage"><h3>Usage</h3><p>%s</p></div>' % self.prose(e["usage_note"], slug, base))
        parts.append(self.render_learner_errors(e, base))
        parts.append(self.render_etymology(e, base))
        see_also = self.render_xref_list("See also", e.get("see_also"), slug, base, cls="xrefs see-also")
        if see_also:
            parts.append(see_also)
        parts.append(self.render_adaptation(e.get("adaptation"), e.get("l1"), slug, base, "For translators"))
        parts.append("</article>")
        return "".join(parts)

    def render_word_family(self, e, base):
        members = [m for m in e.get("word_family") or [] if m and m.get("slug")]
        if not members:
            return ""
        items = []
        for m in members:
            item = self.xref(m["slug"], base, form=m.get("form"))
            if m.get("note"):
                item += ' <span class="xref-note">(%s)</span>' % self.prose(m["note"], e["slug"], base)
            items.append("<li>%s</li>" % item)
        return '<div class="box family"><h3>Word family</h3><ul>%s</ul></div>' % "".join(items)

    def render_synonym_discrimination(self, e, base):
        sd = e.get("synonym_discrimination")
        if not sd or not sd.get("note"):
            return ""
        words = " · ".join(self.xref(w, base) for w in sd.get("words") or [])
        return '<div class="box discrimination"><h3>Choosing between %s</h3><p>%s</p></div>' % (
            words or "similar words", self.prose(sd["note"], e["slug"], base))

    def render_learner_errors(self, e, base):
        errors = [x for x in e.get("learner_errors") or [] if x and x.get("incorrect")]
        if not errors:
            return ""
        rows = []
        for x in errors:
            row = '<span class="incorrect">%s</span> <span class="correct">%s</span>' % (esc(x["incorrect"]), esc(x.get("correct", "")))
            if x.get("note"):
                row += '<br><span class="note">%s</span>' % self.prose(x["note"], e["slug"], base)
            rows.append('<div class="learner-error">%s</div>' % row)
        return '<div class="box errors"><h3>Common mistakes</h3>%s</div>' % "".join(rows)

    def render_etymology(self, e, base):
        et = e.get("etymology")
        if not et or not et.get("text"):
            return ""
        sources = ", ".join(esc(s) for s in et.get("sources_consulted") or [])
        tail = ""
        if sources:
            tail = '<p class="sources">Checked against: %s%s</p>' % (sources, (" (%s)" % esc(et["checked"])) if et.get("checked") else "")
        return '<div class="box etymology"><h3>Word origin</h3><p>%s</p>%s</div>' % (self.prose(et["text"], e["slug"], base), tail)

    # -- headword pages ---------------------------------------------------------

    def headword_page(self, page, group):
        relpath = "w/%s.html" % page
        base = self.base_for(relpath)
        entries = group["entries"]
        parts = ['<h1 class="page-hw">%s</h1>' % esc(group["display"])]
        if len(entries) > 1:
            jumps = " · ".join('<a href="#%s">%s%s</a>' % (esc(e["slug"]), esc(self.pos_label(e.get("pos"))),
                                                          ('<sup>%d</sup>' % e["homograph"]) if int(e.get("homograph") or 1) > 1 else "")
                               for e in entries)
            parts.append('<p class="muted small entry-jumps">%d entries: %s</p>' % (len(entries), jumps))
        for e in entries:
            parts.append(self.render_entry(e, base))
        first = entries[0]
        description = gloss(((first.get("senses") or [{}])[0]).get("definition", ""), 150)
        self.page(relpath, group["display"], "\n".join(parts), kind="entry", description=description)

    def preview_payload(self, page, group):
        payload = {"w": group["display"], "e": []}
        for e in group["entries"]:
            first = (e.get("senses") or [{}])[0]
            payload["e"].append({"s": e["slug"], "pos": self.pos_label(e.get("pos")),
                                 "hn": int(e.get("homograph") or 1), "d": plain_prose(first.get("definition", ""))})
        self.write("p/%s.json" % page, json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))

    def search_index(self):
        words = []
        for page, group in self.pages.items():
            forms = []
            slugs = []
            for e in group["entries"]:
                slugs.append(e["slug"])
                for value in ((e.get("inflections") or {}).get("forms") or {}).values():
                    for piece in link_words._split_forms(value):
                        if piece and piece.lower() != group["display"].lower() and piece not in forms:
                            forms.append(piece)
                for v in e.get("variants") or []:
                    form = (v or {}).get("form")
                    if form and form.lower() != group["display"].lower() and form not in forms:
                        forms.append(form)
            first = (group["entries"][0].get("senses") or [{}])[0]
            record = OrderedDict([("w", group["display"])])
            if page != group["display"]:
                record["p"] = page
            record["s"] = slugs
            if forms:
                record["f"] = forms
            g = gloss(first.get("definition", ""))
            if g:
                record["g"] = g
            words.append(record)
        pos = OrderedDict((code, self.pos_label(code)) for code in eexlib.vocab_values("pos", self.vocab))
        data = OrderedDict([("pos", pos), ("words", words)])
        self.write("search-index.json", json.dumps(data, ensure_ascii=False, separators=(",", ":")))

    # -- lists ------------------------------------------------------------------

    def word_item(self, page, group, base, with_band=True):
        pos = ", ".join(OrderedDict((self.pos_label(e.get("pos")), None) for e in group["entries"]).keys())
        item = '<a href="%sw/%s.html">%s</a> <span class="pos">%s</span>' % (base, esc(page), esc(group["display"]), esc(pos))
        if with_band:
            bands = sorted({int((e.get("frequency") or {}).get("band") or 0) for e in group["entries"]} - {0})
            if bands:
                item += ' <span class="band band-%d" title="%s">%s</span>' % (bands[0], esc(BAND_TITLE), esc(self.band_label(bands[0])))
        return "<li>%s</li>" % item

    @staticmethod
    def letter_of(page):
        first = page[:1]
        return first if first.isalpha() else "0-9"

    def browse_pages(self):
        letters = OrderedDict()
        for page, group in self.pages.items():
            letters.setdefault(self.letter_of(page), []).append((page, group))
        bands = OrderedDict((str(b), []) for b in eexlib.vocab_values("frequency_bands", self.vocab))
        for page, group in self.pages.items():
            for band in sorted({str((e.get("frequency") or {}).get("band") or "") for e in group["entries"]} - {""}):
                bands.setdefault(band, []).append((page, group))
        all_letters = [chr(c) for c in range(ord("a"), ord("z") + 1)] + ["0-9"]

        def letter_row(base):
            items = []
            for letter in all_letters:
                label = letter.upper() if letter != "0-9" else "0-9"
                if letter in letters:
                    items.append('<li><a href="%sbrowse/%s.html">%s</a></li>' % (base, letter, label))
                else:
                    items.append('<li><span>%s</span></li>' % label)
            return '<ul class="letters">%s</ul>' % "".join(items)
        self._letter_row = letter_row

        base = "../"
        content = ["<h1>Browse</h1>", "<h2>By letter</h2>", letter_row(base), "<h2>By frequency band</h2>", "<ul>"]
        for band, items in bands.items():
            info = self.vocab_info("frequency_bands", band)
            content.append('<li><a href="band-%s.html">%s</a> <span class="muted">(%d headwords): %s</span></li>' % (
                esc(band), esc(info.get("label") or band), len(items), esc(info.get("description", ""))))
        content.append("</ul>")
        content.append('<p class="muted small">%s</p>' % esc(BAND_TITLE))
        self.page("browse/index.html", "Browse", "\n".join(content), kind="browse")

        for letter, items in letters.items():
            label = letter.upper() if letter != "0-9" else "0-9"
            body = ['<h1>%s</h1>' % esc(label), letter_row(base),
                    '<p class="muted">%d headwords</p>' % len(items),
                    '<ul class="word-list">%s</ul>' % "".join(self.word_item(p, g, base) for p, g in items)]
            self.page("browse/%s.html" % letter, "Words beginning with %s" % label, "\n".join(body), kind="browse")

        for band, items in bands.items():
            info = self.vocab_info("frequency_bands", band)
            body = ['<h1>%s</h1>' % esc(info.get("label") or band),
                    '<p>%s <span class="muted">(%s)</span></p>' % (esc(info.get("description", "")), esc(BAND_TITLE)),
                    '<p class="muted">%d headwords</p>' % len(items),
                    '<ul class="word-list">%s</ul>' % "".join(self.word_item(p, g, base, with_band=False) for p, g in items)]
            self.page("browse/band-%s.html" % band, "Frequency band %s: %s" % (band, info.get("label") or ""), "\n".join(body), kind="browse")

    def recent_entries(self):
        def created(e):
            return str((e.get("provenance") or {}).get("created") or "")
        return sorted(self.entries, key=lambda e: (created(e), e["slug"]), reverse=True)[:RECENT_COUNT]

    def recent_item(self, e, base):
        first = (e.get("senses") or [{}])[0]
        return ('<li><span class="date">%s</span><a href="%sw/%s.html#%s">%s</a> <span class="pos">%s</span>'
                '<span class="gloss">%s</span></li>' % (
                    esc(str((e.get("provenance") or {}).get("created") or "")[:10]), base, esc(self.page_of(e)), esc(e["slug"]),
                    esc(e["headword"]), esc(self.pos_label(e.get("pos"))), self.prose(first.get("definition", ""), e["slug"], base)))

    def recent_page(self):
        recent = self.recent_entries()
        body = ["<h1>Recently added</h1>",
                '<p class="muted">The %d most recently created entries, newest first.</p>' % len(recent),
                '<ul class="recent-list">%s</ul>' % "".join(self.recent_item(e, "") for e in recent)]
        self.page("recent.html", "Recently added", "\n".join(body), kind="recent")

    def random_page(self):
        body = ["<h1>A random word</h1>",
                '<p class="redirect-note">Picking a random headword… If nothing happens, '
                '<a href="browse/index.html">browse the dictionary</a> instead.</p>']
        self.page("random.html", "Random word", "\n".join(body), kind="random")

    def home_page(self):
        n_entries = len(self.entries)
        n_pages = len(self.pages)
        n_phrases = sum(len(e.get("phrases") or []) for e in self.entries)
        recent = self.recent_entries()[:10]
        body = [
            "<h1>%s</h1>" % esc(SITE_NAME),
            '<p class="lead">An original English-English dictionary for intermediate and advanced learners. '
            'Plain definitions, examples that show the grammar and the typical word combinations, notes on the '
            'mistakes learners make, and, behind the toggle at the top, notes for translators. Every word in an '
            'entry that has its own entry is a link, and the search box understands inflected forms '
            '(type <i>ran</i> to find <i>run</i>).</p>',
            '<form class="search home-search" role="search" action="index.html" method="get" autocomplete="off">'
            '<label class="visually-hidden" for="home-search">Search the dictionary</label>'
            '<input id="home-search" class="search-input" type="search" name="q" placeholder="Search a word or any of its forms" '
            'spellcheck="false" autocapitalize="none"><ul class="search-results" hidden></ul></form>',
            '<ul class="counts"><li><b>%d</b> entries</li><li><b>%d</b> headwords</li><li><b>%d</b> phrases</li></ul>' % (
                n_entries, n_pages, n_phrases),
            '<ul class="home-links"><li><a href="browse/index.html">Browse A to Z</a></li>'
            '<li><a href="browse/band-1.html">By frequency band</a></li><li><a href="random.html">Random word</a></li>'
            '<li><a href="recent.html">Recently added</a></li><li><a href="journal/index.html">Journal</a></li>'
            '<li><a href="about.html">About</a></li></ul>',
            "<h2>Browse by letter</h2>", self._letter_row(""),
        ]
        if recent:
            body.append("<h2>Recently added</h2>")
            body.append('<ul class="recent-list">%s</ul>' % "".join(self.recent_item(e, "") for e in recent))
            body.append('<p><a href="recent.html">All recent entries</a></p>')
        body.append('<p class="muted small">%s <a href="about.html">Read how the dictionary is made.</a></p>' % esc(DISCLOSURE))
        self.page("index.html", "Home", "\n".join(body), kind="home",
                  description="An original English-English learner's dictionary written by language models, with plain definitions, "
                              "grammar patterns, collocations, and notes for translators.")

    # -- journal ----------------------------------------------------------------

    def journal_pages(self):
        journal_dir = self.root / "journal"
        reports = []
        if journal_dir.is_dir():
            for path in sorted(journal_dir.glob("*.md")):
                text = path.read_text(encoding="utf-8")
                title = md_title(text, path.stem)
                date = path.stem[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", path.stem) else ""
                reports.append((path.stem, title, date, text))
        for stem, title, date, text in reports:
            body = md_to_html(text, link=journal_link_rewriter)
            if not body.startswith("<h1"):
                body = "<h1>%s</h1>\n%s" % (esc(title), body)
            body += '\n<p class="muted small"><a href="index.html">All journal entries</a></p>'
            self.page("journal/%s.html" % stem, title, body, kind="journal")
        items = []
        for stem, title, date, _text in sorted(reports, key=lambda r: r[0], reverse=True):
            items.append('<li><span class="date">%s</span><a href="%s.html">%s</a></li>' % (esc(date), esc(stem), esc(title)))
        body = ["<h1>Journal</h1>",
                "<p>One plain-language report per session, written for the dictionary's owner and published here unchanged: "
                "what the session did, what it found, what went wrong, and what comes next.</p>",
                ('<ul class="journal-list">%s</ul>' % "".join(items)) if items else '<p class="muted">No reports yet.</p>']
        self.page("journal/index.html", "Journal", "\n".join(body), kind="journal")

    # -- about and keys -----------------------------------------------------------

    def latest_metrics(self):
        path = self.root / "metrics" / "history.jsonl"
        rows = []
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
        return rows

    def about_page(self):
        rows = self.latest_metrics()
        latest = rows[-1] if rows else {}
        n_entries = len(self.entries)
        by_band = OrderedDict()
        for band in eexlib.vocab_values("frequency_bands", self.vocab):
            by_band[band] = sum(1 for e in self.entries if str((e.get("frequency") or {}).get("band")) == band)
        dv = sum(1 for e in self.entries if (e.get("frequency") or {}).get("defining_vocabulary"))
        body = [
            "<h1>About this dictionary</h1>",
            "<p>The %s is an original English-English learner's dictionary written by language models under the direction "
            "of Tom Gally, a lexicographer, and published as a static website from the repository "
            '<a href="%s">%s</a>. It is meant for intermediate and advanced learners: the definitions are plain enough for an '
            "intermediate reader, and the grammar, collocations, and notes are complete enough for an advanced one.</p>" % (
                esc(SITE_NAME), GITHUB_URL, esc(GITHUB_URL.replace("https://", ""))),
            "<h2>Who wrote it</h2>",
            "<p><b>%s</b> The entries are drafted by a language model from its own knowledge and a written house style, then "
            "checked field by field by two other language models; a further model adjudicates their objections and records "
            "every decision. Pronunciations and inflected forms are checked by agreement between several models. Nothing in an "
            "entry is copied from another dictionary. Errors remain possible on every page: if a definition or example looks wrong, "
            "it may well be wrong.</p>" % esc(DISCLOSURE),
            "<h2>Frequency bands and levels</h2>",
            "<p>Each entry shows a frequency band in words, from <i>very common</i> to <i>rare</i>. <b>The bands are the "
            "dictionary's own editorial estimates</b>: several models were asked how basic, common, and important each word is, "
            "and the answers were settled editorially. No corpus counts, external frequency lists, or published word lists were "
            "used, and the bands are not CEFR levels. The <i>defining vocabulary</i> mark shows a word that belongs to the "
            "about 2,500 words the definitions are written with.</p>",
            "<h2>Counts</h2>",
            '<ul class="counts"><li><b>%d</b> entries published</li><li><b>%d</b> headwords</li><li><b>%d</b> phrases</li>'
            '<li><b>%d</b> defining-vocabulary entries</li></ul>' % (
                n_entries, len(self.pages), sum(len(e.get("phrases") or []) for e in self.entries), dv),
            '<div class="table-wrap"><table class="key-table"><thead><tr><th>Band</th><th>Entries</th></tr></thead><tbody>%s</tbody></table></div>' % "".join(
                "<tr><td>%s (%s)</td><td>%d</td></tr>" % (esc(self.band_label(b)), esc(b), n) for b, n in by_band.items()),
        ]
        if self.drafts:
            body.append('<p class="muted small">%d further entries are in draft and not yet published.</p>' % self.drafts)
        if latest:
            dvm = latest.get("defining_vocabulary") or {}
            queue = latest.get("queue") or {}
            coverage = dvm.get("coverage")
            body.append("<h3>From the project's run records</h3>")
            body.append("<ul>")
            body.append("<li>%d run%s recorded; the latest on %s.</li>" % (len(rows), "" if len(rows) == 1 else "s", esc(str(latest.get("ts", ""))[:10])))
            if "entries_total" in latest:
                body.append("<li>Entries in the repository at that run: %s (%s reviewed, %s draft).</li>" % (
                    esc(latest.get("entries_total")), esc(latest.get("entries_reviewed")), esc(latest.get("entries_draft"))))
            if dvm.get("size"):
                body.append("<li>Defining vocabulary: %s of %s words have an entry%s.</li>" % (
                    esc(dvm.get("with_entry")), esc(dvm.get("size")), (" (%d%%)" % round(coverage * 100)) if isinstance(coverage, (int, float)) else ""))
            if queue:
                body.append("<li>Headword queue: %s pending, %s done.</li>" % (esc(queue.get("pending", 0)), esc(queue.get("done", 0))))
            body.append("</ul>")
        else:
            body.append('<p class="muted small">No run records yet.</p>')
        body += [
            "<h2>Licences</h2>",
            "<p>The dictionary data (every entry, in JSON and as rendered here) is released under "
            '<a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>: it is in the public domain and may be '
            "copied, changed, and reused for any purpose without permission. The code that builds and runs this site is "
            'released under the <a href="https://opensource.org/licenses/MIT">MIT licence</a>. The repository contains only '
            "the project's own work: no word list, frequency list, pronouncing dictionary, or other data set is included or "
            "derived from, whatever its licence.</p>",
            "<h2>Resources consulted</h2>",
            "<p>The register below lists every outside resource the project's tools consult while checking a fact. None of "
            "them is included in the dictionary; a resource is read at run time and only the verdict is recorded.</p>",
        ]
        sources = self.root / "sources" / "README.md"
        if sources.is_file():
            body.append('<div class="box sources-register">%s</div>' % md_to_html(sources.read_text(encoding="utf-8"), link=repo_link_rewriter("sources")))
        else:
            body.append('<p class="muted">The register has not been written yet.</p>')
        body += [
            "<h2>Reading an entry</h2>",
            '<p>Grammar codes are explained in the <a href="grammar-key.html">grammar key</a>, usage labels in the '
            '<a href="labels-key.html">labels key</a>, and the phonetic symbols in the <a href="pronunciation-key.html">pronunciation key</a>. '
            'Every word in a definition, explanation, example, or note that has an entry of its own is a link; resting the pointer on it '
            '(or tapping it once on a phone) shows a preview. In an explanation or a note, a word in <b class="mention">bold</b> is being talked about as a word, '
            'and a phrase in <i class="illus">italics</i> is quoted as an illustration of use; in an example sentence the headword itself is in bold. '
            'The <b>translator\'s view</b> button at the top reveals notes written for '
            'anyone adapting the dictionary into another language: how the senses split across languages, grammar traps, cultural '
            'background, false friends, and pronunciation traps.</p>',
            '<p class="muted small">Site built on %s.</p>' % esc(self.date),
        ]
        self.page("about.html", "About", "\n".join(body), kind="about",
                  description="How the dictionary is written, reviewed, and licensed; who wrote it; what it counts.")

    def key_table(self, table, columns):
        rows = []
        for value in eexlib.vocab_values(table, self.vocab):
            info = self.vocab_info(table, value)
            cells = []
            for col in columns:
                if col == "label":
                    cells.append("<td>%s</td>" % esc(info.get("label") or value))
                elif col == "code":
                    cells.append('<td><span class="code">%s</span></td>' % esc(info.get("code") or ""))
                elif col == "value":
                    cells.append("<td>%s</td>" % esc(value))
                elif col == "applies_to":
                    applies = info.get("applies_to")
                    if isinstance(applies, list):
                        applies = ", ".join(str(x) for x in applies)
                    cells.append("<td>%s</td>" % esc(applies or ""))
                else:
                    cells.append("<td>%s</td>" % esc(info.get(col) or ""))
            rows.append('<tr id="%s">%s</tr>' % (esc(anchor_id(table, value)), "".join(cells)))
        return rows

    def grammar_key_page(self):
        def section(title, table, columns, headers, intro):
            return ('<h2 id="%s">%s</h2><p>%s</p><div class="table-wrap"><table class="key-table"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                    % (esc(table.replace("_", "-")), esc(title), esc(intro), "".join("<th>%s</th>" % esc(h) for h in headers),
                       "".join(self.key_table(table, columns))))
        body = [
            "<h1>Grammar key</h1>",
            "<p>Every sense shows its grammar spelled out, with the short code in brackets: <i>countable [C]</i>, "
            "<i>verb + object [V + obj]</i>. This page lists every code the dictionary uses.</p>",
            section("Countability (nouns)", "countability", ["label", "code", "description"], ["Label", "Code", "Meaning"],
                    "Whether a noun has a plural and can follow a or an."),
            section("Transitivity (verbs)", "transitivity", ["label", "code", "description"], ["Label", "Code", "Meaning"],
                    "Whether a verb takes a direct object in the sense shown."),
            section("Verb patterns", "verb_patterns", ["label", "code", "description", "example"], ["Pattern", "Code", "Meaning", "Example"],
                    "What follows the verb. An example marked with a pattern shows that pattern."),
            section("Other grammar codes", "grammar_codes", ["label", "code", "description", "applies_to"], ["Label", "Code", "Meaning", "Applies to"],
                    "Restrictions on position, gradability, and number."),
        ]
        self.page("grammar-key.html", "Grammar key", "\n".join(body), kind="key")

    def labels_key_page(self):
        titles = {"register": "Register", "region": "Region", "domain": "Domain", "currency": "Currency", "attitude": "Attitude"}
        intros = {
            "register": "How formal the word is, and warnings for words that offend.",
            "region": "Where a word is mainly used. A word used everywhere has no region label.",
            "domain": "The field a word belongs to, given only when the word is tied to the field.",
            "currency": "Words that sound old, words for things of the past, and words that are new.",
            "attitude": "The speaker's stance, which a definition alone cannot show.",
        }
        body = ["<h1>Labels key</h1>",
                "<p>Labels appear as small chips on an entry or a sense. They come from five closed sets written in plain words for this dictionary.</p>"]
        for group in LABEL_GROUPS:
            doc = (self.vocab.get(group) or {}).get("_doc")
            body.append('<h2 id="%s">%s</h2><p>%s</p>' % (esc(group), esc(titles[group]), esc(doc or intros[group])))
            body.append('<div class="table-wrap"><table class="key-table"><thead><tr><th>Label</th><th>Meaning</th></tr></thead><tbody>%s</tbody></table></div>'
                        % "".join(self.key_table(group, ["value", "description"])))
        self.page("labels-key.html", "Labels key", "\n".join(body), kind="key")

    def used_symbols(self):
        used = set()
        for e in self.entries:
            p = e.get("pronunciation") or {}
            for t in (p.get("american"), p.get("british")):
                if t and t.get("ipa"):
                    used.update(ch for ch in t["ipa"] if not ch.isspace())
            for s in e.get("senses") or []:
                sp = s.get("pronunciation") or {}
                for t in (sp.get("american"), sp.get("british")):
                    if t and t.get("ipa"):
                        used.update(ch for ch in t["ipa"] if not ch.isspace())
        return used

    def pronunciation_key_page(self):
        def table(title, rows, head=("Symbol", "As in")):
            body = "".join('<tr><td><span class="ipa">%s</span></td><td>%s</td></tr>' % (esc(sym), esc(word)) for sym, word in rows)
            return '<h2>%s</h2><div class="table-wrap"><table class="key-table"><thead><tr><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>' % (
                esc(title), esc(head[0]), esc(head[1]), body)
        known = set()
        for rows in PRON_KEY.values():
            for sym, _ in rows:
                known.update(sym)
        used = self.used_symbols()
        extra = sorted(used - known - {"/", "-", " "})
        body = ["<h1>Pronunciation key</h1>",
                "<p>Every entry gives an American pronunciation (General American) and a British one (Standard Southern British) "
                "in the International Phonetic Alphabet, between slashes. The mark <span class=\"mark\">?</span> after a transcription "
                "means the checks disagreed about it; <span class=\"mark\">*</span> means it has not been checked yet. "
                "The key words below are ordinary words that contain the sound in the accent named.</p>",
                table("Stress and syllables", PRON_KEY["marks"], head=("Mark", "Meaning")),
                table("Consonants (both accents)", PRON_KEY["consonants"]),
                table("Vowels, American", PRON_KEY["american"]),
                table("Vowels, British", PRON_KEY["british"])]
        if extra:
            body.append('<p class="muted small">Other symbols that occur in entries: %s.</p>' % ", ".join(esc(s) for s in extra))
        self.page("pronunciation-key.html", "Pronunciation key", "\n".join(body), kind="key")

    # -- redirects -----------------------------------------------------------------

    def redirect_page(self, relpath, target_slug, old_slug):
        base = self.base_for(relpath)
        page = link_words.page_name(target_slug)
        target = "%sw/%s.html#%s" % (base, page, target_slug)
        display = self.by_slug[target_slug]["headword"] if target_slug in self.by_slug else link_words.headword_from_slug(target_slug)
        head = '<meta http-equiv="refresh" content="0; url=%s">' % esc(target)
        body = ['<h1>Moved</h1>',
                '<p class="redirect-note">The entry <i>%s</i> is now at <a href="%s">%s</a>.</p>' % (esc(old_slug), esc(target), esc(display))]
        self.page(relpath, "Moved: %s" % display, "\n".join(body), kind="redirect", head=head)

    def redirect_pages(self):
        for old, new in self.redirects.items():
            self.redirect_page("redirect/%s.html" % old, new, old)
            old_page = link_words.page_name(old)
            if old_page not in self.pages and old_page != link_words.page_name(new):
                self.redirect_page("w/%s.html" % old_page, new, old)

    # -- run -----------------------------------------------------------------------

    def build(self):
        self.load()
        self.prepare_out()
        self.write("site.css", (TEMPLATE_DIR / "site.css").read_text(encoding="utf-8"))
        self.write("site.js", (TEMPLATE_DIR / "site.js").read_text(encoding="utf-8"))
        for page, group in self.pages.items():
            self.headword_page(page, group)
            self.preview_payload(page, group)
        self.search_index()
        self.browse_pages()
        self.home_page()
        self.recent_page()
        self.random_page()
        self.journal_pages()
        self.about_page()
        self.grammar_key_page()
        self.labels_key_page()
        self.pronunciation_key_page()
        self.redirect_pages()
        self.log("build_site: %d entries on %d headword pages, %d drafts withheld, %d redirects; %d files written to %s"
                 % (len(self.entries), len(self.pages), self.drafts, len(self.redirects), self.files_written, self.out))
        return self


def build(root=None, entries_dir=None, out=None, quiet=False):
    """Build the site and return the Builder (for tests)."""
    return Builder(root=root, entries_dir=entries_dir, out=out, quiet=quiet).build()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render the static site from the entries, the journal, the metrics, and the sources register.")
    parser.add_argument("--out", default=None, help="output directory (default <root>/docs)")
    parser.add_argument("--root", default=None, help="repository root (default: the checkout this tool lives in)")
    parser.add_argument("--entries", default=None, help="entries directory (default <root>/entries)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    build(root=args.root, entries_dir=args.entries, out=args.out, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
