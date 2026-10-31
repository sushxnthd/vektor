#!/usr/bin/env python3
"""V310 independent exact strong-reuse-control admission falsifier.

Exhaustive over four physical registers (two aliases per bank), four issue
slots and every request-valid mask. No GPU performance or signoff inference.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path

REGISTERS = (0, 1, 2, 3)
BANK = {0: 0, 1: 0, 2: 1, 3: 1}
SLOTS = 4
PORTS = 2


def grant_counting(mask, src0, src1, reuse):
    """Constructive fixed-priority allocator with explicit per-bank ports."""
    demand = [0, 0]
    grant = 0
    for i in range(SLOTS):
        if not mask & (1 << i):
            continue
        reads = [BANK[src0[i]]]
        if not (reuse and src0[i] == src1[i]):
            reads.append(BANK[src1[i]])
        trial = demand.copy()
        for bank in reads:
            trial[bank] += 1
        if max(trial) <= PORTS:
            demand = trial
            grant |= 1 << i
    return grant


def grant_candidate_pairwise(mask, src0, src1):
    """Independent Python translation of the RTL pair/triple conflict logic."""
    a = tuple(BANK[x] for x in src0)
    b = tuple(BANK[x] for x in src1)
    d = tuple(x == y for x, y in zip(src0, src1))

    def pair(i, j):
        return not (((not d[i]) and a[i] == b[i] and
                     (a[j] == a[i] or b[j] == a[i])) or
                    ((not d[j]) and a[j] == b[j] and
                     (a[i] == a[j] or b[i] == a[j])))

    def triple(i, j, k):
        return ((a[i] in (a[j], b[j]) and a[i] in (a[k], b[k])) or
                (b[i] in (a[j], b[j]) and b[i] in (a[k], b[k])))

    grant = 0
    for slot in range(SLOTS):
        if not mask & (1 << slot):
            continue
        accepted = [i for i in range(slot) if grant & (1 << i)]
        if all(pair(i, slot) for i in accepted) and all(
            not triple(i, j, slot)
            for i, j in itertools.combinations(accepted, 2)
        ):
            grant |= 1 << slot
    return grant


def verify():
    checked = 0
    old_worse = old_equal = old_better = 0
    old_total = strong_total = candidate_total = 0
    # Four registers / two banks, two *distinct* physical IDs per bank.
    # All 4^8 operand configurations and all 16 valid masks: 1,048,576.
    for operands in itertools.product(REGISTERS, repeat=8):
        src0, src1 = operands[:4], operands[4:]
        for mask in range(16):
            old = grant_counting(mask, src0, src1, False)
            strong = grant_counting(mask, src0, src1, True)
            candidate = grant_candidate_pairwise(mask, src0, src1)
            if candidate != strong:
                raise AssertionError(
                    f"STRONG_CONTROL_MISMATCH mask={mask} a={src0} b={src1}"
                    f" candidate={candidate} strong={strong}"
                )
            oc, sc = old.bit_count(), strong.bit_count()
            old_worse += sc > oc
            old_equal += sc == oc
            old_better += sc < oc
            old_total += oc
            strong_total += sc
            candidate_total += candidate.bit_count()
            checked += 1
    assert checked == 1_048_576
    assert old_worse > 0 and old_better == 0
    assert candidate_total == strong_total and old_total < candidate_total

    # Adversarial bank alias: same bank does not imply same physical register.
    a = (0, 0, 0, 0)
    b = (1, 1, 1, 1)
    assert grant_counting(3, a, b, True) == 1
    assert grant_candidate_pairwise(3, a, b) == 1
    # Mutation control: a no-reuse implementation must be distinguishable.
    a = b = (0, 0, 0, 0)
    assert grant_counting(3, a, b, True) == 3
    assert grant_counting(3, a, b, False) == 1
    assert grant_candidate_pairwise(3, a, b) == 3
    return {
        "evidence_tier": "EXHAUSTIVE_REDUCED_DOMAIN_ADMISSION_FALSIFICATION",
        "physical_registers": 4,
        "banks": 2,
        "ports_per_bank": PORTS,
        "request_slots": SLOTS,
        "input_cases": checked,
        "strong_control_grant_mismatches": 0,
        "historical_no_reuse_worse_cases": old_worse,
        "historical_no_reuse_equal_cases": old_equal,
        "historical_no_reuse_better_cases": old_better,
        "historical_total_admissions": old_total,
        "strong_total_admissions": strong_total,
        "candidate_total_admissions": candidate_total,
        "candidate_vs_strong_admission_ratio": "1/1",
        "candidate_vs_historical_admission_ratio":
            f"{candidate_total}/{old_total}",
        "verdict": "REJECT_V310_INCREMENTAL_ADMISSION_NOVELTY",
        "not_established": [
            "GPU throughput", "full comparator/fanout RTL",
            "routed electrical signoff", "area/power superiority",
            "novel architecture"
        ]
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    data = json.dumps(verify(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
    print(data, end="")


if __name__ == "__main__":
    main()
