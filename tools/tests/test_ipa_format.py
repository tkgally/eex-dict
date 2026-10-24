"""Tests for tools/ipa_format.py (the owner's ruling B4 (iv) of 2026-10-24): periods move, nothing else."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eexlib  # noqa: E402
import ipa_format  # noqa: E402


class HouseFormTest(unittest.TestCase):
    def test_house_form(self):
        self.assertEqual(eexlib.ipa_house_form("prɪ.ˈvɛnt"), "prɪˈvɛnt")
        self.assertEqual(eexlib.ipa_house_form("ə.ˈdɪ.ʃə.nəl"), "əˈdɪ.ʃə.nəl")
        self.assertEqual(eexlib.ipa_house_form("ˌaʊt.ˈsaɪd"), "ˌaʊtˈsaɪd")
        self.assertEqual(eexlib.ipa_house_form("ˈdɪf.ər.ənt"), "ˈdɪf.ər.ənt")
        self.assertEqual(eexlib.ipa_house_form("ɡɪv ˈʌp"), "ɡɪv ˈʌp")

    def test_proof(self):
        self.assertTrue(eexlib.ipa_only_periods_moved("prɪ.ˈvɛnt", "prɪˈvɛnt"))
        self.assertFalse(eexlib.ipa_only_periods_moved("prɪ.ˈvɛnt", "ˈprɪvɛnt"))
        self.assertFalse(eexlib.ipa_only_periods_moved("prɪ.ˈvɛnt", "prɪˈvent"))


class FormatEntryTest(unittest.TestCase):
    def entry(self):
        return {"slug": "inside-n", "pronunciation": {
            "american": {"ipa": "ɪn.ˈsaɪd", "checked_by": "agreement:1/4;owner-ruling:2026-10-05:ɪn.ˈsaɪd", "status": "verified"},
            "british": {"ipa": "ˌɪnˈsaɪd", "checked_by": "agreement:3/3", "status": "verified"},
            "variants": [{"ipa": "ˈɪn.saɪd", "region": None, "note": None}], "notes": "Stress *in.SIDE*."},
            "senses": [{"pronunciation": {"american": {"ipa": "ri.ˈkɔrd"}}}]}

    def test_only_ipa_and_the_owner_ruling_copy_change(self):
        e = self.entry()
        changes = ipa_format.format_entry(e)
        self.assertEqual(e["pronunciation"]["american"]["ipa"], "ɪnˈsaɪd")
        self.assertEqual(e["pronunciation"]["american"]["checked_by"], "agreement:1/4;owner-ruling:2026-10-05:ɪnˈsaɪd")
        self.assertEqual(e["pronunciation"]["variants"][0]["ipa"], "ˈɪn.saɪd")   # a period not beside a stress mark stays
        self.assertEqual(e["pronunciation"]["notes"], "Stress *in.SIDE*.")      # prose is never touched
        self.assertEqual(e["senses"][0]["pronunciation"]["american"]["ipa"], "riˈkɔrd")
        self.assertEqual(len(changes), 3)
        self.assertEqual(ipa_format.format_entry(e), [])                        # idempotent

    def test_owner_ruling_still_matches_after_the_move(self):
        import pronounce_check
        self.assertEqual(pronounce_check.owner_ruling("owner-ruling:2026-10-05:ɪn.ˈsaɪd", "ɪnˈsaɪd"), "2026-10-05")


if __name__ == "__main__":
    unittest.main()
