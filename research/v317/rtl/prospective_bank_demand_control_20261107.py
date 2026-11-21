#!/usr/bin/env python3
"""Exhaustive prospective bank-demand ordering control; no routed-RTL claim.

Four requests, each two bank reads from 3 banks, 2 ports/bank, cap=4.
Score only observed bank-demand vectors, never the oracle outcome. Every
workload is evaluated under the same physical port and output constraints.
"""
from collections import Counter
from itertools import product, permutations
from fractions import Fraction

BANKS=3
N=4
ORDERS=tuple(permutations(range(N)))

def admit(req, order):
    used=Counter(); n=0
    for i in order:
        d=Counter(req[i])
        if all(used[b]+v<=2 for b,v in d.items()):
            used.update(d); n+=1
    return n

def prospective(req):
    # Demand-weighted contention: total competing reads on the two banks.
    total=Counter(b for pair in req for b in pair)
    return tuple(sorted(range(N),key=lambda i:(sum(total[b] for b in req[i]),i)))

def run():
    total=Counter(); hist=Counter()
    for flat in product(range(BANKS),repeat=2*N):
        req=tuple((flat[2*i],flat[2*i+1]) for i in range(N))
        scores=[admit(req,o) for o in ORDERS]
        oracle=max(scores)
        fixed=scores[0]
        rot=Fraction(sum(admit(req,tuple(range(k,N))+tuple(range(k))) for k in range(N)),N)
        chosen=admit(req,prospective(req))
        total['cases']+=1
        for name,value in [('oracle',oracle),('fixed',fixed),('rotation',rot),('prospective',chosen)]:total[name]+=value
        hist[(chosen>rot,chosen<rot,chosen==oracle)]+=1
    print('cases',total['cases'])
    for name in ('oracle','fixed','rotation','prospective'):
        print(name,'mean',float(total[name]/total['cases']),'total',total[name])
    print('prospective_vs_rotation',float(total['prospective']/total['rotation']))
    print('oracle_vs_prospective',float(total['oracle']/total['prospective']))
    print('hist',sorted(hist.items()))
    assert total['cases']==3**8
    assert total['prospective']==15387 and total['oracle']==15435
    assert total['fixed']==14391 and total['rotation']==14391
    assert hist[(False,True,False)]==48
    return total

if __name__=='__main__':run()
