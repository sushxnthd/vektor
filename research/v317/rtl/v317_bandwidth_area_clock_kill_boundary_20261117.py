#!/usr/bin/env python3
"""Prospective bandwidth/physical-overhead kill boundary for a strict-FIFO pair scheduler.
Synthetic queue service only; not V296 RTL, GPU IPC, or routed timing evidence.
No new architecture mechanism is proposed.
"""
from fractions import Fraction as Q
from itertools import product

# Freeze before examining results: alternating two-bank stream is the
# predicted-win regime; single-bank stream is predicted-no-win.
FROZEN = {"win": tuple(i % 2 for i in range(256)),
          "no_win": (0,) * 256}
AREA_RATIO = Q(101, 100)
PERIOD_RATIO = Q(101, 100)

def service_cycles(stream, pair_cap=2):
    assert pair_cap in (1, 2)
    i = cycles = 0
    while i < len(stream):
        cycles += 1
        dual = (pair_cap == 2 and i + 1 < len(stream)
                and stream[i] != stream[i + 1])
        i += 2 if dual else 1
    return cycles

def efficiency_ratio(stream, cap, area=AREA_RATIO, period=PERIOD_RATIO):
    # Same number of useful requests; matched single-issue reference has
    # normalized area and clock period 1. The pair design incurs penalties.
    baseline = len(stream)
    candidate = service_cycles(stream, cap)
    return Q(baseline, candidate) / (area * period)

def exact_markov_expected(n, q, cap):
    # Independent enumeration is intentionally distinct from the queue DP.
    out = Q(0)
    for seq in product((0, 1), repeat=n):
        p = Q(1, 2)
        for a, b in zip(seq, seq[1:]):
            p *= q if a == b else 1 - q
        out += p * service_cycles(seq, cap)
    return out

def dp_expected(n, q, cap):
    if cap == 1:
        return Q(n)
    e = [Q(0)] * (n + 1)
    for k in range(1, n + 1):
        e[k] = Q(1) if k == 1 else 1 + q * e[k-1] + (1-q) * e[k-2]
    return e[n]

def main():
    for q in (Q(0), Q(1,4), Q(1,2), Q(3,4), Q(1)):
        for cap in (1, 2):
            for n in range(1, 9):
                assert exact_markov_expected(n, q, cap) == dp_expected(n, q, cap)
    assert service_cycles(FROZEN["win"], 2) == 128
    assert service_cycles(FROZEN["no_win"], 2) == 256
    assert all(service_cycles(s, 1) == len(s) for s in FROZEN.values())
    assert efficiency_ratio(FROZEN["win"], 2) > 1
    assert efficiency_ratio(FROZEN["no_win"], 2) < 1
    for label, stream in FROZEN.items():
        for cap in (1, 2):
            ratio = efficiency_ratio(stream, cap)
            print(f"{label} cap={cap} cycles={service_cycles(stream,cap)} "
                  f"throughput_per_area_ratio={float(ratio):.8f}")
    # Exact necessary-and-sufficient boundary for THIS synthetic model:
    # cycle reduction must exceed 1 - 1/(area_ratio * period_ratio).
    threshold = 1 - 1 / (AREA_RATIO * PERIOD_RATIO)
    assert threshold == Q(201, 10201)
    print(f"minimum_cycle_reduction={float(threshold):.8%}")
    print("PASS 80 exhaustive Markov/cap comparisons; synthetic only")

if __name__ == "__main__":
    main()
