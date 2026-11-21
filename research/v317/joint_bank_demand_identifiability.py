#!/usr/bin/env python3
"""Exact joint-demand identifiability audit for V317's restricted 4-slot/2R model.
No physical GPU performance claims. Python standard library only.
Run: python3 research/v317/joint_bank_demand_identifiability.py
"""
from itertools import product
from collections import defaultdict

def greedy(requests, banks):
    remaining = [2] * banks
    grants = 0
    for a, b in requests:
        need = [0] * banks
        need[a] += 1
        need[b] += 1
        if all(need[k] <= remaining[k] for k in range(banks)):
            remaining = [remaining[k] - need[k] for k in range(banks)]
            grants += 1
    return grants

def oracle(requests, banks):
    best = 0
    for mask in range(1 << len(requests)):
        remaining = [2] * banks
        valid = True
        count = 0
        for i, (a, b) in enumerate(requests):
            if mask & (1 << i):
                remaining[a] -= 1
                remaining[b] -= 1
                count += 1
                if min(remaining) < 0:
                    valid = False
                    break
        if valid:
            best = max(best, count)
    return best

def audit(banks):
    by_hist = defaultdict(lambda: {'min': 9, 'max': -1, 'win': None, 'no': None, 'n': 0})
    opportunities = 0
    for operands in product(range(banks), repeat=8):
        requests = tuple(zip(operands[::2], operands[1::2]))
        histogram = tuple(sorted(operands.count(k) for k in range(banks)))
        delta = oracle(requests, banks) - greedy(requests, banks)
        assert delta in (0, 1), (banks, requests, delta)
        opportunities += delta
        row = by_hist[histogram]
        row['n'] += 1
        row['min'] = min(row['min'], delta)
        row['max'] = max(row['max'], delta)
        if delta and row['win'] is None: row['win'] = requests
        if not delta and row['no'] is None: row['no'] = requests
    mixed = [(h, row) for h, row in sorted(by_hist.items()) if row['min'] < row['max']]
    assert mixed, banks
    print(f"B={banks}: exhaustive={banks**8}, opportunities={opportunities}, mixed_histograms={len(mixed)}")
    h, row = mixed[0]
    print(f"  same sorted bank histogram {h}: delta=1 {row['win']} vs delta=0 {row['no']}")
    return opportunities

if __name__ == '__main__':
    assert [audit(b) for b in (2, 3, 4)] == [52, 1044, 7896]
    print('PASS: marginal bank occupancy does not identify oracle scheduling opportunity.')
