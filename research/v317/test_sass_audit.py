"""Independent behavioral checks for V317 lexical SASS audit. Synthetic syntax only."""
from __future__ import annotations
import json
from pathlib import Path
import unittest
from research.v317.sass_audit import audit, parse_instruction, split_operands

HERE = Path(__file__).parent


class SassAuditTests(unittest.TestCase):
    def test_split_bracketed_address(self):
        self.assertEqual(split_operands("R1, [R2+0x4], {R3,R4}"),
                         ("R1", "[R2+0x4]", "{R3,R4}"))
        with self.assertRaises(ValueError):
            split_operands("R1, [R2, R3")

    def test_alu_destination_excluded_and_duplicates_preserved(self):
        x = audit("/*0000*/ FFMA R1, R2, R2, R3; /* encoding */")
        self.assertEqual(x["source_register_occurrences"], {"R2": 2, "R3": 1})
        self.assertEqual(x["source_occurrences_total"], 3)
        self.assertEqual(x["counts"]["classified"], 1)

    def test_store_address_and_load_destination(self):
        x = audit("/*0000*/ STG.E [R2+0x4], R1;\n"
                  "/*0010*/ LDG.E R3, [R2];")
        self.assertEqual(x["source_register_occurrences"], {"R1": 1, "R2": 2})
        self.assertEqual(x["counts"]["classified"], 2)

    def test_reuse_is_hint_not_physical_cache_hit(self):
        x = audit("/*0000*/ FFMA R1, R2.reuse, R3, RZ;")
        self.assertEqual(x["source_register_occurrences"], {"R2": 1, "R3": 1})
        self.assertEqual(x["reuse_hint_occurrences"], {"R2": 1})
        self.assertFalse(x["reuse_hint_is_cache_hit"])
        self.assertFalse(x["physical_bank_map_known"])

    def test_predication_is_counted_not_rf_read(self):
        x = audit("/*0010*/ @!P0 FADD R0, R1, R2;")
        self.assertEqual(x["counts"]["predicated"], 1)
        self.assertEqual(x["source_occurrences_total"], 2)

    def test_unknown_is_not_zero_demand(self):
        x = audit("/*0000*/ ATOM.E.ADD R0, [R1], R2;\n"
                  "/*0010*/ BRA label;\n/*0020*/ NOP;")
        self.assertEqual(x["counts"]["unknown_semantics"], 3)
        self.assertEqual(x["counts"]["classified"], 0)
        self.assertEqual(x["source_occurrences_total"], 0)
        self.assertEqual(x["coverage_fraction"], 0.0)
        self.assertEqual(len(x["unknown_opcodes"]), 3)

    def test_malformed_and_missing_pc_not_silently_accepted(self):
        x = audit("/*0000*/ FFMA R1, [R2, R3;\nMOV R0, R1;\n"
                  "/*0020*/ MOV R0, R1\n")
        self.assertEqual(x["counts"]["unparsed_candidate"], 3)
        self.assertEqual(x["counts"]["instructions"], 0)

    def test_fixture_and_determinism(self):
        data = (HERE / "synthetic_sass_fixture.sass").read_text()
        x = audit(data)
        self.assertEqual(x, audit(data))
        self.assertEqual(json.dumps(x, sort_keys=True), json.dumps(audit(data), sort_keys=True))
        self.assertEqual(x["counts"]["instructions"], 6)
        self.assertEqual(x["counts"]["classified"], 5)
        self.assertEqual(x["counts"]["unknown_semantics"], 1)
        self.assertEqual(x["counts"]["predicated"], 1)
        self.assertEqual(x["reuse_hint_occurrences"], {"R1": 1})
        self.assertEqual(x["source_register_occurrences"],
                         {"R1": 1, "R2": 1, "R3": 1, "R4": 3, "R8": 2})
        self.assertEqual(x["source_occurrences_total"], 8)
        self.assertEqual(x["coverage_fraction"], 5 / 6)

    def test_no_instructions_is_missing_not_perfect_coverage(self):
        x = audit("// header only")
        self.assertIsNone(x["coverage_fraction"])
        self.assertEqual(x["counts"]["instructions"], 0)


if __name__ == "__main__":
    unittest.main()
