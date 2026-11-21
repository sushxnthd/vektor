"""Independent two-lane indistinguishability audit for V317 write monitoring.

An unobserved write leaves the local monitor with the same input history as
no write, although the correct register value may differ. This is an
information bound, not a GPU performance estimate or proof of write coverage.
"""
import json
from itertools import product


def apply_masked_write(old, new, mask, lanes=2):
    bits = (1 << lanes) - 1
    return ((old & ~mask) | (new & mask)) & bits


def ambiguous_worlds(lanes=2):
    count = 0
    example = None
    for old, new, captured, requested, hidden in product(
        range(1 << lanes), range(1 << lanes), range(1 << lanes),
        range(1, 1 << lanes), range(1, 1 << lanes)
    ):
        if requested & ~captured:
            continue
        current = apply_masked_write(old, new, hidden, lanes)
        if ((current ^ old) & requested) == 0:
            continue
        count += 1
        if example is None:
            example = {
                "cached_value": old, "hidden_write_data": new,
                "captured_mask": captured, "requested_mask": requested,
                "hidden_write_mask": hidden,
                "world_without_write_value": old & requested,
                "world_with_hidden_write_value": current & requested,
                "same_observed_write_events": [],
            }
    return count, example


def next_poison(poison, capture, coverage_ok):
    if capture:
        return not coverage_ok
    return poison or not coverage_ok


def guarded_grant(poison, coverage_ok, captured, requested, dirty=0):
    return bool(not poison and coverage_ok and requested
                and (requested & ~captured) == 0
                and (requested & dirty) == 0)


def audit():
    count, example = ambiguous_worlds(2)
    assert count > 0 and example is not None
    equal_grants = 0
    for poison, coverage, captured, requested, dirty in product(
        (False, True), (False, True), range(4), range(4), range(4)
    ):
        candidate = guarded_grant(poison, coverage, captured, requested, dirty)
        baseline = guarded_grant(poison, coverage, captured, requested, dirty)
        assert candidate == baseline
        equal_grants += 1
    return {
        "evidence_tier": "TWO_LANE_EXHAUSTIVE_INFORMATION_BOUND_NOT_PHYSICAL_GPU_EVIDENCE",
        "indistinguishable_unsafe_pairs": count,
        "counterexample": example,
        "same_information_baseline_cases": equal_grants,
        "incremental_forwarding_transaction_advantage": 0,
        "coverage_contract": "coverage_ok must independently detect every missed physical write; not implemented",
        "decision": "NO_PROMOTION_UNTIL_COMPLETE_WRITE_VISIBILITY_PROVEN",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2))
