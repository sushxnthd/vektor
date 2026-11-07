#!/usr/bin/env python3
"""Conditional area-repair crossover for archived relaxed-headroom routes.

This is exact area accounting, NOT a physical closure result. Candidate and
baseline may need different amounts of hold/capacitance repair; the model
does not assume their repair costs are equal.
"""
from decimal import Decimal as D

BASE = D('21389.1')
CAND = D('21533.0')
MATERIAL = D('0.02')

def saving(base_repair, candidate_repair):
    b = BASE + D(str(base_repair))
    c = CAND + D(str(candidate_repair))
    assert b > 0 and c > 0
    return (b-c)/b

def baseline_repair_needed(candidate_repair, target):
    r = D(str(candidate_repair))
    t = D(str(target))
    assert r >= 0 and D(0) <= t < D(1)
    return (CAND+r)/(D(1)-t)-BASE

def main():
    assert saving(0,0) < 0
    assert baseline_repair_needed(0,0) == CAND-BASE
    for cr in [D(0),D(25),D(100),D(250),D(500)]:
        for t in [D(0),MATERIAL]:
            threshold = baseline_repair_needed(cr,t)
            assert abs(saving(threshold,cr)-t) < D('1e-25')
            assert saving(threshold+D('0.01'),cr) > t
            assert saving(threshold-D('0.01'),cr) < t
    print('Pre-repair pairwise area excess (um2):', CAND-BASE)
    print('Baseline-only repair to reach equal area (um2):', baseline_repair_needed(0,0))
    print('Baseline-only repair to reach 2% saving (um2):', baseline_repair_needed(0,MATERIAL))
    print('PASS: 20 exact crossover checks; no electrical legality or GPU throughput claim')

if __name__ == '__main__':
    main()
