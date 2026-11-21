#!/usr/bin/env python3
"""Exact 7-wise-indistinguishable traffic falsifier; synthetic service only.

Four ordered requests, two bank operands each, two banks with two read
ports each. Even/odd parity distributions on the eight bank bits have
identical marginals for EVERY strict subset of coordinates (up to 7-way).
No GPU throughput, routed timing, or hardware legality is inferred.
"""
from itertools import combinations, product
from collections import Counter
from fractions import Fraction

def greedy(bits):
    used = [0, 0]
    accepted = 0
    for i in range(0, 8, 2):
        counts = Counter(bits[i:i+2])
        if all(used[b] + n <= 2 for b, n in counts.items()):
            accepted += 1
            for b, n in counts.items():
                used[b] += n
    return accepted

def oracle(bits):
    best = 0
    for select in range(16):
        used = [0, 0]
        n = 0
        for i in range(4):
            if (select >> i) & 1:
                n += 1
                for b in bits[2*i:2*i+2]:
                    used[b] += 1
        if max(used) <= 2:
            best = max(best, n)
    return best

def run():
    groups = [[x for x in product((0, 1), repeat=8)
               if sum(x) % 2 == parity] for parity in (0, 1)]
    assert all(len(g) == 128 for g in groups)
    # Independent exact check of all strict-subset joint distributions.
    for size in range(8):
        for indices in combinations(range(8), size):
            hist = [Counter(tuple(x[i] for i in indices) for x in g)
                    for g in groups]
            assert hist[0] == hist[1], (size, indices)
    outputs = []
    for group in groups:
        gs = sum(greedy(x) for x in group)
        os = sum(oracle(x) for x in group)
        improved = sum(oracle(x) > greedy(x) for x in group)
        outputs.append((gs, os, improved, Fraction(os, gs)))
    assert outputs == [(230, 254, 24, Fraction(127,115)),
                       (212, 240, 28, Fraction(60,53))], outputs
    for label, (gs, os, improved, ratio) in zip(("even", "odd"), outputs):
        print(f"{label}: n=128 greedy_total={gs} oracle_total={os} "
              f"improved={improved} oracle/greedy={ratio} "
              f"decimal={float(ratio):.9f}")
    print("PASS: identical all <=7-way bank-bit marginals, unequal service.")
    print("LIMITATION: exact small synthetic upper bound, not GPU IPC.")

if __name__ == "__main__":
    run()
