"""Independent V317 dual-port correctness and negative integration witness.

Semantic model, not a performance simulator or physical signoff.
"""
from __future__ import annotations

import json
from itertools import product


def grant(captured: int, requested: int, dirty: int, live: int,
          coverage: bool = True) -> bool:
    return bool(coverage and requested and
                not (requested & ~captured) and
                not (requested & (dirty | live)))


def union_hits(mask0: int, hit0: bool, mask1: int, hit1: bool) -> int:
    return (mask0 if hit0 else 0) | (mask1 if hit1 else 0)


def exhaustive_audit() -> dict:
    worlds = 0
    unsafe_dual = 0
    unsafe_one_port = 0
    extra_rejections = 0
    # Two lanes, all capture/request/write masks and independent namespaces.
    for captured, requested, mask0, mask1 in product(range(4), repeat=4):
        for hit0, hit1 in product((False, True), repeat=2):
            observed0 = mask0 if hit0 else 0
            observed_both = union_hits(mask0, hit0, mask1, hit1)
            # An observed write to a requested lane may change its value.
            # Worst-case adversary chooses a changed value on every such lane.
            dual = grant(captured, requested, 0, observed_both)
            single = grant(captured, requested, 0, observed0)
            stale_possible = bool(requested & observed_both)
            worlds += 1
            unsafe_dual += bool(dual and stale_possible)
            unsafe_one_port += bool(single and stale_possible)
            extra_rejections += bool(single and not dual)
            # Independent same-information reference: inspect both writes
            # separately, without calling union_hits or grant.
            reference = bool(requested and (requested & captured) == requested
                             and (not hit0 or not (requested & mask0))
                             and (not hit1 or not (requested & mask1)))
            if dual != reference:
                raise AssertionError("dual-port predicate differs from reference")
    if unsafe_dual or not unsafe_one_port or not extra_rejections:
        raise AssertionError("expected safe dual / unsafe single-port integration")
    return {
        "evidence_tier": "EXHAUSTIVE_TWO_LANE_SEMANTIC_NOT_PHYSICAL",
        "worlds": worlds,
        "unsafe_dual_admissions": unsafe_dual,
        "unsafe_single_port_integration_admissions": unsafe_one_port,
        "single_port_extra_admissions": extra_rejections,
        "incremental_same_information_transaction_advantage": 0,
    }


if __name__ == "__main__":
    print(json.dumps(exhaustive_audit(), sort_keys=True, indent=2))
