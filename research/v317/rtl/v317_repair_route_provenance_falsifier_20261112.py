#!/usr/bin/env python3
"""Fail-closed source-level falsifier for V317 repair-route provenance.

Not an electrical signoff tool. Successful ORFS routing before repair does not
establish that the repaired ODB was rerouted or extracted.
"""
import argparse
import json
from pathlib import Path


def audit(workflow, repair):
    w, t = workflow.lower(), repair.lower()
    script = "v317_matched_electrical_repair_candidate_20261110.tcl"
    read = t.find("read_db $::env(input_odb)")
    clock = t.find("all_clocks")
    checks = {
        "repair_script_referenced": script in w,
        "matched_compact_present": "compact" in w,
        "matched_pairwise_present": "pairwise" in w,
        "repair_writes_candidate_odb": "write_db" in t,
        "repair_reads_db_before_clock_guard": read >= 0 and clock >= 0 and read < clock,
    }
    return {
        "checks": checks,
        "source_level_prerequisites_met": all(checks.values()),
        "post_repair_detailed_route_verified": False,
        "post_repair_extracted_rc_verified": False,
        "post_repair_drc_verified": False,
        "physical_signoff_supported": False,
        "evidence_tier": "static_source_falsification",
        "reason": "Only independently checked post-repair artifacts can establish electrical legality.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("workflow", type=Path)
    p.add_argument("repair_tcl", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    result = audit(a.workflow.read_text(), a.repair_tcl.read_text())
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(output, end="")
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(output)
    if result["physical_signoff_supported"]:
        raise AssertionError("Static-source evidence cannot certify routed signoff")


if __name__ == "__main__":
    main()
