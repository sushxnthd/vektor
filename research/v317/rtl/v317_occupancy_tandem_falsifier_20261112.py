#!/usr/bin/env python3
"""Exact deterministic tandem model with candidate occupancy throttling.

Candidate starts one request every h compute-stage service slots instead of
one; bank service is accelerated R and clock period inflates by c. This is a
restricted initiation-interval model, not a GPU occupancy measurement.
"""
from fractions import Fraction as F
from itertools import product

def sim(n,a,b,h):
    ca=cb=F(0)
    for i in range(n):
        ca=max(ca, F(i)*h)+a
        cb=max(ca,cb)+b
    return cb

def closed(n,a,b,h):
    return a+b+(n-1)*max(a,b,h)

def speedup(n,a,b,r,c,h):
    return closed(n,a,b,a)/(c*closed(n,a,b/r,h))

def main():
    for n,a,b,r,c,hfactor in product((1,2,7,100),map(F,(1,2,4)),map(F,(1,3,7)),
                                     (F(1),F(3,2),F(4)),(F(1),F(101,100)),
                                     (F(1),F(5,4),F(2))):
        h=a*hfactor
        assert closed(n,a,b,h)==sim(n,a,b,h), (n,a,b,h)
        assert speedup(n,a,b,r,c,h)==sim(n,a,b,a)/(c*sim(n,a,b/r,h))
    n=10000; a=F(1); b=F(2); r=F(2); c=F(101,100)
    favorable=speedup(n,a,b,r,c,a)
    throttled=speedup(n,a,b,r,c,F(5,2))
    assert favorable>1 and throttled<1
    print('PASS: 648 exact finite-N model/event checks')
    print('favorable=',float(favorable),'throttled=',float(throttled))
    print('LAW: S_N=[a+b+(N-1)max(a,b)]/[c*(a+b/R+(N-1)max(a,b/R,h))]')
    print('SCOPE: deterministic saturated tandem, candidate initiation interval h>=a; no routed GPU evidence')
if __name__=='__main__':main()
