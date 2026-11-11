#!/usr/bin/env python3
"""Exact small-bank falsification of four-slot bank-service headroom.

No physical/RTL/IPC claim. Enumerates ordered two-source requests and compares
a fixed-order compact greedy grant with the maximum-cardinality subset under
two read ports per bank. The oracle is deliberately unfair and zero-cost.
"""
from collections import Counter
from itertools import product, combinations
from fractions import Fraction
import argparse
import json

def feasible(requests, indices, ports=2):
    uses = Counter(bank for i in indices for bank in requests[i])
    return all(count <= ports for count in uses.values())

def greedy(requests, ports=2):
    chosen = []
    for i in range(len(requests)):
        if feasible(requests, chosen + [i], ports):
            chosen.append(i)
    return len(chosen)

def oracle(requests, ports=2):
    n = len(requests)
    for k in range(n, -1, -1):
        if any(feasible(requests, subset, ports)
               for subset in combinations(range(n), k)):
            return k
    raise AssertionError("unreachable")

def exact(banks=2, slots=4, ports=2):
    if not (1 <= banks <= 4 and 1 <= slots <= 4 and ports >= 1):
        raise ValueError("small exhaustive checker only")
    operands = tuple(product(range(banks), repeat=2))
    total = 0
    sum_g = sum_o = improved = max_delta = 0
    histogram = Counter()
    for requests in product(operands, repeat=slots):
        g = greedy(requests, ports)
        o = oracle(requests, ports)
        assert 0 <= g <= o <= slots
        d = o - g
        histogram[d] += 1
        max_delta = max(max_delta, d)
        improved += d > 0
        sum_g += g
        sum_o += o
        total += 1
    ratio = Fraction(sum_o, sum_g)
    return dict(banks=banks, slots=slots, ports=ports, cases=total,
                mean_greedy=str(Fraction(sum_g, total)),
                mean_oracle=str(Fraction(sum_o, total)),
                oracle_to_greedy=str(ratio),
                improvement_probability=str(Fraction(improved, total)),
                max_grant_delta=max_delta,
                delta_histogram=dict(sorted(histogram.items())))

def self_test():
    assert greedy(((0, 0), (0, 0), (1, 1))) == 2
    assert oracle(((0, 0), (0, 0), (1, 1))) == 2
    for b in (2, 3):
        result = exact(b, 4)
        assert sum(result["delta_histogram"].values()) == result["cases"]
        assert result["max_grant_delta"] <= 1, result
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--banks", type=int, default=2)
    parser.add_argument("--slots", type=int, default=4)
    parser.add_argument("--ports", type=int, default=2)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    print(json.dumps(exact(args.banks, args.slots, args.ports),
                     sort_keys=True, indent=2))
