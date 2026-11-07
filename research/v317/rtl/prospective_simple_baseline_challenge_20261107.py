#!/usr/bin/env python3
"""Independent equal-port, low-complexity controls for V317 prospective selector.

Exhaustive ordered four-request, three-bank, two-read-port toy model.
No physical timing, area, queueing, or GPU IPC claim. Deterministic tie
breaks preserve original request index; controls see only current demand.
"""
from collections import Counter
from itertools import product

N = 4
BANKS = 3
PORTS = 2

def admitted(req, order):
    used = [0] * BANKS
    grants = 0
    for i in order:
        demand = Counter(req[i])
        if all(used[b] + count <= PORTS for b, count in demand.items()):
            for b, count in demand.items():
                used[b] += count
            grants += 1
    return grants

def orders(req):
    totals = Counter(b for pair in req for b in pair)
    def sort(key):
        return sorted(range(N), key=lambda i: (key(i), i))
    return {
        "contention_sum": sort(lambda i: sum(totals[b] for b in req[i])),
        "min_contention": sort(lambda i: min(totals[b] for b in req[i])),
        "max_contention": sort(lambda i: max(totals[b] for b in req[i])),
        "distinct_first": sort(lambda i: req[i][0] == req[i][1]),
        "fixed": list(range(N)),
    }

def run():
    total = Counter()
    pairwise = Counter()
    for flat in product(range(BANKS), repeat=2*N):
        req = tuple((flat[2*i], flat[2*i+1]) for i in range(N))
        score = {name: admitted(req, order) for name, order in orders(req).items()}
        for name, n in score.items():
            total[name] += n
        for name in ("min_contention", "max_contention", "distinct_first", "fixed"):
            pairwise[(name, "win")] += score["contention_sum"] > score[name]
            pairwise[(name, "loss")] += score["contention_sum"] < score[name]
    assert total == Counter({
        "contention_sum": 15387, "min_contention": 15315,
        "distinct_first": 14667, "max_contention": 14427, "fixed": 14391
    }), total
    assert all(pairwise[(name, "loss")] == 0 for name in
               ("min_contention", "max_contention", "distinct_first", "fixed"))
    assert pairwise[("min_contention", "win")] == 72
    assert pairwise[("max_contention", "win")] == 960
    assert pairwise[("distinct_first", "win")] == 720
    print("Ordered configurations:", BANKS ** (2*N))
    print("Total admissions:", dict(total))
    print("Pairwise controls:", dict(pairwise))
    print("Interpretation: toy-model dominance only; no RTL or routed physical win.")

if __name__ == "__main__":
    run()
