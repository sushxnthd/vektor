#!/usr/bin/env python3
"""Strict FIFO dual-issue lookahead impossibility: independent exhaustive audit.

For two issue slots and an in-order commit/issue contract, each cycle issues
the next one or two requests, never a deeper queue element. Under identical
bank-port constraints, a depth>2 selector cannot improve on greedy legal
prefix issue. This is a semantic theorem, NOT physical GPU validation.
"""
from itertools import product

def fifo(b):
    i=0; out=[]
    while i<len(b):
        k=2 if i+1<len(b) and b[i]!=b[i+1] else 1
        out.append(tuple(range(i,i+k))); i+=k
    return out

def independent_dp(b):
    n=len(b); d=[10**9]*(n+1); d[n]=0
    for i in range(n-1,-1,-1):
        d[i]=1+d[i+1]
        if i+1<n and b[i]!=b[i+1]:
            d[i]=min(d[i],1+d[i+2])
    return d[0]

def bypass(b,depth=4):
    q=list(enumerate(b)); out=[]
    while q:
        first=q.pop(0); issue=[first[0]]
        for j,(_,bank) in enumerate(q[:depth-1]):
            if bank!=first[1]:
                issue.append(q.pop(j)[0]); break
        out.append(tuple(issue))
    return out

def audit():
    tested=wins=0
    for alphabet in (2,3):
        for n in range(10):
            for b in product(range(alphabet),repeat=n):
                ordered=fifo(b); loose=bypass(b)
                assert len(ordered)==independent_dp(b)
                assert [i for cycle in ordered for i in cycle]==list(range(n))
                flat=[i for cycle in loose for i in cycle]
                assert sorted(flat)==list(range(n))
                if len(loose)<len(ordered):
                    wins+=1
                    assert flat!=list(range(n)),(b,loose)
                tested+=1
    b=(0,0,1,1)*128
    assert (len(fifo(b)),len(bypass(b)))==(257,256)
    print(f"PASS: {tested} binary/ternary sequences, {wins} bypass-only wins")
    print("PASS: clustered 512 requests: strict FIFO 257, bypass 256")
    print("THEOREM: strict in-order two-wide issue has zero depth>2 scheduling headroom")
    print("LIMIT: no legal reorder implementation, RTL synthesis, routed timing or GPU IPC")

if __name__=="__main__":
    audit()
