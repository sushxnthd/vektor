#!/usr/bin/env python3
"""V317 prospective matching-baseline falsifier; analytical only, not routed silicon.

Unlike ordered-adjacent pairing, this comparator grants BOTH candidates the
same independent ready set and identical bank-port limits. A purported V317
benefit must survive this stronger resource-matched scheduling control.
"""
from functools import lru_cache
from itertools import product
from fractions import Fraction

A0 = Fraction("21314.6")
A1 = Fraction("21324.7")
PORTS = 2
# Request = bank-0 reads, bank-1 reads, active lane mask.
REQUESTS = tuple(product((0, 1, 2), (0, 1, 2), (1, 2, 3)))

def compatible(a, b):
    return not (a[2] & b[2]) and all(a[i] + b[i] <= PORTS for i in (0, 1))

def maximum_pairing_cycles(trace):
    """Exact subset DP, no greedy pairing assumption."""
    n = len(trace)
    @lru_cache(None)
    def solve(bits):
        if not bits:
            return 0
        i = (bits & -bits).bit_length() - 1
        rest = bits ^ (1 << i)
        best = 1 + solve(rest)
        for j in range(i + 1, n):
            if (rest >> j) & 1 and compatible(trace[i], trace[j]):
                best = min(best, 1 + solve(rest ^ (1 << j)))
        return best
    return solve((1 << n) - 1)

def upper_bound(candidate_cycles, baseline_cycles, clock_ratio=Fraction(1),
                control_cycles=0, extra_area=Fraction(0)):
    """Throughput/area ratio; clock_ratio = candidate period / baseline period."""
    assert candidate_cycles > 0 and baseline_cycles > 0
    assert clock_ratio > 0 and extra_area >= 0 and control_cycles >= 0
    return Fraction(baseline_cycles, candidate_cycles + control_cycles) * A0 / (A1 + extra_area) / clock_ratio

def audit():
    # Frozen distinct prospective regimes, not calibrated to silicon.
    win_vs_ordered_only = ((2,0,1), (2,0,1), (0,2,2), (0,2,2))
    no_win_saturated = ((2,0,1), (2,0,2), (2,0,1), (2,0,2))
    for name, trace in (("ordered-control-win", win_vs_ordered_only),
                        ("saturated-no-win", no_win_saturated)):
        best = maximum_pairing_cycles(trace)
        ratio = upper_bound(best, best)
        assert ratio == A0 / A1 < 1
        print(name, "matched cycles", best, "equal-clock throughput/area", float(ratio))
    # Prospective unseen trace family: independent exhaustive samples with
    # varying masks and read demand, no fitted parameters.
    tested = 0
    for trace in product(REQUESTS, repeat=3):
        best = maximum_pairing_cycles(trace)
        assert 2 <= best <= 3
        assert upper_bound(best, best) < 1
        tested += 1
    assert tested == len(REQUESTS)**3 == 19683
    # To win with equal matching service, candidate must clock faster than
    # the strict area ratio; any overhead tightens the boundary.
    clock_break_even = A0 / A1
    assert upper_bound(2, 2, clock_ratio=clock_break_even) == 1
    assert upper_bound(2, 2, clock_ratio=1) < 1
    assert upper_bound(2, 2, clock_ratio=clock_break_even, control_cycles=1) < 1
    print("unseen three-request traces", tested, "clock break-even", float(clock_break_even))
    print("PASS: no service-only win against same-port optimal matching comparator")
    print("LIMIT: no physical reordering engine, routed timing, power, or measured workload IPC")

if __name__ == "__main__":
    audit()
