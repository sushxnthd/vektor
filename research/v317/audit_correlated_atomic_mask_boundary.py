#!/usr/bin/env python3
"""Exact two-bank atomic co-issue law with correlated requests.

Each request uses bank mask 1, 2, or 3 (both). Two single-port banks,
two output slots, one-cycle service, no queues. Joint distribution is
required: marginal atomic fraction alone is not sufficient.
"""
from fractions import Fraction
from itertools import product

MASKS = (1, 2, 3)

def service(x, y):
    return 2 if (x & y) == 0 else 1

def expected_service(joint):
    assert set(joint).issubset(set(product(MASKS, repeat=2)))
    assert all(isinstance(p, Fraction) and p >= 0 for p in joint.values())
    assert sum(joint.values(), Fraction()) == 1
    return sum((p * service(*pair) for pair, p in joint.items()), Fraction())

def independent(atomic):
    singleton = (1 - atomic) / 2
    marg = {1: singleton, 2: singleton, 3: atomic}
    return {(x, y): marg[x] * marg[y] for x, y in product(MASKS, repeat=2)}

def law(atomic, opposite_singleton_covariance=Fraction()):
    # Covariance defined relative to the independent opposite-singleton
    # event probability, NOT covariance of the binary atomic indicators.
    return 1 + (1 - atomic)**2 / 2 + opposite_singleton_covariance

def main():
    for numerator in range(11):
        a = Fraction(numerator, 10)
        joint = independent(a)
        assert expected_service(joint) == law(a)
    # Identical per-request marginals: each request independently appears
    # to use bank 1 or bank 2 with probability 1/2, never both.
    # But the pairing correlation changes service from 1 to 2.
    aligned = {(1, 1): Fraction(1, 2), (2, 2): Fraction(1, 2)}
    opposed = {(1, 2): Fraction(1, 2), (2, 1): Fraction(1, 2)}
    independent_case = independent(Fraction())
    assert expected_service(aligned) == 1
    assert expected_service(independent_case) == Fraction(3, 2)
    assert expected_service(opposed) == 2
    for joint in (aligned, independent_case, opposed):
        a = sum((p for (x, y), p in joint.items() if x == 3), Fraction())
        assert a == 0
        covariance = sum((p for (x, y), p in joint.items() if (x, y) in ((1, 2), (2, 1))), Fraction()) - (1-a)**2 / 2
        assert expected_service(joint) == law(a, covariance)
    # Any purported universal law of the marginal atomic fraction alone
    # is falsified by the two endpoint couplings above.
    print("PASS: independent law 11 exact points; correlated counterexamples 1, 1.5, 2")
    print("Scope: two masks, one-cycle zero-queue model; no RTL/physical/GPU evidence")

if __name__ == "__main__":
    main()
