#!/usr/bin/env python3
"""Independent issue-width falsifier for V317; synthetic, NOT physical evidence.

A comparator with the same RF ports but a *different* issue width is not an
equal-resource comparator. The previously used optimal-pairing baseline
implicitly assumes dual-issue hardware. Report both service bounds, and
refuse to treat the dual-issue comparator as physically established.
"""
from fractions import Fraction
from functools import lru_cache

AREA_COMPACT = Fraction("21314.6")
AREA_PAIR = Fraction("21324.7")
PORTS = (2, 2)

def legal_pair(a, b):
    return (a[2] & b[2]) == 0 and all(a[k] + b[k] <= PORTS[k] for k in range(2))

def exact_cycles(requests, issue_width):
    assert issue_width in (1, 2)
    n = len(requests)
    @lru_cache(None)
    def solve(mask):
        if not mask: return 0
        i = (mask & -mask).bit_length() - 1
        rest = mask ^ (1 << i)
        best = 1 + solve(rest)
        if issue_width == 2:
            for j in range(i + 1, n):
                if rest & (1 << j) and legal_pair(requests[i], requests[j]):
                    best = min(best, 1 + solve(rest ^ (1 << j)))
        return best
    return solve((1 << n) - 1)

def score(base_cycles, pair_cycles, clock_ratio=Fraction(1)):
    return Fraction(base_cycles, pair_cycles) * AREA_COMPACT / AREA_PAIR / clock_ratio

def audit():
    separate = ((2,0,1),(0,2,2))*4
    saturated = ((2,0,1),(2,0,2))*4
    for name, trace in (("separate-bank",separate),("saturated-bank",saturated)):
        single = exact_cycles(trace,1)
        dual = exact_cycles(trace,2)
        assert single == len(trace)
        assert dual >= (len(trace)+1)//2
        ideal_gain = score(single,dual)
        matched_dual_gain = score(dual,dual)
        assert matched_dual_gain < 1
        print(name, "single_issue",single,"dual_issue",dual,
              "ideal_vs_single",float(ideal_gain),
              "vs_dual_issue_baseline",float(matched_dual_gain))
    assert exact_cycles(separate,2) == 4
    assert exact_cycles(saturated,2) == 8
    assert score(8,4) > 1
    assert score(8,8) < 1
    print("PASS: issue width changes the comparison; port matching alone is insufficient")
    print("PHYSICAL GATE: prove baseline issue width, area, RF ports, clock, wire load, and power;")
    print("do not claim equal-resource optimal pairing until dual-issue baseline is implemented.")

if __name__ == "__main__":
    audit()
