#!/usr/bin/env python3
"""Sensitivity audit for the V317 independent-uniform bank assignment law."""
from fractions import Fraction
import argparse
COEFF={3:153,4:212,5:61,6:4}
def falling(n,k):
    x=1
    for j in range(k): x*=n-j
    return x
def opportunity(b):
    assert b>=2
    return Fraction(sum(c*falling(b,k) for k,c in COEFF.items()),b**8)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--clock-penalty',type=float,default=.005)
    a=parser.parse_args()
    assert 0<=a.clock_penalty<1
    print('banks,independent_fraction,opportunity_probability,optimistic_net_upper_bound')
    for b in (4,8,12,16,32,48,64):
        for q in (Fraction(0),Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)):
            p=q*opportunity(b)
            upper=(1+float(p))/(1+a.clock_penalty)
            print(f'{b},{float(q):.2f},{float(p):.9f},{upper:.9f}')
    assert opportunity(16)>opportunity(48)
    assert (1+float(opportunity(48)))/1.005<1
if __name__=='__main__': main()
