"""V317 conservative forwarding freshness check, exhaustive two-lane model.

This is a semantic model, not a GPU timing or physical-bank model. A producer
captures an immutable per-lane value vector. A sticky dirty mask observes ALL
writes to the physical warp/register while that producer remains live.
"""
from dataclasses import dataclass
from itertools import product
import json


@dataclass(frozen=True)
class Snapshot:
    warp: int
    reg: int
    bank: int
    captured: int
    data: int
    dirty: int
    valid: bool = True


def forwarding_allowed(cache: Snapshot, warp: int, reg: int,
                       bank: int, requested: int) -> bool:
    """Conservative sufficient condition for bit-exact reuse, not necessity."""
    return bool(cache.valid and requested and cache.warp == warp
                and cache.reg == reg and cache.bank == bank
                and (requested & ~cache.captured) == 0
                and (requested & cache.dirty) == 0)


def masked_equal(a: int, b: int, mask: int) -> bool:
    return (a & mask) == (b & mask)


def audit():
    total = legal = safe_accepted = unsafe_safe = naive_accepted = naive_bad = naive_wrong_values = 0
    unsafe_examples = []
    for cw, rw, cr, rr, cb, rb in product(range(2), repeat=6):
        for captured, requested, dirty, old, current in product(
                range(4), (1, 2, 3), range(4), range(4), range(4)):
            # For a stable physical namespace, lanes without intervening writes
            # cannot change. A different namespace is independently valued.
            same_location = (cw, cr, cb) == (rw, rr, rb)
            if same_location and not masked_equal(old, current, 3 & ~dirty):
                continue
            legal += 1
            cache = Snapshot(cw, cr, cb, captured, old, dirty)
            safe = forwarding_allowed(cache, rw, rr, rb, requested)
            naive = (cr == rr)  # previous textual-register identity approximation
            if safe:
                safe_accepted += 1
                if not masked_equal(old, current, requested):
                    unsafe_safe += 1
            if naive:
                naive_accepted += 1
                if not masked_equal(old, current, requested):
                    naive_wrong_values += 1
                if (not same_location or (requested & ~captured)
                        or not masked_equal(old, current, requested)):
                    naive_bad += 1
                    if len(unsafe_examples) < 3:
                        unsafe_examples.append({"cache": vars(cache),
                                                "consumer": [rw, rr, rb, requested],
                                                "current": current})
            total += 1
    assert total == legal and unsafe_safe == 0 and naive_bad > 0
    # Wraparound is a genuine stale-value witness for any finite tag width
    # without invalidation/lifetime control. A final write sets the lane to 1.
    wrap = []
    for width in (1, 2, 3, 4):
        writes = 1 << width
        initial_tag = 0
        tag = (initial_tag + writes) % (1 << width)
        stale = Snapshot(0, 0, 0, 1, 0, 1)
        assert tag == initial_tag and not forwarding_allowed(stale, 0, 0, 0, 1)
        wrap.append({"tag_bits": width, "writes": writes,
                     "tag_alias": True, "old_value": 0,
                     "current_value": 1, "dirty_gate_rejects": True})
    # An unrelated masked write need not invalidate the clean requested lane.
    masked_transfer = Snapshot(0, 0, 0, 3, 1, 2)
    assert forwarding_allowed(masked_transfer, 0, 0, 0, 1)
    assert not forwarding_allowed(masked_transfer, 0, 0, 0, 2)
    return {
        "evidence_tier": "EXHAUSTIVE_TWO_LANE_SEMANTIC_MODEL_NOT_GPU_RTL_TIMING",
        "enumerated_legal_worlds": total,
        "conservative_gate_accepted": safe_accepted,
        "conservative_gate_unsafe_admissions": unsafe_safe,
        "naive_register_name_admissions": naive_accepted,
        "naive_register_name_invalid_admissions": naive_bad,
        "naive_register_name_wrong_value_admissions": naive_wrong_values,
        "naive_invalid_examples": unsafe_examples,
        "finite_tag_wrap_witnesses": wrap,
        "disjoint_masked_write_transfer": {"clean_lane_accepted": True,
                                           "written_lane_rejected": True},
        "matched_reuse_aware_baseline_incremental_transaction_advantage": 0,
        "decision": "REJECT_NAME_ONLY_FORWARDING_AND_UNQUALIFIED_VERSION_TAGS"
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2))
