"""Independent semantic checks for V317's frozen B-deletion challenge."""
import unittest
from research.v317.functional_information_gate import (
    MODULUS, ab_op, bc_op, drop_b, remat_equal_a, remat_from_a_c,
    forward_b, two_world_witness, exhaustive_audit, MATCHED_COSTS,
)


class FunctionalInformationGate(unittest.TestCase):
    def test_two_world_information_impossibility(self):
        witness = two_world_witness()
        self.assertEqual(witness["required_ab_outputs"], [0, 3])
        self.assertEqual(witness["candidate_output"], 0)
        # Independently: with fixed A,C, AB takes 16 different values as B varies.
        for a in range(MODULUS):
            outputs = {ab_op(a, b) for b in range(MODULUS)}
            self.assertEqual(len(outputs), MODULUS)
            self.assertEqual(len({drop_b(a) for _ in range(MODULUS)}), 1)

    def test_exhaustive_frozen_regimes(self):
        report = exhaustive_audit()
        c = report["counts"]
        self.assertEqual((c["unconstrained_worlds"], c["invalid_drop_worlds"]), (4096, 3840))
        for name in ("b_eq_a", "b_eq_a_xor_c", "shared_identity"):
            self.assertEqual(c[name + "_worlds"], c[name + "_pass"])
        self.assertEqual(c["distinct_identity_rejections"], 4096)

    def test_recomputation_does_not_magically_supply_b(self):
        for a in range(MODULUS):
            for b in range(MODULUS):
                self.assertEqual(remat_equal_a(a) == ab_op(a, b), a == b)
        for a in range(MODULUS):
            for c in range(MODULUS):
                b = a ^ c
                self.assertEqual(remat_from_a_c(a, c), ab_op(a, b))
                self.assertEqual(bc_op(b, c), b ^ c)

    def test_forwarding_requires_identity_not_coincidental_value(self):
        self.assertEqual(forward_b(4, 7, "R5", "R5"), ab_op(4, 7))
        with self.assertRaises(ValueError):
            forward_b(4, 7, "R5", "R6")

    def test_strong_baseline_has_identical_transaction_capabilities(self):
        self.assertEqual(MATCHED_COSTS["proven_b_eq_a"].b_bank_reads, 0)
        self.assertEqual(MATCHED_COSTS["proven_b_eq_a_xor_c"].xor_operations, 1)
        self.assertEqual(MATCHED_COSTS["proven_b_eq_a_xor_c"].c_bank_reads, 1)
        self.assertEqual(MATCHED_COSTS["same_identity_forward_from_bc"].b_bank_reads, 1)
        report = exhaustive_audit()
        self.assertTrue(all(x["incremental_transaction_advantage"] == 0
                            for x in report["candidate_vs_equal_knowledge_baseline"].values()))


if __name__ == "__main__":
    unittest.main()
