#!/usr/bin/env python3
"""Independent V296 mapped-STA falsification and RC-discrimination audit.

Usage: python3 physical_evidence_audit.py path/to/sta_summary.json
Reads only the public STA artifact; does not open workload holdouts.
"""
import json
import math
import pathlib
import re
import sys

AREA_UM2 = {"optimized": 3780.126, "pairwise": 3098.368}
PERIOD_NS = 2.0
VARIANTS = ("original", "optimized", "pairwise")
SCENARIOS = ("low", "nominal", "high")


def audit(path):
    evidence = json.loads(pathlib.Path(path).read_text())
    assert evidence["holdouts"] == "SEALED", "Workload holdouts must remain sealed"
    assert evidence["evidence_class"] == "preplacement_lumped_RC_STA_only_not_signoff"
    assert math.isclose(evidence["clock_period_ns"], PERIOD_NS)
    rows = evidence["raw"]
    results = {}
    for scenario in SCENARIOS:
        assert set(rows[scenario]) == set(VARIANTS)
        results[scenario] = {}
        for variant in VARIANTS:
            row = rows[scenario][variant]
            path_text = row["data_critical_paths"]
            assert "Path Group: coreclk" in path_text
            assert "Startpoint:" in path_text and "Endpoint:" in path_text
            assert "asynchronous" not in path_text.lower()
            slack = float(row["worst_setup_slack_ns"])
            assert math.isfinite(slack)
            assert int(row["max_slew_violations"]) >= 0
            assert int(row["max_capacitance_violations"]) >= 0
            results[scenario][variant] = {
                "path_budget_proxy_ns": PERIOD_NS - slack,
                "setup_slack_ns_at_2ns": slack,
                "slew_violations": row["max_slew_violations"],
                "cap_violations": row["max_capacitance_violations"],
                "path_startpoint": re.search(r"Startpoint:\s*([^\n]+)", path_text).group(1),
                "path_endpoint": re.search(r"Endpoint:\s*([^\n]+)", path_text).group(1),
            }
    nom = results["nominal"]
    area_delta = AREA_UM2["optimized"] - AREA_UM2["pairwise"]
    ratio = nom["optimized"]["path_budget_proxy_ns"] / nom["pairwise"]["path_budget_proxy_ns"]
    rc_delta = {}
    for variant in VARIANTS:
        low = results["low"][variant]["path_budget_proxy_ns"]
        high = results["high"][variant]["path_budget_proxy_ns"]
        rc_delta[variant] = {
            "low_to_high_path_proxy_change_ns": high - low,
            "relative_change_pct": 100 * (high - low) / results["nominal"][variant]["path_budget_proxy_ns"],
        }
    any_electrical_failure = any(
        results[s][v]["slew_violations"] or results[s][v]["cap_violations"]
        for s in SCENARIOS for v in VARIANTS
    )
    any_setup_failure = any(results[s][v]["setup_slack_ns_at_2ns"] < 0
                            for s in SCENARIOS for v in VARIANTS)
    weak_rc_discrimination = all(abs(rc_delta[v]["relative_change_pct"]) < 1
                                 for v in VARIANTS)
    return {
        "decision": "PHYSICAL_GATE_FAIL" if any_electrical_failure or any_setup_failure else "REQUIRES_POST_PLACE_VALIDATION",
        "mechanism": "V296 pairwise bank admission",
        "holdouts": "SEALED",
        "evidence": "mapped, pre-placement, lumped RC; not extracted wires or signoff",
        "nominal_path_budget_proxy_ratio_pairwise_vs_optimized": ratio,
        "ratio_is_validated_frequency_gain": False,
        "optimized_area_um2": AREA_UM2["optimized"],
        "pairwise_area_um2": AREA_UM2["pairwise"],
        "mapped_area_saving_um2": area_delta,
        "mapped_area_saving_pct": 100 * area_delta / AREA_UM2["optimized"],
        "net_extra_repair_area_budget_um2": area_delta,
        "electrical_failures_present": bool(any_electrical_failure),
        "two_ns_setup_failures_present": bool(any_setup_failure),
        "rc_sweep_changes_path_proxy_under_one_percent": weak_rc_discrimination,
        "rc_sensitivity": rc_delta,
        "cases": results,
        "falsifier": "Retire if equal-resource, electrically repaired and placed V296 has no positive timing/area benefit over repaired optimized control."
    }


if __name__ == "__main__":
    result = audit(sys.argv[1])
    print(json.dumps(result, indent=2))
    if result["decision"] == "PHYSICAL_GATE_FAIL":
        sys.exit(3)
