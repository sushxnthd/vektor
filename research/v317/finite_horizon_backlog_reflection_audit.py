#!/usr/bin/env python3
"""Exact finite-horizon queue accounting. Synthetic only; not GPU evidence."""
from itertools import product

def simulate(arrivals, capacity, initial=0):
    q=initial; done=0
    for a in arrivals:
        q+=a
        served=min(q,capacity)
        q-=served; done+=served
    return done,q

def independent_identity(arrivals,capacity,initial=0):
    # Lindley reflection: Q_T is maximum of total residual,
    # suffix residuals, and zero. Arrival precedes service each slot.
    n=len(arrivals)
    q=max([0,initial+sum(arrivals)-capacity*n]+[
        sum(arrivals[k:])-capacity*(n-k) for k in range(n)])
    return initial+sum(arrivals)-q,q

def test():
    cases=0
    for n in range(1,7):
        for seq in product(range(3),repeat=n):
            for cap in (0,1,2,3):
                for initial in (0,1,3):
                    observed=simulate(seq,cap,initial)
                    expected=independent_identity(seq,cap,initial)
                    assert observed==expected,(seq,cap,initial,observed,expected)
                    assert sum(observed)==initial+sum(seq)
                    cases+=1
    early=(100,)+(0,)*99
    late=(0,)*99+(100,)
    assert simulate(early,1)[0]==100
    assert simulate(late,1)[0]==1
    assert simulate(late,2)[0]==2
    print(f"PASS {cases} exhaustive queue/independent-reflection comparisons")
if __name__=="__main__":test()
