#!/usr/bin/env python3
"""Deterministic queue-level falsification of batch-local oracle speedups.

Toy service system only: no GPU IPC, no hardware implementation.
"""
from fractions import Fraction


def simulate(arrivals, capacity, cycles):
    backlog = 0
    completed = 0
    peak = 0
    for t in range(cycles):
        backlog += arrivals[t]
        peak = max(peak, backlog)
        done = min(backlog, capacity)
        completed += done
        backlog -= done
    return completed, backlog, peak


def test():
    cycles = 1000
    low = [1] * cycles
    high = [2] * cycles
    for label, seq in (("low", low), ("high", high)):
        base = simulate(seq, 1, cycles)
        oracle = simulate(seq, 2, cycles)
        print(label, "baseline", base, "oracle", oracle,
              "throughput_ratio", Fraction(oracle[0], base[0]))
        if label == "low":
            assert base[0] == oracle[0] == cycles
        else:
            assert base[0] == cycles and oracle[0] == 2 * cycles
    # Finite burst: local service advantage exists, but total completed
    # work converges to arrivals when the measurement window drains.
    burst = [2] * 100 + [0] * 900
    b = simulate(burst, 1, cycles)
    o = simulate(burst, 2, cycles)
    assert b[0] == o[0] == 200
    print("burst_then_idle", b, o, "throughput_ratio", Fraction(o[0], b[0]))
    for seq in (low, high, burst):
        for cap in (1, 2):
            done, backlog, _ = simulate(seq, cap, cycles)
            assert done + backlog == sum(seq)
    print("PASS: demand-limited and burst-drained workloads erase service headroom")


if __name__ == "__main__":
    test()
