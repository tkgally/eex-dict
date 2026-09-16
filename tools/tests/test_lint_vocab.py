"""Tests for tools/lint_vocab.py: a temporary repository with a small defining vocabulary, an
inflection-exceptions table and three entries built from the bank-n fixture (one clean, one with
an out-of-vocabulary definition word, one defining-vocabulary word with a loose first sense)."""

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REPO = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import eexlib  # noqa: E402
import link_words  # noqa: E402
import lint_vocab  # noqa: E402

FIXTURE = TOOLS / "tests" / "fixtures" / "bank-n.json"
VOCABULARY = """a an the and of to or for in on at by with that this
be go do have say keep can
place thing store ground river sea land money person
raised safe more than cost pay near office walk wet clear beside here""".split()
EXCEPTIONS = {"_comment": "test table", "go": {"past_tense": "went", "past_participle": "gone"},
              "keep": {"past_tense": "kept", "past_participle": "kept"}}
PROSE_KEYS = {"explanation", "note", "notes", "usage_note", "incorrect", "correct", "text",
              "semantic", "grammar", "culture", "false_friends", "pronunciation"}


def blank_prose(value):
    """The fixture with every free-text field emptied, so a test controls all the words."""
    if isinstance(value, dict):
        return {k: ([] if k == "items" else None if k in PROSE_KEYS and isinstance(v, str) else blank_prose(v))
                for k, v in value.items()}
    if isinstance(value, list):
        return [blank_prose(v) for v in value]
    return value


def make_entry(slug, headword, defining, first, second, sub, phrase, core, examples=(), note=None):
    entry = blank_prose(json.loads(FIXTURE.read_text(encoding="utf-8")))
    entry["id"] = entry["slug"] = slug
    entry["headword"] = headword
    entry["frequency"]["defining_vocabulary"] = defining
    entry["core_idea"] = core
    entry["senses"][0]["definition"] = first
    entry["senses"][0]["subsenses"][0]["definition"] = sub
    entry["senses"][1]["definition"] = second
    entry["phrases"][0]["text"] = "break the " + headword
    entry["phrases"][0]["definition"] = phrase
    entry["senses"][0]["examples"] = [{"text": t, "note": None, "pattern": None} for t in examples]
    entry["usage_note"] = note
    return entry


def quiet_main(argv):
    """lint_vocab.main() with its report captured: (exit code, stdout)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = lint_vocab.main(argv)
    return code, out.getvalue()


class TempRepo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="eex-lint-")
        cls.root = Path(cls.tmp.name)
        shutil.copytree(REPO / "schema", cls.root / "schema")
        (cls.root / "schema" / "defining-vocabulary.txt").write_text(
            "# test vocabulary\n" + "\n".join(VOCABULARY) + "\n", encoding="utf-8")
        eexlib.save_json(cls.root / "schema" / "inflection-exceptions.json", EXCEPTIONS)
        (cls.root / "tools").mkdir()
        for name in ("queue.py", "eexlib.py"):
            shutil.copy(TOOLS / name, cls.root / "tools" / name)
        cls.entries = {
            "bank-n": make_entry("bank-n", "bank", True, "a place that keeps money safe", "the raised ground beside a [[river-n|river]]",
                                 "a store of things", "cost more than a person can pay", "a place for money or the ground beside a river",
                                 ["Mari and Omar went to the bank.", "Kim's banks are near the office."]),
            "shore-n": make_entry("shore-n", "shore", False, "the sandy land beside the sea", "the land beside the sea",
                                  "a store of things", "cost more than a person can pay", "the land beside the sea",
                                  ["Sam walked on the shore.", "The pebbles were wet."], "The pebbles here are wet."),
            "water-n": make_entry("water-n", "water", True, "a clear liquid", "the sea", "a store of things",
                                  "cost more than a person can pay", None),
        }
        for slug, entry in cls.entries.items():
            eexlib.save_json(eexlib.entry_path(slug, cls.root), entry)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def path(self, slug):
        return str(eexlib.entry_path(slug, self.root))


class LemmatizerTests(TempRepo):
    def test_forms_exceptions_rules_and_builtins(self):
        lem = lint_vocab.Lemmatizer(root=self.root)
        self.assertEqual(lem.lemmatize("banks"), "bank")      # the entry's own inflections.forms
        self.assertEqual(lem.lemmatize("went"), "go")         # schema/inflection-exceptions.json
        self.assertEqual(lem.lemmatize("kept"), "keep")
        self.assertEqual(lem.lemmatize("keeps"), "keep")      # rules, accepted because keep is a lemma
        self.assertEqual(lem.candidates("walked"), ["walk"])
        self.assertEqual(lem.lemmatize("is"), "be")           # built-in grammatical verbs
        self.assertEqual(lem.lemmatize("zebras"), "zebras")   # nothing known: the token itself
        self.assertEqual(lem.candidates("zebras"), ["zebras"])
        self.assertEqual(lem.lemmatize("sandy"), "sandy")     # no -y stripping
        self.assertIn("bank", lem.known)
        self.assertIn("go", lem.vocabulary)

    def test_headwords_argument_and_link_words_contract(self):
        lem = lint_vocab.Lemmatizer({"bank", "give up"}, root=self.root)
        self.assertEqual(lem.known, {"bank", "give up"})
        self.assertEqual(lem.lemmatize("banks"), "bank")
        self.assertIsInstance(lem.lemmatize("running"), str)
        self.assertIsInstance(lem.candidates("running"), list)
        for cls in (lint_vocab.Lemmatizer,):
            self.assertTrue(all(hasattr(cls, m) for m in ("lemmatize", "candidates")))
        fn = link_words.external_lemmatizer({"run"})   # the linker's probe against the real repository
        self.assertIsNotNone(fn)
        self.assertIn("run", fn("running"))

    def test_tokenize(self):
        self.assertEqual(lint_vocab.tokenize("a [[cash-n|cash machine]] and [[give-up-phrv]]"), ["cash", "machine", "and", "give", "up"])
        self.assertEqual(lint_vocab.tokenize("Don't say it's Kim's; they're I'm o'clock. Can't we?"),
                         ["do", "say", "it", "they", "o'clock", "can", "we"])
        self.assertEqual(lint_vocab.tokenize("The boys' 3d TVs, e-mail, Mari and Omar, anti-"), ["the", "boys", "tvs", "e-mail", "and", "anti-"])
        self.assertEqual(lint_vocab.tokenize("café ən"), ["cafe"])


class CheckTests(TempRepo):
    def setUp(self):
        self.lem = lint_vocab.Lemmatizer(root=self.root)

    def test_clean_entry(self):
        res = lint_vocab.check_entry(self.lem, self.entries["bank-n"])
        self.assertEqual(res["violations"], [])
        self.assertEqual(res["relaxed"], [])
        self.assertEqual(dict(res["warnings"]), {})   # names skipped, went -> go, banks is the entry's own form

    def test_violation_and_warnings(self):
        res = lint_vocab.check_entry(self.lem, self.entries["shore-n"])
        self.assertEqual([(v["field"], v["lemma"]) for v in res["violations"]], [("senses[0].definition", "sandy")])
        self.assertEqual(dict(res["warnings"]), {"pebbles": 2})   # walked -> walk; were -> be; twice in prose

    def test_first_sense_of_a_defining_word_is_relaxed(self):
        res = lint_vocab.check_entry(self.lem, self.entries["water-n"])
        self.assertEqual(res["violations"], [])
        self.assertEqual([(v["field"], v["lemma"]) for v in res["relaxed"]], [("senses[0].definition", "liquid")])

    def test_multi_word_lemma_and_hyphen_parts(self):
        lem = lint_vocab.Lemmatizer({"in spite of", "well-known"}, root=self.root)
        self.assertEqual(lint_vocab.out_of_vocabulary(lem, "in spite of the sea"), [])
        self.assertEqual(lint_vocab.out_of_vocabulary(lem, "a well-known, sea-safe place"), [])
        self.assertEqual(lint_vocab.out_of_vocabulary(lem, "the spite"), [("spite", None)])


class CommandTests(TempRepo):
    def test_gate_exit_codes(self):
        code, out = quiet_main(["--root", str(self.root), "--gate", self.path("shore-n")])
        self.assertEqual(code, 1)
        self.assertIn("VIOLATION shore-n senses[0].definition: sandy", out)
        self.assertIn("GATE FAILED", out)
        code, out = quiet_main(["--root", str(self.root), "--gate", "bank-n", "water-n"])
        self.assertEqual(code, 0)
        self.assertIn("WARN water-n senses[0].definition: liquid", out)
        code, out = quiet_main(["--root", str(self.root), "--all"])   # no --gate: violations only reported
        self.assertEqual(code, 0)
        self.assertIn("entries checked: 3; violations: 1 in 1 entries", out)
        self.assertIn("WARN shore-n: 1 out-of-vocabulary lemma in examples and notes: pebbles (2)", out)

    def test_dv_option(self):
        extended = self.root / "extended.txt"
        extended.write_text("\n".join(VOCABULARY + ["sandy", "pebble"]) + "\n", encoding="utf-8")
        code, out = quiet_main(["--root", str(self.root), "--dv", str(extended), "--gate", "--all"])
        self.assertEqual(code, 0)
        self.assertNotIn("VIOLATION", out)
        self.assertNotIn("pebbles", out)

    def test_queue(self):
        queue = self.root / "headwords" / "queue.tsv"
        if queue.exists():
            queue.unlink()
        code, out = quiet_main(["--root", str(self.root), "--queue", "shore-n", "water-n"])
        self.assertEqual(code, 0)
        self.assertIn("queue: added 2", out)
        rows = [line.split("\t") for line in queue.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rows[0], ["headword", "pos", "band", "source", "status", "added", "note"])
        by_word = {r[0]: r for r in rows[1:]}
        self.assertEqual(by_word["sandy"][1:5], ["n", "3", "closure", "pending"])
        self.assertEqual(by_word["sandy"][6], "used in shore-n senses[0].definition")
        self.assertEqual(by_word["liquid"][6], "used in water-n senses[0].definition")
        quiet_main(["--root", str(self.root), "--queue", "shore-n"])     # a second run adds no duplicate
        self.assertEqual(len(queue.read_text(encoding="utf-8").splitlines()), 3)

    def test_pos_guess(self):
        lem = lint_vocab.Lemmatizer(root=self.root)
        self.assertEqual(lint_vocab.pos_guess(lem, "wove", "past_tense"), "v")
        self.assertEqual(lint_vocab.pos_guess(lem, "safely", None), "adv")
        self.assertEqual(lint_vocab.pos_guess(lem, "family", None), "n")
        self.assertEqual(lint_vocab.pos_guess(lem, "worse", "comparative"), "adj")

    def test_json(self):
        code, out = quiet_main(["--root", str(self.root), "--json", "--all"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual((data["entries_checked"], data["violations"], data["relaxed"], data["warnings"]), (3, 1, 1, 2))
        self.assertEqual(data["entries"]["shore-n"]["violations"], [{"field": "senses[0].definition", "lemma": "sandy", "kind": None}])
        self.assertIn(["sandy", 1], data["top_definition_lemmas"])
        self.assertIn(["pebbles", 1], data["top_lemmas"])
        self.assertEqual(data["gate"], {"enabled": False, "failed": False, "entries": ["shore-n"]})

    def test_command_line(self):
        proc = subprocess.run([sys.executable, str(TOOLS / "lint_vocab.py"), "--root", str(self.root), "--gate", self.path("shore-n")],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("VIOLATION shore-n", proc.stdout)
        proc = subprocess.run([sys.executable, str(TOOLS / "lint_vocab.py"), "--root", str(self.root), "--gate", self.path("bank-n")],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
