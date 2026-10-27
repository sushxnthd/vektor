#!/usr/bin/env python3
"""Fail-closed independent audit of V296 D4/D8 extracted-route transfer.

Inputs are transcribed aggregate measurements from GitHub Actions #40557136436.
Job success alone never implies physical feasibility. Conditional clock-period
bounds assume fixed path delay and are NOT timing signoff.
"""
import argparse
import copy
import json
import math
from pathlib import Path

REQUIRED = ("setup_ns", "hold_ns", "area_um2", "cap", "slew")


def classify(row, limits):
    if row.get("status") != "complete":
        return {"complete": False, "feasible": False, "reasons": ["incomplete_or_timed_out"]}
    f = row.get("final")
    if not isinstance(f, dict) or any(k not in f for k in REQUIRED):
        return {"complete": False, "feasible": False, "reasons": ["missing_required_physical_metric"]}
    if any(not isinstance(f[k], (float, int)) or isinstance(f[k], bool)
           or not math.isfinite(f[k]) for k in REQUIRED):
        return {"complete": False, "feasible": False, "reasons": ["nonfinite_or_invalid_metric"]}
    reasons = []
    if f["setup_ns"] < limits["min_setup_ns"]:
        reasons.append("setup")
    if f["hold_ns"] < limits["min_hold_ns"]:
        reasons.append("hold")
    if f["area_um2"] > limits["max_area_um2"]:
        reasons.append("area")
    if f["cap"] != 0:
        reasons.append("capacitance")
    if f["slew"] != 0:
        reasons.append("slew")
    recovery = max(0.0, limits["min_setup_ns"] - f["setup_ns"])
    period = limits["clock_period_ns"] + recovery
    return {"complete": True, "feasible": not reasons, "reasons": reasons,
            "setup_recovery_ns": recovery, "conditional_min_period_ns": period,
            "conditional_max_clock_mhz": 1000.0 / period,
            "area_headroom_um2": limits["max_area_um2"] - f["area_um2"]}


def audit(doc):
    assert doc["run_id"] == 40557136436
    assert set(doc["observations"]) == {
        "D4_pairwise", "D4_serial_onehot", "D8_pairwise", "D8_serial_onehot"}
    results = {k: classify(v, doc["frozen_limits"])
               for k, v in doc["observations"].items()}
    matched = {}
    for depth in ("D4", "D8"):
        a = results[f"{depth}_pairwise"]
        b = results[f"{depth}_serial_onehot"]
        matched[depth] = {"both_complete": a["complete"] and b["complete"],
                          "both_feasible": a["feasible"] and b["feasible"],
                          "matched_feasible_advantage_claim_allowed": a["feasible"] and b["feasible"]}
    return {"run_id": doc["run_id"], "results": results, "matched": matched,
            "any_matched_feasible_claim": any(
                x["matched_feasible_advantage_claim_allowed"] for x in matched.values())}


def self_test(doc):
    r = audit(doc)
    assert not r["any_matched_feasible_claim"]
    assert r["results"]["D4_serial_onehot"]["reasons"] == ["setup", "capacitance"]
    assert r["results"]["D8_pairwise"]["reasons"] == ["setup", "capacitance"]
    assert not r["results"]["D4_pairwise"]["complete"]
    assert not r["results"]["D8_serial_onehot"]["complete"]
    assert not r["matched"]["D4"]["both_complete"]
    assert not r["matched"]["D8"]["both_complete"]
    d = copy.deepcopy(doc)
    d["observations"]["D8_pairwise"]["final"]["setup_ns"] = 0.30
    assert "capacitance" in audit(d)["results"]["D8_pairwise"]["reasons"]
    d = copy.deepcopy(doc)
    d["observations"]["D8_pairwise"]["final"]["cap"] = 0
    assert "setup" in audit(d)["results"]["D8_pairwise"]["reasons"]
    d = copy.deepcopy(doc)
    del d["observations"]["D8_pairwise"]["final"]["hold_ns"]
    assert not audit(d)["results"]["D8_pairwise"]["complete"]
    d = copy.deepcopy(doc)
    d["observations"]["D8_pairwise"]["final"]["area_um2"] = 30000.01
    assert "area" in audit(d)["results"]["D8_pairwise"]["reasons"]
    d = copy.deepcopy(doc)
    d["observations"]["D8_pairwise"]["final"]["setup_ns"] = float("nan")
    assert not audit(d)["results"]["D8_pairwise"]["complete"]
    d = copy.deepcopy(doc)
    d["observations"]["D4_pairwise"]["status"] = "complete"
    assert not audit(d)["results"]["D4_pairwise"]["complete"]
    print("V296_DEEP_ROUTE_FAIL_CLOSED_SELFTEST_PASS")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("evidence", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    doc = json.loads(args.evidence.read_text())
    if args.self_test:
        self_test(doc)
    print(json.dumps(audit(doc), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
