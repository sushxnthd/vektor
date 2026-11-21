#!/usr/bin/env python3
"""Discrete tile-budget falsification of continuous frequency/area proxy.
Uses archived electrically illegal routed values only; not GPU signoff.
"""
from fractions import Fraction as F

def count(budget, area, common=0):
    return int(F(budget)//(F(area)+F(common)))

def service(budget, area, freq, common=0):
    return count(budget,area,common)*F(freq)

def main():
    a0,a1,f0,f1=map(F,['21389.1','21533.0','446.10','454.59'])
    assert a1>a0 and f1>f0
    assert f1/a1>f0/a0
    assert count(a0,a0)==1 and count(a0,a1)==0
    assert count(2*a0,a0)==2 and count(2*a0,a1)==1
    assert service(2*a0,a1,f1)<service(2*a0,a0,f0)
    assert count(a1,a0)==count(a1,a1)==1
    assert service(a1,a1,f1)>service(a1,a0,f0)
    for common in [F(0),F(1000),F(10000)]:
        for n in range(1,65):
            b=n*(a0+common)
            assert count(b,a1,common)<=count(b,a0,common)
            assert count(b,a0,common)==n
            assert count(b,a1,common)<n
    assert f1/f0 < F(2)
    print('PASS: 192 exact discrete-budget counterexamples and equal-count control')
    print('frequency/area continuous ratio:',float((f1/a1)/(f0/a0)))
    print('two-baseline-tile budget service ratio:',float(service(2*a0,a1,f1)/service(2*a0,a0,f0)))
    print('NOT legal P&R, throughput or a calibrated tile model')
if __name__=='__main__': main()
