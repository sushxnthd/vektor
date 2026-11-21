#!/usr/bin/env python3
"""Exact finite-horizon staged operand service with GLOBAL partial-request storage.

One read per bank/cycle; each request needs two distinct bank reads. One
completion consumes a return slot. A partial request occupies one storage
slot from first read until second operand arrives. Reads/completion occur
within a cycle. Combinatorial upper bound only; NOT RTL or physical evidence.
"""
from functools import lru_cache
from itertools import combinations, product
TRI=((0,1),(1,2),(0,2))

def oracle(reqs,cycles,returns,partial_slots):
    n=len(reqs)
    banks=range(1+max((max(r) for r in reqs),default=-1))
    @lru_cache(None)
    def dp(t,done,ready):
        if t==cycles:return done.bit_count()
        options=[]
        for b in banks:
            options.append([None]+[(i,j) for i,r in enumerate(reqs) for j,v in enumerate(r)
                if v==b and not (done>>i&1) and not (ready>>(2*i+j)&1)])
        best=done.bit_count()
        for selected in product(*options):
            rdy=ready
            for x in selected:
                if x is not None:rdy|=1<<(2*x[0]+x[1])
            eligible=[i for i in range(n) if not (done>>i&1) and (rdy>>(2*i)&3)==3]
            for k in range(min(returns,len(eligible))+1):
                for completed in combinations(eligible,k):
                    mask=done
                    for i in completed:mask|=1<<i
                    partial=sum((rdy>>(2*i)&3).bit_count()==1 for i in range(n) if not(mask>>i&1))
                    if partial<=partial_slots:best=max(best,dp(t+1,mask,rdy))
        return best
    return dp(0,0,0)

def atomic(reqs,cycles,returns):
    n=len(reqs)
    @lru_cache(None)
    def dp(t,done):
        if t==cycles:return done.bit_count()
        best=dp(t+1,done)
        remaining=[i for i in range(n) if not(done>>i&1)]
        for k in range(1,min(returns,len(remaining))+1):
            for chosen in combinations(remaining,k):
                banks=[b for i in chosen for b in reqs[i]]
                if len(banks)==len(set(banks)):
                    best=max(best,dp(t+1,done|sum(1<<i for i in chosen)))
        return best
    return dp(0,0)

def test():
    count=0; wins={s:0 for s in range(4)}
    for n in range(1,5):
        for reqs in product(TRI,repeat=n):
            for cycles in (1,2,3):
                for ret in (1,2,3):
                    a=atomic(reqs,cycles,ret)
                    last=a
                    for slots in range(4):
                        v=oracle(reqs,cycles,ret,slots)
                        assert a<=v<=min(n,cycles*ret),(reqs,cycles,ret,slots,a,v)
                        assert last<=v
                        wins[slots]+=v>a
                        last=v
                    count+=1
    print('PASS',count,'configurations; strict staging advantage by partial slots',wins)
    print('triangle two cycles three returns:',[(s,oracle(TRI,2,3,s)) for s in range(4)])
if __name__=='__main__':test()
