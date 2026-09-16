#!/usr/bin/env python3
"""Tests for tools/schema_check.py, the standard-library JSON Schema subset validator.

Run from the repository root:  python3 -m unittest discover -s tools/tests -t .
"""

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eexlib  # noqa: E402
import schema_check  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "bank-n.json"


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = eexlib.load_schema()
        cls.vocab = eexlib.load_vocab()
        cls.entry = eexlib.load_json(FIXTURE)

    def check(self, entry):
        return schema_check.validate(entry, self.schema, self.vocab)

    def mutated(self):
        return copy.deepcopy(self.entry)

    def test_fixture_is_valid(self):
        self.assertEqual(self.check(self.entry), [])

    def test_missing_required_key(self):
        e = self.mutated()
        del e["headword"]
        errors = self.check(e)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], "(root)")
        self.assertIn("headword", errors[0][1])

    def test_missing_required_key_in_nested_object(self):
        e = self.mutated()
        del e["senses"][0]["examples"][1]["note"]
        errors = self.check(e)
        self.assertEqual([p for p, _ in errors], ["senses[0].examples[1]"])
        self.assertIn("'note'", errors[0][1])

    def test_bad_vocabulary_value(self):
        e = self.mutated()
        e["pos"] = "noun"
        errors = self.check(e)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], "pos")
        self.assertIn("vocabulary", errors[0][1])
        e = self.mutated()
        e["senses"][0]["labels"]["domain"] = ["finance", "_doc"]
        errors = self.check(e)
        self.assertEqual([p for p, _ in errors], ["senses[0].labels.domain[1]"])

    def test_wrong_type(self):
        e = self.mutated()
        e["homograph"] = "1"
        errors = self.check(e)
        self.assertEqual([p for p, _ in errors], ["homograph"])
        self.assertIn("integer", errors[0][1])
        e = self.mutated()
        e["homograph"] = True  # booleans are not integers
        self.assertEqual([p for p, _ in self.check(e)], ["homograph"])
        e = self.mutated()
        e["senses"][0]["definition"] = None
        self.assertEqual([p for p, _ in self.check(e)], ["senses[0].definition"])

    def test_additional_property(self):
        e = self.mutated()
        e["extra"] = 1
        errors = self.check(e)
        self.assertEqual(len(errors), 1)
        self.assertIn("'extra'", errors[0][1])
        e = self.mutated()
        e["senses"][1]["synonyms"][0]["comment"] = "x"
        self.assertEqual([p for p, _ in self.check(e)], ["senses[1].synonyms[0]"])

    def test_one_of_reports_the_branch_that_applies(self):
        e = self.mutated()
        del e["pronunciation"]["american"]["ipa"]
        errors = self.check(e)
        self.assertEqual([p for p, _ in errors], ["pronunciation.american"])
        self.assertIn("'ipa'", errors[0][1])
        e = self.mutated()
        e["etymology"] = "unknown"  # neither null nor an object
        errors = self.check(e)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], "etymology")
        self.assertIn("none of the oneOf", errors[0][1])

    def test_pattern_min_items_and_property_names(self):
        e = self.mutated()
        e["etymology"]["checked"] = "16 Sep 2026"
        self.assertEqual([p for p, _ in self.check(e)], ["etymology.checked"])
        e = self.mutated()
        e["etymology"]["sources_consulted"] = ["one"]
        self.assertEqual([p for p, _ in self.check(e)], ["etymology.sources_consulted"])
        e = self.mutated()
        e["l1"] = {"Japanese": {"equivalents": [], "note": None, "status": "draft"}}
        self.assertEqual([p for p, _ in self.check(e)], ["l1"])
        e = self.mutated()
        e["l1"] = {"ja": {"equivalents": [], "note": None, "status": "checked"}}
        self.assertEqual([p for p, _ in self.check(e)], ["l1.ja.status"])

    def test_numeric_bounds_and_const(self):
        e = self.mutated()
        e["frequency"]["band"] = 6
        self.assertEqual([p for p, _ in self.check(e)], ["frequency.band"])
        e = self.mutated()
        e["schema_version"] = "2.0"
        self.assertEqual([p for p, _ in self.check(e)], ["schema_version"])

    def test_null_and_vocabulary(self):
        e = self.mutated()
        e["senses"][0]["grammar"]["countability"] = None  # type allows null
        self.assertEqual(self.check(e), [])
        e["senses"][0]["grammar"]["countability"] = "mass noun"
        self.assertEqual([p for p, _ in self.check(e)], ["senses[0].grammar.countability"])
        e = self.mutated()
        e["inflections"]["source"] = None  # type is string only
        self.assertEqual([p for p, _ in self.check(e)], ["inflections.source"])


class KeywordTests(unittest.TestCase):
    def test_types_and_lists_of_types(self):
        self.assertEqual(schema_check.validate(1, {"type": "integer"}), [])
        self.assertEqual(schema_check.validate(1.0, {"type": "integer"}), [])
        self.assertNotEqual(schema_check.validate(1.5, {"type": "integer"}), [])
        self.assertNotEqual(schema_check.validate(True, {"type": "integer"}), [])
        self.assertNotEqual(schema_check.validate(True, {"type": "number"}), [])
        self.assertEqual(schema_check.validate(None, {"type": ["string", "null"]}), [])
        self.assertNotEqual(schema_check.validate([], {"type": ["string", "null"]}), [])

    def test_enum_const_lengths(self):
        self.assertEqual(schema_check.validate("a", {"enum": ["a", "b"]}), [])
        self.assertNotEqual(schema_check.validate("c", {"enum": ["a", "b"]}), [])
        self.assertNotEqual(schema_check.validate(1, {"const": True}), [])
        self.assertNotEqual(schema_check.validate("", {"type": "string", "minLength": 1}), [])
        self.assertNotEqual(schema_check.validate("abc", {"maxLength": 2}), [])
        self.assertNotEqual(schema_check.validate([1, 2], {"maxItems": 1}), [])

    def test_ref_and_definitions(self):
        schema = {"definitions": {"s": {"type": "string"}}, "properties": {"a": {"$ref": "#/definitions/s"}}}
        self.assertEqual(schema_check.validate({"a": "x"}, schema), [])
        self.assertEqual([p for p, _ in schema_check.validate({"a": 1}, schema)], ["a"])

    def test_any_of_and_additional_properties_schema(self):
        schema = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        self.assertEqual(schema_check.validate("x", schema), [])
        self.assertEqual(schema_check.validate(3, schema), [])
        self.assertNotEqual(schema_check.validate(None, schema), [])
        schema = {"type": "object", "additionalProperties": {"type": "integer"}}
        self.assertEqual(schema_check.validate({"a": 1}, schema), [])
        self.assertEqual([p for p, _ in schema_check.validate({"a": "x"}, schema)], ["a"])

    def test_one_of_with_two_matches(self):
        errors = schema_check.validate(1, {"oneOf": [{"type": "integer"}, {"type": "number"}]})
        self.assertEqual(len(errors), 1)
        self.assertIn("exactly one", errors[0][1])

    def test_unknown_keywords_are_ignored(self):
        self.assertEqual(schema_check.validate("x", {"type": "string", "format": "email", "$comment": "ignored"}), [])


if __name__ == "__main__":
    unittest.main()
