#!/usr/bin/env python3
"""Exact, seed-free small-bank challenge to V317 four-slot headroom.

Uniform independent operand bank IDs, four valid requests, two operands each,
two reads per bank, and at most four grants. Greedy is strict request-order
admission. Oracle is maximum-cardinality subset (unfair, zero-cost). The exact
ratio is an instantaneous bank-service upper bound, NOT a routed GPU result.
"""
from fractions import Fraction
from itertools import product

def greedy(requests, banks):
    loads = [0] * banks
    grants = 0
    for a, b in requests:
        la = loads[a] + 1 + (a == b)
        lb = loads[b] + 1 if a != b else la
        if la <= 2 and lb <= 2:
            loads[a] = la
            loads[b] = lb
            grants += 1
    return grants

def oracle(requests, banks):
    best = 0
    for mask in range(1, 16):
        if mask.bit_count() <= best:
            continue
        loads = [0] * banks
        legal = True
        for i, (a, b) in enumerate(requests):
            if mask & (1 << i):
                loads[a] += 1
                loads[b] += 1
                if loads[a] > 2 or loads[b] > 2:
                    legal = False
                    break
        if legal:
            best = mask.bit_count()
    return best

def exhaustive(banks):
    assert 1 <= banks <= 4
    greedy_sum = oracle_sum = improved = cases = 0
    for flat in product(range(banks), repeat=8):
        requests = tuple(zip(flat[::2], flat[1::2]))
        g = greedy(requests, banks)
        o = oracle(requests, banks)
        assert g <= o <= g + 1, (requests, g, o)
        greedy_sum += g
        oracle_sum += o
        improved += (o > g)
        cases += 1
    assert cases == banks**8
    ratio = Fraction(oracle_sum, greedy_sum)
    p = Fraction(improved, cases)
    mean_g = Fraction(greedy_sum, cases)
    assert ratio == 1 + p / mean_g
    return {'banks': banks, 'cases': cases, 'greedy_total': greedy_sum,
            'oracle_total': oracle_sum, 'improved_cases': improved,
            'oracle_ratio': str(ratio),
            'oracle_ratio_float': float(ratio),
            'required_clock_occupancy_for_2pct': str(Fraction(51,50)/ratio),
            'material_at_equal_clock_occupancy': ratio >= Fraction(51,50)}

def test():
    assert greedy(((0,1),(0,0),(1,1),(2,2)),3) == 2
    assert oracle(((0,1),(0,0),(1,1),(2,2)),3) == 3
    assert exhaustive(1)['oracle_ratio'] == '1'

if __name__ == '__main__':
    import json
    test()
    print(json.dumps([exhaustive(b) for b in (2,3,4)], indent=2))
