#!/usr/bin/env python3
"""V317 fail-closed evidence gate: never turn lexical SASS counts into RF traffic.

The companion sass_audit.py counts explicitly written source register tokens.
This gate identifies cases where even complete lexical coverage cannot identify
physical read demand. It deliberately produces no throughput or bank estimates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from research.v317.sass_audit import audit, parse_instruction

# Conservative flags, not claims about exact SASS ISA encoding.
# A widened store may read a register tuple despite one printed base register.
WIDE_STORE = re.compile(r"\.(?:64|128)(?:\.|$)", re.IGNORECASE)
DOUBLE_SOURCE = frozenset({"DADD", "DMUL", "DFMA"})
STORE_ROOT = frozenset({"STG", "STS", "STL", "ST"})


def gate(disassembly: str, *, binary_verified: bool = False,
         disassembler_verified: bool = False,
         target_verified: bool = False) -> dict:
    """Return explicit evidence tiers and semantic hazards.

    binary_verified must be set only by an external independent binary-hash
    check; this function cannot verify it. Passing it never authorizes a
    physical RF-read estimate.
    """
    lexical = audit(disassembly)
    c = lexical["counts"]
    hazards: list[dict] = []
    widened = 0
    double = 0
    for line_no, line in enumerate(disassembly.splitlines(), 1):
        try:
            inst = parse_instruction(line)
        except ValueError:
            continue
        if inst is None or inst.classification == "unknown":
            continue
        root = inst.opcode.split(".")[0]
        if root in STORE_ROOT and WIDE_STORE.search(inst.opcode):
            widened += 1
            hazards.append({"line": line_no, "kind": "wide_store_base_register",
                            "opcode": inst.opcode})
        if root in DOUBLE_SOURCE:
            double += 1
            hazards.append({"line": line_no, "kind": "double_precision_source_width",
                            "opcode": inst.opcode})
    if c["unknown_semantics"]:
        hazards.append({"kind": "unknown_instruction_semantics",
                        "count": c["unknown_semantics"]})
    if c["unparsed_candidate"]:
        hazards.append({"kind": "unparsed_instruction_candidates",
                        "count": c["unparsed_candidate"]})
    if c["predicated"]:
        hazards.append({"kind": "dynamic_predicate_execution_unknown",
                        "count": c["predicated"]})
    if lexical["reuse_hints_total"]:
        hazards.append({"kind": "reuse_hint_is_not_cache_hit",
                        "count": lexical["reuse_hints_total"]})
    missing = [name for name, verified in (
        ("binary", binary_verified),
        ("disassembler", disassembler_verified),
        ("target", target_verified),
    ) if not verified]
    if missing:
        hazards.append({"kind": "unverified_provenance", "fields": missing})

    complete_lexical = (c["instructions"] > 0 and
                        c["unknown_semantics"] == 0 and
                        c["unparsed_candidate"] == 0)
    # Lower bound on *written tokens in the disassembly*, not on RF reads.
    # Dynamic predicates, cache, compiler lowering and vector register
    # expansion make a physical-read lower bound from these counts unsound.
    return {
        "schema": "vektor.v317.sass_demand_identifiability.v1",
        "classified_lexical_source_occurrences": lexical["source_occurrences_total"],
        "all_instruction_lexical_coverage": complete_lexical,
        "wide_store_instances": widened,
        "double_precision_instances": double,
        "semantic_register_width_unambiguous": widened == 0 and double == 0,
        "hazards": hazards,
        "physical_rf_reads_lower_bound": None,
        "physical_rf_reads_upper_bound": None,
        "physical_bank_conflicts": None,
        "predicted_gpu_throughput": None,
        "eligible_for_physical_performance_claim": False,
        "evidence_tier": "static_lexical_only",
        "note": "No physical RF demand or speedup is identifiable from lexical SASS alone.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(gate(args.input.read_text()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
