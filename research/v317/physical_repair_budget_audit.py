#!/usr/bin/env python3
"""Independent physical repair-budget audit; no physical closure is inferred.

Reads the pinned three-way routed artifact, never estimates repair costs.
For pairwise P and compact C, repaired pairwise can be smaller only if
repair_cost_compact - repair_cost_pairwise > P.area - C.area.
This is a necessary condition, not a prediction or a sufficient win gate.
"""
import json
from decimal import Decimal
from pathlib import Path

DATA = Path(__file__).with_name("STRONG_BASELINE_THREE_WAY_AUDIT_20261102.json")

def audit(data):
    v = data["variants"]
    p, c = v["pairwise"], v["compact"]
    area = lambda x: Decimal(str(x["area_um2"]))
    gap = area(p) - area(c)
    assert gap > 0, "Pinned compact dominance no longer holds"
    for name, x in v.items():
        legal_from_raw = (
            x["route_exit"] == 0
            and x["route_drc_violations"] == 0
            and x["hold_violations"] == 0
            and x["max_cap_violations"] == 0
            and Decimal(str(x["setup_slack_ps"])) >= 0
            and Decimal(str(x["hold_slack_ps"])) >= 0
        )
        assert legal_from_raw == x["legal"], f"{name}: legality flag inconsistent"
    assert not p["legal"] and not c["legal"]
    return gap

def repaired_pairwise_smaller(gap, compact_repair, pairwise_repair):
    c = Decimal(str(compact_repair))
    p = Decimal(str(pairwise_repair))
    if c < 0 or p < 0:
        raise ValueError("Repair area must be nonnegative")
    return c - p > gap

def self_test():
    gap = Decimal("10.1")
    assert not repaired_pairwise_smaller(gap, "10.1", 0)
    assert repaired_pairwise_smaller(gap, "10.1001", 0)
    assert not repaired_pairwise_smaller(gap, 0, 0)
    assert not repaired_pairwise_smaller(gap, 20, 10)
    assert repaired_pairwise_smaller(gap, 20, 9)
    try:
        repaired_pairwise_smaller(gap, -1, 0)
        raise AssertionError("negative repair accepted")
    except ValueError:
        pass

if __name__ == "__main__":
    self_test()
    data = json.loads(DATA.read_text())
    gap = audit(data)
    print(f"Raw pairwise minus compact area: {gap} um^2")
    print(f"Necessary reversal: compact repair area minus pairwise repair area > {gap} um^2")
    print("Both raw routes electrically illegal; repair costs unknown.")
    print("No legal area ordering, performance, clock, or GPU throughput is certified.")
