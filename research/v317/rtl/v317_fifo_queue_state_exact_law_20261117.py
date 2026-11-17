#!/usr/bin/env python3
"""Exact finite-stream queue-state law for strict FIFO 2-issue, one port/bank.

No physical/RTL performance inference. This replaces the invalid N/E[grants]
extrapolation with a state-aware expected completion-time recurrence.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


def cycles(stream):
    i = t = 0
    while i < len(stream):
        t += 1
        i += 2 if i + 1 < len(stream) and stream[i] != stream[i + 1] else 1
    return t


def exact_expected_cycles(n, probabilities):
    """E[T_n] with i.i.d. bank arrivals and retained blocked second head.

    F(m,b) = 1 + p_b F(m-1,b) + sum_{c!=b} p_c G(m-2),
    where G(k)=sum_b p_b F(k,b), F(0,b)=0, F(1,b)=1.
    A collision issues head b but retains next request b; a noncollision
    consumes both. m counts the head and all following requests.
    """
    p = tuple(F(x) for x in probabilities)
    assert p and all(x >= 0 for x in p) and sum(p) == 1
    @lru_cache(None)
    def head(m, b):
        if m == 0: return F(0)
        if m == 1: return F(1)
        return F(1) + p[b] * head(m-1,b) + sum(
            p[c] * fresh(m-2) for c in range(len(p)) if c != b)
    @lru_cache(None)
    def fresh(m):
        if m == 0: return F(0)
        return sum((p[b] * head(m,b) for b in range(len(p))), F(0))
    return fresh(n)


def independent_exhaustive(n, p):
    return sum((F(cycles(s)) * __import__('math').prod(p[b] for b in s)
                for s in product(range(len(p)), repeat=n)), F(0))


def main():
    for p in ((F(1,2), F(1,2)), (F(3,4), F(1,4)),
              (F(1,2), F(1,3), F(1,6))):
        for n in range(1, 9):
            observed = independent_exhaustive(n,p)
            predicted = exact_expected_cycles(n,p)
            assert predicted == observed, (p,n,predicted,observed)
        print('EXACT independent exhaustive cross-check PASS', p)
    p = (F(1,2), F(1,2))
    assert exact_expected_cycles(10,p) == F(3527,512)
    for n in (64,256,512):
        exact = exact_expected_cycles(n,p)
        naive = F(n,1) / (2-sum(x*x for x in p))
        print(f'n={n} exact={float(exact):.8f} naive={float(naive):.8f} relative_error={(float(naive/exact)-1):.6%}')
    alt = [i%2 for i in range(256)]
    clustered = [0]*128+[1]*128
    assert cycles(alt) == 128 and cycles(clustered) == 255
    print('TEMPORAL TRANSFER COUNTEREXAMPLE PASS: same marginals, 128 vs 255 cycles')
    print('PASS: exact queue-state law; physical credibility remains untested')

if __name__ == '__main__': main()
