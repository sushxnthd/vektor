#!/usr/bin/env python3
"""Exhaustive ordering-identifiability falsification, restricted V317 4-slot/2R model.

Identical request multisets (hence identical joint bank-pair histograms) can
have different greedy service. The maximum-cardinality oracle is invariant to
ordering. Standard library only; no GPU/RTL performance claims.
Run: python3 research/v317/request_order_identifiability.py
"""
from itertools import combinations_with_replacement, permutations

def greedy(order, banks):
    remaining = [2] * banks
    grants = 0
    for a, b in order:
        need_a = 2 if a == b else 1
        if remaining[a] >= need_a and remaining[b] >= need_a if a == b else remaining[a] >= 1 and remaining[b] >= 1:
            remaining[a] -= 1
            remaining[b] -= 1
            grants += 1
    return grants

def oracle(order, banks):
    best = 0
    for mask in range(16):
        used = [0] * banks
        for i, (a, b) in enumerate(order):
            if mask & (1 << i):
                used[a] += 1
                used[b] += 1
        if max(used) <= 2:
            best = max(best, mask.bit_count())
    return best

def audit(banks):
    pairs = tuple(combinations_with_replacement(range(banks), 2))
    sensitive = 0
    witness = None
    for multiset in combinations_with_replacement(pairs, 4):
        orders = set(permutations(multiset))
        oracle_values = {oracle(order, banks) for order in orders}
        assert len(oracle_values) == 1, (banks, multiset)
        outcomes = {greedy(order, banks) for order in orders}
        if len(outcomes) > 1:
            sensitive += 1
            if witness is None:
                low = next(o for o in orders if greedy(o, banks) == min(outcomes))
                high = next(o for o in orders if greedy(o, banks) == max(outcomes))
                witness = (multiset, low, high, min(outcomes), max(outcomes), next(iter(oracle_values)))
    print(f"B={banks}: order-sensitive request multisets={sensitive}; first witness={witness}")
    return sensitive

if __name__ == "__main__":
    assert [audit(b) for b in (2, 3, 4)] == [6, 48, 238]
    print("PASS: even joint bank-pair counts cannot determine greedy service without order.")
