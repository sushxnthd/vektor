#!/usr/bin/env python3
"""Falsify applying a fusion-opportunity bound to arbitrary rescheduling.

A compatible-pair count M only bounds *additional* completions if every
candidate-only completion can be injectively charged to a measured pair.
A work-conserving scheduler may instead recover baseline idle cycles.
This script uses explicit service traces, not a claim of V317 speedup.
"""
from fractions import Fraction

def old_bound(T, C, N, M, H=0):
    return min(M, C * (T-H) - N)

def service(trace, C):
    assert all(0 <= n <= C for n in trace)
    return sum(trace)

def audit():
    # A deliberately non-work-conserving baseline leaves one free port idle.
    # No fusion opportunities exist; reordering alone recovers the idle slot.
    baseline = (1, 0)
    candidate = (1, 1)
    T, C, M, H = 2, 1, 0, 0
    N = service(baseline, C)
    actual_extra = service(candidate, C) - N
    claimed_extra = old_bound(T, C, N, M, H)
    assert actual_extra == 1 and claimed_extra == 0
    # Correct unconditional conservation ceiling: physical service only.
    unconditional = C * (T-H) - N
    assert actual_extra <= unconditional
    # The M-limited ceiling is valid only with an independently proved
    # injective mapping of each incremental completion to an opportunity.
    # With that premise, at most M distinct extra completions are possible.
    for capacity in range(1, 5):
        for baseline_count in range(capacity+1):
            for M in range(capacity+1):
                for candidate_count in range(capacity+1):
                    extras = candidate_count-baseline_count
                    if 0 <= extras <= M:
                        assert extras <= min(M, capacity-baseline_count)
    print("PASS: counterexample to unconditional compatibility bound")
    print("PASS: conditional injective-charge and capacity checks")
    print("No GPU RTL, measured traffic, or physical win is established.")

if __name__ == "__main__":
    audit()
