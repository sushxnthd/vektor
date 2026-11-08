#!/usr/bin/env python3
"""V317 prospective throughput boundary, analytic falsification only (not RTL evidence).

Frozen BEFORE RTL evaluation. Equal-resource comparisons require measured
clock periods and bank/return service traces. This script computes necessary
upper bounds, never claims realized GPU speedup.
"""
import argparse
import json
from math import isfinite

# Prospective regimes. Workload traces and physical timing remain unseen.
REGIMES = {
    "predicted_win": dict(compatibility=0.80, overlap=0.05, occupancy=0.90,
                          bank_pressure=0.30, return_pressure=0.30, overhead=0.04),
    "predicted_no_win": dict(compatibility=0.15, overlap=0.50, occupancy=0.50,
                             bank_pressure=0.90, return_pressure=0.90, overhead=0.12),
}

def bound(x, clock_ratio, extra_issue=1.0):
    """Upper bound on throughput ratio; shared ports and time scaling charged.

    compatibility*(1-overlap)*occupancy bounds eligible fusion;
    overhead reduces candidate issue efficiency. Shared port pressure
    limits *both* designs to the same per-cycle port ceiling. A faster
    issue path cannot increase that ceiling.
    """
    if not all(isfinite(v) for v in [clock_ratio, extra_issue, *x.values()]):
        raise ValueError("nonfinite parameter")
    if clock_ratio <= 0 or extra_issue < 0 or not all(0 <= v <= 1 for v in x.values()):
        raise ValueError("invalid parameter")
    eligible = x["compatibility"] * (1-x["overlap"]) * x["occupancy"]
    nominal = 1 + extra_issue * eligible
    candidate_issue = nominal * (1-x["overhead"])
    # Baseline has one issue per cycle. A pressure of 1 means ports
    # are fully saturated at baseline demand and cannot improve.
    port_ceiling = 1 / max(x["bank_pressure"], x["return_pressure"], 1e-12)
    candidate_cycle = min(candidate_issue, port_ceiling)
    return {"eligible_fraction": eligible,
            "candidate_cycle_upper": candidate_cycle,
            "clock_adjusted_upper": candidate_cycle / clock_ratio,
            "positive_possible": candidate_cycle > clock_ratio}

def selftest():
    assert bound(REGIMES["predicted_win"], 1.0)["positive_possible"]
    assert not bound(REGIMES["predicted_no_win"], 1.0)["positive_possible"]
    x = dict(REGIMES["predicted_win"], bank_pressure=1.0)
    assert bound(x, 1.0)["clock_adjusted_upper"] == 1.0
    assert not bound(REGIMES["predicted_win"], 2.0)["positive_possible"]
    assert bound(REGIMES["predicted_win"], 1.0)["clock_adjusted_upper"] >= 1
    print("PASS: prospective regimes and bandwidth/clock falsification controls")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-period-over-baseline", type=float, default=1.0)
    a = ap.parse_args()
    selftest()
    print(json.dumps({k: bound(v, a.candidate_period_over_baseline)
                      for k,v in REGIMES.items()}, indent=2))
