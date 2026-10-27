#!/usr/bin/env python3
"""Independent exact-integer sensitivity audit for V296's censored density-0.35 control.

Not a router, frequency estimator, physical signoff, or GPU throughput model.
Inputs are the immutable SHA-pinned 2026-10-27 forensic JSON.
"""
import argparse
import json
from pathlib import Path

SOURCE = Path("research/v296/DENSITY035_FROZEN_ROUTE_FORENSICS_20261027.json")
BASE_CANDIDATE = 12020
BASE_SERIAL = 5281
CANDIDATE_LIMIT = 8414


def minimum_serial_drc(candidate_drc):
    """Exact integer boundary for (candidate/serial)/(12020/5281) <= 3/4."""
    if type(candidate_drc) is not int or candidate_drc < 0:
        raise ValueError("Candidate DRC must be a nonnegative integer")
    numerator = 4 * candidate_drc * BASE_SERIAL
    denominator = 3 * BASE_CANDIDATE
    return (numerator + denominator - 1) // denominator


def classify(candidate, serial):
    if candidate is None or serial is None:
        return "INCOMPLETE_CENSORED_NO_COMPARATIVE_CLAIM"
    if any(type(x) is not int or x < 0 for x in (candidate, serial)):
        raise ValueError("DRC counts must be nonnegative integers")
    if serial == 0:
        return "FALSIFIED_SERIAL_ZERO_DRC" if candidate else "UNINFORMATIVE_BOTH_ZERO"
    reduction_pass = candidate <= CANDIDATE_LIMIT
    ratio_pass = 4 * candidate * BASE_SERIAL <= 3 * serial * BASE_CANDIDATE
    return ("DIAGNOSTIC_SUPPORTED_NOT_SIGNOFF" if reduction_pass and ratio_pass
            else "DIAGNOSTIC_FALSIFIED")


def read_frozen(path):
    d = json.loads(path.read_text())
    if (d.get("run_id") != 40411106938 or
            d.get("verdict") != "INCOMPLETE_CONTROL_CENSORED_NO_CAUSAL_CLAIM" or
            d["frozen"].get("clock_ns") != 3.5 or
            d["frozen"].get("rc_multiplier") != 2 or
            d["frozen"].get("trial_density") != 0.35 or
            d["frozen"].get("serial_extra_repair") is not True or
            d["frozen"].get("iteration3_candidate_max_drc") != CANDIDATE_LIMIT or
            d["frozen"].get("iteration3_relative_ratio_max") != 0.75):
        raise ValueError("Frozen source protocol mismatch")
    candidate = d["drc_trajectories"]["density035_pairwise"]
    serial = d["drc_trajectories"]["density035_serial"]
    if len(candidate) <= 3 or candidate[3] != 3632 or serial:
        raise ValueError("Unexpected or retrospectively filled original checkpoint")
    return d


def report(data):
    candidate = data["drc_trajectories"]["density035_pairwise"][3]
    estimate = data["candidate_postcts_global"]["density035"]["setup_slack_ns"]
    # At fixed candidate DRC, this is a necessary-and-sufficient control boundary,
    # not an estimate of the unobserved control outcome.
    sensitivity = []
    for delta_percent in (-10, -5, 0, 5, 10):
        c = (candidate * (100 + delta_percent) + 50) // 100
        minimum = minimum_serial_drc(c)
        sensitivity.append({
            "candidate_drc_change_percent_hypothetical": delta_percent,
            "candidate_drc_hypothetical": c,
            "serial_drc_min_for_relative_gate": minimum,
            "both_gates_if_serial_drc_2000": classify(c, 2000),
            "both_gates_if_serial_drc_2500": classify(c, 2500),
        })
    return {
        "evidence": "EXACT_INTEGER_PARTIAL_IDENTIFICATION_FROM_FROZEN_CENSORED_RUN",
        "source_run": data["run_id"],
        "candidate_iteration3_drc": candidate,
        "serial_iteration3_drc": None,
        "candidate_only_reduction_percent": 100 * (BASE_CANDIDATE - candidate) / BASE_CANDIDATE,
        "minimum_missing_serial_drc_for_relative_gate": minimum_serial_drc(candidate),
        "original_verdict": classify(candidate, None),
        "candidate_global_route_setup_guard_margin_ps_not_extracted_rc":
            (estimate - 0.050) * 1000,
        "sensitivity": sensitivity,
        "physical_signoff": False,
        "gpu_speedup_claim": False,
    }


def self_test():
    assert minimum_serial_drc(3632) == 2128
    assert classify(3632, None) == "INCOMPLETE_CENSORED_NO_COMPARATIVE_CLAIM"
    assert classify(3632, 2127) == "DIAGNOSTIC_FALSIFIED"
    assert classify(3632, 2128) == "DIAGNOSTIC_SUPPORTED_NOT_SIGNOFF"
    assert classify(8415, 5281) == "DIAGNOSTIC_FALSIFIED"
    assert classify(0, 0) == "UNINFORMATIVE_BOTH_ZERO"
    assert classify(3632, 0) == "FALSIFIED_SERIAL_ZERO_DRC"
    for invalid in (-1, 1.5, True):
        try:
            minimum_serial_drc(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid DRC accepted")
    data = read_frozen(SOURCE)
    result = report(data)
    assert result["minimum_missing_serial_drc_for_relative_gate"] == 2128
    assert result["physical_signoff"] is False
    print("V296_DENSITY035_CONTROL_SENSITIVITY_SELFTEST_PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--report", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
    if args.report:
        print(json.dumps(report(read_frozen(SOURCE)), indent=2, sort_keys=True))
    if not args.self_test and not args.report:
        p.error("Select --self-test or --report")
