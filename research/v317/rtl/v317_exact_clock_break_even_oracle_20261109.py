#!/usr/bin/env python3
"""Exact break-even clock/area boundary for the frozen V317 identical-demand trace.
Analytical upper bound only: NOT routed timing, power, or measured GPU IPC.
No imports from the candidate implementation; independent oracle for its arithmetic.
"""
from fractions import Fraction
from itertools import product

AREA_COMPACT = Fraction("21314.6")
AREA_PAIR = Fraction("21324.7")
PORTS = 2

def admissible(a, b):
    # (bank0_reads, bank1_reads, mask, compatible)
    return a[3] and b[3] and not (a[2] & b[2]) and all(
        a[k] + b[k] <= PORTS for k in (0, 1))

def schedule(trace):
    i = cycles = fused = 0
    while i < len(trace):
        pair = i + 1 < len(trace) and admissible(trace[i], trace[i + 1])
        i += 2 if pair else 1
        cycles += 1
        fused += int(pair)
    return cycles, fused

def boundary(trace, shared_area=Fraction(0)):
    """Maximum pair/compact clock period ratio that still wins throughput/area."""
    assert trace and shared_area >= 0
    cycles, pairs = schedule(trace)
    return (Fraction(len(trace), cycles)
            * (AREA_COMPACT + shared_area) / (AREA_PAIR + shared_area)), pairs

def exact_optimal_adjacent(trace):
    """Independent exhaustive search of all legal adjacent pair partitions."""
    def visit(i):
        if i == len(trace):
            return 0
        best = 1 + visit(i + 1)
        if i + 1 < len(trace) and admissible(trace[i], trace[i + 1]):
            best = min(best, 1 + visit(i + 2))
        return best
    return visit(0)

def audit():
    demands = [(2, 0), (0, 2), (1, 1), (2, 2)]
    alphabet = [(x, y, mask, True) for (x, y), mask in product(demands, (1, 2))]
    # Exhaustively verify greedy issue-cycle optimum for short ordered queues.
    for n in range(1, 6):
        for trace in product(alphabet, repeat=n):
            assert schedule(trace)[0] == exact_optimal_adjacent(trace)
    a, b = (2, 0, 1, True), (0, 2, 2, True)
    c = (2, 0, 2, True)
    win = [a, b] * 100
    no_win = [a, c] * 100
    for name, trace in (("frozen_separate_bank", win), ("frozen_saturated_bank", no_win)):
        threshold, pairs = boundary(trace)
        assert (threshold > 1) == (name == "frozen_separate_bank")
        print(name, "pairs", pairs, "max_legal_period_ratio", float(threshold),
              "exact", str(threshold))
    # An area-normalized win at fixed throughput requires a *faster* pair clock.
    threshold, _ = boundary(no_win)
    assert threshold < 1
    # Even the ideal pair win vanishes if its period doubles.
    assert boundary(win)[0] < 2
    for extra_area in (0, 10000, 100000):
        assert boundary(no_win, Fraction(extra_area))[0] <= 1
    print("PASS exhaustive ordered-queue oracle and frozen break-even boundaries")
    print("NOTE: no electrical legality, load/wire delay, occupancy, or GPU IPC proven")

if __name__ == "__main__":
    audit()
