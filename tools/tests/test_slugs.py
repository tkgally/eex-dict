#!/usr/bin/env python3
"""Tests for the slug, shard, path, and prose helpers in tools/eexlib.py.

Run from the repository root:  python3 -m unittest discover -s tools/tests -t .
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eexlib  # noqa: E402


class SlugifyTests(unittest.TestCase):
    CASES = [
        (("bank", "n"), "bank-n"),
        (("give up", "phrv"), "give-up-phrv"),
        (("in spite of", "prep"), "in-spite-of-prep"),
        (("un-", "prefix"), "un-prefix"),
        (("o'clock", "adv"), "oclock-adv"),
        (("o’clock", "adv"), "oclock-adv"),
        (("café", "n"), "cafe-n"),
        (("naïve", "adj"), "naive-adj"),
        (("a.m.", "abbr"), "am-abbr"),
        (("ASAP", "abbr"), "asap-abbr"),
        (("Bank", "n"), "bank-n"),
        (("  two   spaces ", "n"), "two-spaces-n"),
        (("x-ray", "n"), "x-ray-n"),
        (("3D", "adj"), "3d-adj"),
        (("rock & roll", "n"), "rock-roll-n"),
    ]

    def test_cases(self):
        for (headword, pos), expected in self.CASES:
            with self.subTest(headword=headword, pos=pos):
                self.assertEqual(eexlib.slugify(headword, pos), expected)

    def test_homographs(self):
        self.assertEqual(eexlib.slugify("bat", "n", 2), "bat-n-2")
        self.assertEqual(eexlib.slugify("bat", "n", 3), "bat-n-3")
        self.assertEqual(eexlib.slugify("bat", "n", 1), "bat-n")
        self.assertEqual(eexlib.slugify("bat", "n", "2"), "bat-n-2")

    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            eexlib.slugify("bank", "noun")
        with self.assertRaises(ValueError):
            eexlib.slugify("...", "n")
        with self.assertRaises(ValueError):
            eexlib.slugify("bank", "n", 0)

    def test_pos_codes_come_from_the_vocabulary(self):
        self.assertIn("n", eexlib.POS_CODES)
        self.assertIn("phrv", eexlib.POS_CODES)
        self.assertEqual(list(eexlib.POS_CODES), eexlib.vocab_values("pos"))
        self.assertFalse(any(code.startswith("_") for code in eexlib.vocab_values("region")))


class ParseSlugTests(unittest.TestCase):
    def test_round_trips(self):
        for headword, pos, homograph in [("bank", "n", 1), ("give up", "phrv", 1), ("in spite of", "prep", 1),
                                         ("bat", "n", 2), ("x-ray", "n", 1), ("3d", "adj", 1), ("a", "det", 1),
                                         ("catch-22", "n", 1), ("catch-22", "n", 2)]:
            slug = eexlib.slugify(headword, pos, homograph)
            with self.subTest(slug=slug):
                head, parsed_pos, parsed_homograph = eexlib.parse_slug(slug)
                self.assertEqual((parsed_pos, parsed_homograph), (pos, homograph))
                self.assertEqual(eexlib.slugify(head, parsed_pos, parsed_homograph), slug)

    def test_values(self):
        self.assertEqual(eexlib.parse_slug("bat-n-2"), ("bat", "n", 2))
        self.assertEqual(eexlib.parse_slug("in-spite-of-prep"), ("in-spite-of", "prep", 1))
        self.assertEqual(eexlib.parse_slug("3d-adj"), ("3d", "adj", 1))

    def test_rejects(self):
        for bad in ["bank", "bank-noun", "Bank-n", "bank--n", "-bank-n", "bank-n-1", "bank-n-0", "n", "", "bank n"]:
            with self.subTest(slug=bad):
                with self.assertRaises(ValueError):
                    eexlib.parse_slug(bad)


class ShardAndPathTests(unittest.TestCase):
    def test_shards(self):
        self.assertEqual(eexlib.shard("bank-n"), "ba")
        self.assertEqual(eexlib.shard("a-det"), "a")
        self.assertEqual(eexlib.shard("x-ray-n"), "x")
        self.assertEqual(eexlib.shard("3d-adj"), "0-9")
        self.assertEqual(eexlib.shard("oclock-adv"), "oc")

    def test_entry_path(self):
        self.assertEqual(eexlib.entry_path("bank-n"), eexlib.ROOT / "entries" / "ba" / "bank-n.json")
        self.assertEqual(eexlib.relative_entry_path("3d-adj"), "entries/0-9/3d-adj.json")
        self.assertEqual(eexlib.entry_path("a-det", root="/x"), Path("/x/entries/a/a-det.json"))

    def test_set_root(self):
        original = eexlib.get_root()
        try:
            eexlib.set_root(original)  # same layout, exercises the reload
            self.assertEqual(eexlib.get_root(), original)
            self.assertIn("n", eexlib.POS_CODES)
        finally:
            eexlib.set_root(original)


class PhraseAndProseTests(unittest.TestCase):
    def test_phrase_sub_id(self):
        self.assertEqual(eexlib.phrase_sub_id("give someone a hand"), "give-someone-a-hand")
        self.assertEqual(eexlib.phrase_sub_id("break the bank"), "break-the-bank")
        self.assertEqual(eexlib.phrase_sub_id("at sb's beck and call".replace("sb's", "someone's")), "at-someones-beck-and-call")
        self.assertEqual(eexlib.phrase_sub_id("Something's up!"), "somethings-up")

    def test_word_count(self):
        self.assertEqual(eexlib.word_count("one two  three\nfour"), 4)
        self.assertEqual(eexlib.word_count(""), 0)

    def test_iter_prose_paths(self):
        entry = {
            "core_idea": "c", "usage_note": None,
            "senses": [{"definition": "d", "examples": [{"text": "t", "note": "n"}],
                        "collocations": [{"items": ["i1", "i2"]}],
                        "subsenses": [{"definition": "sd", "examples": [{"text": "st", "note": None}]}],
                        "adaptation": {"semantic": "s", "grammar": None}}],
            "phrases": [{"text": "p", "definition": "pd", "adaptation": {"culture": "pc"}}],
            "learner_errors": [{"incorrect": "i", "correct": "c", "note": None}],
            "etymology": {"text": "e"}, "adaptation": {"false_friends": "f"},
        }
        got = dict(eexlib.iter_prose(entry))
        for path in ["core_idea", "senses[0].definition", "senses[0].examples[0].text", "senses[0].examples[0].note",
                     "senses[0].collocations[0].items[1]", "senses[0].subsenses[0].definition",
                     "senses[0].subsenses[0].examples[0].text", "senses[0].adaptation.semantic",
                     "phrases[0].text", "phrases[0].definition", "phrases[0].adaptation.culture",
                     "learner_errors[0].incorrect", "learner_errors[0].correct", "etymology.text", "adaptation.false_friends"]:
            self.assertIn(path, got)
        self.assertNotIn("usage_note", got)
        self.assertNotIn("senses[0].adaptation.grammar", got)

    def test_reorder_entry_follows_schema_order(self):
        schema = eexlib.load_schema()
        entry = {"slug": "a-n", "id": "a-n", "schema_version": "1.0", "extra": 1,
                 "pronunciation": {"notes": None, "american": {"status": "verified", "ipa": "a"}},
                 "l1": {"ja": {"status": "draft", "equivalents": []}}}
        out = eexlib.reorder_entry(entry, schema)
        self.assertEqual(list(out), ["schema_version", "id", "slug", "pronunciation", "l1", "extra"])
        self.assertEqual(list(out["pronunciation"]), ["american", "notes"])
        self.assertEqual(list(out["pronunciation"]["american"]), ["ipa", "status"])
        self.assertEqual(list(out["l1"]["ja"]), ["equivalents", "status"])
        top = list(eexlib.schema_key_order(schema))
        self.assertEqual(top, schema["required"])


if __name__ == "__main__":
    unittest.main()
