#!/usr/bin/env python3
"""V310 independent prospective law check. Standard library only.

This checker models *admission* rather than GPU throughput. It deliberately
uses explicit per-bank port counts, not the RTL's pair/triple conflict logic.
Frozen regimes and seeds: see VERIFIED_READ_COALESCING_PREREG_20261031.md.
"""
from __future__ import annotations
import argparse
import json
import math
import random

REGIMES = (
    ("frozen_win", 31031, 0.75, 1.5625),
    ("frozen_no_win", 31032, 0.0, 1.0),
    ("unseen_low", 31033, 0.4, 1.16),
    ("unseen_high", 31034, 0.9, 1.81),
)
N = 100_000
TOL = 0.01


def greedy_count(valid: int, bank0: tuple[int, ...], bank1: tuple[int, ...],
                 duplicate: tuple[bool, ...]) -> tuple[int, int]:
    """Independent physical-port counting oracle for four slots."""
    demand = [0] * 16
    grant = 0
    for i in range(4):
        if not ((valid >> i) & 1):
            continue
        # Flag alone cannot coalesce distinct-bank requests.
        reads = [bank0[i]]
        if not (duplicate[i] and bank0[i] == bank1[i]):
            reads.append(bank1[i])
        if all(demand[b] + reads.count(b) <= 2 for b in set(reads)):
            for b in reads:
                demand[b] += 1
            grant |= 1 << i
    return grant, grant.bit_count()


def sample_regime(name: str, seed: int, q: float, prediction: float) -> dict:
    rng = random.Random(seed)
    new_total = old_total = both = 0
    for _ in range(N):
        d0 = rng.random() < q
        d1 = rng.random() < q
        d = (d0, d1, False, False)
        # Two active requests; both source banks of both requests are zero.
        _, old = greedy_count(0b0011, (0, 0, 0, 0), (0, 0, 0, 0),
                              (False, False, False, False))
        _, new = greedy_count(0b0011, (0, 0, 0, 0), (0, 0, 0, 0), d)
        old_total += old
        new_total += new
        both += int(d0 and d1)
        if new != 1 + int(d0 and d1) or old != 1:
            raise AssertionError("exact two-request boundary violated")
    observed = new_total / old_total
    # Standard deviation of 1 + Bernoulli(q^2), reported as a sampling
    # uncertainty, not a confidence interval for real GPU workloads.
    sigma = math.sqrt((q * q) * (1 - q * q) / N)
    if abs(observed - prediction) > TOL:
        raise AssertionError(f"{name}: {observed} vs frozen {prediction}")
    return dict(regime=name, seed=seed, q=q, n=N,
                predicted_issue_ratio=prediction, observed_issue_ratio=observed,
                empirical_both_duplicate=both / N, theoretical_standard_error=sigma,
                absolute_error=abs(observed - prediction), verdict="PASS")


def adversarial_controls() -> None:
    a = (0, 0, 0, 0)
    b = (0, 0, 0, 0)
    # Same BANK but different physical registers must never be coalesced.
    assert greedy_count(3, a, b, (False,) * 4) == (1, 1)
    assert greedy_count(3, a, b, (True, True, False, False)) == (3, 2)
    # Malformed duplicate flags with unequal banks must be ignored.
    a = (0, 0, 0, 0)
    b = (1, 1, 0, 0)
    assert greedy_count(3, a, b, (True,) * 4) == greedy_count(3, a, b, (False,) * 4)
    # A request with both sources on one bank consumes two ports unless
    # *verified* identical. Two such requests cannot both be admitted.
    assert greedy_count(3, (5, 5, 0, 0), (5, 5, 0, 0), (False,) * 4) == (1, 1)
    assert greedy_count(3, (5, 5, 0, 0), (5, 5, 0, 0), (True, True, False, False)) == (3, 2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    adversarial_controls()
    rows = [sample_regime(*regime) for regime in REGIMES]
    result = dict(evidence_tier="SYNTHETIC_ISSUE_ADMISSION_ONLY",
                  not_evidence_of="GPU_SPEEDUP_OR_PHYSICAL_TIMING",
                  independent_oracle="per_bank_port_demand",
                  frozen_prediction_date="2026-10-31",
                  adversarial_controls="PASS",
                  regimes=rows)
    s = json.dumps(result, sort_keys=True, indent=2)
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(s + "\n")
    print(s)


if __name__ == "__main__":
    main()
