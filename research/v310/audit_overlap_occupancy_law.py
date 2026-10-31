#!/usr/bin/env python3
"""Independent prospective V310 occupancy/overlap boundary falsifier.

No hardware speedup is inferred. The law is for two single-bank requests,
independent validity, overlap and verified duplicate flags.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import json
from pathlib import Path
import random

N = 200_000
TOL = 0.015
CASES = (
    ("overlap_medium", 31035, Fraction(3,4), Fraction(1,2), Fraction(3,5)),
    ("overlap_zero_no_win", 31036, Fraction(3,4), Fraction(0,1), Fraction(4,5)),
    ("overlap_hot", 31037, Fraction(3,5), Fraction(9,10), Fraction(7,10)),
)


def predicted(o: Fraction, h: Fraction, q: Fraction) -> Fraction:
    if o == 0:
        raise ValueError("zero offered load gives undefined throughput ratio")
    return 1 + o*h*q*q/(2-o*h)


def independent_count(valid0: bool, valid1: bool, bank1: int,
                      duplicate0: bool, duplicate1: bool) -> int:
    # A second implementation of the admission rule using explicit
    # two-port occupancy, rather than the RTL's pair/triple equations.
    ports = [0, 0]
    admitted = 0
    for valid, bank, duplicate in (
        (valid0, 0, duplicate0), (valid1, bank1, duplicate1)
    ):
        if not valid:
            continue
        reads = 1 if duplicate else 2
        if ports[bank] + reads <= 2:
            ports[bank] += reads
            admitted += 1
    return admitted


def run(name, seed, o, h, q):
    rng = random.Random(seed)
    base = new = 0
    for _ in range(N):
        v0, v1 = rng.random() < float(o), rng.random() < float(o)
        same = rng.random() < float(h)
        d0, d1 = rng.random() < float(q), rng.random() < float(q)
        b1 = 0 if same else 1
        base += independent_count(v0, v1, b1, False, False)
        new += independent_count(v0, v1, b1, d0, d1)
    expected = predicted(o,h,q)
    observed = new/base
    if abs(observed - float(expected)) > TOL:
        raise AssertionError(f"{name}: observed={observed}, frozen={expected}")
    beta = Fraction(9,10)
    d = Fraction(1,1)
    # A bandwidth-limited roofline illustration, not measured traffic.
    bottleneck_ratio = min(expected/d,beta) / min(Fraction(1,1),beta)
    if bottleneck_ratio != 1:
        raise AssertionError("bandwidth-saturated no-win control failed")
    return dict(regime=name, seed=seed, opportunities=N,
                offered_load=str(o), overlap_probability=str(h),
                verified_duplicate_probability=str(q),
                baseline_admissions=base, candidate_admissions=new,
                predicted_issue_ratio=str(expected),
                observed_issue_ratio=observed,
                absolute_error=abs(observed-float(expected)),
                bandwidth_limited_beta=str(beta),
                bandwidth_limited_predicted_speedup=str(bottleneck_ratio),
                verdict="PASS")


def selftest():
    assert predicted(Fraction(3,4),Fraction(1,2),Fraction(3,5)) == Fraction(352,325)
    assert predicted(Fraction(3,4),Fraction(0,1),Fraction(4,5)) == 1
    assert independent_count(True,True,0,False,False) == 1
    assert independent_count(True,True,0,True,True) == 2
    assert independent_count(True,True,1,False,False) == 2
    assert independent_count(True,True,0,True,False) == 1
    try:
        predicted(Fraction(0),Fraction(1),Fraction(1))
    except ValueError:
        pass
    else:
        raise AssertionError("zero-load ratio was not rejected")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    selftest()
    rows = [run(*case) for case in CASES]
    result = dict(evidence_tier="PROSPECTIVE_SYNTHETIC_ADMISSION_ONLY",
                  frozen_protocol="OCCUPANCY_OVERLAP_BANDWIDTH_LAW_PREREG_20261031.md",
                  real_gpu_throughput="NOT_MEASURED",
                  results=rows)
    text = json.dumps(result,indent=2,sort_keys=True)
    if args.output:
        Path(args.output).write_text(text+"\n")
    print(text)


if __name__ == "__main__":
    main()
