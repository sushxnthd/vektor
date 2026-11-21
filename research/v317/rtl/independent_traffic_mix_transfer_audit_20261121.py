#!/usr/bin/env python3
"""Independent V317 traffic-floor adversarial audit. Development-only; no holdouts.

Checks that a proposed bandwidth ceiling is valid for each admitted workload
mix, not merely at the mean. Exact fractions prevent rounding-dependent gates.
No GPU measurement, synthesis, or physical signoff is implied.
"""
from fractions import Fraction as F
from itertools import product

def bound(work_rate, issue_capacity, byte_capacity, per_class_min_bytes, counts):
    assert work_rate > 0 and issue_capacity > 0 and byte_capacity > 0
    assert len(per_class_min_bytes) == len(counts) and len(counts) > 0
    assert all(x >= 0 for x in counts) and sum(counts) > 0
    assert all(x >= 0 for x in per_class_min_bytes)
    floor = sum(F(n)*F(b) for n,b in zip(counts,per_class_min_bytes))/sum(counts)
    issue = F(issue_capacity)/F(work_rate)
    return min(issue, F(byte_capacity)/(floor*F(work_rate))) if floor > 0 else issue

def audit():
    # A single workload-wide mean floor is unsound when workload mix shifts.
    baseline, issue, bw = F(50), F(100), F(1000)
    traffic = [F(2), F(30)]
    trained_mix = [1, 1]
    unseen_mix = [9, 1]
    train_floor = sum(F(n)*b for n,b in zip(trained_mix,traffic))/sum(trained_mix)
    naive = min(issue/baseline, bw/(train_floor*baseline))
    valid = bound(baseline,issue,bw,traffic,unseen_mix)
    assert naive == F(5,4)
    assert valid == 2 and naive < valid, "mean floor incorrectly generalized"
    # Every class-conditional floor yields a valid ceiling for its stated mix.
    for counts in product(range(5),repeat=2):
        if not sum(counts): continue
        expected_floor = sum(F(n)*b for n,b in zip(counts,traffic))/sum(counts)
        expected = min(issue/baseline,bw/(expected_floor*baseline))
        assert bound(baseline,issue,bw,traffic,counts) == expected
    # A zero-traffic class makes an unconditional positive traffic floor invalid.
    assert bound(baseline,issue,bw,[F(0),F(30)],[1,0]) == 2
    # Stronger claims require measured issue capacity, per-class traffic
    # lower bounds, and a preregistered prospective class-mix envelope.
    print("PASS: 24 exact-rational workload mixes; mean-floor transfer falsified")

if __name__ == "__main__":
    audit()
