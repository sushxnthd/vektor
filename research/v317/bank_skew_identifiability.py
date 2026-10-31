#!/usr/bin/env python3
"""V317: exact bank-skew counterexample to aggregate RF no-win inference.

All rates are *optimistic resource-envelope ceilings*, not simulated or measured
GPU IPC. Bank mapping, cache hits, and dynamic demand are not inferred from SASS.
"""
from __future__ import annotations

from fractions import Fraction as F
import json


def bank_rate(ports: tuple[F, ...], reads: tuple[F, ...],
              issue: F, alu: F) -> F:
    """Ideal steady-state rate with independent bank capacities."""
    if len(ports) != len(reads) or not ports:
        raise ValueError("nonempty equal-length banks required")
    if issue <= 0 or alu <= 0 or any(p <= 0 for p in ports):
        raise ValueError("positive capacities required")
    if any(d < 0 for d in reads):
        raise ValueError("nonnegative demand required")
    limits = [issue, alu]
    limits.extend(p / d for p, d in zip(ports, reads) if d)
    return min(limits)


def candidate_gain(ports: tuple[F, ...], reads: tuple[F, ...],
                   removed: tuple[F, ...], issue: F, alu: F,
                   issue_overhead: F = F(0), alu_overhead: F = F(0),
                   period_penalty: F = F(0)) -> F:
    """Shared ports; candidate only removes demand, and may pay overhead."""
    if len(removed) != len(reads):
        raise ValueError("removal vector length mismatch")
    if any(k < 0 or k > d for k, d in zip(removed, reads)):
        raise ValueError("removal cannot exceed existing demand")
    if min(issue_overhead, alu_overhead, period_penalty) < 0:
        raise ValueError("nonnegative overhead required")
    base = bank_rate(ports, reads, issue, alu)
    new_reads = tuple(d - k for d, k in zip(reads, removed))
    new = bank_rate(ports, new_reads,
                    issue / (1 + issue_overhead),
                    alu / (1 + alu_overhead)) / (1 + period_penalty)
    return new / base


def aggregate_gain(ports: tuple[F, ...], reads: tuple[F, ...],
                   removed: tuple[F, ...], issue: F, alu: F) -> F:
    """The *invalid for independent banks* pooled-port approximation."""
    return candidate_gain((sum(ports),), (sum(reads),),
                          (sum(removed),), issue, alu)


def sufficient_no_win(ports: tuple[F, ...], reads: tuple[F, ...],
                      issue: F, alu: F) -> bool:
    """Sufficient no-win condition for read-removal-only, nonnegative overhead."""
    return bank_rate(ports, reads, issue, alu) == min(issue, alu)


PORTS = (F(2), F(2))
ISSUE = ALU = F(5, 4)
REMOVED = (F(1, 2), F(0))
NO_WIN = (F(3, 2), F(3, 2))
WIN = (F(5, 2), F(1, 2))


def exhaustive_half_unit_worlds() -> list[dict]:
    """All six admissible allocations with total demand 3, step 1/2."""
    worlds = []
    for bank0_units in range(1, 7):
        reads = (F(bank0_units, 2), F(6 - bank0_units, 2))
        gain = candidate_gain(PORTS, reads, REMOVED, ISSUE, ALU)
        worlds.append({
            "reads": [str(x) for x in reads],
            "banked_gain_exact": str(gain),
            "banked_gain_float": float(gain),
            "aggregate_gain_exact": str(aggregate_gain(
                PORTS, reads, REMOVED, ISSUE, ALU)),
            "sufficient_no_win": sufficient_no_win(PORTS, reads, ISSUE, ALU),
        })
    return worlds


def report() -> dict:
    worlds = exhaustive_half_unit_worlds()
    gains = [F(w["banked_gain_exact"]) for w in worlds]
    assert sum(NO_WIN) == sum(WIN) == F(3)
    assert candidate_gain(PORTS, NO_WIN, REMOVED, ISSUE, ALU) == 1
    assert candidate_gain(PORTS, WIN, REMOVED, ISSUE, ALU) == F(5, 4)
    assert aggregate_gain(PORTS, NO_WIN, REMOVED, ISSUE, ALU) == 1
    assert aggregate_gain(PORTS, WIN, REMOVED, ISSUE, ALU) == 1
    return {
        "schema": "vektor.v317.banked_rf_identifiability.v1",
        "evidence_tier": "synthetic_exact_resource_envelope_counterexample",
        "physical_gpu_measurements": False,
        "ports_per_bank": [str(p) for p in PORTS],
        "issue_capacity": str(ISSUE),
        "alu_capacity": str(ALU),
        "total_reads_per_instruction": "3",
        "bank0_removed_reads": "1/2",
        "predicted_no_win_gain": "1",
        "observed_analytic_no_win_gain": str(candidate_gain(
            PORTS, NO_WIN, REMOVED, ISSUE, ALU)),
        "predicted_win_gain": "5/4",
        "observed_analytic_win_gain": str(candidate_gain(
            PORTS, WIN, REMOVED, ISSUE, ALU)),
        "aggregate_prediction_both_worlds": "1",
        "enumerated_worlds": worlds,
        "exact_gain_min": str(min(gains)),
        "exact_gain_max": str(max(gains)),
        "decision": "aggregate_only_no_win_not_identifiable_for_banked_RF",
        "limitations": ("No real SASS or physical bank mapping; "
                        "no dynamic cache hit rates, latency, PPA, or measured IPC."),
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
