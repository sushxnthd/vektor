#!/usr/bin/env python3
"""Independent two-geometry physical envelope and conditional tile-boundary law.

Input values transcribed from GitHub Actions 40134996756 aggregate logs.
The period conversion is a FIXED-CONSTRAINT PROXY, not measured Fmax.
Do not treat this as equal-consumed-area or measured GPU performance.
"""
import argparse
import json
import math

CLOCK_NS = 3.5
SOURCE_RUN = 40134996756
CASES = {
    "top": {
        "pairwise": {"area_um2": 6240.094219123193, "setup_ns": 0.398363,
                     "hold_ns": 0.252838, "slew": 0, "cap": 0},
        "serial_onehot": {"area_um2": 7315.532180030004, "setup_ns": 0.072303,
                          "hold_ns": 0.250092, "slew": 0, "cap": 0},
    },
    "bottom": {
        "pairwise": {"area_um2": 6239.828209686493, "setup_ns": 0.430410,
                     "hold_ns": 0.284848, "slew": 0, "cap": 0},
        "serial_onehot": {"area_um2": 7284.9419829879025, "setup_ns": 0.104791,
                          "hold_ns": 0.249547, "slew": 0, "cap": 0},
    },
}

def check_positive(x, name):
    if not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x) or x <= 0:
        raise ValueError(name + " must be finite and positive")
    return float(x)

def physical_case(edge):
    if edge not in CASES:
        raise ValueError("unregistered geometry")
    a, b = CASES[edge]["pairwise"], CASES[edge]["serial_onehot"]
    for row in (a, b):
        check_positive(row["area_um2"], "area")
        if row["setup_ns"] < 0.05 or row["hold_ns"] < 0 or row["slew"] or row["cap"]:
            raise ValueError("physical feasibility gate failed")
    area_saving = 1.0 - a["area_um2"] / b["area_um2"]
    setup_lead = a["setup_ns"] - b["setup_ns"]
    if area_saving < 0.10 or setup_lead < 0.20:
        raise ValueError("preregistered Pareto gate failed")
    pa = check_positive(CLOCK_NS - a["setup_ns"], "pairwise period proxy")
    pb = check_positive(CLOCK_NS - b["setup_ns"], "control period proxy")
    return {"area_saving_fraction": area_saving, "setup_lead_ns": setup_lead,
            "area_margin_to_10pct_um2": 0.90 * b["area_um2"] - a["area_um2"],
            "pairwise_path_period_proxy_ns": pa, "control_path_period_proxy_ns": pb,
            "controller_only_optimistic_gain": pb / pa - 1.0}

def conditional_tile_gain(edge, other_tile_period_ns, bandwidth_cap_ops_per_ns,
                          ipc=1.0, overhead=0.0):
    """Same IPC/occupancy and no additional overhead; no measured tile claim.

    This upper-bound illustration uses setup-slack-derived period proxies.
    A real integration must re-time the tile and measure traffic, IPC and power.
    """
    other = check_positive(other_tile_period_ns, "other tile period")
    bw = check_positive(bandwidth_cap_ops_per_ns, "bandwidth cap")
    ipc = check_positive(ipc, "IPC")
    if not isinstance(overhead, (int, float)) or not math.isfinite(overhead) or overhead < 0:
        raise ValueError("invalid overhead")
    c = physical_case(edge)
    a = min(ipc / ((1.0 + overhead) * max(other, c["pairwise_path_period_proxy_ns"])), bw)
    b = min(ipc / ((1.0 + overhead) * max(other, c["control_path_period_proxy_ns"])), bw)
    return a / b - 1.0

def self_test():
    for edge in ("top", "bottom"):
        c = physical_case(edge)
        assert c["area_saving_fraction"] > 0.14
        assert c["setup_lead_ns"] > 0.325
        assert conditional_tile_gain(edge, 3.0, 0.5) > 0.10
        assert abs(conditional_tile_gain(edge, 3.5, 0.5)) < 1e-12
        assert abs(conditional_tile_gain(edge, 3.0, 0.1)) < 1e-12
        assert conditional_tile_gain(edge, 3.0, 0.5, overhead=0.2) > 0.10
    for edge in ("left", "", None):
        try: physical_case(edge)
        except ValueError: pass
        else: raise AssertionError("unknown geometry accepted")
    for bad in (0, -1, float("nan"), float("inf")):
        try: conditional_tile_gain("top", bad, 0.5)
        except ValueError: pass
        else: raise AssertionError("invalid period accepted")
    print("V296_PIN_PHYSICAL_BOUNDARY_SELFTEST_PASS")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test: self_test()
    out = {
        "source_run": SOURCE_RUN, "physical_evidence": "post-CTS extracted; not signoff",
        "strict_equal_consumed_area": False, "measured_tile_fmax": False,
        "measured_tile_ipc": False, "holdouts": "SEALED",
        "geometries": {edge: physical_case(edge) for edge in CASES},
        "conditional_predictions_not_workload_results": {
            "predicted_win_proxy": {"other_tile_period_ns": 3.0,
                                    "bandwidth_cap_ops_per_ns": 0.5,
                                    "gains": {e: conditional_tile_gain(e, 3.0, 0.5) for e in CASES}},
            "predicted_no_win_other_path": {"other_tile_period_ns": 3.5,
                                            "bandwidth_cap_ops_per_ns": 0.5,
                                            "gains": {e: conditional_tile_gain(e, 3.5, 0.5) for e in CASES}},
            "predicted_no_win_bandwidth": {"other_tile_period_ns": 3.0,
                                           "bandwidth_cap_ops_per_ns": 0.1,
                                           "gains": {e: conditional_tile_gain(e, 3.0, 0.1) for e in CASES}},
        },
    }
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
