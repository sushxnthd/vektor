"""Frozen V317 strong-baseline identity-sharing challenge (synthetic only)."""
import unittest
from research.v317.operand_identity_reuse import (
    make_instructions, legal_cycle, exact_matching_schedule, validate_witness,
    independent_partition_optimum, predicted_cycles, evaluate, margin_with_overhead,
)

FROZEN = {
    "win": (3, 3, 0, 2, (6, 3)),
    "no_win": (3, 3, 3, 2, (3, 3)),
    "partial": (4, 3, 2, 2, (5, 4)),
    "K1": (2, 2, 2, 1, (4, 4)),
    "transfer_A": (5, 4, 1, 2, (8, 5)),
    "transfer_B": (2, 5, 2, 3, (5, 5)),
}


class IdentityReuseAudit(unittest.TestCase):
    def test_frozen_predictions(self):
        for name, (a, b, s, k, expected) in FROZEN.items():
            with self.subTest(name=name):
                observed = tuple(v[0] for v in evaluate(a, b, s, k))
                self.assertEqual(observed, expected)
                self.assertEqual(observed, predicted_cycles(a, b, s, k))

    def test_complete_reduced_sweep(self):
        worlds = 0
        for a in range(5):
            for b in range(5):
                if not a+b:
                    continue
                for s in range(min(a, b) + 1):
                    for k in (1, 2, 3):
                        with self.subTest(a=a, b=b, s=s, k=k):
                            result = evaluate(a, b, s, k)
                            self.assertEqual(tuple(x[0] for x in result),
                                             predicted_cycles(a, b, s, k))
                            for cand, (cycles, witness) in zip((False, True), result):
                                rows = make_instructions(a, b, s, cand)
                                self.assertTrue(validate_witness(rows, witness, k))
                                if a+b <= 7:
                                    self.assertEqual(
                                        cycles, independent_partition_optimum(rows, k))
                        worlds += 1
        self.assertEqual(worlds, 162)

    def test_adversarial_false_sharing_rejected(self):
        unshared = make_instructions(1, 1, 0, False)
        shared = make_instructions(1, 1, 1, False)
        self.assertFalse(legal_cycle(unshared, (0, 1), 2))
        self.assertTrue(legal_cycle(shared, (0, 1), 2))
        with self.assertRaises(AssertionError):
            validate_witness(unshared, ((0, 1),), 2)
        self.assertEqual(exact_matching_schedule(unshared, 2)[0], 2)
        self.assertEqual(exact_matching_schedule(shared, 2)[0], 1)

    def test_strong_baseline_never_worse_and_overhead(self):
        self.assertEqual(margin_with_overhead(3, 3, 3, 2), 1)
        self.assertLess(margin_with_overhead(3, 3, 3, 2, clock_penalty=.01), 1)
        self.assertGreater(
            margin_with_overhead(3, 3, 0, 2, extra_cycles=.1, clock_penalty=.01), 1.02)
        for s in range(4):
            self.assertEqual(margin_with_overhead(3, 3, s, 2), (6-s)/3)

    def test_invalid_inputs(self):
        for a,b,s,k in ((1,1,2,2),(1,1,-1,2),(0,0,0,1),(1,1,0,0)):
            with self.subTest(case=(a,b,s,k)):
                with self.assertRaises(ValueError):
                    predicted_cycles(a,b,s,k)


if __name__ == "__main__":
    unittest.main()
