"""Frozen and independent port-oracle regression for Vektor RF arbiter."""
import unittest

from research.v317.rf_arbiter_port_audit import (
    audit_case, bank_demands, legal, optimal_grant, rtl_priority_model,
    safe_priority_model, sweep,
)


class ArbiterPortAudit(unittest.TestCase):
    def test_frozen_failed_prediction_is_preserved(self):
        pairs = ((0, 0), (0, 0), (0, 0), (0, 0))
        x = audit_case(3, pairs)
        self.assertFalse(x["overgrant"])
        self.assertEqual(x["raw_mask"], 1)
        self.assertEqual(x["safe_mask"], 1)
        self.assertEqual(bank_demands(x["raw_mask"], pairs)[0], 2)

    def test_frozen_pass(self):
        pairs = ((0, 0), (1, 1), (0, 0), (1, 1))
        x = audit_case(3, pairs)
        self.assertFalse(x["overgrant"])
        self.assertEqual(x["safe_mask"], 3)

    def test_same_bank_charges_two_ports(self):
        self.assertEqual(
            bank_demands(1, ((2, 2), (0, 0), (0, 0), (0, 0)))[2], 2
        )

    def test_invalid_slots_never_granted(self):
        pairs = ((0, 1), (1, 2), (2, 3), (3, 0))
        for valid in range(16):
            self.assertEqual(rtl_priority_model(valid, pairs) & ~valid, 0)
            self.assertTrue(legal(safe_priority_model(valid, pairs), valid, pairs))

    def test_independent_exact_maximum(self):
        pairs = ((0, 0), (0, 1), (1, 1), (2, 2))
        for valid in range(16):
            result = optimal_grant(valid, pairs)
            self.assertTrue(legal(result, valid, pairs))
            self.assertGreaterEqual(
                result.bit_count(), safe_priority_model(valid, pairs).bit_count()
            )

    def test_full_frozen_and_random_sweep(self):
        r = sweep()
        self.assertEqual(r["exhaustive_two_bank"]["cases"], 4096)
        self.assertEqual(r["random_four_bank"]["cases"], 10000)
        self.assertEqual(r["exhaustive_two_bank"]["overgrant_cases"], 0)
        self.assertEqual(r["random_four_bank"]["overgrant_cases"], 0)
        self.assertEqual(r["exhaustive_two_bank"]["safe_suboptimal_cases"], 244)
        self.assertEqual(r["random_four_bank"]["safe_suboptimal_cases"], 178)


if __name__ == "__main__":
    unittest.main()
