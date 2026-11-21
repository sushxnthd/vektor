#!/usr/bin/env python3
"""Deterministic bank-skew transfer: adjacent vs depth-four lookahead.

Finite streams, 2 issue slots, one service port per bank, head-order preserved.
Scheduling upper-bound experiment, NOT physical GPU evidence.
"""
from fractions import Fraction
from random import Random
from itertools import product

def cycles(stream, depth):
    q=list(stream); n=0
    while q:
        first=q.pop(0)
        for i,bank in enumerate(q[:depth-1]):
            if bank != first:
                q.pop(i); break
        n+=1
    return n

def measure(stream):
    a,b=cycles(stream,2),cycles(stream,4)
    return dict(adjacent=a,lookahead=b,headroom=float(Fraction(a,b)))

def audit():
    regimes={
      'clustered_win':[0,0,1,1]*128,
      'hotspot_no_win':[0]*512,
      'alternating_no_win':[0,1]*256,
    }
    results={k:measure(v) for k,v in regimes.items()}
    assert results['clustered_win']['headroom']>1
    assert results['hotspot_no_win']['headroom']==1
    assert results['alternating_no_win']['headroom']==1
    # Independent deterministic IID-skew transfer; exploratory, not preregistered.
    for hot in (0.5,0.75,0.9,0.99):
        rng=Random(9173)
        seq=[int(rng.random()>=hot) for _ in range(4096)]
        results[f'transfer_hot_{hot}']=measure(seq)
    # Three-bank exhaustive independent control.
    for n in range(2,9):
        for s in product(range(3),repeat=n):
            assert cycles(s,4)<=cycles(s,2), (n,s)
    # Equal-work, equal-bank-port throughput-per-area condition:
    # (A_look/A_adj)*(T_look/T_adj) < cycles_adj/cycles_look.
    threshold=Fraction(results['clustered_win']['adjacent'],results['clustered_win']['lookahead'])
    assert threshold==Fraction(257,256)
    assert not (Fraction(101,100)**2 < threshold)
    print(results)
    print('BOUND: combined area x clock penalty must be STRICTLY below',threshold)
    print('LIMIT: no mapped area, wire RC, extracted timing or GPU workload.')

if __name__=='__main__': audit()
