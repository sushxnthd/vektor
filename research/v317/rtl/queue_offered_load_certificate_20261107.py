"""Independent offered-load stability certificate for V317 queue experiments.

The generator produces 3 Bernoulli(0.68) requests/cycle, each with two
independent operands. Operand bank zero has probability h+(1-h)/3.
A bank has exactly two read ports/cycle. This is a necessary flow bound,
not a sufficient stability proof or a measured GPU result.
Run: python research/v317/rtl/queue_offered_load_certificate_20261107.py
"""
from fractions import Fraction

ARRIVALS = 3 * Fraction(68,100)
OPERANDS = 2
PORTS = 2
BANKS = 3

def hot_load(h):
    h=Fraction(h)
    p0=h+(1-h)/BANKS
    return ARRIVALS*OPERANDS*p0

def capacity_ratio(h):
    return hot_load(h)/PORTS

def critical_hot():
    # 3*.68*2*(1+2*h)/3 = 2
    return (Fraction(PORTS*BANKS,1)/(ARRIVALS*OPERANDS)-1)/2

def unavoidable_backlog_growth(h):
    # Necessary long-run growth of unserved bank-zero operand demand;
    # not a request-queue lower bound because a request consumes two reads.
    return max(Fraction(0),hot_load(h)-PORTS)

def main():
    assert critical_hot()==Fraction(4,17)
    assert hot_load(0)==Fraction(34,25)*1  # 1.36
    assert hot_load(Fraction(3,10))==Fraction(272,125) # 2.176
    assert hot_load(Fraction(7,10))==Fraction(408,125) # 3.264
    assert capacity_ratio(0)<1
    assert capacity_ratio(Fraction(3,10))>1
    assert capacity_ratio(Fraction(7,10))>1
    print('h,expected_bank0_reads_per_cycle,bank0_utilization,unavoidable_excess_reads_per_cycle')
    for h in (Fraction(0),Fraction(3,10),Fraction(7,10)):
        print(f'{float(h):.1f},{float(hot_load(h)):.6f},{float(capacity_ratio(h)):.6f},{float(unavoidable_backlog_growth(h)):.6f}')
    print('critical_hot=',critical_hot(),'PASS')
if __name__=='__main__':
    main()
