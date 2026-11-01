"""Independent adversarial tests for two-port V317 observer semantics."""
import unittest
from research.v317.dual_write_audit import grant, union_hits, exhaustive_audit


class DualWriteAuditTest(unittest.TestCase):
    def test_hidden_second_port_stale_admission(self):
        self.assertTrue(grant(1, 1, 0, 0))
        self.assertFalse(grant(1, 1, 0, union_hits(0, False, 1, True)))

    def test_union_and_namespace_isolation(self):
        self.assertEqual(union_hits(1, True, 2, True), 3)
        self.assertEqual(union_hits(1, False, 2, False), 0)
        self.assertTrue(grant(3, 3, 0, union_hits(3, False, 3, False)))
        self.assertFalse(grant(3, 3, 0, union_hits(1, True, 2, True)))

    def test_sticky_and_coverage(self):
        self.assertFalse(grant(3, 2, 2, 0))
        self.assertFalse(grant(3, 1, 0, 0, coverage=False))
        self.assertTrue(grant(3, 1, 0, 0, coverage=True))

    def test_exhaustive_independent_reference(self):
        r = exhaustive_audit()
        self.assertEqual(r["worlds"], 1024)
        self.assertEqual(r["unsafe_dual_admissions"], 0)
        self.assertGreater(r["unsafe_single_port_integration_admissions"], 0)
        self.assertEqual(r["incremental_same_information_transaction_advantage"], 0)


if __name__ == "__main__":
    unittest.main()
