#!/usr/bin/env python3
"""Exact adversarial ordering sensitivity for the restricted four-request bank model.

This is a measurement-model falsification, NOT a GPU throughput or RTL result.
"""
from collections import Counter
from fractions import Fraction
from itertools import permutations

REQUESTS = ((0, 0), (0, 0), (0, 1), (0, 1))
PORTS = 2
CLOCK_PENALTY = Fraction(1, 200)

def greedy(order):
    used = [0, 0]
    accepted = 0
    for a, b in order:
        demand = [int(a == k) + int(b == k) for k in range(2)]
        if all(used[k] + demand[k] <= PORTS for k in range(2)):
            used = [used[k] + demand[k] for k in range(2)]
            accepted += 1
    return accepted

def oracle(order):
    best = 0
    for subset in range(1 << len(order)):
        used = [0, 0]
        count = 0
        for i, (a, b) in enumerate(order):
            if subset & (1 << i):
                used[a] += 1
                used[b] += 1
                count += 1
        if max(used) <= PORTS:
            best = max(best, count)
    return best

def main():
    orders = sorted(set(permutations(REQUESTS)))
    counts = Counter(greedy(order) for order in orders)
    assert len(orders) == 6
    assert counts == {1: 3, 2: 3}, counts
    assert all(oracle(order) == 2 for order in orders)
    uniform_mean = Fraction(sum(greedy(o) for o in orders), len(orders))
    assert uniform_mean == Fraction(3, 2)
    # q = probability of selecting a bad-order permutation, distributed
    # uniformly within each of the two service-outcome classes.
    # E[greedy] = q*1 + (1-q)*2 = 2-q.
    # The zero-cost oracle's net ratio is 2 / ((1+d)*(2-q)).
    # Win iff q > 2*d/(1+d).
    q_critical = 2 * CLOCK_PENALTY / (1 + CLOCK_PENALTY)
    assert q_critical == Fraction(2, 201)
    # An observed unordered multiset alone permits q in [0,1],
    # and therefore cannot certify a win at any d>0.
    assert Fraction(2, 1) / ((1+CLOCK_PENALTY)*2) < 1
    assert Fraction(2, 1) / ((1+CLOCK_PENALTY)*1) > 1
    # Distribution-shift bound: |E_P G-E_U G| <=
    # (max G-min G) TV(P,U). Here TV between a class-biased
    # distribution and uniform permutations equals |q-1/2|.
    for q in (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(1)):
        actual = 2-q
        tv = abs(q-Fraction(1,2))
        assert abs(actual-uniform_mean) == tv
    print("PASS: 6 unique orders; greedy service histogram", dict(counts))
    print("Uniform mean greedy", uniform_mean, "oracle", 2)
    print("Critical bad-order mass for d=0.005:", q_critical)
    print("No unconditional win certificate from unordered demand.")
    print("LIMIT: zero-cost oracle and assumed clock penalty; no RTL/physical gain.")

if __name__ == "__main__":
    main()
