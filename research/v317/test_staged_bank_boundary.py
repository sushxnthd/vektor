"""V317 staged-service bank-B bottleneck boundary and frozen transfer.

Independent concrete witnesses establish attainability only for listed cases.
Capacity formula is an optimistic lower bound, NOT a general GPU IPC law.
"""
from itertools import product
from math import ceil
import unittest

from research.v317.test_staged_bank_service import (
    BASE, CANDIDATE, cycles, instructions, lower_bound, validate,
)

def service_bounds(a, b, c):
    if min(a, b, c) < 0:
        raise ValueError("negative instruction count")
    n = a + b + c
    unchanged = max(ceil(n / 2), a + c, b + c)
    return max(unchanged, a + b), max(unchanged, b)

WITNESSES = {
    "bank_B_win": {
        "counts": (2, 2, 0),
        "baseline": cycles(
            ("AB1", "AB1", "BC1"),
            ("AB2", "AB2", "BC2"),
            ("-", "BC1", "-"),
            ("-", "BC2", "-")),
        "candidate": cycles(
            ("AB1", "BC1", "BC1"),
            ("AB2", "BC2", "BC2")),
        "expected": (4, 2),
    },
    "new_count_transfer": {
        "counts": (2, 1, 0),
        "baseline": cycles(
            ("AB1", "AB1", "BC1"),
            ("AB2", "AB2", "-"),
            ("-", "BC1", "-")),
        "candidate": cycles(
            ("AB1", "BC1", "BC1"),
            ("AB2", "-", "-")),
        "expected": (3, 2),
    },
}

class StagedBoundaryAudit(unittest.TestCase):
    def test_frozen_predicted_win_and_transfer_have_optimal_witnesses(self):
        for name, case in WITNESSES.items():
            with self.subTest(name=name):
                counts = case["counts"]
                actual = []
                for policy, classes in (("baseline", BASE), ("candidate", CANDIDATE)):
                    req = instructions(counts, classes)
                    cycles_used = validate(req, case[policy])
                    self.assertEqual(cycles_used, lower_bound(req))
                    actual.append(cycles_used)
                self.assertEqual(tuple(actual), case["expected"])
                self.assertEqual(tuple(actual), service_bounds(*counts))

    def test_balanced_no_win_from_independent_previous_witness(self):
        from research.v317.test_staged_bank_service import WITNESSES as earlier
        counts = (2, 2, 2)
        self.assertEqual(service_bounds(*counts), (4, 4))
        for policy, classes in (("baseline", BASE), ("candidate", CANDIDATE)):
            req = instructions(counts, classes)
            self.assertEqual(validate(req, earlier["atomic_predicted_win"][policy]), 4)

    def test_strict_bottleneck_condition_exhaustive_capacity_envelope(self):
        # This checks the *capacity-envelope* condition, not the feasibility
        # of schedules for every count tuple.
        wins = 0
        for a, b, c in product(range(6), repeat=3):
            if not (a or b or c):
                continue
            before, after = service_bounds(a, b, c)
            n = a + b + c
            strict_B = a + b > max(ceil(n / 2), a + c, b + c)
            self.assertEqual(before > after, strict_B)
            self.assertGreaterEqual(before, after)
            wins += int(strict_B)
        self.assertGreater(wins, 0)

if __name__ == "__main__":
    unittest.main()
