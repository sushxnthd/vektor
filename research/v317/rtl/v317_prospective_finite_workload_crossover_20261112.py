#!/usr/bin/env python3
"""Prospective finite-workload clock/area crossover; analytical falsifier only.

The comparison is valid only for identical completed work, workload ordering,
resource budget, technology corner, and independently legal physical routes.
No physical measurements are supplied here.
"""
from fractions import Fraction as F
from itertools import product

def throughput_area_ratio(base_cycles, cand_cycles, base_period, cand_period,
                          base_area, cand_area):
    """Candidate/baseline throughput-per-area for equal completed work."""
    vals = (base_cycles, cand_cycles, base_period, cand_period, base_area, cand_area)
    if any(F(v) <= 0 for v in vals):
        raise ValueError("positive cycles, periods and areas required")
    return (F(base_cycles)*F(base_period)*F(base_area) /
            (F(cand_cycles)*F(cand_period)*F(cand_area)))

def maximum_candidate_period(base_cycles, cand_cycles, base_period,
                             base_area, cand_area):
    """Strictly below this period is required for throughput/area win."""
    return (F(base_cycles)*F(base_period)*F(base_area) /
            (F(cand_cycles)*F(cand_area)))

def minimum_cycle_reduction(base_period, cand_period, base_area, cand_area):
    """Fraction of baseline cycles that must be saved for strict win."""
    return 1 - F(base_period)*F(base_area)/(F(cand_period)*F(cand_area))

def independently_cross_multiply(bc, cc, bp, cp, ba, ca):
    # Independent integer cross-product test, not a call to ratio().
    n = F(bc)*F(bp)*F(ba)
    d = F(cc)*F(cp)*F(ca)
    return (n > d) - (n < d)

def self_test():
    checks = 0
    for bc, cc, cp, ca in product((64, 100, 1024),
                                  (48, 64, 96, 100, 1100),
                                  (F(99,100), F(1), F(101,100), F(105,100)),
                                  (F(1), F(1001,1000), F(105,100))):
        bp, ba = F(1), F(1)
        r = throughput_area_ratio(bc,cc,bp,cp,ba,ca)
        assert ((r > 1) - (r < 1)) == independently_cross_multiply(
            bc,cc,bp,cp,ba,ca)
        boundary = maximum_candidate_period(bc,cc,bp,ba,ca)
        assert throughput_area_ratio(bc,cc,bp,boundary,ba,ca) == 1
        assert throughput_area_ratio(bc,cc,bp,boundary*F(999,1000),ba,ca) > 1
        assert throughput_area_ratio(bc,cc,bp,boundary*F(1001,1000),ba,ca) < 1
        checks += 1
    # Prospective synthetic regimes: no outcome-derived parameter fitting.
    regimes = {
      "predicted_win_service_bound": (100, 80, F(1), F(101,100), F(1), F(1001,1000)),
      "predicted_no_win_clock_area": (100, 99, F(1), F(105,100), F(1), F(102,100)),
      "predicted_no_win_occupancy": (100, 108, F(1), F(99,100), F(1), F(1)),
    }
    expected = (1, -1, -1)
    for args, sign in zip(regimes.values(), expected):
        ratio = throughput_area_ratio(*args)
        assert ((ratio > 1) - (ratio < 1)) == sign
    # Exact matched-area example from historical *electrically illegal* routes:
    # pairwise=21324.7, compact greedy=21314.6 um^2.
    period = maximum_candidate_period(100,100,F(3),F("21314.6"),F("21324.7"))
    assert F("2.998") < period < F("2.999")
    return checks, regimes, period

if __name__ == "__main__":
    count, regimes, period = self_test()
    print("exact cross-product and boundary comparisons:", count)
    for name, args in regimes.items():
        print(name, "hypothetical throughput/area ratio:", throughput_area_ratio(*args))
    print("historical illegal-route period crossover (ns):", period, float(period))
    print("NOT PHYSICAL SIGNOFF: no SPEF, DRC, legal timing, or measured workload.")
