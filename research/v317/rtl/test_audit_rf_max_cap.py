"""Independent synthetic fixtures for V317 mapped max-capacitance auditor."""
import unittest

from research.v317.rtl.audit_rf_max_cap import audit_core, liberty_pins, parse_netlist

LIB = """
library (synthetic) {
  capacitive_load_unit (1,ff);
  cell (NAND2_X1) {
    pin (A) { direction : input; capacitance : 1.5; }
    pin (B) { direction : input; capacitance : 1.0; }
    pin (ZN) { direction : output; max_capacitance : 8.0; }
  }
  cell (BUF_X1) {
    pin (A) { direction : input; capacitance : 2.0; }
    pin (Z) { direction : output; max_capacitance : 60.6537; }
  }
  cell (BUF_X2) {
    pin (A) { direction : input; capacitance : 3.0; }
    pin (Z) { direction : output; max_capacitance : 121.155; }
  }
}
"""
NET = """
module example(req, req2, grant);
  input req;
  input req2;
  output [0:0] grant;
  wire _n_;
  NAND2_X1 _0_ (
    .A(req),
    .B(req2),
    .ZN(_n_)
  );
  assign grant = { _n_ };
endmodule
"""


class TestMaxCap(unittest.TestCase):
    def test_liberty_and_legal_output(self):
        lib = liberty_pins(LIB)
        result = audit_core(NET, lib, "BUF_X1", 24, grant_width=1)
        self.assertTrue(result["all_max_cap_legal"])
        self.assertEqual(result["mapped_instances"], 1)
        self.assertEqual(result["mapped_output_nets"], 1)
        self.assertAlmostEqual(result["worst_internal"][0]["margin_ff"], 6.0)

    def test_frozen_buffer_boundaries(self):
        lib = liberty_pins(LIB)
        self.assertTrue(audit_core(NET, lib, "BUF_X2", 100, 1)["all_max_cap_legal"])
        self.assertFalse(audit_core(NET, lib, "BUF_X1", 100, 1)["all_max_cap_legal"])

    def test_internal_overload_is_not_silently_passed(self):
        lib = liberty_pins(LIB)
        lib["NAND2_X1"]["ZN"]["max_cap_ff"] = 1.0
        result = audit_core(NET, lib, "BUF_X1", 24, 1)
        self.assertFalse(result["all_max_cap_legal"])
        self.assertEqual(len(result["internal_violations"]), 1)

    def test_missing_cell_fails_closed(self):
        lib = liberty_pins(LIB)
        with self.assertRaisesRegex(ValueError, "unknown mapped cell"):
            parse_netlist(NET.replace("NAND2_X1", "UNCHARACTERIZED"), lib)

    def test_missing_driver_fails_closed(self):
        lib = liberty_pins(LIB)
        with self.assertRaisesRegex(ValueError, "no mapped driver"):
            audit_core(NET.replace("assign grant = { _n_ };", "assign grant = { undriven };"),
                       lib, "BUF_X1", 24, 1)

    def test_bad_cap_unit_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unit"):
            liberty_pins(LIB.replace("(1,ff)", "(1,pf)"))

    def test_assign_width_mismatch_fails_closed(self):
        lib = liberty_pins(LIB)
        with self.assertRaisesRegex(ValueError, "assign width mismatch"):
            parse_netlist(NET.replace("{ _n_ }", "{ _n_, _n_ }"), lib)


if __name__ == "__main__":
    unittest.main()
