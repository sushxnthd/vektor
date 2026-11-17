#!/usr/bin/env python3
"""Exact matched-resource physical break-even law; not routed evidence."""
from fractions import Fraction as F
from itertools import product

def ratio(cycles_baseline, cycles_candidate, period_baseline, period_candidate, area_baseline, area_candidate):
    c,p,tc,tp,ac,ap = [F(str(x)) for x in (cycles_baseline,cycles_candidate,period_baseline,period_candidate,area_baseline,area_candidate)]
    if min(c,p,tc,tp,ac,ap)<=0: raise ValueError("positive measurements required")
    return c*tc*ac/(p*tp*ap)

def required_cycle_reduction(period_ratio, area_ratio):
    t,a=F(str(period_ratio)),F(str(area_ratio))
    if min(t,a)<=0: raise ValueError("positive factors required")
    return 1-1/(t*a)

def fifo_cycles(banks, ports):
    if ports not in (1,2): raise ValueError("ports must be 1 or 2")
    i=cycles=0
    while i<len(banks):
        i+=2 if ports==2 and i+1<len(banks) and banks[i]!=banks[i+1] else 1
        cycles+=1
    return cycles

def self_test():
    assert ratio(100,50,1,1,100,100)==2
    assert ratio(100,100,1,F(101,100),100,101)==F(10000,10201)
    assert required_cycle_reduction(F(101,100),F(101,100))==F(201,10201)
    for n in range(1,9):
        for banks in product((0,1),repeat=n):
            assert fifo_cycles(banks,1)==n
            c=fifo_cycles(banks,2)
            assert (n+1)//2<=c<=n
            if all(banks[i]!=banks[i+1] for i in range(n-1)):
                assert c==(n+1)//2
    for t in (F(1),F(101,100),F(11,10)):
        for a in (F(1),F(101,100),F(11,10)):
            for reduction in (F(0),F(1,100),F(1,10),F(1,2)):
                assert (ratio(1,1-reduction,1,t,1,a)>1)==(reduction>required_cycle_reduction(t,a))
    print("PASS exact boundary and exhaustive FIFO bank streams through length 8")

if __name__=="__main__": self_test()
