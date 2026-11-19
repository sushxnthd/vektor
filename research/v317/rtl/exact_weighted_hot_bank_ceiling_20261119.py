#!/usr/bin/env python3
"""Exact weighted four-request bank-service ceiling, exploratory not preregistered.

Four requests, two independent operand banks per request, B banks with two
read ports each. Greedy accepts in order; oracle selects the maximum-cardinality
subset with no fairness, timing, area or implementation cost. This is an
instantaneous service upper bound, NOT a GPU throughput or physical result.
"""
from fractions import Fraction
from itertools import product

def greedy(req, banks):
    loads = [0] * banks
    count = 0
    for a, b in req:
        if loads[a] + 1 + (a == b) <= 2 and (a == b or loads[b] + 1 <= 2):
            loads[a] += 1
            loads[b] += 1
            count += 1
    return count

def oracle(req, banks):
    best = 0
    for mask in range(1, 16):
        if mask.bit_count() <= best:
            continue
        loads = [0] * banks
        for i, (a, b) in enumerate(req):
            if (mask >> i) & 1:
                loads[a] += 1
                loads[b] += 1
        if max(loads) <= 2:
            best = mask.bit_count()
    return best

def sweep(banks, hot_num, denom):
    """Exact probability sums, no Monte Carlo. One hot bank; others equal."""
    assert banks >= 2 and 0 < hot_num < denom
    weights = [hot_num * (banks - 1)] + [denom - hot_num] * (banks - 1)
    total = sum(weights)
    greedy_weight = oracle_weight = improvement_weight = 0
    for flat in product(range(banks), repeat=8):
        weight = 1
        for x in flat:
            weight *= weights[x]
        req = tuple(zip(flat[::2], flat[1::2]))
        g, o = greedy(req, banks), oracle(req, banks)
        assert g <= o <= g + 1
        greedy_weight += weight * g
        oracle_weight += weight * o
        improvement_weight += weight * (o > g)
    ratio = Fraction(oracle_weight, greedy_weight)
    probability = Fraction(improvement_weight, total ** 8)
    mean_greedy = Fraction(greedy_weight, total ** 8)
    assert ratio == 1 + probability / mean_greedy
    return ratio, probability, mean_greedy

def test():
    assert sweep(4, 1, 4)[0] == sweep(4, 2, 8)[0]
    assert greedy(((0, 1), (0, 0), (1, 1), (2, 2)), 3) == 2
    assert oracle(((0, 1), (0, 0), (1, 1), (2, 2)), 3) == 3

if __name__ == "__main__":
    test()
    for n, d in [(1, 4), (1, 2), (13, 20), (3, 4), (7, 8)]:
        ratio, p, g = sweep(4, n, d)
        print(f"hot={n}/{d} ratio={float(ratio):.9f} "
              f"improvement_probability={float(p):.9f} "
              f"greedy_mean={float(g):.9f} "
              f"materiality_possible={ratio >= Fraction(51, 50)}")
