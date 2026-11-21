#!/usr/bin/env python3
"""V317 periodic adversarial finite-FIFO independent audit. Synthetic only."""
from itertools import combinations
from collections import deque
B=4; CAP=4; PORTS=2

def feasible(q,ids):
    c=[0]*B
    for i in ids:
        for b in q[i]:
            c[b]+=1
            if c[b]>PORTS:return False
    return True

def select(q,policy):
    if not q:return ()
    if policy=='greedy':
        out=[]
        for i in range(len(q)):
            if feasible(q,out+[i]):out.append(i)
        return tuple(out)
    return max((s for n in range(1,len(q)+1) for s in combinations(range(len(q)),n) if 0 in s and feasible(q,s)),key=lambda s:(len(s),tuple(-i for i in s)))

def run(pattern,policy,cycles=3000,warmup=500):
    q=deque(); done=drop=offered=0
    for t in range(cycles):
        selected=select(list(q),policy)
        for i in reversed(selected):del q[i]
        if t>=warmup:done+=len(selected)
        for req in pattern[t%len(pattern)]:
            if t>=warmup:offered+=1
            if len(q)<CAP:q.append(req)
            elif t>=warmup:drop+=1
    return done,drop,offered

def main():
    cases=[]
    for period in (1,2,3):
        for skew in (0,1,2,3):
            p=tuple(tuple(((skew+t)%4,(skew+t)%4) if j==0 else ((skew+t)%4,(skew+t+1)%4) for j in range(2)) for t in range(period))
            g=run(p,'greedy');o=run(p,'protected')
            assert g[2]==o[2]==5000
            assert g[0]==o[0],(period,skew,g,o)
            cases.append((period,skew,g,o))
    print('PASS: 12 deterministic periodic traces, zero oracle throughput advantage')
    for case in cases:print(case)
if __name__=='__main__':main()
