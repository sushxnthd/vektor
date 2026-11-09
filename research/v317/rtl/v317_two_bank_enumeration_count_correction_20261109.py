#!/usr/bin/env python3
"""Independent exhaustive audit of two-bank fusion legality and cycle lower bounds.

Finite combinatorial model only. Not a routed timing, energy, or IPC result.
Each warp has a demand vector (bank0,bank1), each in {0,1,2}.
Fusion requires compatible and disjoint masks plus per-bank read conservation.
"""
from itertools import product
from fractions import Fraction

PORTS = 2
AREA_COMPACT = Fraction("21314.6")
AREA_PAIRWISE = Fraction("21324.7")

def enumerate_cases():
    vectors = tuple(product(range(PORTS + 1), repeat=2))
    for a in vectors:
        for b in vectors:
            for compatible in (False, True):
                for disjoint in (False, True):
                    yield a, b, compatible, disjoint

def legal(a, b, compatible, disjoint):
    return compatible and disjoint and all(a[i] + b[i] <= PORTS for i in (0, 1))

def independent_legal(a, b, compatible, disjoint):
    if not compatible or not disjoint:
        return False
    occupancy = [0, 0]
    for warp in (a, b):
        for bank, reads in enumerate(warp):
            for _ in range(reads):
                occupancy[bank] += 1
                if occupancy[bank] > PORTS:
                    return False
    return True

def audit():
    cases = list(enumerate_cases())
    assert len(cases) == 324, "9 demand vectors per warp x 4 Boolean combinations"
    feasible = 0
    for a, b, compatible, disjoint in cases:
        actual = legal(a, b, compatible, disjoint)
        assert actual == independent_legal(a, b, compatible, disjoint)
        feasible += int(actual)
    assert feasible == 36, "per bank 6 admissible ordered pairs, both flags true"
    assert not legal((2, 0), (2, 0), True, True)
    assert legal((2, 0), (0, 2), True, True)
    assert not legal((0, 0), (0, 0), False, True)
    bound = AREA_COMPACT / AREA_PAIRWISE
    assert bound < 1
    print(f"PASS {len(cases)} cases, {feasible} legal, {len(cases)-feasible} illegal")
    print(f"Equal-clock saturated TPA upper bound: {float(bound):.9f}")
    print("Scope: zero-bypass two-port per-bank demand conservation only; no measured timing/IPC.")

if __name__ == "__main__":
    audit()
