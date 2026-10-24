#!/usr/bin/env python3
"""Independent two-point *observed* output-load sensitivity for V296.

The derivative is a secant across two completed matched post-CTS runs,
NOT an extrapolation, process-corner estimate, or GPU frequency measurement.
"""
import argparse
import json
import math
from pathlib import Path

REQUIRED = ("area_um2", "setup_ps", "hold_ps", "slew_violations",
            "cap_violations", "drc_violations")


def compare(rows):
    if len(rows) != 2:
        raise ValueError("exactly two observed load points required")
    a, b = sorted(rows, key=lambda x: x["output_load_ff"])
    if a["output_load_ff"] == b["output_load_ff"]:
        raise ValueError("load points must differ")
    for row in (a, b):
        if row.get("evidence_tier") != "post_CTS_extracted_Nangate45_not_signoff":
            raise ValueError("evidence tier missing or mismatched")
        if row.get("matched_policy") != "cts45_fanout16_setup250_2xRC_density45":
            raise ValueError("physical policy mismatch")
        for design in ("pairwise", "serial_onehot"):
            metrics = row.get(design)
            if not isinstance(metrics, dict):
                raise ValueError("missing contestant")
            for key in REQUIRED:
                value = metrics.get(key)
                if not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise ValueError("missing or nonfinite measurement: " + key)
            if not (0 < metrics["area_um2"] <= 7400 and metrics["setup_ps"] >= 50
                    and metrics["hold_ps"] >= 0 and all(metrics[k] == 0 for k in
                    ("slew_violations", "cap_violations", "drc_violations"))):
                raise ValueError("infeasible contestant: " + design)
    delta_ff = b["output_load_ff"] - a["output_load_ff"]
    def metrics(row):
        p, c = row["pairwise"], row["serial_onehot"]
        return {"candidate_area_saving_fraction": 1 - p["area_um2"] / c["area_um2"],
                "setup_lead_ps": p["setup_ps"] - c["setup_ps"],
                "candidate_setup_ps": p["setup_ps"],
                "control_setup_ps": c["setup_ps"]}
    m0, m1 = metrics(a), metrics(b)
    return {
        "observed_load_interval_ff": [a["output_load_ff"], b["output_load_ff"]],
        "paired_results": {str(a["output_load_ff"]): m0, str(b["output_load_ff"]): m1},
        "secant_ps_per_ff": {
            "candidate_setup": (m1["candidate_setup_ps"] - m0["candidate_setup_ps"]) / delta_ff,
            "control_setup": (m1["control_setup_ps"] - m0["control_setup_ps"]) / delta_ff,
            "candidate_relative_setup_lead": (m1["setup_lead_ps"] - m0["setup_lead_ps"]) / delta_ff,
        },
        "area_saving_change_percentage_points": 100 * (m1["candidate_area_saving_fraction"] - m0["candidate_area_saving_fraction"]),
        "load10_feasible_pareto_supported": m1["candidate_area_saving_fraction"] >= .10 and m1["setup_lead_ps"] >= 200,
        "validity": "Two measured points only. No interpolation/extrapolation accuracy guarantee.",
        "tile_throughput": "UNMEASURED; unchanged clock and resource admission gain = 0",
        "independent_artifact_byte_redownload": False,
    }


def self_test():
    def row(load, p_slack, c_slack):
        return {"output_load_ff": load,
                "evidence_tier": "post_CTS_extracted_Nangate45_not_signoff",
                "matched_policy": "cts45_fanout16_setup250_2xRC_density45",
                "pairwise": dict(area_um2=6200, setup_ps=p_slack, hold_ps=100,
                                 slew_violations=0, cap_violations=0, drc_violations=0),
                "serial_onehot": dict(area_um2=7300, setup_ps=c_slack, hold_ps=100,
                                      slew_violations=0, cap_violations=0, drc_violations=0)}
    x, y = row(5, 430, 105), row(10, 420, 100)
    result = compare([y, x])
    assert result["secant_ps_per_ff"]["candidate_setup"] == -2
    assert result["secant_ps_per_ff"]["control_setup"] == -1
    assert result["load10_feasible_pareto_supported"]
    for bad in ([x, x], [x], [x, {**y, "matched_policy": "changed"}],
                [x, {**y, "pairwise": {**y["pairwise"], "slew_violations": 1}}],
                [x, {**y, "serial_onehot": {**y["serial_onehot"], "setup_ps": float("nan")}}]):
        try:
            compare(bad)
        except ValueError:
            continue
        raise AssertionError("adversarial input accepted")
    print("V296_LOAD_PAIR_SENSITIVITY_SELFTEST_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--observations", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.observations:
        print(json.dumps(compare(json.loads(args.observations.read_text())["observations"]), indent=2))
    else:
        parser.error("choose --self-test or --observations FILE")
