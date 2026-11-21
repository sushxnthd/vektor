#!/usr/bin/env python3
"""V317 prospective robust clock/traffic rejection gate (model, NOT silicon evidence).

Inputs are predeclared intervals, not measured values. Candidate must beat the
strongest equal-resource baseline even under unfavorable workload and clock
conditions to earn a robust predicted win. A possible win is not a robust win.
"""
from fractions import Fraction as F
from itertools import product

def speedup(r, f, c):
    assert r >= 1 and 0 <= f <= 1 and c > 0
    return 1 / (c * (1 - f + f / r))

def bound(r_interval, f_interval, c_interval):
    """Monotonic extrema for r>=1, f in [0,1], c>0."""
    rlo, rhi = r_interval
    flo, fhi = f_interval
    clo, chi = c_interval
    assert 1 <= rlo <= rhi and 0 <= flo <= fhi <= 1 and 0 < clo <= chi
    lower = speedup(rlo, flo, chi)
    upper = speedup(rhi, fhi, clo)
    # Independent corner enumeration guards the monotonic argument.
    corners = [speedup(r, f, c) for r, f, c in
               product(r_interval, f_interval, c_interval)]
    assert lower == min(corners) and upper == max(corners)
    return lower, upper

def classify(interval):
    lo, hi = interval
    if hi <= 1: return "REJECT: no possible speedup within bounds"
    if lo > 1: return "ROBUST PREDICTED WIN: still requires physical proof"
    return "INDETERMINATE: only conditional opportunity"

def main():
    # Explicit sensitivity hypotheses; no timing, bandwidth or workload measurement.
    regimes = {
      "uniform16_predicted_no_win": ((F(1), F(1001025,1000000)),
                                      (F(1,10), F(3,10)),
                                      (F(1005,1000), F(102,100))),
      "hotbank_predicted_possible_win": ((F(1), F(1099869,1000000)),
                                         (F(7,10), F(9,10)),
                                         (F(1005,1000), F(103,100))),
    }
    for name, (r, f, c) in regimes.items():
        lo, hi = bound(r, f, c)
        print(f"{name}: [{float(lo):.8f}, {float(hi):.8f}] {classify((lo,hi))}")
    assert classify(bound(*regimes["uniform16_predicted_no_win"])).startswith("REJECT")
    assert classify(bound(*regimes["hotbank_predicted_possible_win"])).startswith("INDETERMINATE")
    # A ceiling with zero bank fraction cannot benefit from service improvements.
    assert speedup(F(10), F(0), F(101,100)) == F(100,101)
    # Exact break-even threshold c*=1/(1-f+f/r).
    r, f = F(11,10), F(4,5)
    threshold = 1 / (1-f+f/r)
    assert speedup(r,f,threshold) == 1
if __name__ == "__main__":
    main()
