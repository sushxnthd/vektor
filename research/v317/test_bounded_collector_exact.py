"""Prospective bounded-collector checks; no physical GPU claims."""
from itertools import product
import unittest
from research.v317.bounded_collector_exact import (
    solve, independent_validate, independent_reachable, lower_bound,
)

FROZEN = {
    "win": ((2, 2, 0), 2, (4, 2)),
    "no_win": ((2, 2, 2), 4, (4, 4)),
    "transfer": ((2, 1, 0), 2, (3, 2)),
    # Frozen (8,6) prediction was WRONG. A K=1 collector can read two
    # distinct banks for one instruction in the same cycle, so both take 4.
    "tight_occupancy": ((2, 2, 0), 1, (4, 4)),
}
UNOPENED = {
    "transfer_321": ((3, 2, 1), 2, (5, 4)),
    "transfer_132": ((1, 3, 2), 3, (5, 5)),
    "transfer_303": ((3, 0, 3), 2, (6, 6)),
}


class BoundedCollectorAudit(unittest.TestCase):
    def test_frozen_and_transfer(self):
        for name, (counts, k, expected) in (FROZEN | UNOPENED).items():
            with self.subTest(name=name):
                actual = []
                for cand in (False, True):
                    cycles, path = solve(counts, k, cand)
                    self.assertTrue(independent_validate(counts, k, cand, path))
                    self.assertGreaterEqual(cycles, lower_bound(counts, cand))
                    actual.append(cycles)
                self.assertEqual(tuple(actual), expected)

    def test_k1_falsifies_preregistered_formula(self):
        for a, b, c in product(range(3), repeat=3):
            if a+b+c == 0:
                continue
            for cand in (False, True):
                cycles, path = solve((a, b, c), 1, cand)
                self.assertEqual(cycles, a+b+c)
                self.assertTrue(independent_validate((a, b, c), 1, cand, path))

    def test_exactness_against_independent_depth_limited_oracle(self):
        for a, b, c in product(range(2), repeat=3):
            if a+b+c == 0:
                continue
            for k in (1, 2, 3):
                for cand in (False, True):
                    counts = (a, b, c)
                    cycles, path = solve(counts, k, cand)
                    self.assertTrue(independent_validate(counts, k, cand, path))
                    self.assertFalse(independent_reachable(counts, k, cand, cycles-1))
                    self.assertTrue(independent_reachable(counts, k, cand, cycles))

    def test_collector_monotonicity_and_no_negative_gain(self):
        for counts in ((2,2,0), (2,2,2), (2,1,0),
                       (3,2,1), (1,3,2), (3,0,3)):
            previous = [999, 999]
            for k in range(1, 7):
                result = []
                for cand in (False, True):
                    n, path = solve(counts, k, cand)
                    self.assertTrue(independent_validate(counts, k, cand, path))
                    result.append(n)
                self.assertLessEqual(result[0], previous[0])
                self.assertLessEqual(result[1], previous[1])
                self.assertGreaterEqual(result[0], result[1])
                previous = result

    def test_adversarial_invalid_trace(self):
        counts = (1,1,0)
        _, path = solve(counts, 2, False)
        bad = list(path)
        bad[0] = ((3,0,0), bad[0][1])
        with self.assertRaises(AssertionError):
            independent_validate(counts, 2, False, bad)
        bad = list(path)
        bad[0] = (bad[0][0], (999,-1,-1))
        with self.assertRaises(AssertionError):
            independent_validate(counts, 2, False, bad)


if __name__ == "__main__":
    unittest.main()
