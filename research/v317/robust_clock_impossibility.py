#!/usr/bin/env python3
"""Exact rational robustness certificate for V317's restricted two-cycle oracle.
No GPU throughput or electrical legality is inferred.
"""
from fractions import Fraction
from sys import argv

P_COEFF = {3:153, 4:212, 5:61, 6:4}
G_COEFF = {1:2, 2:404, 3:3511, 4:6536, 5:4139, 6:1060, 7:112, 8:4}

def falling(n, k):
    v = 1
    for i in range(k):
        v *= n-i
    return v

def polynomial(b, coefficients):
    return Fraction(sum(v*falling(b,k) for k,v in coefficients.items()), b**8)

def certificate(b, d):
    assert b >= 2 and d >= 0
    p, g = polynomial(b, P_COEFF), polynomial(b, G_COEFF)
    assert 0 <= p <= 1 and 2 <= g <= 4
    # R(q) = (1 + q*p/(2+q*(g-2)))/(1+d).
    # dR/dq >= 0: derivative of the positive term = 2p/(2+q(g-2))**2.
    max_delay = p/g
    denom = p-d*(g-2)
    q_min = 2*d/denom if denom > 0 else None
    possible = q_min is not None and q_min < 1
    if possible:
        assert p > d*g
    else:
        assert p <= d*g
    return p,g,max_delay,q_min,possible

def main():
    d = Fraction(argv[1]) if len(argv)>1 else Fraction(1,200)
    print("bank_count,opportunity_probability,greedy_expectation,max_clock_penalty,q_threshold,positive_win_possible")
    for b in (4,8,12,16,32,48,64):
        p,g,dmax,qmin,possible = certificate(b,d)
        print(f"{b},{float(p):.10f},{float(g):.10f},{float(dmax):.10f},{float(qmin):.10f}" if qmin is not None else f"{b},{float(p):.10f},{float(g):.10f},{float(dmax):.10f},undefined",end="")
        print(f",{possible}")
    assert certificate(8,Fraction(1,200))[4]
    assert not certificate(16,Fraction(1,200))[4]

if __name__ == "__main__":
    main()
