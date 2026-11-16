#!/usr/bin/env python3
"""Falsify extrapolating a one-cycle pair-grant expectation to sustained IPC.

Strict FIFO, two issue slots, one service port per bank, always ready.
The previous 2-sum(p_i**2) law applies to an independently sampled PAIR,
not necessarily the distribution of queue heads after variable-size dequeue.
No RTL/physical performance claims are made.
"""
from fractions import Fraction
from itertools import product

def cycles(stream):
    i = t = 0
    while i < len(stream):
        t += 1
        i += 2 if i+1 < len(stream) and stream[i] != stream[i+1] else 1
    return t

def prod(xs):
    z = Fraction(1)
    for x in xs:
        z *= x
    return z

def iid_expected_cycles(n, probs):
    # Exhaustive, exact expectation; valid only for small n.
    return sum((Fraction(cycles(s)) * prod(probs[b] for b in s)
                for s in product(range(len(probs)), repeat=n)), Fraction())

def main():
    p = (Fraction(1,2), Fraction(1,2))
    conditional_grants = 2-sum(x*x for x in p)
    assert conditional_grants == Fraction(3,2)
    # Exact finite-stream counterexample: expectation of cycles is not
    # N / conditional_grants, because rejected younger requests are retained.
    for n in (2, 4, 6, 8, 10):
        ec = iid_expected_cycles(n, p)
        naive = Fraction(n,1)/conditional_grants
        print(f'n={n}: exact_E_cycles={ec} naive_N_over_E_grants={naive} delta={ec-naive}')
        assert ec != naive
    # Same bank marginals; different temporal structure.
    alt = [i % 2 for i in range(256)]
    clustered = [0]*128 + [1]*128
    assert cycles(alt) == 128
    assert cycles(clustered) == 255
    print('PASS: alternating 128 cycles, clustered 255 cycles; same bank marginals')

if __name__ == '__main__': main()
