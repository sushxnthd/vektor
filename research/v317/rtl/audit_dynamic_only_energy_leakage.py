#!/usr/bin/env python3
"""Independent leakage sensitivity of V317's dynamic-only energy gate.

The existing matched_physical_gate.py computes energy/service from dynamic
power alone. This checker derives the exact common leakage threshold at which
its dynamic-energy decision reverses. Inputs are *hypothetical*, not PPA data.
"""
from fractions import Fraction as F

def energy_ratio(service_a, service_b, dynamic_a, dynamic_b, leakage_a, leakage_b):
    assert min(service_a, service_b) > 0
    assert min(dynamic_a, dynamic_b, leakage_a, leakage_b) >= 0
    return (dynamic_a + leakage_a) * service_b / ((dynamic_b + leakage_b) * service_a)

def common_leakage_crossover(sa, sb, pa, pb):
    """Solve (pa+L)/sa == (pb+L)/sb. None if equal service rates."""
    if sa == sb:
        return None
    return (pb*sa - pa*sb)/(sb-sa)

def audit():
    # Case A: candidate wins dynamic-only at a faster clock and equal area,
    # but loses once a common positive leakage component is accounted for.
    sa, sb = F(11,10), F(1)
    pa, pb = F(10), F(10)
    # With higher service and equal dynamic power, common leakage cannot
    # reverse the win. This is a negative control.
    for L in (F(0), F(10), F(1000)):
        assert energy_ratio(sa,sb,pa,pb,L,L) < 1

    # Case B: candidate is slower but consumes sufficiently less dynamic power.
    # Dynamic-only gate passes energy (0.8/0.9 < 1), while leakage eventually
    # favors the higher-throughput baseline.
    sa, sb = F(9,10), F(1)
    pa, pb = F(8), F(10)
    crossing = common_leakage_crossover(sa,sb,pa,pb)
    assert crossing == F(10)
    assert energy_ratio(sa,sb,pa,pb,F(0),F(0)) == F(8,9)
    assert energy_ratio(sa,sb,pa,pb,F(10),F(10)) == 1
    assert energy_ratio(sa,sb,pa,pb,F(11),F(11)) > 1

    # Case C: even a faster candidate can lose once *differential* leakage
    # is included. No general energy claim follows from dynamic-only power.
    sa, sb, pa, pb = F(11,10), F(1), F(10), F(10)
    assert energy_ratio(sa,sb,pa,pb,F(0),F(0)) < 1
    assert energy_ratio(sa,sb,pa,pb,F(3),F(0)) > 1
    print("PASS: exact leakage crossover and negative controls (synthetic only)")
    print("Case B: common leakage crossover = 10 arbitrary power units")
    print("Interpretation: dynamic-only energy gate cannot certify total energy.")

if __name__ == "__main__":
    audit()
