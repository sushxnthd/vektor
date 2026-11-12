#!/usr/bin/env python3
"""Independent RF demand-conservation falsifier for the V317 pairing upper bound.

Exact integer accounting, not an RTL/physical result. A two-operand warp with
both operands on one two-read-port bank cannot share its issue cycle with
another such warp, regardless of disjoint execution masks.
"""
from fractions import Fraction as F

PORTS = 2
COMPACT_AREA = F("21314.6")
PAIRWISE_AREA = F("21324.7")

def cycles_for_bank_demand(warps, reads_per_warp, ports=PORTS):
    assert warps >= 0 and reads_per_warp >= 0 and ports > 0
    return (warps * reads_per_warp + ports - 1) // ports

def upper_bound_tpa(reads_per_warp, clock_ratio=F(1), extra_area=F(0)):
    """Upper bound when pairing cannot reduce total bank reads or issue cycles."""
    assert reads_per_warp >= PORTS and clock_ratio > 0 and extra_area >= 0
    area_ratio = (COMPACT_AREA + extra_area) / (PAIRWISE_AREA + extra_area)
    return area_ratio / clock_ratio

def main():
    for warps in (2, 4, 16, 128):
        assert cycles_for_bank_demand(warps, 2) == warps
        assert cycles_for_bank_demand(warps, 2) < cycles_for_bank_demand(warps, 4)
    # Exact, prospective no-win regime: all active warps require two
    # reads from the same two-port bank; no caching/bypass/bank spreading.
    # Even perfectly compatible, disjoint masks do not remove RF demand.
    assert upper_bound_tpa(2) < 1
    assert upper_bound_tpa(2, F(1, 1), F(100000)) < 1
    # Pairwise could win only through a verified clock advantage or a
    # separately measured reduction in reads, not scheduler pairing alone.
    threshold = (COMPACT_AREA / PAIRWISE_AREA)
    assert upper_bound_tpa(2, threshold) == 1
    print("PASS demand-conservation no-win regime")
    print("equal-clock TPA upper bound:", float(upper_bound_tpa(2)))
    print("required clock-period ratio for any TPA win:", float(threshold))
    print("NOT measured: bank mapping, RTL throughput, timing or electrical closure")

if __name__ == "__main__":
    main()
