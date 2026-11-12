#!/usr/bin/env python3
"""Exact break-even workload-share certificate; restricted V317 synthetic model."""
from fractions import Fraction as F
from robust_clock_impossibility import polynomial, P_COEFF, G_COEFF

def margin(b, q, d):
    """Expected additional completions minus clock cost per batch."""
    g = 2 + q * (polynomial(b, G_COEFF) - 2)
    e = q * polynomial(b, P_COEFF)
    return e - d * g

def boundary(win_b, lose_b, d, q_win=F(1), q_lose=F(1)):
    a, z = margin(win_b, q_win, d), margin(lose_b, q_lose, d)
    assert a > 0 and z < 0, "Need one individually winning and one losing regime"
    return -z / (a-z)

def independent_audit():
    # Independent explicit count of two-regime weighted completion and clock cost.
    d=F(1,200)
    t=boundary(4,64,d)
    for w in (F(0),t-F(1,100000),t,t+F(1,100000),F(1)):
        regimes=((w,4),(1-w,64))
        base=sum((weight*polynomial(b,G_COEFF) for weight,b in regimes),F())
        extra=sum((weight*polynomial(b,P_COEFF) for weight,b in regimes),F())
        net=(base+extra)/(base*(1+d))
        sign=(net>1)-(net<1)
        assert sign == (w>t)-(w<t)
    assert t==F(4182118219409,29448873950865)
    return t

if __name__=="__main__":
    t=independent_audit()
    print("PASS: exact aggregate sign, zero-boundary equality, five workload-share checks")
    print("B4 batch-share break-even at 0.5% clock penalty:",t,float(t))
    for q in (F(1,4),F(1,2),F(1)):
        try:
            print("q4=q64=",q,"threshold=",float(boundary(4,64,F(1,200),q,q)))
        except AssertionError:
            print("q4=q64=",q,"no opposing-sign pair: threshold inapplicable")
