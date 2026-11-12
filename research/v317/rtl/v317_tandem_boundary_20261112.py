#!/usr/bin/env python3
"""Prospective exact throughput boundary for a deterministic two-stage pipeline.

A request consumes a compute stage of duration a followed by a bank stage of
duration b. Different requests may occupy different stages concurrently.
Candidate bank stage b/R, both stage durations scaled by clock factor c.
This is a restricted mathematical model, NOT a GPU physical signoff.
"""
from fractions import Fraction as F
from itertools import product


def exact_makespan(n, a, b):
    assert n >= 1 and a > 0 and b > 0
    return a + b + (n-1)*max(a,b)


def simulated_makespan(n, a, b):
    done_a = done_b = F(0)
    for _ in range(n):
        done_a += a
        done_b = max(done_a, done_b) + b
    return done_b


def speedup(n, a, b, r, c):
    a,b,r,c = map(F,(a,b,r,c))
    assert r >= 1 and c > 0
    return exact_makespan(n,a,b)/(c*exact_makespan(n,a,b/r))


def break_even_clock(n,a,b,r):
    return speedup(n,a,b,r,1)


def asymptotic_ceiling(a,b,r,c):
    a,b,r,c=map(F,(a,b,r,c))
    return max(a,b)/(c*max(a,b/r))


def main():
    for n,a,b,r,c in product((1,2,3,17), (F(1),F(3,2),F(4)),
                             (F(1,2),F(2),F(7)), (F(1),F(3,2),F(4)),
                             (F(1),F(101,100))):
        assert exact_makespan(n,a,b)==simulated_makespan(n,a,b)
        measured=simulated_makespan(n,a,b)/(c*simulated_makespan(n,a,b/r))
        assert speedup(n,a,b,r,c)==measured
        assert (speedup(n,a,b,r,c)>1)==(c<break_even_clock(n,a,b,r))
    # Compute bottleneck: no throughput win after any clock penalty.
    assert asymptotic_ceiling(4,1,2,F(101,100))<1
    # Bank bottleneck: doubling service gives nearly 2x before clock loss.
    assert asymptotic_ceiling(1,4,2,F(101,100))==F(200,101)
    # Bank speedup saturates once compute becomes the bottleneck.
    assert asymptotic_ceiling(2,4,100,1)==2
    # No bank acceleration can beat the compute-stage floor.
    assert asymptotic_ceiling(2,4,100,1)==asymptotic_ceiling(2,4,2,1)
    print('PASS: exact finite-N pipeline law and independent event simulation')
    print('PASS: break-even clock boundary, bottleneck migration, saturation')
    print('Model: S_N=[a+b+(N-1)max(a,b)]/[c(a+b/R+(N-1)max(a,b/R))]')
    print('Scope: deterministic tandem stages; no queues, memory contention, or routed hardware')


if __name__=='__main__':
    main()
