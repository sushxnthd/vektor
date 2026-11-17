#!/usr/bin/env python3
"""Exact correlated-bank FIFO service law; synthetic reference, not GPU PPA.

Two banks, strict FIFO, at most two requests per cycle. A pair issues iff
its banks differ. Source banks follow a stationary symmetric Markov chain:
P(B[t+1] == B[t]) = q. No stalls; all requests available.

This is a prospective workload-correlation sensitivity control, NOT a
validated V296 datapath, physical timing, or GPU throughput claim.
"""
from fractions import Fraction as F
from itertools import product


def cycles(seq):
    i = c = 0
    while i < len(seq):
        c += 1
        i += 2 if i + 1 < len(seq) and seq[i] != seq[i + 1] else 1
    return c


def expected_cycles_enumerated(n, q):
    total = F(0)
    for seq in product((0, 1), repeat=n):
        p = F(1, 2)
        for a, b in zip(seq, seq[1:]):
            p *= q if a == b else 1 - q
        total += p * cycles(seq)
    return total


def expected_cycles_dp(n, q):
    # Conditional on the current head bank; symmetry makes its value immaterial.
    # Same next bank (probability q): issue one. Different: issue two.
    e = [F(0)] * (n + 1)
    for k in range(1, n + 1):
        e[k] = F(1) if k == 1 else 1 + q * e[k - 1] + (1 - q) * e[k - 2]
    return e[n]


def main():
    for q in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
        for n in range(1, 11):
            assert expected_cycles_dp(n, q) == expected_cycles_enumerated(n, q), (n, q)
        # Renewal-reward asymptotic: 2-q requests/cycle. Finite N has boundary loss.
        n = 10000
        predicted_rate = 2 - q
        finite_rate = F(n) / expected_cycles_dp(n, q)
        assert abs(finite_rate - predicted_rate) < F(1, 1000)
        print(f'q={q} rate_limit={predicted_rate} finite_n={n} rate={float(finite_rate):.6f}')
    print('PASS 50 exact enumerated Markov FIFO cases and asymptotic limits')


if __name__ == '__main__':
    main()
