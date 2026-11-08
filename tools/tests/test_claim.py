import unittest

from tools import claim


class RemainingTest(unittest.TestCase):
    def test_n_is_the_run_total(self):
        self.assertEqual(claim.remaining(12, 0), 12)
        self.assertEqual(claim.remaining(12, 1), 11)
        self.assertEqual(claim.remaining(12, 12), 0)
        self.assertEqual(claim.remaining(12, 15), 0)

    def test_never_above_cap(self):
        self.assertEqual(claim.remaining(50, 0), claim.CAP)
        self.assertEqual(claim.remaining(50, 5), claim.CAP - 5)


if __name__ == "__main__":
    unittest.main()
