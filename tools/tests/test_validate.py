#!/usr/bin/env python3
"""End-to-end tests for tools/validate.py on a temporary copy of the repository layout.

Each test builds a repository under a temporary directory (schema/ and tools/
copied, entries/ba/bank-n.json made from the fixture), then runs validate.py
as a subprocess with --root pointing at it.

Run from the repository root:  python3 -m unittest discover -s tools/tests -t .
"""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REPO = TOOLS.parent
FIXTURE = TOOLS / "tests" / "fixtures" / "bank-n.json"


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class TempRepo:
    """A throwaway repository layout with one entry made from the fixture."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="eex-validate-"))
        shutil.copytree(REPO / "schema", self.dir / "schema")
        shutil.copytree(TOOLS, self.dir / "tools", ignore=shutil.ignore_patterns("__pycache__", "tests"))
        (self.dir / "entries").mkdir()
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.entry_path = self.dir / "entries" / "ba" / "bank-n.json"
        write_json(self.entry_path, self.fixture)

    def entry(self):
        return copy.deepcopy(self.fixture)

    def write(self, entry, relpath="entries/ba/bank-n.json"):
        write_json(self.dir / relpath, entry)

    def run(self, *args):
        proc = subprocess.run([sys.executable, str(self.dir / "tools" / "validate.py"), "--root", str(self.dir), *args],
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout + proc.stderr

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class ValidateTests(unittest.TestCase):
    def setUp(self):
        self.repo = TempRepo()
        self.addCleanup(self.repo.cleanup)

    def assertPasses(self, *args):
        code, out = self.repo.run(*args)
        self.assertEqual(code, 0, out)
        self.assertIn("0 errors", out)
        return out

    def assertFails(self, needle, *args):
        code, out = self.repo.run(*args)
        self.assertEqual(code, 1, out)
        self.assertIn("ERROR", out)
        self.assertIn(needle, out)
        return out

    def test_fixture_passes(self):
        out = self.assertPasses()
        self.assertIn("validate: 1 files, 0 errors, 0 warnings", out)
        self.assertPasses("--all")
        self.assertPasses("--gate")
        self.assertPasses(str(self.repo.entry_path))
        self.assertPasses("entries")

    def test_abbreviation_in_definition(self):
        e = self.repo.entry()
        e["senses"][0]["definition"] = "a business, e.g. one that keeps money"
        self.repo.write(e)
        self.assertFails("'e.g.'")

    def test_abbreviation_with_possessive(self):
        e = self.repo.entry()
        e["usage_note"] = "Use it for sb's money."
        self.repo.write(e)
        self.assertFails("'sb'")

    def test_abbreviation_inside_a_word_is_fine(self):
        e = self.repo.entry()
        e["usage_note"] = "Her husband bought something at the best price."
        self.repo.write(e)
        self.assertPasses()

    def test_sense_with_one_example(self):
        e = self.repo.entry()
        e["senses"][1]["examples"] = e["senses"][1]["examples"][:1]
        self.repo.write(e)
        self.assertFails("senses[1] has 1 example")

    def test_adaptation_note_over_the_cap(self):
        e = self.repo.entry()
        e["adaptation"]["culture"] = " ".join(["word"] * 61)
        self.repo.write(e)
        self.assertFails("61 words")
        e["adaptation"]["culture"] = " ".join(["word"] * 60)
        self.repo.write(e)
        self.assertPasses()

    def test_wrong_shard_path(self):
        self.repo.entry_path.unlink()
        self.repo.write(self.repo.entry(), "entries/bn/bank-n.json")
        self.assertFails("shard")

    def test_reviewed_without_reviews(self):
        e = self.repo.entry()
        e["provenance"]["status"] = "reviewed"
        e["provenance"]["flags"] = ["pronunciation-unverified"]
        self.repo.write(e)
        self.assertFails("provenance.reviews")

    def test_reviewed_needs_verified_or_flagged_pronunciation(self):
        e = self.repo.entry()
        e["provenance"]["status"] = "reviewed"
        e["provenance"]["reviews"] = self.reviews()
        self.repo.write(e)
        self.write_review_file(blocking=0)
        self.assertFails("pronunciation flag")

    def test_reviewed_blocking_issues_need_decisions(self):
        e = self.repo.entry()
        e["provenance"]["status"] = "reviewed"
        e["provenance"]["flags"] = ["pronunciation-unverified"]
        e["provenance"]["reviews"] = self.reviews()
        self.repo.write(e)
        self.assertFails("does not exist")  # no review file yet
        self.write_review_file(blocking=1)
        self.assertFails("decision line")
        decision = {"ts": "2026-09-16T13:00:00Z", "run_id": "run1", "slug": "bank-n", "field": "senses[0].definition",
                    "role": "reviewer-a", "family": "definition-meaning", "severity": "blocking", "decision": "apply", "note": "fixed"}
        (self.repo.dir / "reviews" / "decisions.jsonl").write_text(json.dumps(decision) + "\n", encoding="utf-8")
        self.assertPasses()

    def reviews(self):
        return [{"run_id": "run1", "role": role, "model": "reviewer", "date": "2026-09-16",
                 "file": "reviews/run1/bank-n.json", "ok": 10, "issues": 0, "blocking": 0}
                for role in ("reviewer-a", "reviewer-b")]

    def write_review_file(self, blocking):
        verdicts = [{"field": "senses[0].definition", "verdict": "issue", "quote": "x", "severity": "blocking",
                     "family": "definition-meaning", "reason": "r"}] * blocking
        write_json(self.repo.dir / "reviews" / "run1" / "bank-n.json",
                   {"run_id": "run1", "slug": "bank-n", "entry_modified": "2026-09-16T12:00:00Z",
                    "reviewers": [{"role": "reviewer-a", "verdicts": verdicts}, {"role": "reviewer-b", "verdicts": []}]})

    def test_identity_and_schema_errors(self):
        e = self.repo.entry()
        e["id"] = "bank-v"
        self.repo.write(e)
        self.assertFails("id 'bank-v' does not equal slug")
        e = self.repo.entry()
        e["headword"] = "banks"
        self.repo.write(e)
        self.assertFails("should be 'banks-n'")
        e = self.repo.entry()
        del e["etymology"]
        self.repo.write(e)
        self.assertFails("schema:")
        self.repo.entry_path.write_text("{not json", encoding="utf-8")
        self.assertFails("cannot parse JSON")

    def test_phrase_sub_id_and_core_idea(self):
        e = self.repo.entry()
        e["phrases"][0]["sub_id"] = "break-bank"
        self.repo.write(e)
        self.assertFails("phrases[0].sub_id")
        e = self.repo.entry()
        e["senses"] = e["senses"][:1]
        self.repo.write(e)
        self.assertFails("core_idea is set but the entry has only one sense")

    def test_pronunciation_rules(self):
        e = self.repo.entry()
        e["pronunciation"]["american"] = None
        self.repo.write(e)
        self.assertFails("pronunciation.american is null")
        e = self.repo.entry()
        e["pronunciation"]["british"]["ipa"] = "/bæŋk/"
        self.repo.write(e)
        self.assertFails("pronunciation.british.ipa")
        e = self.repo.entry()
        e["pronunciation"]["british"]["ipa"] = "bæ.ŋk"
        self.repo.write(e)
        out = self.assertPasses()
        self.assertIn("WARN", out)
        self.assertIn("stress", out)

    def test_inline_marks(self):
        e = self.repo.entry()
        e["usage_note"] = "**Bank** takes **the**: *in the bank*, *at the bank*."
        e["senses"][0]["definition"] = "a business that keeps money; compare **account**"
        self.repo.write(e)
        self.assertPasses()
        e = self.repo.entry()
        e["usage_note"] = "A lone * asterisk"
        self.repo.write(e)
        self.assertFails("usage_note: an asterisk that is not a well-formed mark")
        e = self.repo.entry()
        e["usage_note"] = "**a *nested* mark**"
        self.repo.write(e)
        self.assertFails("marks do not nest")
        e = self.repo.entry()
        e["senses"][0]["examples"][0]["text"] = "Mari opened an account at *the bank*."
        self.repo.write(e)
        self.assertFails("an example carries no single-asterisk mark")
        e = self.repo.entry()
        e["senses"][0]["collocations"][0]["items"][0] = "**bank** account"
        self.repo.write(e)
        self.assertFails("marks are not used in this field")
        e = self.repo.entry()
        e["learner_errors"][0]["incorrect"] = "I went to *bank*."
        self.repo.write(e)
        self.assertFails("marks are not used in this field")
        e = self.repo.entry()
        e["usage_note"] = "see [[account-n|**account**]]"
        self.repo.write(e)
        self.assertFails("a link override carries no mark inside it")

    def test_example_without_the_headword_warns_unless_marked(self):
        e = self.repo.entry()
        e["senses"][0]["examples"][0]["text"] = "Mari opened an account near her office."
        self.repo.write(e)
        out = self.assertPasses()
        self.assertIn("examples[0].text: example contains neither the headword nor a listed form", out)
        e["senses"][0]["examples"][0]["text"] = "Mari **banked** the check near her office."
        self.repo.write(e)
        out = self.assertPasses()
        self.assertNotIn("contains neither", out)
        # a plural, a possessive, and a contraction all count as the headword
        for text in ("Two banks closed.", "The bank's door was shut.", "The bank's open, isn't it?"):
            e["senses"][0]["examples"][0]["text"] = text
            self.repo.write(e)
            self.assertNotIn("contains neither", self.assertPasses())
        # affixes live inside their words: no check
        e = self.repo.entry()
        e["pos"], e["slug"], e["id"], e["headword"] = "prefix", "un-prefix", "un-prefix", "un-"
        e["pronunciation"]["american"] = e["pronunciation"]["british"] = None
        e["senses"][0]["examples"][0]["text"] = "The test was unfair."
        self.repo.write(e, "entries/un/un-prefix.json")
        (self.repo.dir / "entries" / "ba" / "bank-n.json").unlink()
        self.assertNotIn("contains neither", self.assertPasses())

    def test_pronunciation_notes_in_plain_words(self):
        e = self.repo.entry()
        e["pronunciation"]["notes"] = "The last sound is a schwa."
        self.repo.write(e)
        self.assertFails("pronunciation.notes: 'schwa' is a technical term")
        e = self.repo.entry()
        e["adaptation"]["pronunciation"] = "The final d is voiced."
        self.repo.write(e)
        self.assertFails("adaptation.pronunciation: 'voiced' is a technical term")
        e = self.repo.entry()
        e["usage_note"] = "Voiced opinions are welcome."     # only pronunciation prose is checked
        self.repo.write(e)
        self.assertPasses()

    def test_warnings_for_example_punctuation_and_unknown_link_target(self):
        e = self.repo.entry()
        e["senses"][0]["examples"][0]["text"] = "No full stop after this bank"
        e["usage_note"] = "See [[shore-n|shore]]."
        self.repo.write(e)
        out = self.assertPasses()
        self.assertIn("WARN", out)
        self.assertIn("does not end", out)
        self.assertIn("'shore-n' has no entry", out)
        code, quiet = self.repo.run("--quiet")
        self.assertEqual(code, 0)
        self.assertNotIn("WARN", quiet)
        self.assertIn("2 warnings", quiet)
        e["usage_note"] = "See [[Bad Slug|x]]."
        self.repo.write(e)
        self.assertFails("not a well-formed slug")

    def test_redirect_stub(self):
        stub = {"schema_version": "1.0", "slug": "banc-n", "redirect_to": "bank-n", "renamed": "2026-09-16", "reason": "spelling"}
        self.repo.write(stub, "entries/ba/banc-n.json")
        self.assertFails("redirects.json")
        write_json(self.repo.dir / "headwords" / "redirects.json", {"banc-n": "bank-n"})
        out = self.assertPasses()
        self.assertIn("2 files", out)
        stub["redirect_to"] = "nowhere-n"
        self.repo.write(stub, "entries/ba/banc-n.json")
        self.assertFails("not an existing entry")

    def test_homograph_rules(self):
        e = self.repo.entry()
        e["homograph"] = 2
        self.repo.write(e)
        self.assertFails("homograph 2")
        e.update(slug="bank-n-2", id="bank-n-2")
        self.repo.write(e, "entries/ba/bank-n-2.json")
        out = self.assertPasses(str(self.repo.dir / "entries" / "ba" / "bank-n-2.json"))
        self.assertNotIn("WARN", out)  # bank-n exists
        self.repo.entry_path.unlink()
        out = self.assertPasses()
        self.assertIn("earlier homograph entries do not exist", out)

    def test_duplicate_slugs_and_draft_ceiling_under_gate(self):
        e = self.repo.entry()
        self.repo.write(e, "entries/xx/bank-n.json")
        out = self.assertFails("appears in 2 files", "--all")
        self.assertIn("shard directory", out)
        (self.repo.dir / "entries" / "xx" / "bank-n.json").unlink()
        for i in range(41):
            head = "word" + chr(ord("a") + i // 26) + chr(ord("a") + i % 26)
            e = self.repo.entry()
            e.update(headword=head, slug=head + "-n", id=head + "-n")
            self.repo.write(e, "entries/wo/%s-n.json" % head)
        self.assertPasses("--all")
        self.assertFails("status draft", "--gate")

    def test_gate_checks_crossref_slugs(self):
        e = self.repo.entry()
        e["word_family"][0]["slug"] = "bank-verb"
        self.repo.write(e)
        self.assertPasses()
        self.assertFails("word_family[0].slug", "--gate")

    def test_fix_format(self):
        scrambled = json.loads(json.dumps(self.repo.fixture, sort_keys=True))
        self.repo.entry_path.write_text(json.dumps(scrambled), encoding="utf-8")
        out = self.assertPasses("--fix-format")
        self.assertIn("formatted entries/ba/bank-n.json", out)
        self.assertEqual(self.repo.entry_path.read_text(encoding="utf-8"), FIXTURE.read_text(encoding="utf-8"))
        out = self.assertPasses("--fix-format")
        self.assertNotIn("formatted", out)
        e = self.repo.entry()
        e["senses"][0]["definition"] = "a place, e.g. a shop"
        self.repo.entry_path.write_text(json.dumps(e), encoding="utf-8")
        out = self.assertFails("'e.g.'", "--fix-format")
        self.assertIn("skipped", out)
        self.assertEqual(self.repo.entry_path.read_text(encoding="utf-8"), json.dumps(e))


if __name__ == "__main__":
    unittest.main()
