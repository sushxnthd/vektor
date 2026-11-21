#!/usr/bin/env python3
"""V317 clock-normalized service break-even against compact greedy.

Pinned routed proxy data are electrically ILLEGAL; this is a conditional
falsification frontier, not a measured throughput or a legal Fmax claim.
The service ratio is an independent *input*, never inferred from the clocks.
"""
import json
from decimal import Decimal
from pathlib import Path

PIN = Path(__file__).with_name("STRONG_BASELINE_THREE_WAY_AUDIT_20261102.json")
D = lambda x: Decimal(str(x))

def frontier(data):
    v = data["variants"]
    p, c = v["pairwise"], v["compact"]
    for name, x in (("pairwise", p), ("compact", c)):
        assert not x["legal"], f"{name} became legal: requalify evidence"
        assert x["macro_count"] == 0, "Unexpected macro mapping"
    assert p["sequential_cells"] == c["sequential_cells"]
    fp, fc = D(p["fmax_mhz"]), D(c["fmax_mhz"])
    assert fp > 0 and fc > 0
    # Pairwise needs service_per_cycle ratio strictly above this value
    # merely to overcome the pinned clock ratio.
    return fc / fp

def clock_normalized_ratio(service_ratio, clock_ratio):
    s, r = D(service_ratio), D(clock_ratio)
    if s < 0 or r <= 0 or not s.is_finite() or not r.is_finite():
        raise ValueError("Invalid service/clock ratio")
    return s / r

def self_test():
    f = frontier(json.loads(PIN.read_text()))
    assert f > 1
    assert clock_normalized_ratio(1, f) < 1
    assert clock_normalized_ratio(f, f) == 1
    assert clock_normalized_ratio(f + D("0.001"), f) > 1
    for bad in ("NaN", "Infinity", "-1"):
        try:
            clock_normalized_ratio(bad, f)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid input accepted")
    print("PASS: conditional clock-normalized service frontier")
    print("Pinned pairwise/compact service-per-cycle break-even:", f)
    print("Minimum pairwise service uplift (%):", (f - 1) * 100)
    print("Assumes identical workload, no external bandwidth ceiling, and pinned clocks.")
    print("Both routes electrically illegal; no post-repair Fmax or throughput inferred.")

if __name__ == "__main__":
    self_test()
