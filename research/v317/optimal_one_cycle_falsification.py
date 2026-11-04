#!/usr/bin/env python3
"""Independent exhaustive one-cycle packing oracle for V317.

Falsifies the interpretation of greedy bypass as a throughput upper bound.
Synthetic scheduler oracle, not a realizable RTL design.
"""
from itertools import combinations, product

def greedy(requests, banks, ports, slots, output):
    used = [0] * banks
    chosen = []
    for i, req in enumerate(requests):
        if len(chosen) == min(slots, output):
            break
        need = [req.count(b) for b in range(banks)]
        if all(used[b] + need[b] <= ports for b in range(banks)):
            chosen.append(i)
            used = [used[b] + need[b] for b in range(banks)]
    return tuple(chosen)

def optimal(requests, banks, ports, slots, output):
    best = ()
    for k in range(1, min(len(requests), slots, output) + 1):
        for subset in combinations(range(len(requests)), k):
            if all(sum(requests[i].count(b) for i in subset) <= ports for b in range(banks)):
                if len(subset) > len(best):
                    best = subset
    return best

def run():
    cases = gaps = maximum_gap = 0
    witness = None
    options = [(0,), (1,), (0, 0), (0, 1), (1, 1)]
    for n in range(5):
        for requests in product(options, repeat=n):
            for ports in (1, 2):
                if any(max(r.count(b) for b in range(2)) > ports for r in requests):
                    continue
                for slots in (1, 2, 3):
                    for output in (1, 2, 3):
                        g = greedy(requests, 2, ports, slots, output)
                        o = optimal(requests, 2, ports, slots, output)
                        assert len(g) <= len(o)
                        cases += 1
                        gap = len(o) - len(g)
                        if gap:
                            gaps += 1
                            if gap > maximum_gap:
                                maximum_gap = gap
                                witness = (requests, ports, slots, output, g, o)
    fixed = ((0, 1), (0,), (1,))
    assert greedy(fixed, 2, 1, 2, 2) == (0,)
    assert optimal(fixed, 2, 1, 2, 2) == (1, 2)
    assert gaps > 0
    print({"cases": cases, "greedy_suboptimal_cases": gaps,
           "max_one_cycle_completion_gap": maximum_gap, "witness": witness,
           "conclusion": "greedy bypass is not an optimal packing upper bound",
           "evidence_tier": "synthetic exact combinatorial oracle; not RTL"})

if __name__ == "__main__":
    run()
