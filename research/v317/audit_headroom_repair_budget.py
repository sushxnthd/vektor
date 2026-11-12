#!/usr/bin/env python3
"""Exact-rational conditional throughput-density repair budget for archived routed proxies.
Not signoff; archived frequency is a timing proxy, not measured GPU clock.
"""
from fractions import Fraction as F

def ratio(candidate_area, baseline_area, candidate_freq, baseline_freq,
          candidate_cycles=1, baseline_cycles=1, candidate_occupancy=1,
          baseline_occupancy=1):
    vals = list(map(F, (candidate_area, baseline_area, candidate_freq,
                        baseline_freq, candidate_cycles, baseline_cycles,
                        candidate_occupancy, baseline_occupancy)))
    ap, ac, fp, fc, cp, cc, op, oc = vals
    assert all(x > 0 for x in vals)
    return (fp / fc) * (ac / ap) * (cc / cp) * (op / oc)

def main():
    ac, ap, fc, fp = map(F, ("21389.1", "21533.0", "446.10", "454.59"))
    r = ratio(ap, ac, fp, fc)
    # Repair area added to candidate only, holding baseline constant and clocks unchanged.
    repair_budget = ap * (r - 1)
    # Candidate-only frequency degradation that erases conditional density gain.
    frequency_floor = fc * ap / ac
    assert r > 1
    assert ratio(ap + repair_budget, ac, fp, fc) == 1
    assert ratio(ap, ac, frequency_floor, fc) == 1
    assert ratio(ap + repair_budget + F(1, 1000), ac, fp, fc) < 1
    assert ratio(ap, ac, frequency_floor - F(1, 1000), fc) < 1
    assert ratio(ap, ac, fp, fc, candidate_occupancy=F(9, 10)) < 1
    assert ratio(ap, ac, fp, fc, candidate_cycles=F(11, 10)) < 1
    print("archived proxy ratio, equal cycles/occupancy:", float(r))
    print("candidate-only additional repair area break-even (um^2):", float(repair_budget))
    print("candidate frequency break-even (MHz):", float(frequency_floor))
    print("candidate frequency drop budget (MHz):", float(fp-frequency_floor))
    print("PASS: exact break-even, negative controls, occupancy and cycle sensitivity")
    print("NOT electrical signoff or GPU throughput: both archived routes illegal")
if __name__ == "__main__":
    main()
