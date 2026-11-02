#!/usr/bin/env python3
"""V317 fixed-netlist extracted-RC clock-to-tile sensitivity.

Only the five prior routed controller paths are measured. Other-path clock
periods are hypothetical; no remapping, P&R, SRAM, IPC or GPU is simulated.
"""
from dataclasses import dataclass
from math import isclose
import json

@dataclass(frozen=True)
class Row:
    name: str
    source_slack_ps: float
    pair_slack_ps: float
    source_area_um2: float
    pair_area_um2: float

ROWS = (
    Row("seed7", -3.063, 106.304, 7426.72, 6595.20),
    Row("seed19", -5.487, 70.861, 7539.50, 6577.12),
    Row("seed37", -3.561, 60.487, 7367.67, 6586.69),
    Row("density005_seed7", -1.483, 101.692, 7539.24, 6609.04),
    Row("density035_seed7", -6.600, 72.408, 7407.83, 6577.91),
)

def period_ns(slack_ps):
    return 2.0 - slack_ps / 1000.0

def tile_clock_ratio(row, other_period_ns):
    if other_period_ns <= 0:
        raise ValueError("Other path period must be positive")
    source = max(other_period_ns, period_ns(row.source_slack_ps))
    pair = max(other_period_ns, period_ns(row.pair_slack_ps))
    return source / pair

def shifted_slack_ps(slack_ps, new_target_ns):
    """Fixed-netlist arithmetic ONLY; target-dependent P&R can change paths."""
    return slack_ps + 1000.0 * (new_target_ns - 2.0)

def evaluate():
    rows = []
    for r in ROWS:
        rows.append({
            "row": r.name,
            "source_period_ns": period_ns(r.source_slack_ps),
            "pair_period_ns": period_ns(r.pair_slack_ps),
            "pair_area_saving_pct": 100 * (1 - r.pair_area_um2 / r.source_area_um2),
            "static_source_slack_ps": {
                str(t): shifted_slack_ps(r.source_slack_ps, t)
                for t in (2.05, 2.2)
            },
            "hypothetical_tile_clock_ratio": {
                str(t): tile_clock_ratio(r, t)
                for t in (1.8, 1.95, 2.0, 2.05, 2.2)
            },
        })
    assert all(isclose(tile_clock_ratio(r, 2.05), 1.0, abs_tol=1e-12)
               and isclose(tile_clock_ratio(r, 2.2), 1.0, abs_tol=1e-12)
               for r in ROWS)
    assert all(shifted_slack_ps(r.source_slack_ps, 2.05) > 43 for r in ROWS)
    assert all(1 < tile_clock_ratio(r, 1.8) < 1.07 for r in ROWS)
    assert all(7 < x["pair_area_saving_pct"] < 14 for x in rows)
    return {
        "evidence_tier": "prior extracted-RC controller paths + fixed-netlist arithmetic + hypothetical other-tile clock",
        "rows": rows,
        "limitation": "No new routed clock target, no GPU tile, SRAM, measured IPC or power",
    }

if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
