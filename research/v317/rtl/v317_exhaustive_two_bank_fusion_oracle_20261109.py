#!/usr/bin/env python3
"""Exact finite-trace adversarial audit of the V317 RF-port upper bound.

Independent of the mean-field boundary script. Enumerates two-warp demands
and exhaustively tests whether a purported fused issue fits a two-port bank.
This is an analytical checker, not RTL timing, mapped area, or GPU IPC.
"""
from itertools import product
from fractions import Fraction

PORTS = 2
COMPACT_AREA = Fraction("21314.6")
PAIRWISE_AREA = Fraction("21324.7")

def minimum_bank_cycles(demands, ports=PORTS):
    """Lower bound from conservation of per-bank reads; no bypass/caching."""
    assert ports > 0 and all(all(x >= 0 for x in d) for d in demands)
    if not demands:
        return 0
    return max((sum(d[b] for d in demands) + ports - 1) // ports
               for b in range(len(demands[0])))

def fusion_legal(a, b, compatible, disjoint, ports=PORTS):
    assert len(a) == len(b)
    return compatible and disjoint and all(x + y <= ports for x, y in zip(a, b))

def audit():
    cases = 0
    legal = 0
    illegal = 0
    for a, b in product(product(range(3), repeat=2), repeat=2):
        for compatible, disjoint in product((False, True), repeat=2):
            cases += 1
            feasible = fusion_legal(a, b, compatible, disjoint)
            if feasible:
                legal += 1
                assert compatible and disjoint
                assert minimum_bank_cycles((a, b)) <= 1
            else:
                illegal += 1
            if compatible and disjoint and minimum_bank_cycles((a, b)) > 1:
                assert not feasible
    # Two full-width warps target the same bank: mask disjointness is insufficient.
    a, b = (2, 0), (2, 0)
    assert minimum_bank_cycles((a, b)) == 2
    assert not fusion_legal(a, b, True, True)
    # Different banks: a genuinely feasible pairing, not a blanket no-win claim.
    assert fusion_legal((2, 0), (0, 2), True, True)
    # For the same-bank saturated regime with no cycle savings, the challenger
    # cannot beat the smaller compact baseline at equal clock and tile resources.
    tpa_bound = COMPACT_AREA / PAIRWISE_AREA
    assert tpa_bound < 1
    print("PASS", cases, "exhaustive two-bank cases", legal, "legal", illegal, "illegal")
    print("same-bank saturated equal-clock TPA upper bound:", float(tpa_bound))
    print("NOT measured: routed electrical closure, tile clock, or workload throughput")

if __name__ == "__main__":
    audit()
