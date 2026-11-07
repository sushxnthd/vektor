#!/usr/bin/env python3
"""Independent matched-resource viability gate for Vektor candidates.

Inputs are measured values, not inferred from abstract queue admissions.
Run: python3 research/v317/rtl/matched_physical_gate.py
Optional: python3 .../matched_physical_gate.py candidate.json
JSON keys: candidate, baseline, each containing area_um2, period_ns,
useful_service_per_cycle, useful_fraction, dynamic_power_mw,
hold_violations, max_cap_violations; optional min_gain (default 0).
"""
import json
import math
import sys

def assess(data):
    a, b = data["candidate"], data["baseline"]
    fields = ("area_um2", "period_ns", "useful_service_per_cycle",
              "useful_fraction", "dynamic_power_mw")
    for name, d in (("candidate", a), ("baseline", b)):
        for field in fields:
            v = float(d[field])
            if not math.isfinite(v) or v <= 0:
                raise ValueError(f"{name}.{field} must be finite and positive")
        if float(d["useful_fraction"]) > 1:
            raise ValueError("useful_fraction must be <= 1")
        for k in ("hold_violations", "max_cap_violations"):
            if not isinstance(d[k], int) or d[k] < 0:
                raise ValueError(f"{name}.{k} must be a nonnegative integer")
    legal = all(d["hold_violations"] == d["max_cap_violations"] == 0
                for d in (a, b))
    throughput = lambda d: (d["useful_service_per_cycle"] *
                             d["useful_fraction"] / d["period_ns"])
    gain = throughput(a) / throughput(b) - 1
    area_ratio = a["area_um2"] / b["area_um2"]
    energy_ratio = (a["dynamic_power_mw"] / throughput(a)) / (
        b["dynamic_power_mw"] / throughput(b))
    min_gain = float(data.get("min_gain", 0))
    if not math.isfinite(min_gain) or min_gain < 0:
        raise ValueError("min_gain must be finite and nonnegative")
    return {"electrically_legal": legal, "throughput_gain": gain,
            "area_ratio": area_ratio, "energy_per_service_ratio": energy_ratio,
            "passes": legal and gain > min_gain and area_ratio <= 1
                      and energy_ratio <= 1}

def self_test():
    base = dict(area_um2=100, period_ns=3, useful_service_per_cycle=2,
                useful_fraction=1, dynamic_power_mw=10,
                hold_violations=0, max_cap_violations=0)
    x = dict(base)
    assert not assess(dict(candidate=x, baseline=base))["passes"]
    x["period_ns"] = 2.9
    assert assess(dict(candidate=x, baseline=base))["passes"]
    x["max_cap_violations"] = 1
    assert not assess(dict(candidate=x, baseline=base))["passes"]
    x["max_cap_violations"] = 0
    x["area_um2"] = 101
    assert not assess(dict(candidate=x, baseline=base))["passes"]
    x["area_um2"] = 100
    x["dynamic_power_mw"] = 11
    assert not assess(dict(candidate=x, baseline=base))["passes"]
    x["dynamic_power_mw"] = 10
    x["useful_fraction"] = 0.9
    assert not assess(dict(candidate=x, baseline=base))["passes"]
    print("self-test PASS; no physical measurements implied")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        self_test()
    elif len(sys.argv) == 2:
        with open(sys.argv[1], encoding="utf-8") as f:
            print(json.dumps(assess(json.load(f)), indent=2, sort_keys=True))
    else:
        raise SystemExit("usage: matched_physical_gate.py [measurements.json]")
