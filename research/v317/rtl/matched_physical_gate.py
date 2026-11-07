#!/usr/bin/env python3
"""Fail-closed matched-resource physical viability gate.

JSON requires candidate and baseline with identical evidence schema. This is an
audit of supplied measurements, NOT a substitute for STA or extracted routing.
Usage: python3 matched_physical_gate.py [measurements.json]
"""
import json
import math
import sys

POSITIVE = ("area_um2", "period_ns", "useful_service_per_cycle",
            "useful_fraction", "dynamic_power_mw")
NONNEGATIVE = ("setup_wns_ns", "hold_wns_ns")
VIOLATIONS = ("setup_violations", "hold_violations", "max_cap_violations",
              "max_transition_violations")
PROVENANCE = ("netlist_sha256", "constraints_sha256", "parasitics_sha256",
              "sta_report_sha256", "power_report_sha256", "workload_report_sha256")
# These identifiers prevent accidental comparison of different corners, tools,
# constraints, technology, workloads, or accounting conventions.
MATCHED = ("technology", "corner", "tool_version", "constraints_id",
           "workload_id", "measurement_protocol_id")

def _validate(name, d):
    if not isinstance(d, dict):
        raise ValueError(name + " must be an object")
    for field in POSITIVE:
        v = d.get(field)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError(f"{name}.{field} must be a numeric measurement")
        if not math.isfinite(v) or v <= 0:
            raise ValueError(f"{name}.{field} must be finite and positive")
    if d["useful_fraction"] > 1:
        raise ValueError(f"{name}.useful_fraction must be <= 1")
    for field in NONNEGATIVE:
        v = d.get(field)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError(f"{name}.{field} must be a finite number")
    for field in VIOLATIONS:
        v = d.get(field)
        if type(v) is not int or v < 0:
            raise ValueError(f"{name}.{field} must be a nonnegative integer")
    for field in PROVENANCE:
        v = d.get(field)
        if not isinstance(v, str) or len(v) != 64 or any(c not in "0123456789abcdef" for c in v):
            raise ValueError(f"{name}.{field} must be a lowercase SHA-256 digest")
    for field in MATCHED:
        if not isinstance(d.get(field), str) or not d[field].strip():
            raise ValueError(f"{name}.{field} must be a nonempty identifier")

def assess(data):
    a, b = data["candidate"], data["baseline"]
    _validate("candidate", a)
    _validate("baseline", b)
    # Identical labels do not imply identical SDC files: require byte-identical\n    # constraints, otherwise period/area comparisons are not matched.\n    mismatches = [k for k in MATCHED if a[k] != b[k]]\n    if a["constraints_sha256"] != b["constraints_sha256"]:\n        mismatches.append("constraints_sha256")
    if mismatches:
        raise ValueError("unmatched physical comparison: " + ", ".join(mismatches))
    legal = all(d["setup_wns_ns"] >= 0 and d["hold_wns_ns"] >= 0
                and all(d[k] == 0 for k in VIOLATIONS) for d in (a, b))
    throughput = lambda d: d["useful_service_per_cycle"] * d["useful_fraction"] / d["period_ns"]
    gain = throughput(a) / throughput(b) - 1
    area_ratio = a["area_um2"] / b["area_um2"]
    energy_ratio = (a["dynamic_power_mw"] / throughput(a)) / (b["dynamic_power_mw"] / throughput(b))
    min_gain = data.get("min_gain", 0)
    if isinstance(min_gain, bool) or not isinstance(min_gain, (int, float)) or not math.isfinite(min_gain) or min_gain < 0:
        raise ValueError("min_gain must be finite and nonnegative")
    return {"electrically_legal": legal, "throughput_gain": gain,
            "area_ratio": area_ratio, "energy_per_service_ratio": energy_ratio,
            "passes": bool(legal and gain > min_gain and area_ratio <= 1 and energy_ratio <= 1),
            "evidence_tier": "supplied_measurements_only"}

def self_test():
    d = dict(area_um2=100, period_ns=3, useful_service_per_cycle=2,
             useful_fraction=1, dynamic_power_mw=10,
             setup_wns_ns=0.1, hold_wns_ns=0.1,
             setup_violations=0, hold_violations=0, max_cap_violations=0,
             max_transition_violations=0,
             **{k: "a"*64 for k in PROVENANCE},
             **{k: "matched" for k in MATCHED})
    base = dict(d)
    candidate = dict(d, period_ns=2.9)
    packet = dict(candidate=candidate, baseline=base)
    assert assess(packet)["passes"]
    for k, v in (("setup_wns_ns", -0.01), ("hold_wns_ns", -0.01),
                 ("setup_violations", 1), ("hold_violations", 1),
                 ("max_cap_violations", 1), ("max_transition_violations", 1)):
        bad = dict(candidate, **{k: v})
        assert not assess(dict(candidate=bad, baseline=base))["passes"], k
    for k in ("setup_wns_ns", "parasitics_sha256", "workload_report_sha256"):
        bad = dict(candidate)
        bad.pop(k)
        try:
            assess(dict(candidate=bad, baseline=base))
        except (ValueError, KeyError):
            pass
        else:
            raise AssertionError("missing evidence accepted: " + k)
    bad = dict(candidate, constraints_sha256="b"*64)\n    try:\n        assess(dict(candidate=bad, baseline=base))\n    except ValueError:\n        pass\n    else:\n        raise AssertionError("different SDC digests accepted despite matching labels")\n    bad = dict(candidate, corner="different")
    try:
        assess(dict(candidate=bad, baseline=base))
    except ValueError:
        pass
    else:
        raise AssertionError("unmatched corner accepted")
    print("self-test PASS (synthetic inputs only; no physical signoff implied)")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        self_test()
    elif len(sys.argv) == 2:
        with open(sys.argv[1], encoding="utf-8") as f:
            print(json.dumps(assess(json.load(f)), indent=2, sort_keys=True))
    else:
        raise SystemExit("usage: matched_physical_gate.py [measurements.json]")
