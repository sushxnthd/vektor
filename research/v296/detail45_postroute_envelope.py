#!/usr/bin/env python3
"""Fail-closed pre-CTS sensitivity from V296 matched detailed-route aggregate.

The single adjustable-skew envelope is optimistic, NOT a clock-tree result.
"""
import argparse
import json
import math
from pathlib import Path

VARIANTS = ("pairwise", "serial_onehot")
SCENARIOS = {
    "zero_guard": (0.0, 0.0, 0.0, 0.0),
    "setup_50ps_hold_0": (0.05, 0.0, 0.0, 0.0),
    "setup_50ps_hold_50ps": (0.05, 0.05, 0.0, 0.0),
    "setup_50ps_hold_50ps_penalty_20ps_each": (0.05, 0.05, 0.02, 0.02),
}


def envelope(setup, hold, setup_guard, hold_guard, setup_penalty, hold_penalty):
    vals = (setup, hold, setup_guard, hold_guard, setup_penalty, hold_penalty)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in vals):
        raise ValueError("All inputs must be finite numeric scalars")
    if min(setup_guard, hold_guard, setup_penalty, hold_penalty) < 0:
        raise ValueError("Negative guardband or penalty")
    # Setup'=setup+skew-setup_penalty; hold'=hold-skew-hold_penalty.
    lo = setup_guard + setup_penalty - setup
    hi = hold - hold_guard - hold_penalty
    return {
        "optimistic_common_skew_feasible": lo <= hi + 1e-12,
        "skew_min_ns": lo,
        "skew_max_ns": hi,
        "skew_window_ns": hi - lo,
        "combined_non_skew_penalty_budget_ns": setup + hold - setup_guard - hold_guard,
    }


def analyze(data):
    rows = data["rows"]
    if set(rows) != set(VARIANTS):
        raise ValueError("Missing or extra contestant")
    results = {}
    for name in VARIANTS:
        row = rows[name]
        if row.get("variant") != name or not row.get("complete"):
            raise ValueError("Incomplete or mismatched contestant")
        if "ideal-clock detailed-route OpenRCX" not in row.get("evidence_tier", ""):
            raise ValueError("Wrong evidence tier")
        final = row["final"]
        if any(final.get(x) != 0 for x in ("drc", "slew", "cap")):
            raise ValueError("DRC or electrical violations")
        area, setup, hold = (final[x] for x in ("area_um2", "setup_ns", "hold_ns"))
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
               for v in (area, setup, hold)) or area <= 0:
            raise ValueError("Invalid physical measurement")
        results[name] = {
            "area_um2": area, "setup_ns": setup, "hold_ns": hold,
            "scenarios": {n: envelope(setup, hold, *args) for n, args in SCENARIOS.items()},
        }
    p, c = results["pairwise"], results["serial_onehot"]
    saving = (c["area_um2"] - p["area_um2"]) / c["area_um2"]
    lead = p["setup_ns"] - c["setup_ns"]
    if data.get("decision") != "CONTROL_INFEASIBLE_NO_MATCHED_PARETO_CLAIM":
        raise ValueError("Unexpected independent-audit decision")
    if abs(data["comparison"]["area_saving_fraction"] - saving) > 1e-8 or abs(
            data["comparison"]["setup_lead_ns"] - lead) > 1e-8:
        raise ValueError("Inconsistent independent comparison")
    return {
        "source_run": 40083815972,
        "evidence_tier": "MEASURED_EXTRACTED_IDEAL_CLOCK_PLUS_ANALYTICAL_PRE_CTS_SENSITIVITY",
        "area_saving_fraction": saving, "extracted_setup_lead_ns": lead,
        "measurements": results,
        "interpretation": "Candidate passes fixed-clock detailed-route gate; control fails setup. No equal-consumed-area, CTS, power or GPU-throughput conclusion.",
        "model_limit": "Single freely adjustable effective skew per design and fixed data paths; real CTS has path-specific skew, altered parasitics and endpoint effects.",
        "workload_holdouts": "SEALED",
    }


def self_test():
    sample = {
        "decision": "CONTROL_INFEASIBLE_NO_MATCHED_PARETO_CLAIM",
        "comparison": {
            "area_saving_fraction": (6942.599828363427 - 5987.926154915613) / 6942.599828363427,
            "setup_lead_ns": 0.591949,
        },
        "rows": {
            name: {
                "variant": name, "complete": True,
                "evidence_tier": "ideal-clock detailed-route OpenRCX; not CTS/signoff",
                "final": {"area_um2": area, "setup_ns": setup, "hold_ns": hold,
                          "slew": 0, "cap": 0, "drc": 0},
            }
            for name, area, setup, hold in (
                ("pairwise", 5987.926154915613, 0.418903, 0.282110),
                ("serial_onehot", 6942.599828363427, -0.173046, 0.267903),
            )
        },
    }
    out = analyze(sample)
    assert abs(out["area_saving_fraction"] - 0.13750953490759654) < 1e-12
    assert abs(out["extracted_setup_lead_ns"] - 0.591949) < 1e-12
    p = out["measurements"]["pairwise"]["scenarios"]
    c = out["measurements"]["serial_onehot"]["scenarios"]
    assert abs(p["setup_50ps_hold_50ps"]["skew_window_ns"] - 0.601013) < 1e-12
    assert abs(c["setup_50ps_hold_0"]["skew_window_ns"] - 0.044857) < 1e-12
    assert c["setup_50ps_hold_0"]["optimistic_common_skew_feasible"]
    assert not c["setup_50ps_hold_50ps"]["optimistic_common_skew_feasible"]
    assert p["setup_50ps_hold_50ps_penalty_20ps_each"]["optimistic_common_skew_feasible"]
    for bad in (float("nan"), True, float("inf")):
        try:
            envelope(bad, 0.2, 0.05, 0, 0, 0)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid scalar accepted")
    sample["rows"]["pairwise"]["final"]["cap"] = 1
    try:
        analyze(sample)
    except ValueError:
        pass
    else:
        raise AssertionError("Electrical violation accepted")
    print("V296_DETAIL45_POSTROUTE_ENVELOPE_SELFTEST_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--aggregate", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.aggregate:
        print(json.dumps(analyze(json.loads(args.aggregate.read_text())), indent=2, sort_keys=True))
    else:
        parser.error("Specify --self-test or --aggregate PATH")
