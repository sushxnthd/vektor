"""V317: semantic impossibility and matched-knowledge controls for B-read deletion.

Four-bit exhaustive dataflow model, not RTL or a GPU performance measurement.
The candidate may not silently access an unaccounted B-dependent value.
"""
from dataclasses import dataclass
from itertools import product

WIDTH = 4
MODULUS = 1 << WIDTH


def ab_op(a: int, b: int) -> int:
    return (a + 3 * b) % MODULUS


def bc_op(b: int, c: int) -> int:
    return b ^ c


def drop_b(a: int) -> int:
    """The actual information available after deleting B, without a replacement."""
    return ab_op(a, 0)


def remat_equal_a(a: int) -> int:
    return ab_op(a, a)


def remat_from_a_c(a: int, c: int) -> int:
    return ab_op(a, a ^ c)


def forward_b(a: int, value: int, ab_b_id: str, bc_b_id: str) -> int:
    """Identity is required, even if two unrelated registers happen to match."""
    if ab_b_id != bc_b_id:
        raise ValueError("different architectural register identities")
    return ab_op(a, value)


@dataclass(frozen=True)
class ResourceCost:
    b_bank_reads: int
    c_bank_reads: int
    xor_operations: int
    forwarded_values: int


# Matched compiler/collector baseline has the *same proof and information*.
# These are transaction counts for the modeled dataflow, not physical costs.
MATCHED_COSTS = {
    "proven_b_eq_a": ResourceCost(0, 0, 0, 0),
    "proven_b_eq_a_xor_c": ResourceCost(0, 1, 1, 0),
    "same_identity_forward_from_bc": ResourceCost(1, 1, 0, 1),
}


def two_world_witness():
    """Same visible A,C, different B, different AB result: no A-only repair."""
    a = c = 0
    b0, b1 = 0, 1
    assert ab_op(a, b0) != ab_op(a, b1)
    return {"visible_a": a, "visible_c": c, "hidden_b_worlds": [b0, b1],
            "required_ab_outputs": [ab_op(a, b0), ab_op(a, b1)],
            "candidate_output": drop_b(a)}


def exhaustive_audit():
    counts = {"unconstrained_worlds": 0, "invalid_drop_worlds": 0,
              "b_eq_a_worlds": 0, "b_eq_a_pass": 0,
              "b_eq_a_xor_c_worlds": 0, "b_eq_a_xor_c_pass": 0,
              "shared_identity_worlds": 0, "shared_identity_pass": 0,
              "distinct_identity_rejections": 0}
    for a, b, c in product(range(MODULUS), repeat=3):
        counts["unconstrained_worlds"] += 1
        expected = ab_op(a, b)
        counts["invalid_drop_worlds"] += (drop_b(a) != expected)
        if b == a:
            counts["b_eq_a_worlds"] += 1
            counts["b_eq_a_pass"] += (remat_equal_a(a) == expected)
        if b == (a ^ c):
            counts["b_eq_a_xor_c_worlds"] += 1
            counts["b_eq_a_xor_c_pass"] += (remat_from_a_c(a, c) == expected)
        # BC reads the *same* architectural B, so forwarding is a legal source.
        assert bc_op(b, c) == (b ^ c)
        counts["shared_identity_worlds"] += 1
        counts["shared_identity_pass"] += (forward_b(a, b, "R7", "R7") == expected)
        try:
            forward_b(a, b, "R7", "R8")
        except ValueError:
            counts["distinct_identity_rejections"] += 1
        else:
            raise AssertionError("false-sharing admission")
    assert counts == {
        "unconstrained_worlds": 4096, "invalid_drop_worlds": 3840,
        "b_eq_a_worlds": 256, "b_eq_a_pass": 256,
        "b_eq_a_xor_c_worlds": 256, "b_eq_a_xor_c_pass": 256,
        "shared_identity_worlds": 4096, "shared_identity_pass": 4096,
        "distinct_identity_rejections": 4096,
    }, counts
    return {"counts": counts, "two_world_witness": two_world_witness(),
            "candidate_vs_equal_knowledge_baseline": {
                name: {"candidate": vars(cost), "baseline": vars(cost),
                       "incremental_transaction_advantage": 0}
                for name, cost in MATCHED_COSTS.items()},
            "decision": "REJECT_UNQUALIFIED_B_DELETION_AS_ARCHITECTURE_MECHANISM",
            "evidence_tier": "EXHAUSTIVE_FOUR_BIT_SEMANTIC_MODEL_ONLY"}


if __name__ == "__main__":
    import json
    print(json.dumps(exhaustive_audit(), sort_keys=True, indent=2))
