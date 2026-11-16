#!/usr/bin/env python3
"""Falsify the claim that depth-four bank lookahead preserves program order.

Two bank service ports and two issue slots are held fixed. Requests carry
monotone sequence numbers and an optional global ordering barrier. The original
lookahead recurrence is reproduced exactly; a guarded variant refuses to bypass
any skipped order-sensitive request. This is a semantic model, not RTL signoff.
"""
from itertools import product

def schedule(banks, depth, ordered=False):
    q=[(i,b) for i,b in enumerate(banks)]
    cycles=[]; bypasses=[]
    while q:
        first=q.pop(0)
        issued=[first]
        for j,(seq,bank) in enumerate(q[:depth-1]):
            if bank==first[1]:
                continue
            skipped=q[:j]
            if ordered and skipped:
                continue
            issued.append(q.pop(j))
            bypasses.extend((x[0],seq) for x in skipped)
            break
        cycles.append(issued)
    return cycles,bypasses

def flatten(cycles):
    return [seq for cycle in cycles for seq,_ in cycle]

def inversion_count(xs):
    return sum(xs[i]>xs[j] for i in range(len(xs)) for j in range(i+1,len(xs)))

def audit():
    # Bank clustering exposes an out-of-order issue in the original recurrence.
    stream=[0,0,1,1]*128
    adjacent,_=schedule(stream,2)
    lookahead,bypasses=schedule(stream,4)
    assert len(adjacent)==257 and len(lookahead)==256
    assert flatten(adjacent)==list(range(len(stream)))
    assert flatten(lookahead)!=list(range(len(stream)))
    assert inversion_count(flatten(lookahead))>0 and bypasses
    # If requests are externally visible ordered effects, the apparent
    # scheduling gain cannot be called equivalent without a reorder/commit
    # mechanism, hazard proof, or explicit relaxed-ordering contract.
    guarded,_=schedule(stream,4,ordered=True)
    assert len(guarded)==len(adjacent)
    assert flatten(guarded)==list(range(len(stream)))
    counterexamples=0
    for n in range(2,11):
        for banks in product((0,1),repeat=n):
            a,_=schedule(banks,2)
            l,_=schedule(banks,4)
            g,_=schedule(banks,4,ordered=True)
            assert sorted(flatten(l))==list(range(n))
            assert len(g)==len(a)
            assert flatten(g)==list(range(n))
            if inversion_count(flatten(l)):
                counterexamples+=1
    assert counterexamples>0
    print('PASS: ordered-commit counterexample; 257 vs 256 cycles on clustered bank stream')
    print('PASS: strict ordered issue restores 257 cycles; all binary streams lengths 2..10 checked')
    print('out_of_order_streams=',counterexamples)
    print('LIMIT: no physical reorder buffer, dependence analysis, power, timing, or RTL result')
if __name__=='__main__':
    audit()
