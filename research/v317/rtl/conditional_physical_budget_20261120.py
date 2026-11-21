#!/usr/bin/env python3
"""Exact necessary physical-budget falsifier for the V317 post-hoc hot=3 stratum.

Not an RTL result, throughput prediction, or prospective validation.
The 816/36246 service increment is a zero-cost, oldest-protected oracle upper bound.
"""
from fractions import Fraction

SERVICE = Fraction(36246 + 816, 36246)
TARGET = Fraction(102, 100)
MAX_CLOCK_OCCUPANCY_LOSS = 1 - TARGET / SERVICE

def attainable(service, clock, occupancy, bandwidth):
    """Optimistic upper bound: even assumes service headroom survives finite buffers."""
    return min(service * clock * occupancy, bandwidth)

def audit():
    assert SERVICE == Fraction(6177, 6041)
    assert SERVICE > TARGET
    assert MAX_CLOCK_OCCUPANCY_LOSS > 0
    assert attainable(SERVICE, 1, 1, 1) == 1
    assert attainable(SERVICE, 1, 1, TARGET) == TARGET
    assert attainable(SERVICE, TARGET / SERVICE, 1, 2) == TARGET
    assert attainable(SERVICE, Fraction(997,1000), 1, 2) < TARGET
    assert attainable(SERVICE, 1, Fraction(997,1000), 2) < TARGET
    assert attainable(SERVICE, 1, 1, Fraction(101,100)) < TARGET
    print("service oracle upper bound:", SERVICE, float(SERVICE))
    print("minimum clock*occupancy retention:", TARGET/SERVICE, float(TARGET/SERVICE))
    print("maximum joint clock*occupancy loss:", MAX_CLOCK_OCCUPANCY_LOSS, float(MAX_CLOCK_OCCUPANCY_LOSS))
    print("necessary bandwidth retention:", TARGET)
    print("PASS: exact necessary-only physical budget; not a sufficiency claim")

if __name__ == "__main__":
    audit()
