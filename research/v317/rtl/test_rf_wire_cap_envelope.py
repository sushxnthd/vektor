"""Independent edge-case tests for the V317 wire-capacitance boundary."""
import math
import unittest

from research.v317.rtl.rf_wire_cap_envelope import apply_uniform_wire, verify_frozen


class WireCapEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"net": "n0", "cell": "NOR4_X1", "instance": "u0",
             "load_ff": 9.5, "max_cap_ff": 10.0},
            {"net": "n1", "cell": "NAND2_X1", "instance": "u1",
             "load_ff": 2.0, "max_cap_ff": 10.0},
        ]

    def test_exact_boundary_is_legal(self):
        self.assertTrue(apply_uniform_wire(self.rows, 0.5)["all_mapped_internal_max_cap_legal"])
        self.assertEqual(apply_uniform_wire(self.rows, 0.5)["violations"], 0)

    def test_one_net_fails_just_past_boundary(self):
        r = apply_uniform_wire(self.rows, 0.50001)
        self.assertEqual(r["violations"], 1)
        self.assertEqual(r["worst_violations"][0]["net"], "n0")

    def test_both_nets_fail_at_high_load(self):
        self.assertEqual(apply_uniform_wire(self.rows, 9)["violations"], 2)

    def test_negative_wire_is_rejected(self):
        with self.assertRaises(ValueError):
            apply_uniform_wire(self.rows, -0.01)

    def test_nonfinite_wire_is_rejected(self):
        for x in (math.inf, -math.inf, math.nan):
            with self.subTest(x=x), self.assertRaises(ValueError):
                apply_uniform_wire(self.rows, x)

    def test_empty_netlist_is_rejected(self):
        with self.assertRaises(ValueError):
            apply_uniform_wire([], 0)

    def test_nonfinite_liberty_margin_is_rejected(self):
        rows = [dict(self.rows[0], max_cap_ff=math.nan)]
        with self.assertRaises(ValueError):
            apply_uniform_wire(rows, 0)

    def test_stable_worst_order(self):
        rows = [dict(self.rows[0], net="z"), dict(self.rows[0], net="a")]
        r = apply_uniform_wire(rows, 1)
        self.assertEqual([x["net"] for x in r["worst_violations"]], ["a", "z"])

    def test_no_false_legal_at_exact_equality(self):
        self.assertTrue(apply_uniform_wire(self.rows, 0.5)["all_mapped_internal_max_cap_legal"])


if __name__ == "__main__":
    unittest.main()
