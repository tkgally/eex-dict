#!/usr/bin/env python3
"""Tests for tools/link_words.py, the build-time linker, on a small in-memory corpus.

Run from the repository root:  python3 -m unittest discover -s tools/tests -t .
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eexlib  # noqa: E402
import link_words  # noqa: E402

TOOLS = Path(__file__).resolve().parents[1]


def entry(headword, pos, forms=None, homograph=1, status="reviewed", variants=None, definition="a definition"):
    return {
        "slug": eexlib.slugify(headword, pos, homograph),
        "headword": headword,
        "pos": pos,
        "homograph": homograph,
        "variants": variants or [],
        "inflections": {"forms": forms or {}, "regular": True, "source": "rules", "status": "verified", "note": None},
        "senses": [{"n": 1, "definition": definition}],
        "provenance": {"status": status},
    }


CORPUS = [
    entry("run", "v", {"third_person_singular": "runs", "past_tense": "ran", "past_participle": "run", "present_participle": "running"}),
    entry("bank", "n", {"plural": "banks"}),
    entry("bank", "v", {"third_person_singular": "banks", "past_tense": "banked", "past_participle": "banked", "present_participle": "banking"}),
    entry("give up", "phrv", {"third_person_singular": "gives up", "past_tense": "gave up", "past_participle": "given up", "present_participle": "giving up"}),
    entry("in spite of", "prep"),
    entry("account", "n"),          # no forms listed: "accounts" must resolve by the rules
    entry("the", "det"),
    entry("big", "adj"),            # no forms listed: "bigger" and "biggest" by the rules
    entry("hope", "v"),
    entry("hop", "v"),              # "hoping" could be either: ambiguous, never linked
    entry("lie", "v", {"past_tense": "lay"}),
    entry("lay", "v"),              # "lay" is a headword and a form of lie: ambiguous
    entry("i", "pron"),
    entry("hi", "interj"),
    entry("color", "n", variants=[{"form": "colour", "kind": "spelling", "region": "British", "note": None}]),
    entry("x-ray", "n"),
    entry("café", "n"),
    entry("bat", "n", {"plural": "bats"}),
    entry("bat", "n", {"plural": "bats"}, homograph=2),
]


class LinkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = link_words.build_index(CORPUS, lemmatizer="rules")

    def link(self, text, self_slug=None, base="../"):
        return self.index.link(text, self_slug, base)

    def test_listed_forms_resolve_to_their_entry(self):
        html = self.link("She ran home.")
        self.assertIn('<a class="w" href="../w/run.html#run-v" data-hw="run">ran</a>', html)
        self.assertTrue(html.endswith(" home."))

    def test_headword_with_several_entries_links_to_the_page_without_anchor(self):
        html = self.link("two banks")
        self.assertIn('<a class="w" href="../w/bank.html" data-hw="bank">banks</a>', html)
        # a form belonging to one entry only keeps its anchor
        self.assertIn('href="../w/bank.html#bank-v"', self.link("he banked it"))
        # homographs of one headword share the page
        self.assertIn('<a class="w" href="../w/bat.html" data-hw="bat">bats</a>', self.link("two bats"))

    def test_base_rel_is_prefixed(self):
        self.assertIn('href="w/run.html#run-v"', self.link("ran", base=""))
        self.assertIn('href="../../w/run.html#run-v"', self.link("ran", base="../../"))

    def test_override_is_honoured(self):
        html = self.link("[[bank-v|banked]] and [[account-n]]")
        self.assertIn('<a class="w" href="../w/bank.html#bank-v" data-hw="bank">banked</a>', html)
        self.assertIn('<a class="w" href="../w/account.html#account-n" data-hw="account">account</a>', html)

    def test_override_to_unknown_slug_shows_plain_text(self):
        html = self.link("[[zzz-n|zed <b>]] here")
        self.assertEqual(html, "zed &lt;b&gt; here")

    def test_self_headword_and_its_forms_are_never_linked(self):
        html = self.link("the bank near the banks", "bank-n")
        self.assertNotIn("bank.html", html)
        self.assertIn('href="../w/the.html#the-det"', html)
        html = self.link("she ran and runs", "run-v")
        self.assertNotIn("run.html", html)

    def test_multi_word_headwords_match_greedily(self):
        html = self.link("Kim gave up smoking in spite of the rain.")
        self.assertIn('<a class="w" href="../w/give-up.html#give-up-phrv" data-hw="give up">gave up</a>', html)
        self.assertIn('<a class="w" href="../w/in-spite-of.html#in-spite-of-prep" data-hw="in spite of">in spite of</a>', html)
        self.assertNotIn(">in<", html)

    def test_hyphenated_headword_is_matched_as_a_whole(self):
        self.assertIn('data-hw="x-ray">X-ray</a>', self.link("an X-ray"))

    def test_escaping(self):
        self.assertEqual(self.link("a < b & c \"d\""), "a &lt; b &amp; c \"d\"")
        html = self.link("ran <script>")
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_function_words_link_only_with_an_entry(self):
        html = self.link("The bank is his.")
        self.assertIn('data-hw="the">The</a>', html)   # the-det exists: linked, case kept
        self.assertNotIn("i.html", html)                # "is" never becomes "I", "his" never "hi"
        self.assertIn(" is his.", html)

    def test_rule_lemmatizer_accepts_only_known_headwords(self):
        html = self.link("the accounts of the biggest and bigger banks")
        self.assertIn('href="../w/account.html#account-n" data-hw="account">accounts</a>', html)
        self.assertIn('data-hw="big">biggest</a>', html)
        self.assertIn('data-hw="big">bigger</a>', html)

    def test_ambiguous_words_are_not_linked(self):
        self.assertNotIn("<a", self.link("hoping"))       # hop or hope
        self.assertNotIn("<a", self.link("She lay down"))  # lay or lie

    def test_possessive_is_split_off(self):
        html = self.link("the bank's door")
        self.assertIn('data-hw="bank">bank</a>\'s door', html)

    def test_variant_spellings_and_accents_resolve(self):
        self.assertIn('data-hw="color">colour</a>', self.link("a colour"))
        self.assertIn('data-hw="café">cafe</a>', self.link("a cafe"))
        self.assertIn('data-hw="café">Café</a>', self.link("Café"))

    def test_links_helper_lists_placed_links(self):
        links = self.index.links("Sam ran to the bank", None, "../")
        self.assertEqual([(v, h) for v, h, _href in links], [("ran", "run"), ("the", "the"), ("bank", "bank")])

    def test_build_index_accepts_path_pairs_and_skips_stubs(self):
        index = link_words.build_index([("x.json", entry("dog", "n", {"plural": "dogs"})),
                                        {"schema_version": "1.0", "slug": "old-n", "redirect_to": "dog-n"}], lemmatizer="rules")
        self.assertEqual(sorted(index.headwords), ["dog"])
        self.assertIn('data-hw="dog">dogs</a>', index.link("dogs", None, ""))

    def test_link_text_uses_the_given_index(self):
        html = link_words.link_text("ran", "bank-n", "../", index=self.index)
        self.assertIn('href="../w/run.html#run-v"', html)

    def test_form_key_and_page_name(self):
        self.assertEqual(link_words.form_key("Give up"), "give up")
        self.assertEqual(link_words.form_key("x-ray"), "x ray")
        self.assertEqual(link_words.form_key("a.m."), "a m")
        self.assertEqual(link_words.page_name("in-spite-of-prep"), "in-spite-of")
        self.assertEqual(link_words.headword_from_slug("building-society-n"), "building society")

    def test_rule_lemmas(self):
        self.assertIn("run", link_words.rule_lemmas("running"))
        self.assertIn("hope", link_words.rule_lemmas("hoping"))
        self.assertIn("happy", link_words.rule_lemmas("happier"))
        self.assertIn("city", link_words.rule_lemmas("cities"))
        self.assertIn("box", link_words.rule_lemmas("boxes"))
        self.assertIn("stop", link_words.rule_lemmas("stopped"))
        self.assertIn("big", link_words.rule_lemmas("biggest"))
        self.assertEqual(link_words.rule_lemmas("as"), [])


class CliTests(unittest.TestCase):
    def test_cli_prints_links_for_a_scratch_entries_dir(self):
        with tempfile.TemporaryDirectory(prefix="eex-link-") as tmp:
            entries = Path(tmp) / "entries"
            (entries / "ru").mkdir(parents=True)
            (entries / "ru" / "run-v.json").write_text(json.dumps(CORPUS[0]), encoding="utf-8")
            draft = entry("walk", "v", {"past_tense": "walked"}, status="draft")
            (entries / "wa").mkdir()
            (entries / "wa" / "walk-v.json").write_text(json.dumps(draft), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(TOOLS / "link_words.py"), "--entries", str(entries),
                                   "--text", "Sam ran and walked"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("ran -> run  ../w/run.html#run-v", proc.stdout)
            self.assertNotIn("walked", proc.stdout)   # a draft entry is not indexed by default
            proc = subprocess.run([sys.executable, str(TOOLS / "link_words.py"), "--entries", str(entries), "--drafts",
                                   "--html", "--text", "walked"], capture_output=True, text=True)
            self.assertIn('data-hw="walk">walked</a>', proc.stdout)


if __name__ == "__main__":
    unittest.main()
