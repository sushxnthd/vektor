#!/usr/bin/env python3
"""Exact order-risk and clock-break-even audit for the V317 synthetic bank scheduler.

This is a *conditional* four-slot service model, not RTL timing or GPU IPC.
Uniform random order is explicitly assumed; no workload provenance is implied.
"""
from fractions import Fraction
from itertools import combinations_with_replacement
from exact_random_order_service_distribution import distribution, independent_brute

def oracle_max(requests, banks, ports=2):
    """Independent exhaustive maximum-cardinality subset oracle."""
    best = 0
    n = len(requests)
    for mask in range(1 << n):
        if mask.bit_count() <= best:
            continue
        load = [0] * banks
        for i, (a, b) in enumerate(requests):
            if mask >> i & 1:
                load[a] += 1
                load[b] += 1
        if max(load) <= ports:
            best = mask.bit_count()
    return best

def audit_case(requests, banks, ports=2, clock_penalty=Fraction(1, 200)):
    hist = distribution(requests, banks, ports)
    opt = oracle_max(requests, banks, ports)
    mean = sum((Fraction(g)*p for g,p in hist.items()), Fraction())
    if mean == 0:
        return dict(oracle=opt, expected_greedy=mean, ratio=None,
                    critical_penalty=None, win_probability=None)
    critical = Fraction(opt, 1)/mean - 1
    # Probability that the oracle's *per-batch* net service exceeds greedy
    # after the same assumed clock-period penalty.
    prob = sum((p for g,p in hist.items() if Fraction(opt,1) > (1+clock_penalty)*g), Fraction())
    return dict(oracle=opt, expected_greedy=mean,
                ratio=Fraction(opt,1)/((1+clock_penalty)*mean),
                critical_penalty=critical, win_probability=prob,
                distribution=hist)

def main():
    # Exact enumeration is an independent implementation of the greedy distribution.
    checked = 0
    rare_wins = []
    for banks in (2,3):
        kinds = tuple(combinations_with_replacement(range(banks), 2))
        for requests in combinations_with_replacement(kinds, 4):
            h = distribution(requests, banks)
            assert h == independent_brute(requests, banks)
            result = audit_case(requests, banks)
            if result["ratio"] is not None:
                # A positive expected net oracle margin does not imply that
                # each ordering produces a positive gain.
                if result["ratio"] > 1 and result["win_probability"] < 1:
                    rare_wins.append((banks, requests, result))
            checked += 1
    assert rare_wins, "Expected a workload with mean win but non-winning orderings"
    banks, requests, result = rare_wins[0]
    print("PASS independent exhaustive distributions:", checked)
    print("First mean-win/non-universal-order example:", banks, requests)
    for k,v in result.items():
        print(k, v)
    print("LIMIT: oracle is a zero-cost upper bound; no physical scheduler claimed.")

if __name__ == "__main__":
    main()
