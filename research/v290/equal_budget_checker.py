#!/usr/bin/env python3
"""Independent V290 vs conventional operand collector state-transition check."""
from itertools import product
import random,json
def partial(pairs,ready,arrival):
    n=len(pairs);have=[[bool(ready[i]&(1<<s)) for s in range(2)] for i in range(n)]
    finish=[None]*n;reads=0
    for t in range(100):
        for bank in (0,1):
            eligible=[(i,s) for i in range(n) for s in range(2) if arrival[i]<=t and pairs[i][s]==bank and not have[i][s]]
            if eligible:
                i,s=min(eligible);have[i][s]=True;reads+=1
        for i in range(n):
            if finish[i] is None and arrival[i]<=t and all(have[i]):finish[i]=t+1
        if all(x is not None for x in finish):return max(finish),reads,tuple(finish)
    raise AssertionError("deadlock")
def collector(pairs,ready,arrival):
    n=len(pairs);queues=[[],[]];have=[[bool(ready[i]&(1<<s)) for s in range(2)] for i in range(n)]
    for i in range(n):
        for s in range(2):
            if not have[i][s]:queues[pairs[i][s]].append((i,s))
    finish=[-1]*n;reads=0
    for t in range(100):
        for bank in (0,1):
            for i,s in queues[bank]:
                if arrival[i]<=t:
                    queues[bank].remove((i,s));have[i][s]=True;reads+=1;break
        for i in range(n):
            if finish[i]<0 and arrival[i]<=t and all(have[i]):finish[i]=t+1
        if all(x>=0 for x in finish):return max(finish),reads,tuple(finish)
    raise AssertionError("deadlock")
def run():
    mismatches=0;cases=0
    for b in product(range(2),repeat=8):
        pairs=[tuple(b[2*i:2*i+2]) for i in range(4)]
        for ready in product(range(4),repeat=4):
            cases+=1
            if partial(pairs,ready,[0]*4)!=collector(pairs,ready,[0]*4):mismatches+=1
    rng=random.Random(29020261023)
    for _ in range(10000):
        pairs=[(rng.randrange(2),rng.randrange(2)) for i in range(4)]
        ready=[rng.randrange(4) for i in range(4)]
        arrival=[rng.randrange(6) for i in range(4)]
        if partial(pairs,ready,arrival)!=collector(pairs,ready,arrival):mismatches+=1
    return dict(exhaustive_cases=cases,random_arrival_cases=10000,mismatches=mismatches,
        evidence="E0 software functional equivalence, not RTL or physical validation",
        strongest_control="conventional per-bank operand collector with identical 4 slots, 2 ports, 2 ready bits/slot")
if __name__=="__main__":print(json.dumps(run(),indent=2))
