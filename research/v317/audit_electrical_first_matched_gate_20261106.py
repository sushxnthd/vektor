#!/usr/bin/env python3
"""Electrical-first, matched-resource physical comparison gate.

Input is a JSON object with 'baseline' and 'candidate' records, each with:
area_um2, frequency_mhz, setup_wns_ns, hold_wns_ns,
hold_violations, max_cap_violations, max_slew_violations,
max_fanout_violations, drc_violations, route_completed, extracted_rc_completed,
and optionally workload_service_per_cycle.
The gate refuses to convert illegal physical estimates into a positive win.
No GPU IPC or signoff is implied by the archived examples.
"""
import argparse
import json
import math
from pathlib import Path

REQUIRED = ("area_um2", "frequency_mhz", "setup_wns_ns",
            "hold_wns_ns", "hold_violations", "max_cap_violations",
            "max_slew_violations", "max_fanout_violations", "drc_violations")

def validate(record):
    for key in REQUIRED:
        if key not in record:
            raise ValueError("missing physical evidence: " + key)
        value = record[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("invalid numeric field: " + key)
    if record["area_um2"] <= 0 or record["frequency_mhz"] <= 0:
        raise ValueError("nonpositive area/frequency")
    for key in REQUIRED[4:]:
        if int(record[key]) != record[key] or record[key] < 0:
            raise ValueError("invalid violation count: " + key)
    for key in ("route_completed", "extracted_rc_completed"):
        if type(record.get(key)) is not bool:
            raise ValueError("missing or invalid route provenance: " + key)
    return (record["route_completed"] and record["extracted_rc_completed"]
            and record["setup_wns_ns"] >= 0 and record["hold_wns_ns"] >= 0
            and all(record[key] == 0 for key in REQUIRED[4:]))

def compare(data):
    base, cand = data["baseline"], data["candidate"]
    legal_base, legal_cand = validate(base), validate(cand)
    result = {"baseline_electrically_legal": legal_base,
              "candidate_electrically_legal": legal_cand,
              "area_ratio": cand["area_um2"] / base["area_um2"],
              "frequency_proxy_ratio": cand["frequency_mhz"] / base["frequency_mhz"],
              "status": "NO_POSITIVE_PHYSICAL_CLAIM"}
    if not (legal_base and legal_cand):
        result["reason"] = "electrical legality failed; clock/area proxies are non-signoff"
        return result
    if "workload_service_per_cycle" not in base or "workload_service_per_cycle" not in cand:
        result["reason"] = "missing matched workload service; legal area/clock alone insufficient"
        return result
    for rec in (base, cand):
        s = rec["workload_service_per_cycle"]
        if isinstance(s, bool) or not isinstance(s, (int, float)) or not math.isfinite(s) or s <= 0:
            raise ValueError("invalid measured workload service")
    result["conditional_service_ratio"] = (
        cand["workload_service_per_cycle"] * cand["frequency_mhz"] /
        (base["workload_service_per_cycle"] * base["frequency_mhz"]))
    if result["conditional_service_ratio"] <= 1.0 + 1e-12:
        result["reason"] = "no positive matched workload service advantage even under legal electrical assumptions"
        return result
    result["status"] = "ELIGIBLE_FOR_FURTHER_AUDIT"
    result["reason"] = "conditional only: requires matched bandwidth, power, area, and wire/load checks"
    return result

def selftest():
    b = dict(area_um2=21389.1, frequency_mhz=446.10,
             setup_wns_ns=.7583, hold_wns_ns=.00245,
             hold_violations=0, max_cap_violations=10,
             max_slew_violations=0, max_fanout_violations=0,
             drc_violations=0, route_completed=True, extracted_rc_completed=True)
    c = dict(area_um2=21533.0, frequency_mhz=454.59,
             setup_wns_ns=.8002, hold_wns_ns=-.00419,
             hold_violations=12, max_cap_violations=13,
             max_slew_violations=0, max_fanout_violations=0,
             drc_violations=0, route_completed=True, extracted_rc_completed=True)
    x = compare(dict(baseline=b, candidate=c))
    assert not x["baseline_electrically_legal"] and not x["candidate_electrically_legal"]
    assert x["status"] == "NO_POSITIVE_PHYSICAL_CLAIM"
    assert x["area_ratio"] > 1 and x["frequency_proxy_ratio"] > 1
    b2, c2 = dict(b), dict(c)
    b2["max_cap_violations"] = 0
    c2["max_cap_violations"] = c2["hold_violations"] = 0
    c2["hold_wns_ns"] = .001
    assert compare(dict(baseline=b2, candidate=c2))["status"] == "NO_POSITIVE_PHYSICAL_CLAIM"
    b2["workload_service_per_cycle"] = c2["workload_service_per_cycle"] = 1
    assert compare(dict(baseline=b2, candidate=c2))["status"] == "ELIGIBLE_FOR_FURTHER_AUDIT"
    # Falsification: a slower electrically legal candidate must not be eligible.
    c3 = {**c2, "workload_service_per_cycle": 0.5}
    slower = compare(dict(baseline=b2, candidate=c3))
    assert slower["conditional_service_ratio"] < 1
    assert slower["status"] == "NO_POSITIVE_PHYSICAL_CLAIM"
    equal = compare(dict(baseline=b2, candidate={**c2, "workload_service_per_cycle": b2["frequency_mhz"] / c2["frequency_mhz"]}))
    assert abs(equal["conditional_service_ratio"] - 1) < 1e-12
    # Floating-point rounding at exact parity cannot be accepted as a physical win.
    assert equal["status"] == "NO_POSITIVE_PHYSICAL_CLAIM"
    # A sub-picopercent numerical advantage is not a defensible performance win.
    near = compare(dict(baseline=b2, candidate={**c2, "workload_service_per_cycle": (b2["frequency_mhz"] / c2["frequency_mhz"]) * (1 + 5e-13)}))
    assert near["status"] == "NO_POSITIVE_PHYSICAL_CLAIM"
    # DRC and incomplete routed RC are hard falsifiers of physical eligibility.
    for field in ("route_completed", "extracted_rc_completed"):
        bad = compare(dict(baseline=b2, candidate={**c2, field: False}))
        assert bad["status"] == "NO_POSITIVE_PHYSICAL_CLAIM", field
    drc = compare(dict(baseline=b2, candidate={**c2, "drc_violations": 1}))
    assert drc["status"] == "NO_POSITIVE_PHYSICAL_CLAIM"
    try:
        compare(dict(baseline={**b2, "area_um2": float("nan")}, candidate=c2))
    except ValueError:
        pass
    else:
        raise AssertionError("NaN accepted")
    print("PASS: archived electrical no-go, hypothetical repaired gates, invalid-input control")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("input", nargs="?", type=Path)
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest:
        selftest()
    if a.input:
        print(json.dumps(compare(json.loads(a.input.read_text())), indent=2, sort_keys=True))
