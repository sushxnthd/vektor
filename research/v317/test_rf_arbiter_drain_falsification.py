"""Independent frozen regression for finite-batch RF issue scheduling."""
import unittest

from research.v317.rf_arbiter_drain_falsification import (
    case, drain_cycles, independent_legal, optimal_multicycle, sweep,
)
from research.v317.rf_arbiter_port_audit import (
    legal, optimal_grant, rtl_priority_model,
)


class RfDrainFalsificationTests(unittest.TestCase):
    def test_frozen_first_cycle_win_does_not_improve_drain(self):
        pairs = ((0, 0), (0, 1), (0, 1), (0, 0))
        self.assertEqual(rtl_priority_model(7, pairs), 1)
        self.assertEqual(optimal_grant(7, pairs), 6)
        self.assertEqual(case(7, pairs), (2, 2, 2))

    def test_frozen_no_win(self):
        pairs = ((0, 0), (1, 1), (0, 0), (0, 0))
        self.assertEqual(case(3, pairs), (1, 1, 1))

    def test_independent_capacity_oracle(self):
        pairs = ((0, 0), (0, 1), (1, 1), (2, 2))
        for valid in range(16):
            for grant in range(16):
                self.assertEqual(
                    independent_legal(grant, valid, pairs),
                    legal(grant, valid, pairs),
                )

    def test_empty_batch(self):
        pairs = ((0, 0),) * 4
        self.assertEqual(drain_cycles(0, pairs, optimal_grant), 0)
        self.assertEqual(optimal_multicycle(0, pairs), 0)

    def test_frozen_exhaustive_and_transfer_counts(self):
        result = sweep()
        two = result["exhaustive_two_bank"]["counts"]
        self.assertEqual(two["cases"], 4096)
        self.assertEqual(two["priority_cycles"], 6508)
        self.assertEqual(two["exact_cycles"], 6508)
        self.assertEqual(two["optimal_cycles"], 6508)
        self.assertEqual(two["exact_better"], 0)
        self.assertEqual(two["exact_worse"], 0)
        four = result["fixed_seed_four_bank_transfer"]["counts"]
        self.assertEqual(four["cases"], 10000)
        self.assertEqual(four["priority_cycles"], 12421)
        self.assertEqual(four["exact_cycles"], 12425)
        self.assertEqual(four["optimal_cycles"], 12410)
        self.assertEqual(four["exact_better"], 7)
        self.assertEqual(four["exact_worse"], 11)
        self.assertEqual(four["greedy_suboptimal"], 11)
        self.assertEqual(four["exact_suboptimal"], 15)


if __name__ == "__main__":
    unittest.main()
