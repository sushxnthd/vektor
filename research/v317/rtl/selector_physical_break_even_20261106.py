#!/usr/bin/env python3
"""V317 selector physical break-even falsification; no RTL/route claims.

Input counts are archived exact toy-model admissions (6561 four-request
configurations). This script evaluates necessary throughput conditions,
NOT sufficient physical viability. No empirical timing is inferred.
"""
from fractions import Fraction

N = 6561
CONTENTION = 15387
MINIMUM = 15315
FIXED = 14391
assert CONTENTION - MINIMUM == 72
assert CONTENTION - FIXED == 996

def ratio(candidate, baseline, candidate_period=Fraction(1), baseline_period=Fraction(1),
          candidate_active=Fraction(1), baseline_active=Fraction(1)):
    """Service per wall-clock time including occupancy/backpressure duty factors."""
    return (Fraction(candidate, baseline) *
            Fraction(baseline_period, candidate_period) *
            Fraction(candidate_active, baseline_active))

def break_even_extra_period(candidate, baseline):
    """Largest fractional candidate clock-period increase for throughput > baseline."""
    return Fraction(candidate - baseline, baseline)

def break_even_active(candidate, baseline, period_ratio=Fraction(1)):
    """Minimum candidate active fraction / baseline active fraction to tie."""
    return Fraction(baseline, candidate) * period_ratio

def main():
    for name, base in [('minimum-contention', MINIMUM), ('fixed-priority', FIXED)]:
        h = break_even_extra_period(CONTENTION, base)
        print(name, 'admission_ratio=', float(Fraction(CONTENTION, base)),
              'maximum_period_penalty=', float(h),
              'minimum_relative_active_fraction=', float(break_even_active(CONTENTION, base)))
        assert ratio(CONTENTION, base, 1+h) == 1
        assert ratio(CONTENTION, base, 1+h+Fraction(1, 100000)) < 1
    # Even 0.5% period penalty eliminates the 0.4701% incremental
    # gain against the strongest low-complexity equal-port control.
    assert ratio(CONTENTION, MINIMUM, Fraction(201, 200)) < 1
    # Equal-period 0.5% lower useful-cycle fraction also kills it.
    assert ratio(CONTENTION, MINIMUM, candidate_active=Fraction(199, 200)) < 1
    # A one-cycle bubble per 200 cycles (199/200 duty) suffices.
    # Conversely zero period penalty and no bubbles retains only a toy-model win.
    assert ratio(CONTENTION, MINIMUM) > 1
    print('PASS: exact break-even and adversarial timing/occupancy controls')

if __name__ == '__main__':
    main()
