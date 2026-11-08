#!/usr/bin/env python3
"""Exact small-instance atomic multi-bank service upper bound.

Independent of V317 RTL. Requests require all named bank ports in one cycle;
no staged reads. A pooled/per-bank fluid envelope is necessary but not sufficient.
"""
from functools import lru_cache
from itertools import combinations, product


def fluid_upper(requests, ports, returns, cycles):
    demand = [sum(b in req for req in requests) for b in range(len(ports))]
    # Every completion uses at least one bank; bank-specific totals alone do
    # not bound number completed when requests differ in bank requirements.
    return min(len(requests), cycles * returns,
               sum(min(d, cycles * p) for d, p in zip(demand, ports)))


def exact_atomic(requests, ports, returns, cycles):
    assert all(req and len(set(req)) == len(req) for req in requests)
    assert all(all(0 <= b < len(ports) for b in req) for req in requests)
    assert cycles >= 0 and returns >= 0 and all(p >= 0 for p in ports)
    n = len(requests)
    @lru_cache(None)
    def solve(remaining, t):
        if not t or not remaining:
            return 0
        best = solve(remaining, t-1)
        for k in range(1, min(returns, len(remaining))+1):
            for chosen in combinations(remaining, k):
                used = [0] * len(ports)
                for i in chosen:
                    for b in requests[i]:
                        used[b] += 1
                if all(u <= p for u, p in zip(used, ports)):
                    nxt = tuple(i for i in remaining if i not in chosen)
                    best = max(best, k + solve(nxt, t-1))
        return best
    return solve(tuple(range(n)), cycles)


def test():
    assert exact_atomic([(0,1),(0,1)], (2,2), 1, 1) == 1
    tri = [(0,1),(1,2),(0,2)]
    assert exact_atomic(tri,(1,1,1),3,2) == 2
    assert exact_atomic(tri,(1,1,1),3,3) == 3
    assert fluid_upper(tri,(1,1,1),3,2) == 3
    cases = 0
    for n in range(5):
        for reqs in product(((0,), (1,), (0,1)), repeat=n):
            for cycles in range(3):
                for ret in (1,2):
                    oracle = 0
                    for assignments in product(range(cycles+1), repeat=n):
                        served = sum(a < cycles for a in assignments)
                        if served <= oracle: continue
                        if all(sum(a == t for a in assignments) <= ret for t in range(cycles)) and all(
                            sum(a == t and b in reqs[i] for i,a in enumerate(assignments)) <= 1
                            for t in range(cycles) for b in range(2)):
                            oracle = served
                    exact = exact_atomic(reqs,(1,1),ret,cycles)
                    assert exact == oracle, (reqs, cycles, ret, exact, oracle)
                    assert exact <= fluid_upper(reqs,(1,1),ret,cycles)
                    cases += 1
    print(f'PASS {cases} independent exhaustive assignment cases; triangle 2/3 in two cycles')
    print('Synthetic atomic-service falsification only; no RTL, STA, SRAM, GPU IPC.')

if __name__ == '__main__':
    test()
