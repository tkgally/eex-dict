#!/usr/bin/env python3
"""Tests for tools/build_site.py: a build into a temporary directory from the fixture entry.

The temporary repository holds schema/ (copied), the fixture as a reviewed
entry, a draft entry that must be withheld, a redirect stub, a redirects file,
one journal report, one metrics row, and a sources register.  Nothing touches
the network or the real entries/ directory.

Run from the repository root:  python3 -m unittest discover -s tools/tests -t .
"""

import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REPO = TOOLS.parent
FIXTURE = TOOLS / "tests" / "fixtures" / "bank-n.json"

sys.path.insert(0, str(TOOLS))
import build_site  # noqa: E402

HREF_RE = re.compile(r'\b(?:href|src)="([^"]*)"')


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class TempSite:
    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="eex-site-"))
        shutil.copytree(REPO / "schema", self.dir / "schema")
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        fixture["provenance"]["status"] = "reviewed"
        self.fixture = fixture
        write_json(self.dir / "entries" / "ba" / "bank-n.json", fixture)
        draft = copy.deepcopy(fixture)
        draft["slug"] = draft["id"] = "bank-v"
        draft["pos"] = "v"
        draft["provenance"]["status"] = "draft"
        write_json(self.dir / "entries" / "ba" / "bank-v.json", draft)
        run = copy.deepcopy(fixture)
        run["slug"] = run["id"] = "run-v"
        run["headword"] = "run"
        run["pos"] = "v"
        run["inflections"] = {"forms": {"third_person_singular": "runs", "past_tense": "ran", "past_participle": "run",
                                        "present_participle": "running"}, "regular": False, "source": "exceptions",
                              "status": "verified", "note": None}
        run["pronunciation"]["british"]["status"] = "disputed"
        run["phrases"], run["word_family"], run["learner_errors"], run["see_also"] = [], [], [], []
        run["synonym_discrimination"] = run["etymology"] = run["core_idea"] = None
        run["senses"] = [run["senses"][0]]
        run["senses"][0].update({"signpost": "MOVE FAST", "definition": "move quickly on foot, faster than walking",
                                 "explanation": None, "subsenses": [], "compare": [], "collocations": []})
        run["senses"][0]["grammar"] = {"countability": None, "transitivity": "intransitive", "codes": [],
                                       "patterns": ["verb + adverb or preposition"]}
        run["senses"][0]["examples"] = [{"text": "Sam ran to the bank.", "note": None, "pattern": "verb + adverb or preposition"},
                                        {"text": "The children were running along the banks of the river.", "note": None, "pattern": None}]
        run["usage_note"] = "**Run** is irregular: *ran*, *run*. Compare **bank**."
        run["pronunciation"]["notes"] = "**Run** rhymes with *fun*."
        run["inflections"]["note"] = "past tense **ran**"
        run["provenance"]["created"] = "2026-09-17T01:00:00Z"
        write_json(self.dir / "entries" / "ru" / "run-v.json", run)
        # a phrasal verb of run (the box on the verb's page, ruling D2)
        away = copy.deepcopy(run)
        away["slug"] = away["id"] = "run-away-phrv"
        away["headword"] = "run away"
        away["pos"] = "phrv"
        away["senses"][0].update({"signpost": None, "definition": "leave a place quickly to escape from someone or something"})
        away["senses"][0]["synonyms"] = [{"slug": "flee-v", "note": None}]       # no entry: grey text (C2)
        away["see_also"] = [{"slug": "escape-v", "note": None}]                   # no entry: hidden (C2)
        away["word_family"] = [{"slug": "runaway-n", "form": None, "note": None}]  # no entry: hidden (C2)
        away["usage_note"] = None
        away["pronunciation"]["notes"] = None
        away["phrases"] = [{"sub_id": "run-away-with-someone", "text": "run away with someone", "labels": {},
                            "definition": "leave home secretly to live with someone", "explanation": None,
                            "examples": [{"text": "She ran away with her teacher.", "note": None, "pattern": None}],
                            "adaptation": {"semantic": None, "grammar": None, "culture": None, "false_friends": None, "pronunciation": None},
                            "l1": {}}]
        write_json(self.dir / "entries" / "ru" / "run-away-phrv.json", away)
        # an entry with six senses (the sense menu, ruling D2)
        big = copy.deepcopy(fixture)
        big["slug"] = big["id"] = "set-n"
        big["headword"] = "set"
        big["phrases"], big["word_family"], big["see_also"] = [], [], []
        sense = big["senses"][0]
        big["senses"] = []
        for n in range(1, 7):
            x = copy.deepcopy(sense)
            x.update({"n": n, "signpost": "GROUP" if n == 1 else None, "definition": "meaning number %d of the noun" % n,
                      "synonyms": [], "antonyms": [], "compare": [{"slug": "brother-in-law-n", "note": None}] if n == 2 else []})
            big["senses"].append(x)
        write_json(self.dir / "entries" / "se" / "set-n.json", big)
        (self.dir / "headwords").mkdir(exist_ok=True)
        (self.dir / "headwords" / "queue.tsv").write_text(
            "headword\tpos\tband\tsource\tstatus\tadded\tnote\n"
            "brother in law\tn\t3\tcrossref\tduplicate\t2026-10-01\t\n"
            "brother-in-law\tn\t2\tdefining\tpending\t2026-09-16\t\n", encoding="utf-8")
        write_json(self.dir / "entries" / "ba" / "banc-n.json",
                   {"schema_version": "1.0", "slug": "banc-n", "redirect_to": "bank-n", "renamed": "2026-09-16", "reason": "test"})
        write_json(self.dir / "headwords" / "redirects.json", {"banc-n": "bank-n", "old-run-v": "run-v"})
        (self.dir / "journal").mkdir()
        (self.dir / "journal" / "2026-09-16-first.md").write_text(
            "# First report\n\n*Plain* English for **Tom**, with `code` and a [link](2026-09-16-first.md).\n\n"
            "- one\n- two\n  - nested\n\n1. first\n2. second\n\n```\nfenced < code\n```\n\n"
            "| a | b |\n|---|---|\n| 1 | 2 |\n", encoding="utf-8")
        (self.dir / "metrics").mkdir()
        (self.dir / "metrics" / "history.jsonl").write_text(
            json.dumps({"ts": "2026-09-16T12:00:00Z", "run_id": "x", "mode": "build", "entries_total": 3, "entries_reviewed": 2,
                        "entries_draft": 1, "defining_vocabulary": {"size": 2300, "with_entry": 2, "coverage": 0.0009},
                        "queue": {"pending": 5, "done": 2}}) + "\n", encoding="utf-8")
        (self.dir / "sources").mkdir()
        (self.dir / "sources" / "README.md").write_text(
            "# Register\n\n| Resource | Used for |\n|---|---|\n| CMU dict | a vote |\n\nSee [the decision](../wiki/decisions/x.md).\n",
            encoding="utf-8")
        self.out = self.dir / "docs"

    def build(self):
        return build_site.build(root=self.dir, out=self.out, quiet=True)

    def read(self, rel):
        return (self.out / rel).read_text(encoding="utf-8")

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class BuildSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = TempSite()
        cls.builder = cls.site.build()

    @classmethod
    def tearDownClass(cls):
        cls.site.cleanup()

    def test_expected_pages_exist(self):
        for rel in ["index.html", "w/bank.html", "w/run.html", "browse/index.html", "browse/b.html", "browse/r.html",
                    "browse/band-1.html", "random.html", "recent.html", "journal/index.html", "404.html", "phrase-index.json",
                    "journal/2026-09-16-first.html", "about.html", "grammar-key.html", "labels-key.html",
                    "pronunciation-key.html", "redirect/banc-n.html", "redirect/old-run-v.html", "w/banc.html",
                    "search-index.json", "p/bank.json", "p/run.json", "site.css", "site.js"]:
            with self.subTest(page=rel):
                self.assertTrue((self.site.out / rel).is_file(), rel)

    def test_draft_entries_are_not_published(self):
        bank = self.site.read("w/bank.html")
        self.assertNotIn('id="bank-v"', bank)
        self.assertEqual(self.builder.drafts, 1)
        index = json.loads(self.site.read("search-index.json"))
        self.assertEqual([w["w"] for w in index["words"]], ["bank", "run", "run away", "set"])
        self.assertEqual(index["words"][0]["s"], ["bank-n"])

    def test_anchors_and_entry_content(self):
        bank = self.site.read("w/bank.html")
        self.assertIn('<article class="entry" id="bank-n">', bank)
        self.assertIn('id="bank-n-break-the-bank"', bank)
        self.assertIn("<h1 class=\"page-hw\">bank</h1>", bank)
        self.assertIn('<span class="pos">noun</span>', bank)
        self.assertIn('class="signpost">MONEY</span>', bank)
        self.assertIn("countable <span class=\"code\">[C]</span>", bank)
        self.assertIn('href="../grammar-key.html#countability-countable"', bank)
        self.assertIn('href="../labels-key.html#domain-finance"', bank)
        self.assertIn("very common", bank)
        self.assertIn("defining vocabulary", bank)
        self.assertIn('class="translator box"', bank)
        self.assertIn("Many languages use one word for the side of a river", bank)
        self.assertIn('<span class="incorrect">I went to bank.</span>', bank)
        self.assertIn("Word origin", bank)
        self.assertIn('<span class="pron-label">American</span>', bank)
        self.assertIn('<span class="pron-label">British</span>', bank)
        self.assertIn('class="mark unverified"', bank)
        self.assertIn('<span class="form-name">plural</span> <b>banks</b>', bank)
        run = self.site.read("w/run.html")
        self.assertIn('class="mark disputed"', run)
        self.assertIn("past tense</span> <b>ran</b>", run)
        self.assertIn('class="pattern"', run)
        self.assertIn("V + adv/prep", run)

    def test_build_time_links_are_placed(self):
        run = self.site.read("w/run.html")
        # "bank" in run's example links to the bank page; run's own forms do not link
        self.assertIn('<a class="w" href="../w/bank.html#bank-n" data-hw="bank" tabindex="-1">bank</a>', run)
        self.assertNotIn('data-hw="run"', run)
        bank = self.site.read("w/bank.html")
        self.assertNotIn('data-hw="bank"', bank)

    def test_inline_marks_and_the_headword_in_examples(self):
        run = self.site.read("w/run.html")
        self.assertIn('<span class="ex">Sam <b class="ex-hw">ran</b> to', run)
        self.assertIn('<b class="ex-hw">running</b>', run)
        self.assertIn('<b class="mention">Run</b> is irregular: <i class="illus">ran</i>, <i class="illus">run</i>. '
                      'Compare <b class="mention"><a class="w" href="../w/bank.html#bank-n" data-hw="bank" tabindex="-1">bank</a></b>.', run)
        self.assertIn('<span class="muted small"><b class="mention">Run</b> rhymes with <i class="illus">fun</i>.</span>', run)
        self.assertIn('<span class="note">past tense <b class="mention">ran</b></span>', run)
        bank = self.site.read("w/bank.html")
        self.assertIn('at the <b class="ex-hw">bank</b> near', bank)
        self.assertIn('burst its <b class="ex-hw">banks</b>', bank)
        self.assertNotIn("*", build_site.plain_prose("**Run** is *irregular*"))
        for name in ("search-index.json", "p/run.json"):
            self.assertNotIn("**", self.site.read(name))

    def test_every_page_has_the_shell(self):
        for path in sorted(self.site.out.rglob("*.html")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(page=path.name):
                self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', text)
                self.assertIn("no human has checked most entries.", text)
                self.assertIn('form class="search', text)
                self.assertIn('class="translator-toggle"', text)
                self.assertIn("TKG English Learner", text)
                for item in ("index.html", "browse/index.html", "random.html", "recent.html", "journal/index.html", "about.html"):
                    self.assertIn('href="%s%s"' % (self.builder.base_for(path.relative_to(self.site.out).as_posix()), item), text)

    def test_relative_links_only(self):
        for path in sorted(self.site.out.rglob("*.html")):
            rel = path.relative_to(self.site.out).as_posix()
            text = path.read_text(encoding="utf-8")
            for href in HREF_RE.findall(text):
                with self.subTest(page=rel, href=href):
                    self.assertFalse(href.startswith("/"), href)
                    if href.startswith("https://github.com/tkgally/eex-dict/issues/new?"):
                        continue                                    # the report link (ruling E4)
                    if href.startswith("http"):
                        self.assertEqual(rel, "about.html")
        about = self.site.read("about.html")
        self.assertIn('href="https://github.com/tkgally/eex-dict"', about)

    def test_search_index_has_forms_and_gloss(self):
        index = json.loads(self.site.read("search-index.json"))
        run = next(w for w in index["words"] if w["w"] == "run")
        self.assertEqual(run["f"], ["runs", "ran", "running"])
        self.assertIn("move quickly on foot", run["g"])
        bank = next(w for w in index["words"] if w["w"] == "bank")
        self.assertEqual(bank["f"], ["banks"])
        self.assertEqual(index["pos"]["n"], "noun")
        self.assertNotIn("Many languages", self.site.read("search-index.json"))   # no notes in the index

    def test_preview_payload(self):
        payload = json.loads(self.site.read("p/bank.json"))
        self.assertEqual(payload["w"], "bank")
        self.assertEqual(payload["e"][0]["pos"], "noun")
        self.assertTrue(payload["e"][0]["d"].startswith("a business"))

    def test_redirects(self):
        page = self.site.read("redirect/banc-n.html")
        self.assertIn('<meta http-equiv="refresh" content="0; url=../w/bank.html#bank-n">', page)
        old_page = self.site.read("w/banc.html")
        self.assertIn("url=../w/bank.html#bank-n", old_page)
        self.assertIn("url=../w/run.html#run-v", self.site.read("redirect/old-run-v.html"))

    def test_keys_and_about(self):
        grammar = self.site.read("grammar-key.html")
        self.assertIn('id="verb-patterns-verb-object"', grammar)
        self.assertIn("She read the letter.", grammar)
        labels = self.site.read("labels-key.html")
        self.assertIn('id="register-informal"', labels)
        self.assertIn('id="domain-finance"', labels)
        pron = self.site.read("pronunciation-key.html")
        self.assertIn("æ", pron)
        about = self.site.read("about.html")
        self.assertIn("CC0 1.0", about)
        self.assertIn("MIT", about)
        self.assertIn("editorial estimates", about)
        self.assertIn("CMU dict", about)
        self.assertIn("1 run recorded", about)
        self.assertIn('href="https://github.com/tkgally/eex-dict/blob/main/wiki/decisions/x.md"', about)

    def test_journal_markdown(self):
        page = self.site.read("journal/2026-09-16-first.html")
        self.assertIn("<h1>First report</h1>", page)
        self.assertIn("<em>Plain</em>", page)
        self.assertIn("<strong>Tom</strong>", page)
        self.assertIn("<code>code</code>", page)
        self.assertIn('<a href="2026-09-16-first.html">link</a>', page)
        self.assertIn("<ul><li>one</li><li>two<ul><li>nested</li></ul></li></ul>", page)
        self.assertIn("<ol><li>first</li><li>second</li></ol>", page)
        self.assertIn("<pre><code>fenced &lt; code</code></pre>", page)
        self.assertIn("<table>", page)
        index = self.site.read("journal/index.html")
        self.assertIn('href="2026-09-16-first.html">First report</a>', index)

    def test_recent_and_browse(self):
        recent = self.site.read("recent.html")
        self.assertLess(recent.index('href="w/run.html#run-v"'), recent.index('href="w/bank.html#bank-n"'))
        browse = self.site.read("browse/b.html")
        self.assertIn('href="../w/bank.html">bank</a>', browse)
        band = self.site.read("browse/band-1.html")
        self.assertIn("bank", band)

    def test_empty_bands_are_hidden(self):
        self.assertFalse((self.site.out / "browse" / "band-5.html").exists())
        self.assertNotIn("band-5.html", self.site.read("browse/index.html"))

    def test_missing_cross_references(self):
        """Ruling C2: grey text with a legend for synonyms; family and see also hidden; no slug in a tooltip."""
        page = self.site.read("w/run-away.html")
        self.assertIn('<span class="xref-missing">flee</span>', page)
        self.assertIn("Grey words have no entry yet.", page)
        self.assertNotIn("runaway", page)
        self.assertNotIn("see-also", page)          # its only see-also item has no entry
        self.assertNotIn('title="no entry yet', page)
        self.assertNotIn("flee-v", page)

    def test_display_forms_keep_hyphens(self):
        """Ruling C3: the queue row's headword, a live row before a duplicate; never the slug's hyphens as spaces."""
        page = self.site.read("w/set.html")
        self.assertIn('<span class="xref-missing">brother-in-law</span>', page)
        self.assertNotIn("brother in law", page)

    def test_sense_menu_and_jump_links(self):
        page = self.site.read("w/set.html")
        self.assertIn('<nav class="sense-menu"', page)
        self.assertIn('href="#set-n-s6"', page)
        self.assertIn('<span class="signpost">GROUP</span>', page)
        self.assertNotIn('class="sense-menu"', self.site.read("w/bank.html"))     # two senses: no menu
        bank = self.site.read("w/bank.html")
        self.assertIn('href="#bank-n-phrases">Phrases (1)</a>', bank)
        self.assertIn('id="bank-n-phrases"', bank)

    def test_phrasal_verbs_box(self):
        page = self.site.read("w/run.html")
        self.assertIn('id="run-v-phrasal-verbs"', page)
        self.assertIn('href="../w/run-away.html#run-away-phrv">run away</a>', page)
        self.assertIn('href="#run-v-phrasal-verbs">Phrasal verbs (1)</a>', page)
        self.assertNotIn("phrasal-verbs", self.site.read("w/bank.html"))

    def test_phrase_index(self):
        data = json.loads(self.site.read("phrase-index.json"))
        self.assertIn("someone", data["fillers"])
        texts = {row[0]: row for row in data["phrases"]}
        self.assertEqual(texts["break the bank"][1:3], ["bank", "bank-n-break-the-bank"])
        self.assertEqual(texts["run away with someone"][2], "run-away-phrv-run-away-with-someone")

    def test_report_link(self):
        page = self.site.read("w/bank.html")
        self.assertIn("Report a problem with this entry", page)
        self.assertIn("issues/new?title=Entry%20report%3A%20bank-n", page)
        self.assertIn("tkgally.github.io/eex-dict/w/bank.html%23bank-n", page)

    def test_home_has_one_search_box_and_journal_is_in_the_footer(self):
        home = self.site.read("index.html")
        self.assertEqual(home.count('<form class="search'), 1)
        self.assertNotIn('<a href="journal/index.html">Journal</a></li>', home)
        nav = home[home.index('<nav class="site-nav"'):home.index("</nav>")]
        self.assertNotIn("journal", nav)
        self.assertIn('href="journal/index.html">Journal</a>', home[home.index("<footer"):])
        self.assertIn('href="#top">Back to top</a>', home)
        about = self.site.read("about.html")
        self.assertLess(about.index("How to read an entry"), about.index("What this dictionary is"))
        self.assertIn('href="journal/index.html"', about)

    def test_not_found_page(self):
        page = self.site.read("404.html")
        self.assertIn('document.write(\'<base href=', page)
        self.assertIn("'/eex-dict/'", page)
        self.assertIn('data-page="404"', page)
        self.assertLess(page.index("<base href"), page.index('rel="stylesheet"'))

    def test_band_split_by_letter(self):
        old = build_site.BAND_SPLIT_MIN
        build_site.BAND_SPLIT_MIN = 2
        try:
            self.site.build()
            band = self.site.read("browse/band-1.html")
            self.assertIn('href="band-1-b.html"', band)
            self.assertIn('href="../w/bank.html">bank</a>', self.site.read("browse/band-1-b.html"))
            self.assertIn('href="../w/run.html">run</a>', self.site.read("browse/band-1-r.html"))
        finally:
            build_site.BAND_SPLIT_MIN = old
            self.site.build()

    def test_build_is_idempotent(self):
        before = {p.relative_to(self.site.out).as_posix(): p.read_bytes() for p in self.site.out.rglob("*") if p.is_file()}
        self.site.build()
        after = {p.relative_to(self.site.out).as_posix(): p.read_bytes() for p in self.site.out.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


class CliTests(unittest.TestCase):
    def test_entries_option_and_cli(self):
        site = TempSite()
        self.addCleanup(site.cleanup)
        scratch = site.dir / "scratch-entries"
        shutil.copytree(site.dir / "entries", scratch)
        out = site.dir / "out"
        proc = subprocess.run([sys.executable, str(TOOLS / "build_site.py"), "--root", str(site.dir), "--entries", str(scratch),
                               "--out", str(out)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("4 entries on 4 headword pages", proc.stdout)
        self.assertTrue((out / "w" / "bank.html").is_file())

    def test_refuses_to_clobber_a_foreign_directory(self):
        site = TempSite()
        self.addCleanup(site.cleanup)
        out = site.dir / "precious"
        out.mkdir()
        (out / "keep.txt").write_text("x", encoding="utf-8")
        proc = subprocess.run([sys.executable, str(TOOLS / "build_site.py"), "--root", str(site.dir), "--out", str(out)],
                              capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertTrue((out / "keep.txt").is_file())


class MarkdownTests(unittest.TestCase):
    def test_inline(self):
        self.assertEqual(build_site.md_inline("a **b** *c* `d<e>` [f](g.html)"),
                         'a <strong>b</strong> <em>c</em> <code>d&lt;e&gt;</code> <a href="g.html">f</a>')

    def test_blocks(self):
        html = build_site.md_to_html("## Head\n\npara one\nstill one\n\n> quoted\n\n---\n")
        self.assertIn("<h2>Head</h2>", html)
        self.assertIn("<p>para one still one</p>", html)
        self.assertIn("<blockquote><p>quoted</p></blockquote>", html)
        self.assertIn("<hr>", html)

    def test_journal_link_to_the_site_is_relative(self):
        rewrite = build_site.journal_link_rewriter
        self.assertEqual(rewrite(build_site.SITE_URL), "../index.html")
        self.assertEqual(rewrite(build_site.SITE_URL + "w/run.html"), "../w/run.html")
        self.assertEqual(rewrite("2026-09-25.md"), "2026-09-25.html")
        self.assertEqual(rewrite("https://example.org/"), "https://example.org/")
        html = build_site.md_inline("<%s>" % build_site.SITE_URL, link=rewrite)
        self.assertIn('href="../index.html"', html)


if __name__ == "__main__":
    unittest.main()
