#!/usr/bin/env python3
"""Predeclared distribution-transfer test for V317's bank-demand selector.

The model is an instantaneous 4-request, 3-bank, 2-read-port admission oracle,
NOT a throughput, routed RTL, energy or timing result. Frozen distributions
and predictions below must not be edited after observing the transfer.
Run: python3 research/v317/rtl/frozen_selector_distribution_transfer_20261107.py
"""
from collections import Counter
from itertools import product
from fractions import Fraction

# Frozen before evaluation: each operand independently samples bank 0/1/2.
# The skewed holdout is a *challenge*, not a guaranteed predicted win.
REGIMES = {
    "uniform_predicted_no_win": (Fraction(1,3),)*3,
    "moderate_skew_challenge": (Fraction(1,2), Fraction(1,3), Fraction(1,6)),
    "severe_skew_challenge": (Fraction(3,4), Fraction(1,8), Fraction(1,8)),
}
# Predictive boundary from prior exhaustive training enumeration:
# weighted > min-contestion ONLY at (max_bank_load=5, same_bank_pairs=3).
# Frozen sign prediction: outside this stratum, no algorithmic advantage.
BOUNDARY = (5,3)

def admit(req, order):
    used = Counter()
    grants = 0
    for i in order:
        demand = Counter(req[i])
        if all(used[b] + n <= 2 for b,n in demand.items()):
            used.update(demand)
            grants += 1
    return grants

def evaluate(p):
    total = Fraction(0)
    weighted_sum = Fraction(0)
    simple_sum = Fraction(0)
    boundary_mass = Fraction(0)
    boundary_delta = Fraction(0)
    outside_delta = Fraction(0)
    counterexamples = 0
    for flat in product(range(3), repeat=8):
        prob = Fraction(1)
        for b in flat:
            prob *= p[b]
        req = tuple((flat[2*i],flat[2*i+1]) for i in range(4))
        load = Counter(flat)
        weighted_order = sorted(range(4), key=lambda i:
                                (sum(load[b] for b in req[i]),i))
        simple_order = sorted(range(4), key=lambda i:
                              (min(load[b] for b in req[i]),i))
        a,b = admit(req,weighted_order), admit(req,simple_order)
        boundary = (max(load.values()),sum(x==y for x,y in req)) == BOUNDARY
        total += prob
        weighted_sum += prob*a
        simple_sum += prob*b
        if boundary:
            boundary_mass += prob
            boundary_delta += prob*(a-b)
        else:
            outside_delta += prob*(a-b)
        counterexamples += (a < b)
    assert total == 1
    assert outside_delta == 0, "Boundary law falsified on transfer support"
    assert counterexamples == 0
    return dict(weighted=weighted_sum, simple=simple_sum,
                gain=weighted_sum/simple_sum, boundary_mass=boundary_mass,
                boundary_delta=boundary_delta, outside_delta=outside_delta)

def main():
    for name,p in REGIMES.items():
        r=evaluate(p)
        print(name)
        for k,v in r.items():
            print(" ",k,str(v),"~",float(v))
    print("These are exact iid-bank toy-model transfers, not unseen trace validation.")
    print("Reject as physical claim until matched routed RTL and realistic traces exist.")

if __name__=="__main__":
    main()
