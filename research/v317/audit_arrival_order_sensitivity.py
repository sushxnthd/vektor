#!/usr/bin/env python3
"""One-cycle arrival-order sensitivity audit (synthetic; not GPU evidence).

Both online greedy and the offline packing optimum are evaluated on the SAME
one-cycle horizon. The prior version inadvertently used two cycles for exact()
and one for online_greedy(), confounding its comparison.
"""
from itertools import combinations, permutations, product
from finite_horizon_offline_oracle import exact
from audit_hindsight_online_gap import online_greedy

OPS = ((0,), (1,), (0, 1))
RESOURCES = ((1, 2, 2), (2, 2, 2))

def independent_pack(order, ports, slots, output):
    """Exhaustive one-cycle subset enumeration, independent of exact()."""
    best = 0
    for k in range(min(len(order), slots, output) + 1):
        for subset in combinations(order, k):
            if all(sum(req.count(bank) for req in subset) <= ports
                   for bank in (0, 1)):
                best = max(best, k)
    return best

def run():
    cases = 0
    divergent = 0
    witnesses = []
    for n in range(1, 6):
        for multiset in product(OPS, repeat=n):
            if tuple(sorted(multiset)) != multiset:
                continue
            orders = sorted(set(permutations(multiset)))
            for ports, slots, output in RESOURCES:
                scores = []
                upper = None
                for order in orders:
                    rows = [{"cycle": 0, "requests": [
                        {"id": str(i), "banks": list(op)}
                        for i, op in enumerate(order)]}]
                    optimum = exact(rows, 2, ports, slots, output, max_live=5)
                    independently = independent_pack(order, ports, slots, output)
                    online = online_greedy((order,), ports, slots, output)
                    assert optimum == independently, (order, optimum, independently)
                    assert online <= optimum, (order, online, optimum)
                    if upper is None:
                        upper = optimum
                    assert upper == optimum, "packing optimum changed under permutation"
                    scores.append((online, order))
                    cases += 1
                if max(s[0] for s in scores) != min(s[0] for s in scores):
                    divergent += 1
                    if len(witnesses) < 5:
                        witnesses.append((multiset, (ports, slots, output),
                                          min(scores), max(scores), upper))
    assert cases == 726, cases
    assert divergent > 0, "expected arrival-order sensitivity not found"
    print(f"PASS matched_horizon_cases={cases} divergent_multisets={divergent}")
    for witness in witnesses:
        print("witness", witness)
    print("EVIDENCE: synthetic one-cycle scheduling only; no RTL or GPU claim")

if __name__ == "__main__":
    run()
