#!/usr/bin/env python3
"""Rounding-robust necessary clock/occupancy sensitivity; NOT GPU IPC.

Inputs are previously published six-decimal oracle/greedy instantaneous
service ratios, not newly measured hardware or finite-buffer throughput.
The product bound assumes proportional service, fixed workload distribution
and no extra stalls. A bandwidth ceiling below 1.02 independently kills
all >=2% claims. Interval +/- 0.0000005 accounts for six-place rounding.
"""
from fractions import Fraction

RATIOS = {
    "uniform16": "1.001025",
    "uniform4": "1.046155",
    "hot50": "1.072037",
    "hot65": "1.106717",
    "hot75": "1.119826",
    "hot875": "1.080401",
}
TARGET = Fraction(51, 50)
EPS = Fraction(1, 2000000)

def necessary_product_interval(six_digit_ratio):
    r = Fraction(six_digit_ratio)
    assert r > EPS
    return TARGET / (r + EPS), TARGET / (r - EPS)

def can_reach_with_known_ratios(name, clock, occupancy, bandwidth):
    low, high = necessary_product_interval(RATIOS[name])
    p = Fraction(clock) * Fraction(occupancy)
    b = Fraction(bandwidth)
    if b < TARGET or p < low:
        return "NO_WIN_CERTIFICATE"
    if p >= high:
        return "NOT_FALSIFIED_ONLY"
    return "ROUNDING_AMBIGUOUS"

def test():
    assert can_reach_with_known_ratios("uniform16", 1, 1, 2) == "NO_WIN_CERTIFICATE"
    assert can_reach_with_known_ratios("hot65", 1, Fraction(95,100), 2) == "NOT_FALSIFIED_ONLY"
    assert can_reach_with_known_ratios("hot65", 2, 1, 1) == "NO_WIN_CERTIFICATE"
    assert can_reach_with_known_ratios("uniform4", 1, Fraction(95,100), 2) == "NO_WIN_CERTIFICATE"
    for v in RATIOS.values():
        a,b = necessary_product_interval(v)
        assert 0 < a < b

if __name__ == "__main__":
    test()
    for name, ratio in RATIOS.items():
        lo, hi = necessary_product_interval(ratio)
        print(f"{name} service={ratio} clock_x_occupancy_needed=[{float(lo):.8f},{float(hi):.8f}] clock_needed_at_95pct_occupancy=[{float(lo/Fraction(95,100)):.8f},{float(hi/Fraction(95,100)):.8f}]")
