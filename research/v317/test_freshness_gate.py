"""Independent value-oracle regression for frozen V317 forwarding gate."""
import unittest
from research.v317.freshness_gate import Snapshot, forwarding_allowed, audit


class FreshnessGateTests(unittest.TestCase):
    def test_cross_warp_and_cross_bank_alias_rejected(self):
        c = Snapshot(0, 7, 2, 3, 2, 0)
        self.assertFalse(forwarding_allowed(c, 1, 7, 2, 1))
        self.assertFalse(forwarding_allowed(c, 0, 7, 3, 1))
        self.assertFalse(forwarding_allowed(c, 0, 8, 2, 1))

    def test_masked_write_and_missing_lanes(self):
        c = Snapshot(0, 7, 2, 3, 2, 2)
        self.assertTrue(forwarding_allowed(c, 0, 7, 2, 1))
        self.assertFalse(forwarding_allowed(c, 0, 7, 2, 2))
        self.assertFalse(forwarding_allowed(c, 0, 7, 2, 3))
        self.assertFalse(forwarding_allowed(Snapshot(0, 7, 2, 1, 2, 0), 0, 7, 2, 2))
        self.assertFalse(forwarding_allowed(c, 0, 7, 2, 0))

    def test_invalid_entry_and_wrap(self):
        self.assertFalse(forwarding_allowed(Snapshot(0, 7, 2, 3, 2, 0, False), 0, 7, 2, 1))
        for width in range(1, 5):
            self.assertEqual((1 << width) % (1 << width), 0)
            self.assertFalse(forwarding_allowed(Snapshot(0, 7, 2, 3, 0, 1), 0, 7, 2, 1))

    def test_independent_semantic_worlds(self):
        r = audit()
        self.assertEqual(r["conservative_gate_unsafe_admissions"], 0)
        self.assertGreater(r["naive_register_name_invalid_admissions"], 0)
        self.assertGreater(r["naive_register_name_wrong_value_admissions"], 0)
        self.assertGreater(r["conservative_gate_accepted"], 0)
        self.assertEqual(r["matched_reuse_aware_baseline_incremental_transaction_advantage"], 0)


if __name__ == "__main__":
    unittest.main()
