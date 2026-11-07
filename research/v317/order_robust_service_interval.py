#!/usr/bin/env python3
"""Exact order-robust greedy service interval for bank-request multisets.

Each request consumes one port at each operand bank (two when identical).
Computes min/max grants over all distinct request permutations by memoized DP,
without enumerating permutations. No hardware or GPU performance claims.
"""
from functools import lru_cache
from itertools import combinations_with_replacement

def interval(requests, banks, ports=2):
    kinds = tuple(sorted(set(tuple(sorted(r)) for r in requests)))
    counts = tuple(sum(tuple(sorted(r)) == k for r in requests) for k in kinds)
    @lru_cache(None)
    def solve(counts, free):
        if not any(counts): return (0, 0)
        results=[]
        for i, (a,b) in enumerate(kinds):
            if not counts[i]: continue
            nxt=list(counts); nxt[i]-=1
            legal=free[a] >= (2 if a==b else 1) and free[b] >= (2 if a==b else 1)
            f=list(free)
            if legal: f[a]-=1; f[b]-=1
            lo,hi=solve(tuple(nxt),tuple(f))
            results.append((lo+int(legal),hi+int(legal)))
        return min(x[0] for x in results),max(x[1] for x in results)
    return solve(counts,(ports,)*banks)

def brute(requests,banks,ports=2):
    from itertools import permutations
    outcomes=[]
    for order in set(permutations(requests)):
        free=[ports]*banks; n=0
        for a,b in order:
            if free[a] >= (2 if a==b else 1) and free[b] >= (2 if a==b else 1):
                free[a]-=1;free[b]-=1;n+=1
        outcomes.append(n)
    return min(outcomes),max(outcomes)

def audit():
    for banks, expected in ((2,6),(3,48),(4,238)):
        kinds=tuple(combinations_with_replacement(range(banks),2))
        count=0
        for multiset in combinations_with_replacement(kinds,4):
            got=interval(multiset,banks)
            assert got==brute(multiset,banks),(banks,multiset,got)
            count+=got[0]!=got[1]
        assert count==expected,(banks,count)
        print('B=',banks,'order-sensitive multisets=',count,'PASS')
    cases=[((0,0),(0,1),(1,1),(0,1),(1,2)),((0,1),(0,2),(1,2),(2,2),(0,0),(1,1))]
    for case in cases:
        assert interval(case,3)==brute(case,3)
    print('PASS extended five/six-request independent permutation checks')
if __name__=='__main__': audit()
