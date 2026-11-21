"""Unit checks for matched output-buffer generation and mapped-area accounting."""
import tempfile
import unittest
from pathlib import Path

from research.v317.rtl.rf_buffer_repair import (
    DRIVES, TOPS, liberty_areas, make_wrappers, mapped_area, wrapper,
)


class BufferRepairTests(unittest.TestCase):
    def test_matched_wrapper_port_and_drive(self):
        for label in TOPS:
            for drive in DRIVES[1:]:
                rtl = wrapper(label, drive)
                self.assertIn(f"{TOPS[label]} core", rtl)
                self.assertEqual(rtl.count(f"BUF_{drive.upper()} output_buf_"), 4)
                for i in range(4):
                    self.assertIn(f".A(raw_grant[{i}]), .Z(grant[{i}])", rtl)
                self.assertNotIn("assign grant =", rtl)

    def test_no_unbuffered_wrapper(self):
        with self.assertRaises(ValueError):
            wrapper("source_fixed", "none")

    def test_generator_is_deterministic(self):
        with tempfile.TemporaryDirectory() as root:
            d = Path(root)
            make_wrappers(d)
            self.assertEqual(len(list(d.glob("*.sv"))), 10)
            before = {p.name: p.read_bytes() for p in d.glob("*.sv")}
            make_wrappers(d)
            self.assertEqual(before, {p.name: p.read_bytes() for p in d.glob("*.sv")})

    def test_liberty_and_mapped_area(self):
        with tempfile.TemporaryDirectory() as root:
            d = Path(root)
            lib = d / "test.lib"
            lib.write_text("".join(
                f"cell ({cell}) {{ area : {area}; }}\n"
                for cell, area in [
                    ("BUF_X1", 1), ("BUF_X2", 2), ("BUF_X4", 4),
                    ("BUF_X8", 8), ("BUF_X16", 16),
                    ("NAND2_X1", 3), ("INV_X1", 1.5),
                ]
            ))
            areas = liberty_areas(lib)
            net = d / "mapped.v"
            net.write_text("""module foo(input a, output y);
NAND2_X1 _000_ (.A1(a), .A2(a), .ZN(y));
INV_X1 _001_ (.A(a), .ZN(y));
endmodule
""")
            area, count = mapped_area(net, areas)
            self.assertEqual((area, count), (4.5, 2))

    def test_unknown_cell_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "mapped.v"
            p.write_text("MISSING_X1 _00_ (.A(a), .Z(b));")
            with self.assertRaises(AssertionError):
                mapped_area(p, {"BUF_X1": 1.0})


if __name__ == "__main__":
    unittest.main()
