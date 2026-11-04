#!/usr/bin/env python3
"""Arrival-order sensitivity falsification for V317 (synthetic scheduling only).

A scheduler claim based only on bank histograms is invalid if permutations
of the same request multiset produce different online completion counts.
This script fixes a one-cycle arrival batch, enumerates its orderings,
and compares greedy against exact equal-resource packing.
"""
from itertools import permutations, product
from finite_horizon_offline_oracle import exact
from audit_hindsight_online_gap import online_greedy

OPS = ((0,), (1,), (0, 1))
RESOURCES = ((1, 2, 2), (2, 2, 2))
def run():
    cases = 0
    divergent = 0
    witnesses = []
    for n in range(1, 6):
        for multiset in product(OPS, repeat=n):
            if tuple(sorted(multiset)) != multiset:
                continue
            orders = set(permutations(multiset))
            for ports, slots, output in RESOURCES:
                scores = []
                upper = None
                for order in orders:
                    rows = [{"cycle": 0, "requests": [
                        {"id": str(i), "banks": list(op)}
                        for i, op in enumerate(order)]}]
                    optimum = exact(rows, 2, ports, slots, output, max_live=5)
                    online = online_greedy((order,), ports, slots, output)
                    assert online <= optimum
                    if upper is None:
                        upper = optimum
                    assert upper == optimum, "packing optimum changed under permutation"
                    scores.append((online, order))
                    cases += 1
                if max(x[0] for x in scores) != min(x[0] for x in scores):
                    divergent += 1
                    if len(witnesses) < 5:
                        lo = min(scores)
                        hi = max(scores)
                        witnesses.append((multiset, (ports, slots, output), lo, hi, upper))
    assert divergent > 0, "expected arrival-order sensitivity not found"
    print(f"PASS permutation_cases={cases} divergent_multisets={divergent}")
    for witness in witnesses:
        print("witness", witness)
    print("EVIDENCE: synthetic one-cycle falsification; no RTL, physical, or GPU claim")

if __name__ == "__main__":
    run()
