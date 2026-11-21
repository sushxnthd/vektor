"""Independent, synthetic V317 prospective electrical-gate regression tests."""
import tempfile
import unittest
from pathlib import Path

from research.v317.rtl.audit_rf_legal_load import audit


class TestLegalLoadAudit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        for load, source, pair, source_slew, pair_slew in (
            (10, 1.23, .60, .16, .14),
            (24, 1.30, .74, .20, .21),
            (26, 1.31, .78, .21, .22),
            (30, 1.33, .85, .24, .25),
        ):
            self.write(load, "source_fixed", source, source_slew)
            self.write(load, "pairwise_fixed", pair, pair_slew)

    def write(self, load, label, arrival, slew):
        slack = round(.20 - slew, 3)
        state = "MET" if slack >= 0 else "VIOLATED"
        (self.path / f"{label}_{load}.log").write_text(
            "STA_PATH_BEGIN\nStartpoint: input\nEndpoint: grant\n"
            f"  {arrival:.3f} data arrival time\nSTA_PATH_END\n"
            "STA_ELECTRICAL_BEGIN\nmax_transition\nPin Limit Trans Slack\n"
            f"cell/ZN 0.20 {slew:.3f} {slack:.3f} ({state})\n"
            "STA_ELECTRICAL_END\n"
        )

    def test_both_frozen_predictions_survive(self):
        result = audit(self.path)
        self.assertTrue(result["both_predictions_survive"])
        self.assertEqual(result["frozen_win"]["observed_margin_ns"], .63)
        self.assertFalse(result["max_capacitance_verified"])
        self.assertEqual(result["grant_equivalent_intrinsic_service_gain"], 1.0)

    def test_falsifies_if_win_load_is_electrically_illegal(self):
        self.write(10, "pairwise_fixed", .60, .25)
        self.assertFalse(audit(self.path)["frozen_win"]["survives"])
        self.assertIsNone(audit(self.path)["conditional_10ff_cell_area_delay_ratio"])

    def test_falsifies_if_timing_margin_too_small(self):
        self.write(10, "pairwise_fixed", 1.10, .14)
        self.assertFalse(audit(self.path)["frozen_win"]["survives"])

    def test_falsifies_if_no_win_load_is_legal(self):
        self.write(30, "source_fixed", 1.33, .19)
        self.assertFalse(audit(self.path)["frozen_no_win"]["survives"])

    def test_fails_closed_if_report_missing(self):
        (self.path / "pairwise_fixed_24.log").unlink()
        with self.assertRaises(FileNotFoundError):
            audit(self.path)

    def test_fails_closed_if_electrical_table_missing(self):
        (self.path / "pairwise_fixed_24.log").write_text(
            "STA_PATH_BEGIN\nStartpoint: a\nEndpoint: b\n 0.5 data arrival time\nSTA_PATH_END\n")
        with self.assertRaises(AssertionError):
            audit(self.path)


if __name__ == "__main__":
    unittest.main()
