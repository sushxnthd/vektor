#!/usr/bin/env python3
"""Necessary (not sufficient) repair frontier for the original matched V296 slice.

Algebraic falsification/sensitivity study anchored to failed postroute run
40156470550. Does not change the frozen gate or predict achievable GPU Fmax.
"""
import argparse
import json
import math

ORIGINAL = {
    "pairwise": {"area_um2": 17857.644252, "setup_ns": -1.047895,
                 "hold_ns": -0.036622, "cap_violations": 3},
    "serial_onehot": {"area_um2": 18953.830505, "setup_ns": -1.859922,
                      "hold_ns": -0.019796, "cap_violations": 3},
}
SETUP_TARGET_NS = 0.050
HOLD_TARGET_NS = 0.0
AREA_LIMIT_UM2 = 30000.0


def check_number(v, label):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError(f"{label}: expected finite real")
    return float(v)


def minimum_repairs():
    return {name: {
        "minimum_setup_gain_ns": SETUP_TARGET_NS - row["setup_ns"],
        "minimum_hold_gain_ns": HOLD_TARGET_NS - row["hold_ns"],
        "remaining_area_to_frozen_limit_um2": AREA_LIMIT_UM2 - row["area_um2"],
        "cap_violations_to_remove": row["cap_violations"],
    } for name, row in ORIGINAL.items()}


def frontier(pairwise_setup_gain_ns, serial_setup_gain_ns,
             pairwise_hold_gain_ns=0.0, serial_hold_gain_ns=0.0,
             pairwise_area_change_um2=0.0, serial_area_change_um2=0.0,
             pairwise_cap_violations=3, serial_cap_violations=3):
    values = locals().copy()
    for k, v in values.items():
        check_number(v, k)
    for k in ("pairwise_cap_violations", "serial_cap_violations"):
        if isinstance(values[k], bool) or not isinstance(values[k], int) or values[k] < 0:
            raise ValueError(k + ": expected nonnegative integer")
    rows = {}
    for name, key in (("pairwise", "pairwise"), ("serial_onehot", "serial")):
        row = ORIGINAL[name]
        s = row["setup_ns"] + values[key + "_setup_gain_ns"]
        h = row["hold_ns"] + values[key + "_hold_gain_ns"]
        a = row["area_um2"] + values[key + "_area_change_um2"]
        if a <= 0:
            raise ValueError("Nonphysical final area")
        cap = values[key + "_cap_violations"]
        rows[name] = {
            "hypothetical_setup_ns": s,
            "hypothetical_hold_ns": h,
            "hypothetical_area_um2": a,
            "hypothetical_cap_violations": cap,
            "setup_gate": s >= SETUP_TARGET_NS - 1e-12,
            "hold_gate": h >= HOLD_TARGET_NS - 1e-12,
            "area_gate": a <= AREA_LIMIT_UM2,
            "cap_gate": cap == 0,
        }
    lead = rows["pairwise"]["hypothetical_setup_ns"] - rows["serial_onehot"]["hypothetical_setup_ns"]
    saving = 1 - rows["pairwise"]["hypothetical_area_um2"] / rows["serial_onehot"]["hypothetical_area_um2"]
    return {
        "original_run": 40156470550,
        "original_gate": "BOTH_INFEASIBLE_FALSIFIED",
        "necessary_repairs": minimum_repairs(),
        "hypothetical_rows": rows,
        "hypothetical_setup_lead_ns": lead,
        "hypothetical_area_saving_fraction": saving,
        "equal_consumed_area": abs(rows["pairwise"]["hypothetical_area_um2"] - rows["serial_onehot"]["hypothetical_area_um2"]) < 1e-9,
        "necessary_four_gate_condition": all(all(r[k] for k in ("setup_gate", "hold_gate", "area_gate", "cap_gate")) for r in rows.values()),
        "full_physical_gate": "NOT_EVALUATED_DRC_SLEW_AND_REEXTRACTION_REQUIRED",
        "gpu_speedup": "NOT_ESTABLISHED",
        "evidence_tier": "MEASURED_INPUTS_HYPOTHETICAL_REPAIR_SENSITIVITY",
    }


def self_test():
    mins = minimum_repairs()
    assert abs(mins["pairwise"]["minimum_setup_gain_ns"] - 1.097895) < 1e-12
    assert abs(mins["serial_onehot"]["minimum_setup_gain_ns"] - 1.909922) < 1e-12
    assert abs(mins["pairwise"]["minimum_hold_gain_ns"] - .036622) < 1e-12
    assert abs(mins["serial_onehot"]["minimum_hold_gain_ns"] - .019796) < 1e-12
    raw = frontier(0, 0)
    assert not raw["necessary_four_gate_condition"]
    assert abs(raw["hypothetical_setup_lead_ns"] - .812027) < 1e-12
    assert abs(raw["hypothetical_area_saving_fraction"] - .0578345) < 1e-6
    both_setup_only = frontier(2, 2)
    assert all(x["setup_gate"] for x in both_setup_only["hypothetical_rows"].values())
    assert not both_setup_only["necessary_four_gate_condition"]
    just_closes = frontier(1.097895, 1.909922, .036622, .019796, 0, 0, 0, 0)
    assert just_closes["necessary_four_gate_condition"]
    assert abs(just_closes["hypothetical_setup_lead_ns"]) < 1e-12
    assert just_closes["full_physical_gate"].startswith("NOT_EVALUATED")
    equal_area = frontier(2, 2, .1, .1, 1096.186253, 0, 0, 0)
    assert equal_area["equal_consumed_area"]
    for kwargs in ({"pairwise_setup_gain_ns": float("nan"), "serial_setup_gain_ns": 2},
                   {"pairwise_setup_gain_ns": 2, "serial_setup_gain_ns": 2, "pairwise_cap_violations": -1},
                   {"pairwise_setup_gain_ns": 2, "serial_setup_gain_ns": 2, "pairwise_cap_violations": 0.5},
                   {"pairwise_setup_gain_ns": 2, "serial_setup_gain_ns": 2, "pairwise_area_change_um2": -20000}):
        try:
            frontier(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("Fail-open input accepted")
    print("V296_PAIRED_REPAIR_FRONTIER_SELFTEST_PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--scenario", choices=("original", "setup_only", "minimum_repairs"))
    a = p.parse_args()
    if a.self_test:
        self_test()
    elif a.scenario == "original":
        print(json.dumps(frontier(0, 0), indent=2))
    elif a.scenario == "setup_only":
        print(json.dumps(frontier(2, 2), indent=2))
    elif a.scenario == "minimum_repairs":
        print(json.dumps(frontier(1.097895, 1.909922, .036622, .019796, 0, 0, 0, 0), indent=2))
    else:
        p.error("Specify --self-test or --scenario")
