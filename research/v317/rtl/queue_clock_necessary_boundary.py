#!/usr/bin/env python3
"""V317 queue-to-clock necessary-condition audit (NOT a physical measurement).

For paired same-length service windows, candidate effective throughput exceeds
baseline only if (candidate_completed / baseline_completed) *
(candidate_useful_fraction / baseline_useful_fraction) *
(baseline_period / candidate_period) > 1.

The fixed seed-11 observations below are historical synthetic queue-model
counts. They are not RTL, power, GPU, or steady-state throughput measurements.
"""
from fractions import Fraction

OBSERVATIONS = {
    "uniform_seed11": (40916, 40910),
    "moderate_skew_seed11": (28782, 35764),
    "severe_skew_seed11": (20932, 24091),
}

def critical_period_ratio(candidate_completed, baseline_completed,
                          candidate_useful=Fraction(1),
                          baseline_useful=Fraction(1)):
    """Candidate must have T_candidate/T_baseline STRICTLY below result."""
    assert candidate_completed > 0 and baseline_completed > 0
    assert 0 < candidate_useful <= 1 and 0 < baseline_useful <= 1
    return (Fraction(candidate_completed, baseline_completed)
            * candidate_useful / baseline_useful)

def survives(candidate_completed, baseline_completed, candidate_period,
             baseline_period, candidate_useful=Fraction(1),
             baseline_useful=Fraction(1)):
    assert candidate_period > 0 and baseline_period > 0
    return (Fraction(candidate_period, baseline_period)
            < critical_period_ratio(candidate_completed, baseline_completed,
                                    candidate_useful, baseline_useful))

def main():
    print("Synthetic finite-window necessary timing boundary; no physical measurements")
    for name, (candidate, baseline) in OBSERVATIONS.items():
        boundary = critical_period_ratio(candidate, baseline)
        required_period_reduction = 100 * (1 - float(boundary))
        print(f"{name}: completed {candidate}/{baseline}; "
              f"T_candidate/T_FIFO < {float(boundary):.9f}; "
              f"required period reduction > {required_period_reduction:.4f}%")
        assert not survives(candidate, baseline, boundary, Fraction(1))
        assert survives(candidate, baseline, boundary * Fraction(999, 1000), Fraction(1))
    assert not survives(28782, 35764, Fraction(1), Fraction(1))
    assert not survives(28782, 35764, Fraction(4, 5), Fraction(1),
                        Fraction(9, 10), Fraction(1))
    assert survives(28782, 35764, Fraction(3, 4), Fraction(1))
    # More idle cycles cannot improve the required candidate timing boundary.
    assert critical_period_ratio(28782, 35764, Fraction(9, 10)) < critical_period_ratio(28782, 35764)
    print("exact-fraction boundary assertions PASS")

if __name__ == "__main__":
    main()
