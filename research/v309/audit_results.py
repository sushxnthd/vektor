#!/usr/bin/env python3
"""Independent V309 evidence arithmetic and provenance audit (no parser imports)."""
import copy
import json
import math
import sys

EXPECTED = {
    "atomic_reduction": {
        "blob": "17873acef2f5137137ca0c4967bd696b97e31c01",
        "instructions": 23,
        "occurrences": 21,
        "unique": 21,
        "duplicates": 0,
    },
    "triton_gelu": {
        "blob": "09d8fce9016b6fe0e36e31ac3a47fc9feddee206",
        "instructions": 134,
        "occurrences": 181,
        "unique": 173,
        "duplicates": 8,
    },
}


def audit(data):
    if data.get("tier") != "static_PTX_only_no_SASS_or_runtime":
        raise ValueError("evidence tier changed")
    if set(data.get("sources", {})) != set(EXPECTED):
        raise ValueError("source set changed")
    for name, expected in EXPECTED.items():
        record = data["sources"][name]
        m = record["metrics"]
        if record["git_blob"] != expected["blob"]:
            raise ValueError(f"{name}: upstream provenance drift")
        for key, field in [("instructions", "instructions"),
                           ("data_source_occurrences", "occurrences"),
                           ("unique_data_sources_per_instruction", "unique"),
                           ("intra_instruction_duplicate_reads", "duplicates")]:
            if m[key] != expected[field]:
                raise ValueError(f"{name}: {key} changed")
        if m["data_source_occurrences"] != (m["unique_data_sources_per_instruction"]
                                            + m["intra_instruction_duplicate_reads"]):
            raise ValueError(f"{name}: read conservation broken")
        if sum(m["opcode_counts"].values()) != m["instructions"]:
            raise ValueError(f"{name}: opcode conservation broken")
        if not (0 <= m["zero_data_source_instructions"] <= m["instructions"]):
            raise ValueError(f"{name}: invalid zero-read count")
        if not (0 <= m["predicated_instructions"] <= m["instructions"]):
            raise ValueError(f"{name}: invalid predicated count")
        if not (0 <= m["memory_instructions"] <= m["instructions"]):
            raise ValueError(f"{name}: invalid memory count")
        for b in (2, 4, 8):
            key = f"{b}banks_1port"
            if m["optimistic_rf_service_lower_bound_cycles"][key] != math.ceil(
                m["unique_data_sources_per_instruction"] / b
            ):
                raise ValueError(f"{name}: service bound inconsistent")
        ratio = m["intra_instruction_duplicate_reads"] / max(
            1, m["data_source_occurrences"]
        )
        if abs(m["duplicate_read_fraction_of_occurrences"] - ratio) > 0.00000051:
            raise ValueError(f"{name}: duplicate fraction inconsistent")
    return True


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python audit_results.py result.json")
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    audit(data)
    # Adversarial mutations must be detected, independently of the parser.
    mutations = []
    for field in ("intra_instruction_duplicate_reads", "unique_data_sources_per_instruction"):
        bad = copy.deepcopy(data)
        bad["sources"]["triton_gelu"]["metrics"][field] += 1
        mutations.append(bad)
    bad = copy.deepcopy(data)
    bad["sources"]["atomic_reduction"]["git_blob"] = "0" * 40
    mutations.append(bad)
    bad = copy.deepcopy(data)
    bad["sources"]["triton_gelu"]["metrics"]["optimistic_rf_service_lower_bound_cycles"]["2banks_1port"] += 1
    mutations.append(bad)
    for mutant in mutations:
        try:
            audit(mutant)
        except ValueError:
            continue
        raise AssertionError("independent checker failed to detect mutant")
    print(json.dumps({"independent_audit": "PASS", "mutants_detected": len(mutations),
                      "source_count": len(EXPECTED)}, sort_keys=True))


if __name__ == "__main__":
    main()
