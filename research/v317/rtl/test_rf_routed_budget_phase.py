"""Independent tests for V317 tile-budget phase law."""
import unittest
from fractions import Fraction
from rf_routed_budget_phase import (
    Regime, SOURCE_AREA, PAIR_AREA, exact_budget_phase_counts,
    extra_tile_fraction, frozen_regimes, tile_count, throughput,
)

class TestBudgetPhase(unittest.TestCase):
    def test_frozen_win_fraction(self):
        c = frozen_regimes()[0]
        self.assertEqual(extra_tile_fraction(c), Fraction(18325, 41316))
        r = exact_budget_phase_counts(c)
        self.assertEqual(r["extra_budget_count"], 18325)
        self.assertEqual(r["win_budget_count"], 18325)
        self.assertEqual(r["loss_budget_count"], 0)
        self.assertEqual(r["max_extra_tiles"], 1)
        self.assertEqual(r["baseline_exact_budget_gain"], 1.0)

    def test_bandwidth_no_win(self):
        r = exact_budget_phase_counts(frozen_regimes()[1])
        self.assertEqual(r["extra_budget_count"], 18325)
        self.assertEqual(r["win_budget_count"], 0)
        self.assertEqual(r["loss_budget_count"], 0)

    def test_transfer_holdouts(self):
        for c in frozen_regimes()[2:5]:
            with self.subTest(name=c.name):
                r = exact_budget_phase_counts(c)
                self.assertTrue(r["predicted_exact_match"])
                self.assertEqual(r["loss_budget_count"], 0)

    def test_clock_critical_is_conditional(self):
        c = frozen_regimes()[5]
        budget = c.n_source * (c.other_area + SOURCE_AREA)
        self.assertEqual(tile_count(budget, c.other_area, PAIR_AREA), c.n_source)
        self.assertAlmostEqual(
            throughput(budget, c, True) / throughput(budget, c, False), 1.56)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            extra_tile_fraction(Regime("invalid", -1, 40000, 2.0))
        with self.assertRaises(ValueError):
            tile_count(-1, 100, 100)

if __name__ == "__main__":
    unittest.main()
