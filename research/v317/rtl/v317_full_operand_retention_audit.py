#!/usr/bin/env python3
"""Audit uncharged fully-read, unreturned requests in V317's staging oracle.

This is a finite-horizon abstract scheduler, NOT RTL or physical evidence.
A request with both operands read but no return grant still retains two
operands. Charging only exactly-one-operand partials omits this live state.
The corrected model charges one slot for EVERY live request with any read.
"""
from functools import lru_cache
from itertools import product, combinations

def solve(reqs, cycles, returns, slots, charge_full):
    n = len(reqs)
    banks = range(max(max(r) for r in reqs) + 1)
    @lru_cache(None)
    def dp(t, done, ready):
        if t == cycles:
            return done.bit_count()
        choices = [[None] + [(i,j) for i,r in enumerate(reqs)
                    for j,b0 in enumerate(r) if b0 == b
                    and not(done >> i & 1)
                    and not(ready >> (2*i+j) & 1)] for b in banks]
        best = done.bit_count()
        for selected in product(*choices):
            rdy = ready
            for x in selected:
                if x is not None:
                    rdy |= 1 << (2*x[0]+x[1])
            eligible = [i for i in range(n) if not(done >> i & 1)
                        and (rdy >> (2*i) & 3) == 3]
            for k in range(min(returns, len(eligible))+1):
                for completed in combinations(eligible, k):
                    mask = done
                    for i in completed:
                        mask |= 1 << i
                    held = sum(
                        ((rdy >> (2*i) & 3) != 0) if charge_full
                        else ((rdy >> (2*i) & 3).bit_count() == 1)
                        for i in range(n) if not(mask >> i & 1))
                    if held <= slots:
                        best = max(best, dp(t+1, mask, rdy))
        return best
    return dp(0, 0, 0)

def test():
    # Direct transition counterexample: two disjoint pairs read in one
    # cycle, one return granted. The other completed pair occupies a
    # live buffer, despite having zero *partial* operands.
    reqs = ((0,1),(2,3))
    ready = 0b1111
    done = 0b0001
    partial_only = sum((ready >> (2*i) & 3).bit_count() == 1
                       for i in range(2) if not(done >> i & 1))
    live_request = sum((ready >> (2*i) & 3) != 0
                       for i in range(2) if not(done >> i & 1))
    assert (partial_only, live_request) == (0, 1)
    # The previous oracle admits this transition at slots=0; a model
    # charging all retained requests rejects it.
    pairs = ((0,1),(0,2),(1,2))
    count = 0
    strict = 0
    for n in range(1,4):
        for workload in product(pairs, repeat=n):
            for cycles in (1,2):
                for returns in (1,2):
                    for slots in (0,1,2):
                        loose = solve(workload,cycles,returns,slots,False)
                        charged = solve(workload,cycles,returns,slots,True)
                        assert charged <= loose
                        strict += charged < loose
                        count += 1
    print("PASS: uncharged-live-state counterexample; exhaustive",count,
          "small configurations; strict completion differences",strict)
    print("LIMIT: zero strict differences in this restricted family does NOT"
          " prove equivalence in larger workloads or equal physical cost.")

if __name__ == "__main__":
    test()
