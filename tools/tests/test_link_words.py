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


class NoLinkWordsTests(unittest.TestCase):
    """The owner's ruling C4 of 2026-10-24: the closed list never links as single words."""

    @classmethod
    def setUpClass(cls):
        cls.index = link_words.build_index(CORPUS + [entry("of", "prep"), entry("very", "adv")], lemmatizer="rules")

    def test_the_list_is_the_closed_vocabulary(self):
        words = set(eexlib.vocab_values("no_link_words"))
        self.assertEqual(len(words), 39)
        self.assertTrue({"the", "of", "very", "towards", "unless"} <= words)
        self.assertEqual(link_words.NO_LINK_WORDS, frozenset(words))

    def test_listed_words_are_not_linked_in_any_capitalization(self):
        html = self.index.link("The bank OF the town is Very big.", None, "../")
        self.assertNotIn('data-hw="the"', html)
        self.assertNotIn('data-hw="of"', html)
        self.assertNotIn('data-hw="very"', html)
        self.assertIn('data-hw="bank" tabindex="-1">bank</a>', html)
        self.assertIn('data-hw="big" tabindex="-1">big</a>', html)

    def test_multi_word_headwords_and_overrides_still_link(self):
        html = self.index.link("in spite of the rain, [[the-det|the]]", None, "../")
        self.assertIn('data-hw="in spite of"', html)
        self.assertIn('href="../w/the.html#the-det" data-hw="the" tabindex="-1">the</a>', html)

    def test_word_links_are_out_of_the_tab_order(self):
        for m in link_words.LINK_RE.finditer(self.index.link("She ran to the bank.", None, "")):
            self.assertIn('tabindex="-1"', m.group(0))


class LinkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # the general linking rules, without the closed no-link list (tested below)
        cls.index = link_words.build_index(CORPUS, lemmatizer="rules", no_link=())

    def link(self, text, self_slug=None, base="../", mark_self=False):
        return self.index.link(text, self_slug, base, mark_self=mark_self)

    def test_listed_forms_resolve_to_their_entry(self):
        html = self.link("She ran home.")
        self.assertIn('<a class="w" href="../w/run.html#run-v" data-hw="run" tabindex="-1">ran</a>', html)
        self.assertTrue(html.endswith(" home."))

    def test_headword_with_several_entries_links_to_the_page_without_anchor(self):
        html = self.link("two banks")
        self.assertIn('<a class="w" href="../w/bank.html" data-hw="bank" tabindex="-1">banks</a>', html)
        # a form belonging to one entry only keeps its anchor
        self.assertIn('href="../w/bank.html#bank-v"', self.link("he banked it"))
        # homographs of one headword share the page
        self.assertIn('<a class="w" href="../w/bat.html" data-hw="bat" tabindex="-1">bats</a>', self.link("two bats"))

    def test_base_rel_is_prefixed(self):
        self.assertIn('href="w/run.html#run-v"', self.link("ran", base=""))
        self.assertIn('href="../../w/run.html#run-v"', self.link("ran", base="../../"))

    def test_override_is_honoured(self):
        html = self.link("[[bank-v|banked]] and [[account-n]]")
        self.assertIn('<a class="w" href="../w/bank.html#bank-v" data-hw="bank" tabindex="-1">banked</a>', html)
        self.assertIn('<a class="w" href="../w/account.html#account-n" data-hw="account" tabindex="-1">account</a>', html)

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
        self.assertIn('<a class="w" href="../w/give-up.html#give-up-phrv" data-hw="give up" tabindex="-1">gave up</a>', html)
        self.assertIn('<a class="w" href="../w/in-spite-of.html#in-spite-of-prep" data-hw="in spite of" tabindex="-1">in spite of</a>', html)
        self.assertNotIn(">in<", html)

    def test_hyphenated_headword_is_matched_as_a_whole(self):
        self.assertIn('data-hw="x-ray" tabindex="-1">X-ray</a>', self.link("an X-ray"))

    def test_escaping(self):
        self.assertEqual(self.link("a < b & c \"d\""), "a &lt; b &amp; c \"d\"")
        html = self.link("ran <script>")
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_function_words_link_only_with_an_entry(self):
        html = self.link("The bank is his.")
        self.assertIn('data-hw="the" tabindex="-1">The</a>', html)   # the-det exists: linked, case kept
        self.assertNotIn("i.html", html)                # "is" never becomes "I", "his" never "hi"
        self.assertIn(" is his.", html)

    def test_rule_lemmatizer_accepts_only_known_headwords(self):
        html = self.link("the accounts of the biggest and bigger banks")
        self.assertIn('href="../w/account.html#account-n" data-hw="account" tabindex="-1">accounts</a>', html)
        self.assertIn('data-hw="big" tabindex="-1">biggest</a>', html)
        self.assertIn('data-hw="big" tabindex="-1">bigger</a>', html)

    def test_ambiguous_words_are_not_linked(self):
        self.assertNotIn("<a", self.link("hoping"))       # hop or hope
        self.assertNotIn("<a", self.link("She lay down"))  # lay or lie

    def test_possessive_is_split_off(self):
        html = self.link("the bank's door")
        self.assertIn('data-hw="bank" tabindex="-1">bank</a>\'s door', html)

    def test_variant_spellings_and_accents_resolve(self):
        self.assertIn('data-hw="color" tabindex="-1">colour</a>', self.link("a colour"))
        self.assertIn('data-hw="café" tabindex="-1">cafe</a>', self.link("a cafe"))
        self.assertIn('data-hw="café" tabindex="-1">Café</a>', self.link("Café"))

    def test_links_helper_lists_placed_links(self):
        links = self.index.links("Sam ran to the bank", None, "../")
        self.assertEqual([(v, h) for v, h, _href in links], [("ran", "run"), ("the", "the"), ("bank", "bank")])

    def test_build_index_accepts_path_pairs_and_skips_stubs(self):
        index = link_words.build_index([("x.json", entry("dog", "n", {"plural": "dogs"})),
                                        {"schema_version": "1.0", "slug": "old-n", "redirect_to": "dog-n"}], lemmatizer="rules")
        self.assertEqual(sorted(index.headwords), ["dog"])
        self.assertIn('data-hw="dog" tabindex="-1">dogs</a>', index.link("dogs", None, ""))

    def test_link_text_uses_the_given_index(self):
        html = link_words.link_text("ran", "bank-n", "../", index=self.index)
        self.assertIn('href="../w/run.html#run-v"', html)

    def test_form_key_and_page_name(self):
        self.assertEqual(link_words.form_key("Give up"), "give up")
        self.assertEqual(link_words.form_key("x-ray"), "x ray")
        self.assertEqual(link_words.form_key("a.m."), "a m")
        self.assertEqual(link_words.page_name("in-spite-of-prep"), "in-spite-of")
        self.assertEqual(link_words.headword_from_slug("building-society-n"), "building society")

    def test_marks_are_rendered_and_linked_inside(self):
        html = self.link("**The** goes before a noun (*the bank*, *the banks*).", "run-v")
        self.assertIn('<b class="mention"><a class="w" href="../w/the.html#the-det" data-hw="the" tabindex="-1">The</a></b> goes', html)
        self.assertIn('(<i class="illus"><a class="w" href="../w/the.html#the-det" data-hw="the" tabindex="-1">the</a> '
                      '<a class="w" href="../w/bank.html" data-hw="bank" tabindex="-1">bank</a></i>, ', html)
        self.assertNotIn("*", html)

    def test_example_marks_the_entry_headword_and_its_forms(self):
        html = self.link("Sam ran and runs to the bank.", "run-v", mark_self=True)
        self.assertIn('<b class="ex-hw">ran</b> and <b class="ex-hw">runs</b>', html)
        self.assertIn('data-hw="bank" tabindex="-1">bank</a>', html)
        self.assertNotIn("run.html", html)
        # a multi-word form, and the possessive of a single word
        self.assertIn('<b class="ex-hw">gave up</b>', self.link("Kim gave up.", "give-up-phrv", mark_self=True))
        self.assertIn("<b class=\"ex-hw\">bank</b>'s", self.link("the bank's door", "bank-n", mark_self=True))
        # a headword with several entries is still the entry's own form
        self.assertIn('<b class="ex-hw">bats</b>', self.link("two bats", "bat-n-2", mark_self=True))
        # without mark_self nothing changes
        self.assertNotIn("ex-hw", self.link("Sam ran.", "run-v"))
        # a form shared with another headword is never linked, but in its own entry's example it is the headword
        self.assertIn('<b class="ex-hw">lay</b>', self.link("She lay down.", "lie-v", mark_self=True))
        self.assertNotIn("<a", self.link("She lay down.", "lie-v", mark_self=True))

    def test_explicit_mark_in_an_example_switches_the_automatic_marking_off(self):
        html = self.link("**Ran** he ever ran?", "run-v", mark_self=True)
        self.assertIn('<b class="ex-hw">Ran</b> he ever ran?', html)
        self.assertEqual(html.count("ex-hw"), 1)

    def test_contractions_are_marked_whole(self):
        index = link_words.build_index([entry("do", "v", {"third_person_singular": "does", "past_tense": "did"}), entry("can", "modal")],
                                       lemmatizer="rules")
        self.assertIn("<b class=\"ex-hw\">doesn't</b>", index.link("She doesn't know.", "do-v", "../", mark_self=True))
        self.assertIn("<b class=\"ex-hw\">can't</b> and <b class=\"ex-hw\">cannot</b>",
                      index.link("I can't and cannot.", "can-modal", "../", mark_self=True))

    def test_plain_text_strips_marks_and_overrides(self):
        self.assertEqual(link_words.plain_text("**All** of [[the-det|the]] *students* and [[account-n]]"),
                         "All of the students and account")

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
            self.assertIn('data-hw="walk" tabindex="-1">walked</a>', proc.stdout)


if __name__ == "__main__":
    unittest.main()
