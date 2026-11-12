#!/usr/bin/env python3
"""V317 conditional register-file capacity feasibility bound.

Dimensionless resource-envelope model, NOT a GPU simulator or measured speedup.
Cache-hit rates and dynamic read counts must be established independently.
A certified upper bound below materiality can reject an RF-demand mechanism.
A lower bound above materiality does NOT establish realizable GPU speedup.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from itertools import product
import json
import math


@dataclass(frozen=True)
class Range:
    lo: float
    hi: float

    def __post_init__(self):
        if not (math.isfinite(self.lo) and math.isfinite(self.hi) and self.lo <= self.hi):
            raise ValueError("invalid finite interval")


@dataclass(frozen=True)
class Envelope:
    logical_reads: float
    read_ports: float
    issue_width: float
    alu_capacity: float
    hit: Range
    extra_reads: Range
    avoided_fraction: Range
    alu_overhead: Range
    issue_overhead: Range
    period_penalty: Range

    def __post_init__(self):
        if min(self.logical_reads, self.read_ports, self.issue_width, self.alu_capacity) <= 0:
            raise ValueError("positive capacities and logical reads required")
        for x in (self.hit, self.avoided_fraction):
            if x.lo < 0 or x.hi > 1:
                raise ValueError("probabilities must be in [0,1]")
        for x in (self.extra_reads, self.alu_overhead, self.issue_overhead, self.period_penalty):
            if x.lo < 0:
                raise ValueError("nonnegative overhead/extra demand required")


def rates(e: Envelope, hit: float, extra: float, avoided: float,
          alu_over: float, issue_over: float, period: float) -> dict:
    demand = e.logical_reads * (1 - hit) + extra
    base_rf = e.read_ports / demand if demand > 0 else math.inf
    candidate_demand = demand * (1 - avoided)
    candidate_rf = e.read_ports / candidate_demand if candidate_demand > 0 else math.inf
    base = min(e.issue_width, e.alu_capacity, base_rf)
    candidate = min(e.issue_width / (1 + issue_over),
                    e.alu_capacity / (1 + alu_over), candidate_rf) / (1 + period)
    return {"baseline_rate": base, "candidate_rate": candidate,
            "ratio": candidate / base, "rf_reads_per_instruction": demand,
            "candidate_rf_reads_per_instruction": candidate_demand}


def bound(e: Envelope, materiality: float = 1.02) -> dict:
    if materiality < 1:
        raise ValueError("materiality must be >= 1")
    axes = (e.hit, e.extra_reads, e.avoided_fraction,
            e.alu_overhead, e.issue_overhead, e.period_penalty)
    # Exact within this nonnegative-overhead model: relative gain cannot
    # increase with cache-hit fraction, or decrease with extra reads or avoided
    # demand. Overheads cannot increase it. Correlate the same hit and extra
    # read values between baseline and candidate; do not compare unrelated
    # optimistic/pessimistic physical worlds.
    lower_args = (e.hit.hi, e.extra_reads.lo, e.avoided_fraction.lo,
                  e.alu_overhead.hi, e.issue_overhead.hi, e.period_penalty.hi)
    upper_args = (e.hit.lo, e.extra_reads.hi, e.avoided_fraction.hi,
                  e.alu_overhead.lo, e.issue_overhead.lo, e.period_penalty.lo)
    lo = rates(e, *lower_args)
    hi = rates(e, *upper_args)
    vertices = [rates(e, *v)["ratio"] for v in product(*((r.lo, r.hi) for r in axes))]
    assert math.isclose(lo["ratio"], min(vertices), rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(hi["ratio"], max(vertices), rel_tol=1e-12, abs_tol=1e-12)
    return {"schema": "vektor.v317.conditional_rf_capacity.v1",
            "evidence_tier": "assumption_conditional_analytic_envelope",
            "input": asdict(e), "gain_lower": lo["ratio"], "gain_upper": hi["ratio"],
            "materiality": materiality,
            "decision": ("reject_under_assumptions" if hi["ratio"] < materiality else
                         "conditionally_above_gate_not_validated" if lo["ratio"] >= materiality else
                         "indeterminate"),
            "baseline_rate_at_upper": hi["baseline_rate"],
            "candidate_rate_at_upper": hi["candidate_rate"],
            "note": "No real SASS, dynamic cache hits, RTL, timing or throughput measured."}


# Synthetic regimes. Explored locally before commit; NOT prospective GPU holdouts.
FROZEN = {
    "bank_limited_predicted_win": Envelope(2.4, 1, 4, 4, Range(0, .1), Range(0, 0),
        Range(.25, .35), Range(0, .02), Range(0, .01), Range(0, .01)),
    "cache_saturated_predicted_no_win": Envelope(2.4, 1, 4, 4, Range(.92, .98), Range(0, 0),
        Range(.25, .35), Range(0, .02), Range(0, .01), Range(0, .01)),
    "mid_reuse_sensitivity": Envelope(2.4, 1, 4, 2, Range(.45, .70), Range(0, .05),
        Range(.25, .35), Range(0, .04), Range(0, .02), Range(0, .02)),
}

if __name__ == "__main__":
    print(json.dumps({k: bound(v) for k, v in FROZEN.items()}, indent=2, sort_keys=True))
