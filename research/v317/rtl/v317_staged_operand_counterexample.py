#!/usr/bin/env python3
"""Exact finite-horizon staged versus atomic operand service, small instances.

Each request needs two distinct banks; staged model may read operands on
separate cycles, retaining a one-bit per-operand ready state. Each bank has
one read port per cycle. Completion requires both operands, and a shared
return port limits completions per cycle. This is a model, not RTL.
"""
from functools import lru_cache
from itertools import combinations, product

def staged(reqs, cycles, returns=1):
    n=len(reqs)
    @lru_cache(None)
    def solve(t, done, ready):
        if t==cycles: return done.bit_count()
        choices=[]
        for b in range(max((max(r) for r in reqs),default=-1)+1):
            choices.append([None]+[(i,j) for i,r in enumerate(reqs) for j,bank in enumerate(r)
                       if bank==b and not (done>>i&1) and not (ready>>(2*i+j)&1)])
        best=0
        for selected in product(*choices):
            rdy=ready
            for item in selected:
                if item is not None: rdy|=1<<(2*item[0]+item[1])
            eligible=[i for i in range(n) if not (done>>i&1) and (rdy>>(2*i)&3)==3]
            for k in range(min(returns,len(eligible))+1):
                for finish in combinations(eligible,k):
                    mask=done
                    for i in finish: mask|=1<<i
                    best=max(best,solve(t+1,mask,rdy))
        return best
    return solve(0,0,0)

def atomic(reqs,cycles,returns=1):
    n=len(reqs)
    @lru_cache(None)
    def solve(t,done):
        if t==cycles:return done.bit_count()
        best=solve(t+1,done)
        remaining=[i for i in range(n) if not (done>>i&1)]
        for k in range(1,min(returns,len(remaining))+1):
            for selected in combinations(remaining,k):
                banks=[b for i in selected for b in reqs[i]]
                if len(banks)==len(set(banks)):
                    best=max(best,solve(t+1,done|sum(1<<i for i in selected)))
        return best
    return solve(0,0)

def test():
    tri=((0,1),(1,2),(0,2))
    assert atomic(tri,2,3)==2
    assert staged(tri,2,3)==3
    assert staged(tri,3,3)==3
    count=0; strict=0
    for n in range(1,5):
        for reqs in product(((0,1),(0,2),(1,2)),repeat=n):
            for cycles in (1,2,3):
                for ret in (1,2,3):
                    a=atomic(reqs,cycles,ret);s=staged(reqs,cycles,ret)
                    assert 0<=a<=s<=min(n,cycles*ret),(reqs,cycles,ret,a,s)
                    strict+=s>a;count+=1
    print(f'PASS {count} exhaustive configurations, staged strictly beats atomic in {strict}')
    print('Triangle 2 cycles, 3 return ports: atomic=2, staged=3; no RTL/physical claim')
if __name__=='__main__':test()
