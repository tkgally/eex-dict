#!/usr/bin/env python3
"""Tests for tools/inflect.py and schema/inflection-exceptions.json.

Run from the repository root:  python3 -m unittest tools.tests.test_inflect
(discovery: python3 -m unittest discover -s tools/tests -t .)

Rule cases are tuples (headword, pos, keyword arguments, expected forms, expected metadata); one test method is
generated per case so that every case counts and fails on its own.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import eexlib  # noqa: E402
import inflect as I  # noqa: E402

UNDECIDED = I.UNDECIDED_NOTE
RULES = {"source": "rules", "status": "verified", "regular": True}
TABLE = {"source": "exceptions", "status": "verified", "regular": False}
NONE = {"source": "none", "status": "verified", "regular": True, "note": None}


def P(plural, **meta):
    return {"plural": plural}, meta


def V(tps, past, pp, prp, **meta):
    return {"third_person_singular": tps, "past_tense": past, "past_participle": pp, "present_participle": prp}, meta


def C(comp, sup, **meta):
    return {"comparative": comp, "superlative": sup}, meta


NOUN_CASES = [
    ("box", "n", {}, *P("boxes", **RULES, note=None)),
    ("city", "n", {}, *P("cities", **RULES)),
    ("potato", "n", {}, *P("potatoes", **RULES)),
    ("radio", "n", {}, *P("radios", **RULES)),
    ("leaf", "n", {}, *P("leaves", **RULES)),
    ("roof", "n", {}, *P("roofs", **RULES)),
    ("child", "n", {}, *P("children", **TABLE, note=None)),
    ("sheep", "n", {}, *P("sheep", **TABLE)),
    ("mother-in-law", "n", {}, *P("mothers-in-law", **TABLE)),
    ("stomach", "n", {}, *P("stomachs", **TABLE)),
    ("TV", "abbr", {"countability": "countable"}, *P("TVs", **RULES)),
    ("ASAP", "abbr", {}, {}, NONE),
    ("information", "n", {"countability": "uncountable"}, *P(None, **RULES, note="no plural")),
    ("scissors", "n", {"countability": "plural only"}, *P(None, **RULES, note="plural only")),
    ("future", "n", {"countability": "singular only"}, *P(None, **RULES, note="no plural")),
    ("water", "n", {"countability": "countable or uncountable"}, *P("waters", **RULES)),
    ("bus", "n", {}, *P("buses", **RULES)),
    ("quiz", "n", {}, *P("quizzes", **RULES)),
    ("day", "n", {}, *P("days", **RULES)),
    ("hero", "n", {}, *P("heroes", **RULES)),
    ("knife", "n", {}, *P("knives", **RULES)),
    ("mango", "n", {}, *P("mangoes", **TABLE, note="also mangos")),
    ("person", "n", {}, *P("people", **TABLE, note="persons in formal and legal use")),
    ("crisis", "n", {}, *P("crises", **TABLE)),
    ("synopsis", "n", {}, *P("synopses", **TABLE)),
    ("nemesis", "n", {}, *P("nemeses", **RULES)),
    ("policeman", "n", {}, *P("policemen", **RULES)),
    ("human", "n", {}, *P("humans", **RULES)),
    ("German", "n", {}, *P("Germans", **RULES)),
    ("Chinese", "n", {}, *P("Chinese", **TABLE)),
    ("x-ray", "n", {}, *P("x-rays", **RULES)),
    ("credit card", "n", {}, *P("credit cards", **RULES)),
    ("step-child", "n", {}, *P("step-children", **TABLE)),
    ("Monday", "n", {}, *P("Mondays", **RULES)),
    ("penknife", "n", {}, *P("penknives", **RULES)),
    ("soliloquy", "n", {}, *P("soliloquies", **RULES)),
    ("church", "n", {}, *P("churches", **RULES)),
    ("waltz", "n", {}, *P("waltzes", **RULES)),
    ("piano", "n", {}, *P("pianos", **RULES)),
    ("people", "n", {"countability": "countable"}, *P("peoples", **RULES)),
]

VERB_CASES = [
    ("stop", "v", {}, *V("stops", "stopped", "stopped", "stopping", **RULES, note=None)),
    ("play", "v", {}, *V("plays", "played", "played", "playing", **RULES)),
    ("fix", "v", {}, *V("fixes", "fixed", "fixed", "fixing", **RULES)),
    ("snow", "v", {}, *V("snows", "snowed", "snowed", "snowing", **RULES)),
    ("rain", "v", {}, *V("rains", "rained", "rained", "raining", **RULES)),
    ("begin", "v", {}, *V("begins", "began", "begun", "beginning", **TABLE)),
    ("prefer", "v", {}, *V("prefers", "preferred", "preferred", "preferring", **RULES)),
    ("visit", "v", {}, *V("visits", "visited", "visited", "visiting", **RULES)),
    ("travel", "v", {}, *V("travels", "traveled", "traveled", "traveling", **RULES,
                          note="British spelling doubles the l: travelled, travelling")),
    ("panic", "v", {}, *V("panics", "panicked", "panicked", "panicking", **RULES)),
    ("lie", "v", {}, *V("lies", "lay", "lain", "lying", **TABLE, note="lie meaning tell an untruth is regular: lied")),
    ("die", "v", {}, *V("dies", "died", "died", "dying", **RULES)),
    ("agree", "v", {}, *V("agrees", "agreed", "agreed", "agreeing", **RULES)),
    ("see", "v", {}, *V("sees", "saw", "seen", "seeing", **TABLE)),
    ("go", "v", {}, *V("goes", "went", "gone", "going", **TABLE)),
    ("have", "v", {}, *V("has", "had", "had", "having", **TABLE)),
    ("be", "v", {}, *V("is", "was", "been", "being", **TABLE, note="am, are; were")),
    ("get", "v", {}, *V("gets", "got", "gotten", "getting", **TABLE, note="also got as the past participle, as in have got; British English uses got")),
    ("give up", "phrv", {}, *V("gives up", "gave up", "given up", "giving up", **TABLE)),
    ("pick up", "phrv", {}, *V("picks up", "picked up", "picked up", "picking up", **RULES)),
    ("look after", "phrv", {}, *V("looks after", "looked after", "looked after", "looking after", **RULES)),
    ("try", "v", {}, *V("tries", "tried", "tried", "trying", **RULES)),
    ("hope", "v", {}, *V("hopes", "hoped", "hoped", "hoping", **RULES)),
    ("quiz", "v", {}, *V("quizzes", "quizzed", "quizzed", "quizzing", **RULES)),
    ("dial", "v", {}, *V("dials", "dialed", "dialed", "dialing", **RULES)),
    ("dry-clean", "v", {}, *V("dry-cleans", "dry-cleaned", "dry-cleaned", "dry-cleaning", **RULES)),
    ("echo", "v", {}, *V("echoes", "echoed", "echoed", "echoing", **RULES)),
    ("tango", "v", {}, *V("tangos", "tangoed", "tangoed", "tangoing", **RULES)),
    ("fly", "v", {}, *V("flies", "flew", "flown", "flying", **TABLE)),
    ("dye", "v", {}, *V("dyes", "dyed", "dyed", "dyeing", **RULES)),
    ("age", "v", {}, *V("ages", "aged", "aged", "aging", **RULES)),
    ("tie", "v", {}, *V("ties", "tied", "tied", "tying", **RULES)),
    ("arc", "v", {}, *V("arcs", "arced", "arced", "arcing", **RULES)),
    ("reformat", "v", {}, *V("reformats", "reformatted", "reformatted", "reformatting", **RULES)),
    ("develop", "v", {}, *V("develops", "developed", "developed", "developing", **RULES)),
    ("learn", "v", {}, *V("learns", "learned", "learned", "learning", **TABLE, note="also learnt, especially British")),
    ("Google", "v", {}, *V("Googles", "Googled", "Googled", "Googling", **RULES)),
    ("can", "modal", {}, {}, NONE),
    ("used to", "modal", {}, {}, NONE),
    ("do", "aux", {}, {}, NONE),
]

MORE = ("comparative with more",)
NOT_GRADABLE = ("not gradable",)
ADJ_CASES = [
    ("big", "adj", {}, *C("bigger", "biggest", **RULES, note=None)),
    ("happy", "adj", {}, *C("happier", "happiest", **RULES)),
    ("narrow", "adj", {}, *C("narrower", "narrowest", **RULES)),
    ("simple", "adj", {}, *C("simpler", "simplest", **RULES)),
    ("quiet", "adj", {}, *C("quieter", "quietest", **RULES)),
    ("clever", "adj", {}, *C("cleverer", "cleverest", **RULES)),
    ("good", "adj", {}, *C("better", "best", **TABLE, note=None)),
    ("beautiful", "adj", {}, *C(None, None, source="rules", status="unverified", regular=True, note=UNDECIDED)),
    ("beautiful", "adj", {"codes": MORE}, *C(None, None, **RULES, note="comparative with more")),
    ("unique", "adj", {"codes": NOT_GRADABLE}, *C(None, None, **RULES, note="not gradable")),
    ("happy", "adj", {"codes": NOT_GRADABLE}, *C(None, None, **RULES, note="not gradable")),
    ("nice", "adj", {}, *C("nicer", "nicest", **RULES)),
    ("gray", "adj", {}, *C("grayer", "grayest", **RULES)),
    ("new", "adj", {}, *C("newer", "newest", **RULES)),
    ("cruel", "adj", {}, *C("crueler", "cruelest", **RULES, note="British spelling doubles the l: crueller, cruellest")),
    ("dry", "adj", {}, *C("drier", "driest", **TABLE, note="also dryer as the comparative")),
    ("free", "adj", {}, *C("freer", "freest", **TABLE)),
    ("far", "adj", {}, *C("farther", "farthest", **TABLE, note="also further, furthest")),
    ("fun", "adj", {}, *C(None, None, **TABLE, note="comparative with more; funner and funnest are informal")),
    ("friendly", "adj", {}, *C("friendlier", "friendliest", **RULES)),
    ("lonely", "adj", {}, *C("lonelier", "loneliest", **RULES)),
    ("polite", "adj", {}, *C(None, None, source="rules", status="unverified", note=UNDECIDED)),
    ("main", "adj", {}, *C(None, None, **TABLE, note="not gradable")),
    ("fast", "adv", {}, *C("faster", "fastest", **TABLE)),
    ("quickly", "adv", {}, *C(None, None, **RULES, note="comparative with more")),
    ("quickly", "adv", {"codes": MORE + NOT_GRADABLE}, *C(None, None, **RULES, note="not gradable")),
    ("well", "adv", {}, *C("better", "best", **TABLE)),
    ("badly", "adv", {}, *C("worse", "worst", **TABLE)),
    ("early", "adv", {}, *C("earlier", "earliest", **TABLE)),
    ("hard", "adv", {}, *C("harder", "hardest", **TABLE)),
    ("straight", "adv", {}, *C("straighter", "straightest", **RULES)),
    ("here", "adv", {}, *C(None, None, **TABLE, note="not gradable")),
    ("often", "adv", {}, *C(None, None, **TABLE, note="comparative with more; oftener is rare")),
    ("actually", "adv", {"codes": NOT_GRADABLE}, *C(None, None, **RULES, note="not gradable")),
]

OTHER_CASES = [(w, p, {}, {}, NONE) for w, p in [
    ("the", "det"), ("of", "prep"), ("and", "conj"), ("it", "pron"), ("one", "num"), ("please", "interj"),
    ("un-", "prefix"), ("-ness", "suffix"), ("eco-", "comb"), ("in spite of", "prep"), ("each other", "pron"),
    ("as far as", "phr"),
]]

ALL_CASES = NOUN_CASES + VERB_CASES + ADJ_CASES + OTHER_CASES


class RuleTests(unittest.TestCase):
    """One generated test per case in the tables above."""


def _make_case(headword, pos, kwargs, forms, meta):
    def test(self):
        got_forms, regular, source, status, note = I.inflect(headword, pos, **kwargs)
        self.assertEqual(got_forms, forms, "%s (%s)" % (headword, pos))
        got = {"regular": regular, "source": source, "status": status, "note": note}
        for key, value in meta.items():
            self.assertEqual(got[key], value, "%s (%s): %s" % (headword, pos, key))
    return test


for _i, _case in enumerate(ALL_CASES):
    _name = "test_%03d_%s_%s" % (_i, eexlib._slug_text(_case[0]).replace("-", "_") or "x", _case[1])
    setattr(RuleTests, _name, _make_case(*_case))


class AllFormsTests(unittest.TestCase):
    def test_verb(self):
        self.assertEqual(I.all_forms("run", "v"), {"run", "runs", "ran", "running"})

    def test_noun_with_alternatives(self):
        self.assertEqual(I.all_forms("mango", "n"), {"mango", "mangoes", "mangos"})
        self.assertEqual(I.all_forms("person", "n"), {"person", "people", "persons"})
        self.assertEqual(I.all_forms("child", "n"), {"child", "children"})

    def test_phrasal_verb(self):
        self.assertEqual(I.all_forms("give up", "phrv"), {"give up", "gives up", "gave up", "given up", "giving up"})

    def test_no_forms(self):
        self.assertEqual(I.all_forms("quickly", "adv"), {"quickly"})
        self.assertEqual(I.all_forms("the", "det"), {"the"})
        self.assertEqual(I.all_forms("information", "n", countability="uncountable"), {"information"})

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            I.inflect("word", "xyz")
        with self.assertRaises(ValueError):
            I.inflect("  ", "n")


class TableTests(unittest.TestCase):
    DENY = ("sb", "sth", "e.g.", "i.e.", "etc.", "approx.", "vs.", "cf.", "esp.", "usu.", "NB")

    def setUp(self):
        self.raw = eexlib.load_json(ROOT / "schema" / "inflection-exceptions.json")

    def test_sections_and_sizes(self):
        for section in ("verbs", "nouns", "adjectives", "adverbs") + I.LIST_SECTIONS:
            self.assertIn(section, self.raw)
        self.assertGreaterEqual(len(self.raw["verbs"]), 180)
        self.assertGreaterEqual(len(self.raw["nouns"]), 100)
        for section in I.LIST_SECTIONS:
            self.assertEqual(len(self.raw[section]), len(set(self.raw[section])), section)

    def test_shapes(self):
        for base, rec in self.raw["verbs"].items():
            self.assertEqual(base, base.lower())
            self.assertTrue(rec.get("past_tense") and rec.get("past_participle"), base)
            self.assertLessEqual(set(rec), {"past_tense", "past_participle", "third_person_singular",
                                            "present_participle", "note"}, base)
        for base, rec in self.raw["nouns"].items():
            self.assertTrue(rec is None or isinstance(rec, (str, list, dict)), base)
            if isinstance(rec, dict):
                self.assertLessEqual(set(rec), {"plural", "also", "note"}, base)
        for section in ("adjectives", "adverbs"):
            for base, rec in self.raw[section].items():
                self.assertLessEqual(set(rec), {"comparative", "superlative", "note"}, base)
                self.assertEqual((rec["comparative"] is None), (rec["superlative"] is None), base)

    def test_notes_are_plain_prose(self):
        def notes(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "note" and isinstance(v, str):
                        yield v
                    else:
                        yield from notes(v)
        for note in notes(self.raw):
            for token in self.DENY:
                self.assertNotIn(" %s " % token, " %s " % note, note)


def _sense(countability=None, codes=()):
    return {"n": 1, "signpost": None, "definition": "a definition", "explanation": None,
            "grammar": {"countability": countability, "transitivity": None, "codes": list(codes), "patterns": []},
            "examples": []}


def _entry(slug, headword, pos, senses, note=None):
    return {"schema_version": "1.0", "id": slug, "slug": slug, "headword": headword, "pos": pos, "homograph": 1,
            "inflections": {"forms": {}, "regular": True, "source": "rules", "status": "unverified", "note": note},
            "senses": senses,
            "provenance": {"created": "2026-01-01T00:00:00Z", "modified": "2026-01-01T00:00:00Z",
                           "drafted_by": "test", "run_id": None, "reviews": [], "status": "draft", "flags": [], "notes": None}}


ENTRIES = [
    _entry("child-n", "child", "n", [_sense("countable"), _sense("countable", ["usually singular"])]),
    _entry("run-v", "run", "v", [_sense()], note="past tense ran, past participle run"),
    _entry("big-adj", "big", "adj", [_sense(), _sense()]),
    _entry("scissors-n", "scissors", "n", [_sense("plural only")]),
    _entry("tv-abbr", "TV", "abbr", [_sense("countable"), _sense("uncountable")]),
    _entry("asap-abbr", "ASAP", "abbr", [_sense()]),
    _entry("happy-adj", "happy", "adj", [_sense(), _sense(codes=["attributive only", "not gradable"])]),
    _entry("quickly-adv", "quickly", "adv", [_sense(codes=["comparative with more"]), _sense(codes=["not gradable"])]),
    _entry("actually-adv", "actually", "adv", [_sense(codes=["not gradable"]), _sense(codes=["sentence adverb", "not gradable"])]),
    _entry("the-det", "the", "det", [_sense()]),
    _entry("give-up-phrv", "give up", "phrv", [_sense()]),
    _entry("color-n", "color", "n", [_sense("countable or uncountable"), _sense("uncountable")]),
]


class CliTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="eex-inflect-"))
        self.entries = self.dir / "entries"
        for entry in ENTRIES:
            eexlib.save_json(self.entries / eexlib.shard(entry["slug"]) / (entry["slug"] + ".json"), entry)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_tool(self, *args):
        cmd = [sys.executable, str(TOOLS / "inflect.py"), "--entries", str(self.entries)] + list(args)
        return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)

    def load(self, slug):
        return eexlib.load_json(self.entries / eexlib.shard(slug) / (slug + ".json"))

    def test_writes_forms_and_touches_nothing_else(self):
        before = self.load("child-n")
        proc = self.run_tool("child-n", "run-v", "big-adj")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        after = self.load("child-n")
        self.assertEqual(after["inflections"], {"forms": {"plural": "children"}, "regular": False,
                                                "source": "exceptions", "status": "verified", "note": None})
        self.assertNotEqual(after["provenance"]["modified"], before["provenance"]["modified"])
        for entry in (before, after):
            entry.pop("inflections")
            entry["provenance"].pop("modified")
        self.assertEqual(before, after)
        self.assertEqual(list(after), list(before))
        self.assertEqual(self.load("run-v")["inflections"]["forms"],
                         {"third_person_singular": "runs", "past_tense": "ran", "past_participle": "run",
                          "present_participle": "running"})
        self.assertEqual(self.load("big-adj")["inflections"]["forms"], {"comparative": "bigger", "superlative": "biggest"})
        self.assertIn("child-n", proc.stdout)
        self.assertIn("plural=children", proc.stdout)

    def test_previous_note_is_printed_and_replaced(self):
        proc = self.run_tool("run-v")
        self.assertIn("previous note replaced: past tense ran, past participle run", proc.stdout)
        self.assertIsNone(self.load("run-v")["inflections"]["note"])

    def test_dry_run_writes_nothing(self):
        before = self.load("child-n")
        proc = self.run_tool("child-n", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("children", proc.stdout)
        self.assertEqual(self.load("child-n"), before)

    def test_entry_codes_and_countability(self):
        proc = self.run_tool("scissors-n", "tv-abbr", "asap-abbr", "happy-adj", "quickly-adv", "actually-adv",
                             "the-det", "give-up-phrv", "color-n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        infl = {slug: self.load(slug)["inflections"] for slug in
                ("scissors-n", "tv-abbr", "asap-abbr", "happy-adj", "quickly-adv", "actually-adv", "the-det",
                 "give-up-phrv", "color-n")}
        self.assertEqual(infl["scissors-n"]["forms"], {"plural": None})
        self.assertEqual(infl["scissors-n"]["note"], "plural only")
        self.assertEqual(infl["tv-abbr"]["forms"], {"plural": "TVs"})
        self.assertEqual((infl["asap-abbr"]["forms"], infl["asap-abbr"]["source"]), ({}, "none"))
        self.assertEqual(infl["happy-adj"]["forms"], {"comparative": "happier", "superlative": "happiest"})
        self.assertEqual((infl["quickly-adv"]["forms"], infl["quickly-adv"]["status"], infl["quickly-adv"]["note"]),
                         ({"comparative": None, "superlative": None}, "verified", "comparative with more"))
        self.assertEqual(infl["actually-adv"]["note"], "not gradable")
        self.assertEqual((infl["the-det"]["forms"], infl["the-det"]["source"]), ({}, "none"))
        self.assertEqual(infl["give-up-phrv"]["forms"]["past_participle"], "given up")
        self.assertEqual(infl["color-n"]["forms"], {"plural": "colors"})

    def test_confirm_sets_status_only(self):
        self.run_tool("big-adj")
        first = self.load("big-adj")
        first["inflections"]["status"] = "unverified"
        eexlib.save_json(self.entries / "bi" / "big-adj.json", first)
        proc = self.run_tool("--confirm", "big-adj")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        after = self.load("big-adj")
        self.assertEqual(after["inflections"]["status"], "verified")
        first["inflections"]["status"] = "verified"
        first["provenance"]["modified"] = after["provenance"]["modified"]
        self.assertEqual(after, first)

    def test_word_prints_json(self):
        proc = self.run_tool("--word", "beautiful", "--pos", "adj", "--code", "comparative with more")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rec = json.loads(proc.stdout)
        self.assertEqual(rec["forms"], {"comparative": None, "superlative": None})
        self.assertEqual((rec["status"], rec["note"]), ("verified", "comparative with more"))
        proc = self.run_tool("--word", "information", "--pos", "n", "--countability", "uncountable")
        self.assertEqual(json.loads(proc.stdout)["forms"], {"plural": None})

    def test_unknown_slug_fails(self):
        proc = self.run_tool("nothing-n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("nothing-n", proc.stderr)

    def test_root_option(self):
        root = self.dir / "root"
        shutil.copytree(ROOT / "schema", root / "schema")
        shutil.copytree(self.entries, root / "entries")
        cmd = [sys.executable, str(TOOLS / "inflect.py"), "--root", str(root), "child-n"]
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(eexlib.load_json(root / "entries" / "ch" / "child-n.json")["inflections"]["forms"],
                         {"plural": "children"})


if __name__ == "__main__":
    unittest.main()
