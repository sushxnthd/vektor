#!/usr/bin/env python3
"""Independent stronger scheduling baseline for V317 bank-port fusion.

Tests whether an ordered adjacent-pair oracle is a valid upper bound when
independent ready warps can be reordered. This is an analytical counterexample,
not a claim that hardware can reorder arbitrary dependent operations.
"""
from functools import lru_cache
from fractions import Fraction

PORTS = 2
COMPACT_AREA = Fraction("21314.6")
PAIR_AREA = Fraction("21324.7")

def legal(a, b):
    # Each request: (reads_bank0, reads_bank1, active_mask).
    return (a[2] & b[2]) == 0 and all(a[k] + b[k] <= PORTS for k in (0, 1))

def ordered_cycles(requests):
    i = cycles = 0
    while i < len(requests):
        i += 2 if i + 1 < len(requests) and legal(requests[i], requests[i+1]) else 1
        cycles += 1
    return cycles

def optimal_ready_cycles(requests):
    """Independent bitmask dynamic program over all pairings of ready requests."""
    n = len(requests)
    @lru_cache(None)
    def solve(remaining):
        if not remaining:
            return 0
        first = (remaining & -remaining).bit_length() - 1
        rest = remaining & ~(1 << first)
        best = 1 + solve(rest)
        for j in range(first + 1, n):
            if rest & (1 << j) and legal(requests[first], requests[j]):
                best = min(best, 1 + solve(rest & ~(1 << j)))
        return best
    return solve((1 << n) - 1)

def audit():
    # Frozen adversarial queue: the adjacent greedy schedule uses 3 cycles,
    # whereas the ready-set matching baseline uses 2.
    a = (2, 0, 1)
    b = (2, 0, 1)
    c = (0, 2, 2)
    d = (0, 2, 2)
    trace = (a, b, c, d)
    assert ordered_cycles(trace) == 3
    assert optimal_ready_cycles(trace) == 2
    assert legal(a, c) and legal(b, d)
    # Physical area accounting, assuming equal clock and zero reordering cost.
    optimistic_ratio = Fraction(3, 2) * COMPACT_AREA / PAIR_AREA
    assert optimistic_ratio > 1
    # A real reordering engine must beat this clock/area/control-cost boundary;
    # the value is NOT a V317 measured win over an implemented equal-resource
    # reorder-capable compact scheduler.
    print("COUNTEREXAMPLE ordered=3 ready-set=2, optimistic ratio=", float(optimistic_ratio))
    # Strongest alternative matters: if compact can use the same ready-set
    # schedule, V317 has no service advantage and loses on area at equal clock.
    strong_baseline_ratio = COMPACT_AREA / PAIR_AREA
    assert strong_baseline_ratio < 1
    print("MATCHED-SCHEDULER NO-WIN area-normalized ratio=", float(strong_baseline_ratio))
    print("PASS: ordered adjacency is not a global scheduling upper bound")
    print("LIMIT: ready-set model assumes independent, simultaneously available requests")

if __name__ == "__main__":
    audit()
