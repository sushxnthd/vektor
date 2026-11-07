#!/usr/bin/env python3
"""V317 resource-conservation kill test, independent of scheduler policy.

A scheduling policy cannot complete more requests than offered, retire more
than one request per bank per cycle, or exceed the shared issue/return ports.
The bound is optimistic: no conflicts, dependencies, wire delay, or control cost.
"""
from fractions import Fraction

def upper_bound(arrivals, banks, shared_ports, cycles):
    assert cycles > 0 and shared_ports > 0 and len(arrivals) == len(banks)
    assert all(a >= 0 and b > 0 for a,b in zip(arrivals,banks))
    return min(sum(arrivals), cycles * shared_ports,
               sum(min(a, cycles*b) for a,b in zip(arrivals,banks)))

def bound_gain(arrivals, banks, ports, cycles, baseline_completed):
    assert 0 < baseline_completed <= upper_bound(arrivals,banks,ports,cycles)
    return Fraction(upper_bound(arrivals,banks,ports,cycles), baseline_completed)-1

def run():
    n=10000
    # Frozen predicted-no-win: saturated single shared return port and a
    # baseline already retiring one request each cycle.
    no_win=dict(arrivals=[n,n,n,n],banks=[1,1,1,1],ports=1,
                cycles=n,baseline=n)
    assert bound_gain(no_win['arrivals'],no_win['banks'],no_win['ports'],n,n)==0
    # Frozen possible-win (NOT predicted empirical win): baseline loses 20%
    # to arbitration; same physical resources have at most 25% headroom.
    possible=dict(arrivals=[n,n,n,n],banks=[1,1,1,1],ports=1,
                  cycles=n,baseline=8000)
    assert bound_gain(possible['arrivals'],possible['banks'],possible['ports'],n,8000)==Fraction(1,4)
    # Increasing compatibility cannot overcome a saturated return port.
    for compatibility in (Fraction(0),Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)):
        assert bound_gain([n]*4,[1]*4,1,n,n)==0
    # Even with four ports, bank-skew imposes a separate conservation ceiling.
    assert upper_bound([n*4,0,0,0],[1]*4,4,n)==n
    print('PASS: exact resource-conservation bounds; synthetic controls only')
    print('frozen no-win upper gain=0; possible-win upper gain=1/4')
    print('Neither control demonstrates a V317 speedup or physical viability.')
if __name__=='__main__': run()
