#!/usr/bin/env python3
"""Prospective selector vs strongest simple control: exact boundary stratification.

Exhaustive 3-bank, four-request, two-read-port instantaneous admission model.
A stratum uses only observable demand: maximum bank load and number of
same-bank operand pairs. Not an unseen-workload, routed-RTL or GPU-IPC result.
"""
from collections import Counter, defaultdict
from itertools import product

def admit(req, order):
    used = Counter()
    grants = 0
    for i in order:
        demand = Counter(req[i])
        if all(used[b] + n <= 2 for b, n in demand.items()):
            used.update(demand)
            grants += 1
    return grants

def evaluate():
    strata = defaultdict(Counter)
    wins = Counter()
    for flat in product(range(3), repeat=8):
        req = tuple((flat[2*i], flat[2*i+1]) for i in range(4))
        totals = Counter(flat)
        weighted = sorted(range(4), key=lambda i:
                          (sum(totals[b] for b in req[i]), i))
        minimum = sorted(range(4), key=lambda i:
                         (min(totals[b] for b in req[i]), i))
        a, b = admit(req, weighted), admit(req, minimum)
        key = (max(totals.values()), sum(x == y for x, y in req))
        strata[key]['cases'] += 1
        strata[key]['weighted'] += a
        strata[key]['minimum'] += b
        wins[key] += (a > b)
        assert a >= b, (req, a, b)
    assert sum(s['cases'] for s in strata.values()) == 6561
    assert sum(s['weighted'] for s in strata.values()) == 15387
    assert sum(s['minimum'] for s in strata.values()) == 15315
    assert {k:v for k,v in wins.items() if v} == {(5,3):72}
    assert strata[(5,3)] == Counter(cases=288, weighted=576, minimum=504)
    for key, s in sorted(strata.items()):
        print(key, dict(s), 'weighted_minus_minimum', s['weighted']-s['minimum'])
    print('Exact uniform gain:', '15387/15315 =', 15387/15315)
    print('Boundary: only max-bank-load=5 and three same-bank requests')
    print('Conditional stratum gain:', '576/504 =', 576/504)
    print('No physical, power, throughput, unseen-workload or generalization claim.')

if __name__ == '__main__':
    evaluate()
