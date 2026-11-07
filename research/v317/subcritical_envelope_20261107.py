#!/usr/bin/env python3
"""V317 preregistered subcritical arrival envelope, exact arithmetic.

This is a necessary capacity audit, NOT proof of queue stability or a
GPU throughput result. Run: python3 research/v317/subcritical_envelope_20261107.py
No random draws, dependencies, or post-hoc workload selection.
"""
from fractions import Fraction as F

BASE_ARRIVALS = F(51, 25)  # 2.04 requests/cycle from prior generator
PORTS_PER_BANK = 2
BANKS = 3
READS_PER_REQUEST = 2

def bank_demands(scale, hot_fraction):
    """Hot-bank demand from prior generator's distributional definition."""
    lam = BASE_ARRIVALS * scale
    hot = lam * F(2, 3) * (1 + 2 * hot_fraction)
    cold = (2 * lam - hot) / 2
    assert hot + 2 * cold == 2 * lam
    return hot, cold, cold

def necessary_capacity(scale, hot_fraction):
    d = bank_demands(scale, hot_fraction)
    return max(d) < PORTS_PER_BANK and sum(d) < BANKS * PORTS_PER_BANK

def critical_scale(h):
    # Strict inequality required for slack, not merely <= capacity.
    return min(F(1), F(2, 1) / (F(34, 25) * (1 + 2 * h)))

# Frozen candidate distribution regimes; do not choose based on measured wins.
# 1/2 baseline arrivals = 1.02 requests/cycle, with bank slack for all three.
# 3/4 baseline arrivals = 1.53 requests/cycle, severe skew necessarily overloaded.
REGIMES = (
    ("uniform-subcritical", F(1, 2), F(0)),
    ("moderate-subcritical", F(1, 2), F(3, 10)),
    ("severe-subcritical", F(1, 2), F(7, 10)),
    ("moderate-overload-control", F(1), F(3, 10)),
    ("severe-overload-control", F(3, 4), F(7, 10)),
)

def main():
    assert critical_scale(F(3, 10)) == F(125, 136)
    assert necessary_capacity(F(1, 2), F(7, 10))
    assert not necessary_capacity(F(1), F(3, 10))
    assert not necessary_capacity(F(3, 4), F(7, 10))
    print("regime,arrival_scale,hot_fraction,hot_reads_per_cycle,headroom_reads_per_cycle,necessary_subcritical")
    for name, scale, h in REGIMES:
        d = bank_demands(scale, h)
        print(f"{name},{float(scale):.6f},{float(h):.6f},{float(d[0]):.6f},{float(2-d[0]):.6f},{necessary_capacity(scale,h)}")
    print("WARNING: necessary bank slack does not prove stability; scheduling, queue order, and service coupling remain untested.")
    print("FROZEN TEST: paired arrival streams; FIFO, rotating FIFO, minimum contention, weighted contention;")
    print("20k warmup + 100k measured cycles, >=10 seeds, finite buffers 16/64/256,")
    print("report completions, per-bank backlog drift, p50/p99 wait, drops, starvation;")
    print("freeze seeds before results; verify independent service checker; no RTL claim.")

if __name__ == "__main__":
    main()
