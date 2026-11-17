#!/usr/bin/env python3
"""V296 decoded mapped-area / clock / service hard boundary (NOT routed evidence).

Area source: V296 Nangate45 mapped areas, 2026-10-26. All clock penalties
and service improvements below are hypothetical prospective sweeps.
A throughput/area win requires service improvement > (A_pair/A_serial)*(T_pair/T_serial).
"""
from fractions import Fraction as F

A_PAIR = F("10426.402")
A_SERIAL = F("10143.112")

def threshold(clock_ratio=F(1)):
    clock_ratio = F(clock_ratio)
    if clock_ratio <= 0: raise ValueError("clock ratio must be positive")
    return A_PAIR * clock_ratio / A_SERIAL

def evaluate(service_ratio, clock_ratio):
    service_ratio = F(service_ratio)
    if service_ratio <= 0: raise ValueError("service ratio must be positive")
    return service_ratio / threshold(clock_ratio)

def test():
    assert threshold() > 1
    assert evaluate(threshold(),1) == 1
    assert evaluate(F(1),F(1)) < 1
    assert evaluate(F(11,10),F(1)) > 1
    assert evaluate(F(1),F(101,100)) < evaluate(F(1),F(1))
    assert threshold(F(99,100)) < threshold()
    for c in (F(98,100),F(1),F(101,100),F(105,100)):
        assert evaluate(threshold(c),c) == 1

if __name__ == "__main__":
    test()
    print("PASS exact-rational V296 mapped-area sensitivity; no physical signoff")
    print("decoded area ratio:", float(A_PAIR/A_SERIAL))
    for label, clock in (("2% clock improvement",F(98,100)),
                         ("equal clock",F(1)),
                         ("1% clock penalty",F(101,100)),
                         ("5% clock penalty",F(105,100))):
        print(label, "minimum service gain % (strictly greater):",
              round(100*float(threshold(clock)-1),6))
    print("No-win frozen control: equal service, equal clock.")
    print("Conditional-win frozen regime: 10% service gain, equal clock; unmeasured.")
    print("Mapped area alone cannot establish a GPU result.")
