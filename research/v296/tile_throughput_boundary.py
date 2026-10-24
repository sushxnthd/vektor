#!/usr/bin/env python3
"""V296 necessary tile-level throughput boundary, NOT a measured speedup.

V296 and serial one-hot have equivalent arbitration semantics. At fixed tile
clock and resource configuration, their admission counts are equal. Any
throughput advantage therefore requires a measured clock or resource change.
"""
import argparse
import json
import math


def boundary(control_path_ns, candidate_path_ns, other_tile_path_ns,
             accepted_ops_per_cycle, bytes_per_op, sustained_bandwidth_gbs):
    values = (control_path_ns, candidate_path_ns, other_tile_path_ns,
              accepted_ops_per_cycle, bytes_per_op, sustained_bandwidth_gbs)
    if not all(math.isfinite(v) and v > 0 for v in values):
        raise ValueError("All inputs must be positive finite numbers")
    # GHz * ops/cycle = giga-ops/second; GB/s / B/op = giga-ops/second.
    period_control = max(control_path_ns, other_tile_path_ns)
    period_candidate = max(candidate_path_ns, other_tile_path_ns)
    memory_limit = sustained_bandwidth_gbs / bytes_per_op
    control = min(accepted_ops_per_cycle / period_control, memory_limit)
    candidate = min(accepted_ops_per_cycle / period_candidate, memory_limit)
    return {
        "control_tile_period_ns": period_control,
        "candidate_tile_period_ns": period_candidate,
        "control_gops": control,
        "candidate_gops": candidate,
        "relative_gain": candidate / control - 1,
        "control_bandwidth_saturation_boundary_gbs": bytes_per_op * accepted_ops_per_cycle / period_control,
        "necessary_positive_gain_conditions": {
            "control_controller_on_tile_critical_path": control_path_ns > other_tile_path_ns,
            "candidate_reduces_tile_period": period_candidate < period_control,
            "baseline_not_memory_saturated": sustained_bandwidth_gbs > bytes_per_op * accepted_ops_per_cycle / period_control,
        },
        "evidence_tier": "ANALYTIC_BOUNDARY_ONLY_NOT_MEASURED_GPU",
        "equal_resource_assumption": True,
        "same_admissions_per_cycle_due_to_functional_equivalence": True,
        "clock_tree_and_power": "NOT_EVALUATED",
    }


def self_test():
    # Synthetic regimes are frozen before any tile/workload measurement.
    win = boundary(4, 3, 2, 1, 4, 2)
    assert abs(win["relative_gain"] - 1/3) < 1e-12
    no_win_memory = boundary(4, 3, 2, 1, 4, .8)
    assert no_win_memory["relative_gain"] == 0
    no_win_clock = boundary(4, 3, 5, 1, 4, 2)
    assert no_win_clock["relative_gain"] == 0
    partial = boundary(4, 3, 2, 1, 4, 1.1)
    assert abs(partial["relative_gain"] - .1) < 1e-12
    same = boundary(4, 4, 2, 1, 4, 2)
    assert same["relative_gain"] == 0
    for invalid in ((0, 3, 2, 1, 4, 2), (4, 3, 2, 1, float("nan"), 2),
                    (4, 3, 2, 1, 4, -1)):
        try:
            boundary(*invalid)
        except ValueError:
            continue
        raise AssertionError("Invalid physical input accepted")
    print("V296_TILE_BOUNDARY_SELFTEST_PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--example-regimes", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
    elif a.example_regimes:
        print(json.dumps({
            "predicted_win_if_controller_limits_clock_and_bandwidth_spare": boundary(4, 3, 2, 1, 4, 2),
            "predicted_no_win_if_bandwidth_bound": boundary(4, 3, 2, 1, 4, .8),
            "predicted_no_win_if_other_path_limits_clock": boundary(4, 3, 5, 1, 4, 2),
        }, indent=2))
    else:
        p.error("Choose --self-test or --example-regimes")
