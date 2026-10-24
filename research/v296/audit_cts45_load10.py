#!/usr/bin/env python3
"""Fail-closed, independently routed V296 10 fF output-load stress audit.

Reuses the already-adversarial setup250 physical checks and adds a strict
stage-ordered 10 fF intervention gate. Does not infer GPU frequency.
"""
import json
import sys
from pathlib import Path
import audit_cts45_setup250 as base

VARIANTS = ("pairwise", "serial_onehot")
LOAD_MARKER = "V296_CTS45_OUTPUT_LOAD_PF 0.010"
STAGE_MARKER = "V296_CTS45_OUTPUT_LOAD_STAGE POST_THIRD_PRECTS"

def require_load_policy(log):
    lines = log.splitlines()
    for marker in (LOAD_MARKER, STAGE_MARKER,
                   "V296_THIRD_PHYSICAL_DONE", "V296_CTS45_CTS_BEGIN",
                   "V296_CTS45_DETAIL_BEGIN"):
        if lines.count(marker) != 1:
            raise ValueError("missing or duplicate output-load provenance: " + marker)
    if any(line.startswith("V296_CTS45_OUTPUT_LOAD_PF ") and line != LOAD_MARKER
           for line in lines):
        raise ValueError("ambiguous output load")
    if not (lines.index("V296_THIRD_PHYSICAL_DONE") < lines.index(LOAD_MARKER)
            < lines.index(STAGE_MARKER) < lines.index("V296_CTS45_CTS_BEGIN")
            < lines.index("V296_CTS45_DETAIL_BEGIN")):
        raise ValueError("output-load intervention outside preregistered window")

def case(root, variant):
    row = base.case(root, variant)
    if not row.get("complete"):
        return row
    require_load_policy((root / (variant + ".high.log")).read_text(errors="replace"))
    row["output_load_pf"] = 0.010
    row["output_load_stage"] = "post-third-pre-CTS"
    return row

def aggregate(root):
    rows = {}
    for variant in VARIANTS:
        try:
            rows[variant] = case(root, variant)
        except (ValueError, OSError, IndexError, KeyError) as exc:
            rows[variant] = {"variant": variant, "complete": False, "error": str(exc)}
    p, c = (rows[v] for v in VARIANTS)
    comparison = None
    decision = "INCOMPLETE_NO_LOAD_STRESS_CLAIM"
    if p.get("complete") and c.get("complete"):
        pv, cv = p["final"], c["final"]
        saving = 1 - pv["area_um2"] / cv["area_um2"]
        lead = pv["setup_ns"] - cv["setup_ns"]
        comparison = {
            "candidate_area_saving_fraction": saving,
            "candidate_extracted_setup_lead_ns": lead,
            "candidate_feasible": p["feasible"],
            "control_feasible": c["feasible"],
            "strict_equal_consumed_area": False,
        }
        if not p["feasible"]:
            decision = "CANDIDATE_LOAD_STRESS_FAIL"
        elif not c["feasible"]:
            decision = "CONTROL_LOAD_STRESS_FAIL_NO_PARETO_CLAIM"
        elif saving + 1e-12 < 0.10 or lead + 1e-12 < 0.200:
            decision = "LOAD_STRESS_PARETO_FALSIFIED"
        else:
            decision = "LOAD_STRESS_FEASIBLE_PARETO_SUPPORTED"
    return {
        "decision": decision, "rows": rows, "comparison": comparison,
        "output_load_pf": 0.010, "baseline_output_load_pf": 0.005,
        "evidence_tier": "post_CTS_extracted_Nangate45_load_stress_not_signoff",
        "workload_holdouts": "SEALED", "tile_performance": "NOT_EVALUATED",
        "strict_equal_consumed_area": False,
    }

def self_test():
    base.self_test()
    sample = ("V296_THIRD_PHYSICAL_DONE\n" + LOAD_MARKER + "\n"
              + STAGE_MARKER + "\nV296_CTS45_CTS_BEGIN\n"
              + "V296_CTS45_DETAIL_BEGIN\n")
    require_load_policy(sample)
    adversaries = [
        sample.replace(LOAD_MARKER, "V296_CTS45_OUTPUT_LOAD_PF 0.005"),
        sample.replace(LOAD_MARKER, LOAD_MARKER + "\n" + LOAD_MARKER),
        sample.replace(STAGE_MARKER, ""),
        sample.replace("V296_THIRD_PHYSICAL_DONE\n", ""),
        sample.replace("V296_CTS45_CTS_BEGIN\n", ""),
        sample.replace("V296_CTS45_DETAIL_BEGIN\n", ""),
        sample.replace("V296_THIRD_PHYSICAL_DONE\n" + LOAD_MARKER,
                       LOAD_MARKER + "\nV296_THIRD_PHYSICAL_DONE"),
    ]
    for bad in adversaries:
        try:
            require_load_policy(bad)
        except ValueError:
            continue
        raise AssertionError("load-provenance adversary accepted")
    print("V296_CTS45_LOAD10_INDEPENDENT_SELFTEST_PASS")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 4 and sys.argv[1] == "--single":
        root, variant = Path(sys.argv[2]), sys.argv[3]
        if variant not in VARIANTS:
            raise SystemExit("invalid variant")
        try:
            row = case(root, variant)
        except (ValueError, OSError, IndexError, KeyError) as exc:
            row = {"variant": variant, "complete": False, "error": str(exc)}
        (root / (variant + ".load10.audit.json")).write_text(json.dumps(row, indent=2) + "\n")
        print(json.dumps(row, indent=2))
        if not row.get("complete"):
            raise SystemExit(3)
    elif len(sys.argv) == 3 and sys.argv[1] == "--aggregate":
        root = Path(sys.argv[2])
        result = aggregate(root)
        (root / "aggregate.load10.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if result["decision"] != "LOAD_STRESS_FEASIBLE_PARETO_SUPPORTED":
            raise SystemExit(3)
    else:
        raise SystemExit("Usage: --self-test | --single ROOT VARIANT | --aggregate ROOT")
