#!/usr/bin/env python3
"""Exact correlated-mixture oracle clock boundary, restricted two-cycle batch model.

Not a GPU throughput estimate. Mixture chooses iid bank assignment with
probability q; otherwise all eight operands map to one common bank.
"""
from fractions import Fraction

EVENT = {3: 153, 4: 212, 5: 61, 6: 4}
GREEDY = {1: 2, 2: 404, 3: 3511, 4: 6536, 5: 4139, 6: 1060, 7: 112, 8: 4}

def falling(b, k):
    x = 1
    for i in range(k):
        x *= b - i
    return x

def expectation(coeff, b):
    assert b >= 2
    return Fraction(sum(v * falling(b, k) for k, v in coeff.items()), b ** 8)

def exact_net(b, q, delta):
    assert 0 <= q <= 1 and delta >= 0
    p = expectation(EVENT, b)
    g = expectation(GREEDY, b)
    # All eight operands on one bank: one complete request per cycle.
    mixed_g = q * g + (1-q) * 2
    return (1 + q*p/mixed_g) / (1+delta)

def minimum_q(b, delta):
    """Strict net win requires q > threshold, if denominator positive."""
    p, g = expectation(EVENT, b), expectation(GREEDY, b)
    denom = p - delta*(g-2)
    return None if denom <= 0 else 2*delta/denom

def main():
    d = Fraction(1, 200)
    print("B,q,E_g_iid,P_event_iid,net_exact,q_min")
    for b in (4, 8, 12, 16, 32, 48, 64):
        p, g = expectation(EVENT,b), expectation(GREEDY,b)
        threshold = minimum_q(b,d)
        for q in (Fraction(0), Fraction(1,4), Fraction(1)):
            net = exact_net(b,q,d)
            print(f"{b},{q},{float(g):.9f},{float(p):.9f},{float(net):.9f},{threshold}")
            assert (net > 1) == (q > threshold if threshold is not None else False)
            # Earlier optimistic bound used E[G]>=1; valid but loose.
            assert net <= (1+q*p)/(1+d)
        assert g >= 2
    assert exact_net(8,Fraction(1,4),d) > 1
    assert exact_net(12,Fraction(1,4),d) < 1
    assert exact_net(16,Fraction(1),d) < 1
    assert exact_net(48,Fraction(1),d) < 1
    print("PASS exact rational correlated-mixture boundary")

if __name__ == "__main__":
    main()
