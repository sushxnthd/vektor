#!/usr/bin/env python3
"""V317 exact workload-mix aggregation audit; restricted two-cycle synthetic model."""
from fractions import Fraction as F
from robust_clock_impossibility import polynomial, P_COEFF, G_COEFF

def row(b,q):
    p,g=polynomial(b,P_COEFF),polynomial(b,G_COEFF)
    baseline=2+q*(g-2)
    opportunity=q*p
    return baseline,opportunity

def aggregate(regimes,d):
    # weights are proportions of *batches*, not proportions of completed work.
    assert sum((w for w,_,_ in regimes),F())==1
    base=sum((w*row(b,q)[0] for w,b,q in regimes),F())
    extra=sum((w*row(b,q)[1] for w,b,q in regimes),F())
    return (base+extra)/(base*(1+d)),extra/base,base,extra

def main():
    d=F(1,200)
    # Frozen, contrasting regimes; all weights and arithmetic exact.
    a=(F(1,2),4,F(1))
    b=(F(1,2),64,F(1))
    mixed=aggregate([a,b],d)
    individual=[aggregate([(F(1),r[1],r[2])],d) for r in (a,b)]
    naive=sum((r[0] for r in individual),F())/2
    weighted=sum((F(1,2)*row(r[1],r[2])[0]*individual[i][0] for i,r in enumerate((a,b))),F())/mixed[2]
    assert mixed[0]==weighted
    assert mixed[0]!=naive
    # Global win is controlled by baseline-completion-weighted opportunity.
    assert (mixed[0]>1)==(mixed[3]>d*mixed[2])
    print('regime B4 net ratio:',float(individual[0][0]))
    print('regime B64 net ratio:',float(individual[1][0]))
    print('naive batch-weighted average ratio:',float(naive))
    print('correct aggregate ratio:',float(mixed[0]))
    print('correct aggregate exact:',mixed[0])
    print('global threshold extra/base:',float(mixed[1]))
    # Deliberately include a case with nonuniform q; check identity.
    for q in (F(0),F(1,4),F(1,2),F(1)):
        regs=[(F(1,3),4,q),(F(2,3),16,F(1)-q)]
        x=aggregate(regs,d)
        assert (x[0]>1)==(x[3]>d*x[2])
    print('PASS: exact aggregate identity and four mixed-correlation controls')

if __name__=='__main__': main()
