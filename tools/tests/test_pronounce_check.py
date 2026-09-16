"""Tests for the pronunciation normalizer, the ARPAbet mapping, and the agreement rule."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pronounce_check as pc  # noqa: E402


class NormalizeTests(unittest.TestCase):
    def test_n1_moves_stress_to_vowel_and_strips_notation(self):
        self.assertEqual(pc.normalize_n1("ˈrɛk.ɚd"), "rˈɛkɚd")
        self.assertEqual(pc.normalize_n1("/bæŋk/"), "bæŋk")
        self.assertEqual(pc.normalize_n1("kəmˈpjuː.tə"), "kəmpjˈutə")

    def test_n2_mergers(self):
        self.assertTrue(pc.agree("ˈθɔt", "ˈθɑt", "american"))          # cot-caught
        self.assertFalse(pc.agree("fɔr", "fɑr", "american"))           # for / far stay distinct
        self.assertTrue(pc.agree("ˈræb.ɪt", "ˈræb.ət", "american"))    # unstressed ɪ / ə
        self.assertTrue(pc.agree("ˈhæp.i", "ˈhæp.ɪ", "british"))       # final happy vowel
        self.assertTrue(pc.agree("ˈbɑt.əl", "ˈbɑt.l̩", "american"))     # syllabic l
        self.assertTrue(pc.agree("ˈrɛk.ɚd", "ˈrek.ər̩d", "american"))   # ɚ / syllabic r, e / ɛ
        self.assertTrue(pc.agree("ˈɡəʊ", "ɡoʊ", "british"))            # missing stress mark tolerated
        self.assertFalse(pc.agree("rɪˈkɔrd", "ˈrɛkɚd", "american"))    # noun / verb record differ
        self.assertTrue(pc.agree("ˈnjuː", "nju", "british"))

    def test_arpabet(self):
        self.assertEqual(pc.arpabet_to_ipa("B AE1 NG K"), "bˈæŋk")
        self.assertEqual(pc.arpabet_to_ipa("R AH0 K AO1 R D"), "rəkˈɔrd")
        self.assertEqual(pc.arpabet_to_ipa("B AH1 T ER0"), "bˈʌtɚ")
        self.assertTrue(pc.agree("rɪˈkɔrd", pc.arpabet_to_ipa("R AH0 K AO1 R D"), "american"))


class VerdictTests(unittest.TestCase):
    def test_verified_disputed_unverified(self):
        v, cb = pc.verdict("ˈrɛk.ɚd", {"p1": "ˈrɛkɚd", "p2": "ˈrɛk.ərd", "p3": "rɪˈkɔrd", "cmudict": "rˈɛkɚd"}, "american")
        self.assertEqual(v, "verified"); self.assertEqual(cb, "agreement:3/4;cmudict:agree")
        v, cb = pc.verdict("rɪˈkɔrd", {"p1": "ˈrɛkɚd", "p2": "ˈrɛk.ərd", "p3": "ˈrɛkɚd", "cmudict": ""}, "american")
        self.assertEqual(v, "disputed"); self.assertEqual(cb, "agreement:0/3;cmudict:absent")
        v, cb = pc.verdict("rɪˈkɔrd", {"p1": "", "p2": "", "p3": ""}, "american")
        self.assertEqual(v, "unverified")
        v, _ = pc.verdict("ˈbæŋk", {"p1": "bæŋk", "p2": "ˈbæŋk", "p3": ""}, "british", threshold=2)
        self.assertEqual(v, "verified")
        v, _ = pc.verdict("ˈbæŋk", {"p1": "bæŋk", "p2": "ˈbæŋk", "p3": ""}, "british", threshold=3)
        self.assertEqual(v, "unverified")


if __name__ == "__main__":
    unittest.main()
