"""Independent adversarial checks: lexical tokens are not physical RF reads."""
from __future__ import annotations

import unittest

from research.v317.demand_identifiability import gate


class DemandIdentifiabilityTests(unittest.TestCase):
    def test_scalar_coverage_still_cannot_certify_rf(self):
        x = gate("/*0000*/ IADD3 R0, R1, R2, R3;")
        self.assertTrue(x["all_instruction_lexical_coverage"])
        self.assertEqual(x["classified_lexical_source_occurrences"], 3)
        self.assertIsNone(x["physical_rf_reads_lower_bound"])
        self.assertIsNone(x["physical_rf_reads_upper_bound"])
        self.assertFalse(x["eligible_for_physical_performance_claim"])

    def test_wide_store_has_implicit_width_hazard(self):
        x = gate("/*0000*/ STG.E.128 [R2], R4;")
        self.assertEqual(x["classified_lexical_source_occurrences"], 2)
        self.assertEqual(x["wide_store_instances"], 1)
        self.assertFalse(x["semantic_register_width_unambiguous"])
        self.assertTrue(any(h["kind"] == "wide_store_base_register" for h in x["hazards"]))

    def test_double_precision_source_width(self):
        x = gate("/*0000*/ DFMA R0, R2, R4, R6;")
        self.assertEqual(x["double_precision_instances"], 1)
        self.assertFalse(x["semantic_register_width_unambiguous"])

    def test_unknown_opcode_taints_coverage(self):
        x = gate("/*0000*/ MOV R0, R1;\n/*0010*/ ATOM.E.ADD R0, [R2], R3;")
        self.assertFalse(x["all_instruction_lexical_coverage"])
        self.assertEqual(x["classified_lexical_source_occurrences"], 1)
        self.assertTrue(any(h["kind"] == "unknown_instruction_semantics" for h in x["hazards"]))

    def test_malformed_instruction_taints_coverage(self):
        x = gate("/*0000*/ MOV R0, R1;\n/*0010*/ FFMA R1, [R2, R3;")
        self.assertFalse(x["all_instruction_lexical_coverage"])
        self.assertTrue(any(h["kind"] == "unparsed_instruction_candidates" for h in x["hazards"]))

    def test_predication_does_not_become_dynamic_read(self):
        x = gate("/*0000*/ @P0 FFMA R1, R2, R3, R4;")
        self.assertTrue(any(h["kind"] == "dynamic_predicate_execution_unknown" for h in x["hazards"]))
        self.assertIsNone(x["predicted_gpu_throughput"])

    def test_reuse_hint_not_physical_hit(self):
        x = gate("/*0000*/ FFMA R1, R2.reuse, R3, R4;")
        self.assertTrue(any(h["kind"] == "reuse_hint_is_not_cache_hit" for h in x["hazards"]))
        self.assertIsNone(x["physical_bank_conflicts"])

    def test_metadata_flags_cannot_override_physical_uncertainty(self):
        x = gate("/*0000*/ MOV R0, R1;", binary_verified=True,
                 disassembler_verified=True, target_verified=True)
        self.assertFalse(any(h["kind"] == "unverified_provenance" for h in x["hazards"]))
        self.assertFalse(x["eligible_for_physical_performance_claim"])

    def test_empty_input_is_not_complete_coverage(self):
        x = gate("// header only")
        self.assertFalse(x["all_instruction_lexical_coverage"])
        self.assertEqual(x["classified_lexical_source_occurrences"], 0)
        self.assertIsNone(x["physical_rf_reads_lower_bound"])


if __name__ == "__main__":
    unittest.main()
