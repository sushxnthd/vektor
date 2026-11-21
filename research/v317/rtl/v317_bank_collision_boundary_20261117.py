#!/usr/bin/env python3
"""Exact bank-conflict boundary for the committed strict-FIFO two-request RTL.

Independent bank draws are an explicit assumption; this is NOT a measured GPU
throughput or a physical V296 result. No reordering, one service port per bank.
"""
from fractions import Fraction
from itertools import product

def exact_pair_issue(bank_probs):
    assert sum(bank_probs) == 1 and all(p >= 0 for p in bank_probs)
    collision = sum(p*p for p in bank_probs)
    # Conditional on both requests valid and downstream ready.
    return Fraction(2) - collision

def enumerate_pair_issue(bank_probs):
    n = len(bank_probs)
    return sum(bank_probs[i]*bank_probs[j]*(1 + (i != j))
               for i,j in product(range(n), repeat=2))

def gain_per_area_clock(bank_probs, area_ratio, period_ratio):
    assert area_ratio > 0 and period_ratio > 0
    # Versus one-issue-per-cycle reference, assuming both banks service-ready.
    return exact_pair_issue(bank_probs) / (area_ratio*period_ratio)

def main():
    cases = {
        "uniform_four": [Fraction(1,4)]*4,
        "single_hot": [Fraction(1),Fraction(0),Fraction(0),Fraction(0)],
        "hot_75": [Fraction(3,4),Fraction(1,12),Fraction(1,12),Fraction(1,12)],
        "two_equal": [Fraction(1,2)]*2,
    }
    for name,p in cases.items():
        predicted = exact_pair_issue(p)
        independent = enumerate_pair_issue(p)
        assert predicted == independent
        # 1% area and 1% period penalty are hypothetical, not measured.
        adjusted = gain_per_area_clock(p,Fraction(101,100),Fraction(101,100))
        print(f"{name}: expected_grants={float(predicted):.9f} "
              f"gain_per_area_clock_hypothetical={float(adjusted):.9f}")
    # Collision probability alone is insufficient for temporal-correlated
    # streams: alternating banks always pair; same-bank runs do not.
    alt = [(i % 2,(i+1) % 2) for i in range(100)]
    runs = [(0,0) for _ in range(50)] + [(1,1) for _ in range(50)]
    assert sum(a != b for a,b in alt) == 100
    assert sum(a != b for a,b in runs) == 0
    print("PASS exact rational checks; temporal-correlation counterexample")

if __name__ == "__main__":
    main()
