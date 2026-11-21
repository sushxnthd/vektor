#!/usr/bin/env python3
"""Shared-output bandwidth falsification of the V317 zero-cost service oracle.

Synthetic deterministic finite-horizon queues, NOT GPU IPC or physical RTL.
Each cycle: inject arrivals, serve bank requests, then drain shared output.
The candidate has identical output bandwidth and hardware budget assumption;
capacity=2 is a deliberately generous (unimplemented) upper bound.
"""
from fractions import Fraction

def simulate(arrivals, bank_capacity, output_capacity, cycles):
    assert bank_capacity > 0 and output_capacity > 0 and cycles > 0
    assert len(arrivals) == cycles and all(isinstance(x, int) and x >= 0 for x in arrivals)
    bank_q = output_q = completed = 0
    for a in arrivals:
        bank_q += a
        served = min(bank_capacity, bank_q)
        bank_q -= served
        output_q += served
        drained = min(output_capacity, output_q)
        output_q -= drained
        completed += drained
    assert completed + bank_q + output_q == sum(arrivals)
    return completed, bank_q, output_q

def fluid_upper_ratio(arrival, base_bank, candidate_bank, shared_output, clock_penalty=0):
    """Long-run saturated/open-loop rate bound; not a finite-window equality."""
    r,b,c,o,d = map(Fraction,(arrival,base_bank,candidate_bank,shared_output,clock_penalty))
    assert r >= 0 and min(b,c,o) > 0 and d >= 0
    baseline = min(r,b,o)
    candidate = min(r,c/(1+d),o)
    return None if baseline == 0 else candidate/baseline

def test():
    n=1000
    saturated=[3]*n
    for arrival, out, expected in [(saturated,1,(1000,1000)),
                                   (saturated,2,(1000,2000)),
                                   ([1]*n,2,(1000,1000)),
                                   ([0]*900+[3]*100,1,(100,100))]:
        base=simulate(arrival,1,out,n)
        cand=simulate(arrival,2,out,n)
        assert (base[0],cand[0]) == expected, (base,cand,expected)
    assert fluid_upper_ratio(3,1,2,1) == 1
    assert fluid_upper_ratio(3,1,2,2) == 2
    assert fluid_upper_ratio(1,1,2,2) == 1
    assert fluid_upper_ratio(3,1,2,1,Fraction(1,100)) == 1
    # Conservation and common-output cap, including burst and alternating demand.
    for arrivals in ([3]*n, [3 if i%2 else 0 for i in range(n)],
                     [0]*500+[4]*500):
        for capacity in (1,2,4):
            for output in (1,2):
                done,bq,oq=simulate(arrivals,capacity,output,n)
                assert done <= n*output
                assert done+bq+oq == sum(arrivals)
    print("PASS: shared-output bottleneck falsifies bank-only oracle throughput gain")
    print("Saturated, output=1: baseline/candidate=1000/1000")
    print("Saturated, output=2: baseline/candidate=1000/2000")
    print("Common output=1 with 1% candidate clock penalty: asymptotic ratio=1")

if __name__ == "__main__":
    test()
