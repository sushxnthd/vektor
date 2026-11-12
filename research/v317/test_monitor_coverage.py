"""Independent V317 monitor-coverage information and fail-closed tests."""
import unittest
from itertools import product
from research.v317.monitor_coverage import (
    ambiguous_worlds, apply_masked_write, guarded_grant, next_poison, audit,
)


class MonitorCoverageAudit(unittest.TestCase):
    def test_hidden_write_indistinguishable(self):
        for lanes in (1, 2, 3):
            count, witness = ambiguous_worlds(lanes)
            self.assertGreater(count, 0)
            self.assertNotEqual(witness["world_without_write_value"],
                                witness["world_with_hidden_write_value"])
            self.assertEqual(witness["same_observed_write_events"], [])

    def test_masked_write_reference(self):
        for old, new, mask in product(range(4), repeat=3):
            updated = apply_masked_write(old, new, mask)
            self.assertEqual((old ^ updated) & ~mask, 0)
            self.assertEqual((new ^ updated) & mask, 0)

    def test_fault_immediately_blocks_and_sticks(self):
        poison = True
        poison = next_poison(poison, capture=True, coverage_ok=True)
        self.assertFalse(poison)
        self.assertTrue(guarded_grant(poison, True, 3, 1))
        self.assertFalse(guarded_grant(poison, False, 3, 1))
        poison = next_poison(poison, capture=False, coverage_ok=False)
        self.assertTrue(poison)
        self.assertFalse(guarded_grant(poison, True, 3, 1))
        poison = next_poison(poison, capture=True, coverage_ok=False)
        self.assertTrue(poison)
        poison = next_poison(poison, capture=True, coverage_ok=True)
        self.assertFalse(poison)
        self.assertTrue(guarded_grant(poison, True, 3, 1))

    def test_undetected_write_is_unsolved(self):
        old, new, requested = 0, 1, 1
        self.assertTrue(guarded_grant(False, True, 1, requested))
        self.assertNotEqual(old & requested,
                            apply_masked_write(old, new, 1) & requested)

    def test_same_information_baseline_no_gain(self):
        report = audit()
        self.assertEqual(report["incremental_forwarding_transaction_advantage"], 0)
        self.assertEqual(report["same_information_baseline_cases"], 2*2*4*4*4)


if __name__ == "__main__":
    unittest.main()
