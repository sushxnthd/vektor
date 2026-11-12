"""Exact workload-mixture falsifier for V317/V296 physical claims.

Averaging per-workload speedups is not equivalent to pooled throughput.
Requires equal completed work per workload on baseline/candidate and identical
workload weights. No physical signoff is inferred from these calculations.
"""
from fractions import Fraction as Q
from itertools import product

def pooled_ratio(baseline, candidate, weights, area_b, area_c, period_b, period_c):
    """Each cycles vector is per identical work unit for both designs."""
    assert len(baseline) == len(candidate) == len(weights) and len(weights) > 0
    b = sum((Q(w)*Q(c) for w,c in zip(weights,baseline)),Q(0))
    c = sum((Q(w)*Q(d) for w,d in zip(weights,candidate)),Q(0))
    assert all(Q(x)>0 for x in baseline+candidate)
    assert all(Q(w)>=0 for w in weights) and sum(map(Q,weights))>0
    assert min(Q(area_b),Q(area_c),Q(period_b),Q(period_c))>0
    return b*Q(area_b)*Q(period_b)/(c*Q(area_c)*Q(period_c))

def per_workload_ratios(baseline,candidate,area_b,area_c,period_b,period_c):
    return [Q(b)*Q(area_b)*Q(period_b)/(Q(c)*Q(area_c)*Q(period_c))
            for b,c in zip(baseline,candidate)]

def predicted_boundary(baseline,candidate,area_b,area_c,period_b,period_c):
    """Two-regime mix: w of regime 0 and (1-w) of regime 1.
    Returns exact equality weight, or None when there is no unique boundary.
    """
    assert len(baseline)==len(candidate)==2
    k=Q(area_b)*Q(period_b)
    h=Q(area_c)*Q(period_c)
    d0=k*Q(baseline[0])-h*Q(candidate[0])
    d1=k*Q(baseline[1])-h*Q(candidate[1])
    return None if d0==d1 else -d1/(d0-d1)

def selftest():
    # Counterexample: arithmetic mean of speedups >1 but pooled result <1.
    b=[10,1000]; c=[5,1100]; w=[1,1]
    r=per_workload_ratios(b,c,1,1,1,1)
    assert sum(r)/2>1
    assert pooled_ratio(b,c,w,1,1,1,1)<1
    threshold=predicted_boundary(b,c,1,1,1,1)
    assert threshold==Q(100,105)
    assert pooled_ratio(b,c,[threshold,1-threshold],1,1,1,1)==1
    # Independent direct cross-product audit for 81 distinct configurations.
    count=0
    for a,t,x,y in product([1,Q(101,100),Q(11,10)],repeat=4):
        b=[10,1000];c=[5,1100]
        got=pooled_ratio(b,c,[x,y],1,a,1,t)
        lhs=(x*b[0]+y*b[1])
        rhs=(x*c[0]+y*c[1])*a*t
        assert (got>1)==(lhs>rhs)
        count+=1
    print('PASS: mixture reversal, exact frozen boundary,',count,'independent comparisons')

if __name__=='__main__': selftest()
