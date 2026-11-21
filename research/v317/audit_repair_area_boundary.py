#!/usr/bin/env python3
"""Exact routed-area repair boundary against compact greedy (not a new PPA run).

The published 2026-11-02 matched OpenROAD comparison has compact C=21314.6
and pairwise P=21324.7 um2; both electrically illegal. This checker calculates
how much *differential* repair would be needed even to meet a 2% materiality
criterion. Common tile overhead H and repair costs rc/rp are nonnegative.
"""
from decimal import Decimal, getcontext
getcontext().prec = 32
D=Decimal
C,P=D('21314.6'),D('21324.7')
TARGET=D('0.02')

def required_compact_repair(pairwise_repair=D(0),common_overhead=D(0)):
    """Minimum compact-only repair area rc needed for P+rp <= .98*(C+rc+H)+H."""
    return (P+pairwise_repair-(D(1)-TARGET)*C+TARGET*common_overhead)/(D(1)-TARGET)

def saving(rc=D(0),rp=D(0),h=D(0)):
    return D(1)-(P+rp+h)/(C+rc+h)

def main():
    assert P>C
    assert saving()<0
    for h in (D(0),D('1000'),D('10000'),D('100000')):
        assert saving(h=h)<0
        rc=required_compact_repair(common_overhead=h)
        assert saving(rc=rc,h=h) >= TARGET-D('1e-25')
        assert saving(rc=rc-D('0.001'),h=h)<TARGET
        print(f'H={h} um2: compact-only repair required >= {rc:.6f} um2; '
              f'pairwise area held fixed; target={TARGET*100}%')
    assert required_compact_repair(D('98'))-required_compact_repair()==D('100')
    print(f'Raw pairwise area disadvantage: {P-C} um2; raw saving: {saving()*100:.8f}%')
    print('PASS: differential-repair boundary and common-overhead monotonicity')
    print('LIMIT: No actual electrical repair, signoff, power, or GPU throughput measured.')

if __name__=='__main__': main()
