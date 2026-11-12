#!/usr/bin/env python3
"""Exact deterministic tandem-pipeline counterexample to an unqualified Amdahl ceiling.

Bank and compute stages operate concurrently on different requests. This is
NOT a GPU performance prediction: it tests whether a serial-fraction formula
can be called a universal upper bound without a no-overlap assumption.
"""
from fractions import Fraction


def makespan(n, compute, bank):
    assert n > 0 and compute > 0 and bank > 0
    compute_done = bank_done = Fraction(0)
    for _ in range(n):
        compute_done += compute
        bank_done = max(compute_done, bank_done) + bank
    return bank_done


def compare(n, compute, bank, improvement, clock=Fraction(1)):
    compute, bank, improvement, clock = map(Fraction, (compute, bank, improvement, clock))
    f = bank / (compute + bank)  # isolated-request fraction, NOT pipeline fraction
    serial_formula = 1 / (clock * (1 - f + f / improvement))
    baseline = makespan(n, compute, bank)
    candidate = clock * makespan(n, compute, bank / improvement)
    return f, serial_formula, baseline / candidate


def main():
    n = 10000
    f, bound, actual = compare(n, 1, 4, 2)
    assert f == Fraction(4, 5)
    assert bound == Fraction(5, 3)
    assert actual > bound, (bound, actual)
    f2, bound2, actual2 = compare(n, 4, 1, 2)
    assert actual2 < bound2, (bound2, actual2)
    assert Fraction(max(1, 4), max(1, 2)) == 2
    print('bank-bound: serial-formula=', float(bound), 'pipeline-speedup=', float(actual))
    print('compute-bound: serial-formula=', float(bound2), 'pipeline-speedup=', float(actual2))
    print('FALSIFIED: serial-fraction expression is not a universal upper bound with pipeline overlap')
    print('Scope: exact deterministic two-stage tandem model; no routed hardware evidence')


if __name__ == '__main__':
    main()
