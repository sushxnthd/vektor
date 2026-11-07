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
            "useful_fraction")
POWER = ("dynamic_power_mw", "leakage_power_mw")
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
    # Power components may be zero (e.g. gated idle leakage or idealized
    # zero-switching traces); total power must remain strictly positive.
    for field in POWER:
        v = d.get(field)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
            raise ValueError(f"{name}.{field} must be finite and nonnegative")
    if d["dynamic_power_mw"] + d["leakage_power_mw"] <= 0:
        raise ValueError(f"{name}.total_power must be positive")
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
    # Identical labels do not imply identical SDC files: require byte-identical
    # constraints, otherwise period/area comparisons are not matched.
    mismatches = [k for k in MATCHED if a[k] != b[k]]
    if a["constraints_sha256"] != b["constraints_sha256"]:
        mismatches.append("constraints_sha256")
    if mismatches:
        raise ValueError("unmatched physical comparison: " + ", ".join(mismatches))
    # A changed clock period cannot be certified from byte-identical physical
    # inputs and STA output. Reject the inconsistent measurement packet before
    # computing any performance gain. Different digests remain unverified.
    physical_keys = ("netlist_sha256", "constraints_sha256",
                     "parasitics_sha256", "sta_report_sha256")
    if a["period_ns"] != b["period_ns"] and all(a[k] == b[k] for k in physical_keys):
        raise ValueError("clock period changed with identical physical evidence")
    legal = all(d["setup_wns_ns"] >= 0 and d["hold_wns_ns"] >= 0
                and all(d[k] == 0 for k in VIOLATIONS) for d in (a, b))
    throughput = lambda d: d["useful_service_per_cycle"] * d["useful_fraction"] / d["period_ns"]
    gain = throughput(a) / throughput(b) - 1
    area_ratio = a["area_um2"] / b["area_um2"]
    # Dynamic-only energy can reverse after leakage is included. Require both.
    total_power = lambda d: d["dynamic_power_mw"] + d["leakage_power_mw"]
    energy_ratio = (total_power(a) / throughput(a)) / (total_power(b) / throughput(b))
    # A zero-dynamic-power baseline has no defined dynamic-energy ratio.
    # Report null rather than crashing or treating zero/zero as evidence.
    dynamic_energy_ratio = (
        (a["dynamic_power_mw"] / throughput(a)) / (b["dynamic_power_mw"] / throughput(b))
        if b["dynamic_power_mw"] > 0 else None
    )
    min_gain = data.get("min_gain", 0)
    if isinstance(min_gain, bool) or not isinstance(min_gain, (int, float)) or not math.isfinite(min_gain) or min_gain < 0:
        raise ValueError("min_gain must be finite and nonnegative")
    return {"electrically_legal": legal, "throughput_gain": gain,
            "area_ratio": area_ratio, "energy_per_service_ratio": energy_ratio,
            "dynamic_energy_per_service_ratio": dynamic_energy_ratio,
            "passes": bool(legal and gain > min_gain and area_ratio <= 1 and energy_ratio <= 1),
            "evidence_tier": "supplied_measurements_only"}

def self_test():
    d = dict(area_um2=100, period_ns=3, useful_service_per_cycle=2,
             useful_fraction=1, dynamic_power_mw=10, leakage_power_mw=1,
             setup_wns_ns=0.1, hold_wns_ns=0.1,
             setup_violations=0, hold_violations=0, max_cap_violations=0,
             max_transition_violations=0,
             **{k: "a"*64 for k in PROVENANCE},
             **{k: "matched" for k in MATCHED})
    base = dict(d)
    candidate = dict(d, period_ns=2.9, netlist_sha256="b"*64,\n                     parasitics_sha256="c"*64, sta_report_sha256="d"*64)
    packet = dict(candidate=candidate, baseline=base)\n    try:\n        assess(dict(candidate=dict(d, period_ns=2.9), baseline=base))\n    except ValueError as exc:\n        assert "identical physical evidence" in str(exc)\n    else:\n        raise AssertionError("fabricated period improvement accepted")
    assert assess(packet)["passes"]
    for k, v in (("setup_wns_ns", -0.01), ("hold_wns_ns", -0.01),
                 ("setup_violations", 1), ("hold_violations", 1),
                 ("max_cap_violations", 1), ("max_transition_violations", 1)):
        bad = dict(candidate, **{k: v})
        assert not assess(dict(candidate=bad, baseline=base))["passes"], k
    # Synthetic reversal: dynamic-only passes, but added candidate leakage fails.
    leaky = dict(candidate, dynamic_power_mw=8, leakage_power_mw=8)
    leak_result = assess(dict(candidate=leaky, baseline=base))
    assert leak_result["dynamic_energy_per_service_ratio"] < 1
    assert leak_result["energy_per_service_ratio"] > 1
    assert not leak_result["passes"]
    # Zero components are valid measurements, but zero total power is not.
    zero_leak = dict(candidate, leakage_power_mw=0)
    assert assess(dict(candidate=zero_leak, baseline=base))["passes"]
    zero_dynamic = dict(candidate, dynamic_power_mw=0)
    assert assess(dict(candidate=zero_dynamic, baseline=base))["passes"]
    # A zero-dynamic baseline must not cause division by zero or invent a ratio.
    base_zero_dynamic = dict(base, dynamic_power_mw=0)
    result_zero_baseline = assess(dict(candidate=zero_dynamic, baseline=base_zero_dynamic))
    assert result_zero_baseline["dynamic_energy_per_service_ratio"] is None
    assert result_zero_baseline["energy_per_service_ratio"] > 0
    assert result_zero_baseline["passes"]
    for k in POWER:
        for v in (-0.01, float("nan"), float("inf"), True):
            try:
                assess(dict(candidate=dict(candidate, **{k: v}), baseline=base))
            except ValueError:
                pass
            else:
                raise AssertionError(f"invalid power accepted: {k}={v}")
    try:
        assess(dict(candidate=dict(candidate, dynamic_power_mw=0, leakage_power_mw=0), baseline=base))
    except ValueError:
        pass
    else:
        raise AssertionError("zero total power accepted")
    for k in ("setup_wns_ns", "parasitics_sha256", "workload_report_sha256", "leakage_power_mw"):
        bad = dict(candidate)
        bad.pop(k)
        try:
            assess(dict(candidate=bad, baseline=base))
        except (ValueError, KeyError):
            pass
        else:
            raise AssertionError("missing evidence accepted: " + k)
    bad = dict(candidate, constraints_sha256="b"*64)
    try:
        assess(dict(candidate=bad, baseline=base))
    except ValueError:
        pass
    else:
        raise AssertionError("different SDC digests accepted despite matching labels")
    bad = dict(candidate, corner="different")
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
