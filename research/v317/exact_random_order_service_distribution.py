#!/usr/bin/env python3
"""Exact distribution of greedy bank-port service under uniform random request order.

Distinct permutations of a fixed multiset are equiprobable. This is a
conditional synthetic scheduling model, not an empirical GPU workload model.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement, permutations

def distribution(requests, banks, ports=2):
    kinds = tuple(sorted(set(tuple(sorted(r)) for r in requests)))
    counts = tuple(sum(tuple(sorted(r)) == k for r in requests) for k in kinds)
    @lru_cache(None)
    def dp(remaining, free):
        if not any(remaining):
            return ((0, Fraction(1)),)
        total = sum(remaining)
        out = defaultdict(Fraction)
        for i, (a, b) in enumerate(kinds):
            if not remaining[i]:
                continue
            nxt = list(remaining)
            nxt[i] -= 1
            f = list(free)
            need_a = 2 if a == b else 1
            legal = f[a] >= need_a and f[b] >= (2 if a == b else 1)
            if legal:
                f[a] -= 1
                f[b] -= 1
            for grants, p in dp(tuple(nxt), tuple(f)):
                out[grants + int(legal)] += p * Fraction(remaining[i], total)
        return tuple(sorted(out.items()))
    return dict(dp(counts, (ports,) * banks))

def independent_brute(requests, banks, ports=2):
    orders = set(permutations(tuple(tuple(sorted(r)) for r in requests)))
    hist = defaultdict(int)
    for order in orders:
        free = [ports] * banks
        grants = 0
        for a, b in order:
            if free[a] >= (2 if a == b else 1) and free[b] >= (2 if a == b else 1):
                free[a] -= 1
                free[b] -= 1
                grants += 1
        hist[grants] += 1
    return {g: Fraction(n, len(orders)) for g, n in hist.items()}

def audit():
    sensitive = 0
    for banks in (2, 3):
        kinds = tuple(combinations_with_replacement(range(banks), 2))
        for size in (3, 4, 5):
            for requests in combinations_with_replacement(kinds, size):
                actual = distribution(requests, banks)
                expected = independent_brute(requests, banks)
                assert actual == expected, (banks, requests, actual, expected)
                assert sum(actual.values()) == 1
                sensitive += len(actual) > 1
    print("PASS exact independent enumeration; order-sensitive cases:", sensitive)
    case = ((0, 0), (0, 1), (1, 1), (0, 1))
    print("Example distribution:", distribution(case, 2))
if __name__ == "__main__":
    audit()
