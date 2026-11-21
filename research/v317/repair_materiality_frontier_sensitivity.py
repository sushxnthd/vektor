#!/usr/bin/env python3
"""V317 routed-area repair frontier, conditional on pinned pre-repair areas.

No electrical legality or throughput is inferred. This is a necessary area
condition for a future matched electrically legal repair experiment.
"""
from dataclasses import dataclass
import math

COMPACT_AREA = 21314.6
PAIRWISE_AREA = 21324.7
MATERIALITY = 0.02

@dataclass(frozen=True)
class Frontier:
    compact_total: float
    pairwise_total: float
    saving: float
    area_win: bool
    material_win: bool

def evaluate(compact_repair: float, pairwise_repair: float) -> Frontier:
    if not (math.isfinite(compact_repair) and math.isfinite(pairwise_repair)
            and compact_repair >= 0 and pairwise_repair >= 0):
        raise ValueError("Repair increments must be finite and nonnegative")
    c = COMPACT_AREA + compact_repair
    p = PAIRWISE_AREA + pairwise_repair
    s = (c - p) / c
    return Frontier(c, p, s, s > 0, s >= MATERIALITY)

def minimum_compact_repair_for_materiality(pairwise_repair: float) -> float:
    if not math.isfinite(pairwise_repair) or pairwise_repair < 0:
        raise ValueError("Invalid repair increment")
    return (PAIRWISE_AREA + pairwise_repair) / (1 - MATERIALITY) - COMPACT_AREA

def self_test():
    assert not evaluate(0, 0).area_win
    assert evaluate(11, 0).area_win
    assert not evaluate(11, 0).material_win
    for p in (0, 10, 100, 1000):
        t = minimum_compact_repair_for_materiality(p)
        assert t > p
        assert not evaluate(t - .01, p).material_win
        assert evaluate(t + .01, p).material_win
        assert math.isclose(evaluate(t, p).saving, MATERIALITY, abs_tol=1e-12)
    for r in (0, 1, 100, 1000, 10000):
        assert not evaluate(r, r).area_win
    for bad in (float("nan"), float("inf"), -1):
        try:
            evaluate(bad, 0)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid repair accepted")
    print("PASS: conditional repair-frontier sensitivity tests")
    print("Initial pairwise area disadvantage:", round(PAIRWISE_AREA-COMPACT_AREA, 3), "um^2")
    print("Minimum compact-only repair for 2% saving:",
          round(minimum_compact_repair_for_materiality(0), 3), "um^2")
    print("No electrical closure, power or workload speedup inferred.")

if __name__ == "__main__":
    self_test()
