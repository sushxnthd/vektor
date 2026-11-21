#!/usr/bin/env python3
"""Independent exact necessary clock-frequency boundary for V317 bank-service gains.

This is a falsification upper bound, NOT a physical timing or GPU throughput claim.
Four simultaneously ready requests, each two read operands, two ports per bank.
The comparator is fixed-order maximal feasible greedy. The challenger is an
UNIMPLEMENTABLE maximum-cardinality oracle, therefore deliberately optimistic.
"""
from collections import Counter
from fractions import Fraction
from itertools import product
import json

def legal(req, subset, banks):
    used = [0] * banks
    for i, (a, b) in enumerate(req):
        if subset & (1 << i):
            used[a] += 1
            used[b] += 1
    return all(x <= 2 for x in used)

def service(req, banks):
    greedy = 0
    for i in range(4):
        trial = greedy | (1 << i)
        if legal(req, trial, banks):
            greedy = trial
    optimum = max(mask.bit_count() for mask in range(16)
                  if legal(req, mask, banks))
    return greedy.bit_count(), optimum

def enumerate_regime(banks, hot_numerator, hot_denominator):
    # P(bank=0)=h; remaining banks equiprobable. Exact rational weights.
    assert 2 <= banks <= 3
    h = Fraction(hot_numerator, hot_denominator)
    assert 0 <= h <= 1
    probabilities = [h] + [(1-h)/(banks-1)]*(banks-1)
    mean_g = mean_o = event = Fraction(0)
    count = 0
    for operands in product(range(banks), repeat=8):
        weight = Fraction(1)
        for b in operands:
            weight *= probabilities[b]
        req = list(zip(operands[::2], operands[1::2]))
        g, o = service(req, banks)
        assert o >= g
        mean_g += weight*g
        mean_o += weight*o
        if o > g:
            event += weight
        count += 1
    assert mean_g > 0
    ratio = mean_o/mean_g
    return dict(banks=banks, hot_probability=str(h),
                enumerated_assignments=count,
                expected_greedy=str(mean_g), expected_oracle=str(mean_o),
                improvement_probability=str(event),
                optimistic_service_ratio=str(ratio),
                maximum_clock_period_inflation=str(ratio),
                maximum_frequency_loss_fraction=str(1-1/ratio))

def run():
    regimes = [enumerate_regime(b,h,d) for b,h,d in
               [(2,1,2),(2,3,4),(2,9,10),
                (3,1,3),(3,2,3),(3,9,10)]]
    # If oracle service is R times greedy, throughput cannot improve when
    # T_new/T_old >= R, even assuming full demand and zero extra control cost.
    return dict(evidence_tier="exact synthetic optimistic necessary bound",
                assumptions="four always-ready requests, 2 operands, 2 ports per bank, independent bank draws, saturated service, no area/power/occupancy penalty",
                clock_period_no_win_rule="T_challenger/T_greedy >= E[oracle_grants]/E[greedy_grants]",
                caveat="physical, queue, traffic, occupancy and control costs can only reduce realizable benefit relative to this oracle under these assumptions",
                regimes=regimes)

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
