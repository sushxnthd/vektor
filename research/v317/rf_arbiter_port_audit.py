"""Independent source-level audit of Vektor's four-slot RF bank arbiter.

Two independent operand reads per instruction; two read ports per bank.
This is not RTL simulation, placed timing, or measured GPU performance.
"""
from collections import Counter
from itertools import product
import json
import random

SLOTS = 4
PORTS = 2


def rtl_priority_model(valid, pairs):
    """Literal translation of used_once/used_twice in rf_bank_arbiter.sv."""
    once, twice, grant = set(), set(), 0
    for i, (b0, b1) in enumerate(pairs):
        if not (valid >> i) & 1:
            continue
        if b0 == b1:
            if b0 not in once:
                grant |= 1 << i
                once.add(b0)
                twice.add(b0)
        elif b0 not in twice and b1 not in twice:
            grant |= 1 << i
            for b in (b0, b1):
                if b in once:
                    twice.add(b)
                else:
                    once.add(b)
    return grant


def bank_demands(grant, pairs):
    """Independent oracle: equal bank indices still require two reads."""
    counts = Counter()
    for i, (b0, b1) in enumerate(pairs):
        if (grant >> i) & 1:
            counts[b0] += 1
            counts[b1] += 1
    return counts


def legal(grant, valid, pairs):
    return (grant & ~valid) == 0 and all(
        n <= PORTS for n in bank_demands(grant, pairs).values()
    )


def safe_priority_model(valid, pairs):
    grant = 0
    for i in range(SLOTS):
        candidate = grant | (1 << i)
        if (valid >> i) & 1 and legal(candidate, valid, pairs):
            grant = candidate
    return grant


def optimal_grant(valid, pairs):
    """Exact max-cardinality subset with deterministic tie break."""
    best = 0
    for subset in range(1 << SLOTS):
        if legal(subset, valid, pairs):
            if subset.bit_count() > best.bit_count() or (
                subset.bit_count() == best.bit_count() and subset > best
            ):
                best = subset
    return best


def audit_case(valid, pairs):
    raw = rtl_priority_model(valid, pairs)
    safe = safe_priority_model(valid, pairs)
    optimal = optimal_grant(valid, pairs)
    assert legal(safe, valid, pairs)
    assert legal(optimal, valid, pairs)
    assert safe.bit_count() <= optimal.bit_count()
    assert raw & ~valid == 0
    assert raw == safe, "RTL translation differs from conservative priority oracle"
    return {
        "overgrant": not legal(raw, valid, pairs),
        "raw_grants": raw.bit_count(),
        "safe_grants": safe.bit_count(),
        "optimal_grants": optimal.bit_count(),
        "raw_mask": raw,
        "safe_mask": safe,
        "optimal_mask": optimal,
        "max_raw_bank_demand": max(bank_demands(raw, pairs).values(), default=0),
    }


def sweep():
    failing = ((0, 0), (0, 0), (0, 0), (0, 0))
    passing = ((0, 0), (1, 1), (0, 0), (1, 1))
    frozen = {
        "predicted_fail": audit_case(3, failing),
        "predicted_pass": audit_case(3, passing),
    }
    # Preserve failed prediction; do not change the frozen protocol.
    exhaustive = Counter()
    witness = None
    suboptimal_witness = None
    for valid in range(16):
        for flat in product(range(2), repeat=8):
            pairs = tuple((flat[2*i], flat[2*i+1]) for i in range(SLOTS))
            x = audit_case(valid, pairs)
            exhaustive["cases"] += 1
            exhaustive["overgrant_cases"] += int(x["overgrant"])
            exhaustive["raw_granted_slots_in_overgrant_cases"] += (
                x["raw_grants"] if x["overgrant"] else 0
            )
            exhaustive["safe_grants_total"] += x["safe_grants"]
            exhaustive["optimal_grants_total"] += x["optimal_grants"]
            exhaustive["safe_suboptimal_cases"] += int(
                x["safe_grants"] < x["optimal_grants"]
            )
            exhaustive["max_raw_bank_demand"] = max(
                exhaustive["max_raw_bank_demand"], x["max_raw_bank_demand"]
            )
            if x["overgrant"] and witness is None:
                witness = {"valid": valid, "pairs": pairs, **x}
            if x["safe_grants"] < x["optimal_grants"] and suboptimal_witness is None:
                suboptimal_witness = {"valid": valid, "pairs": pairs, **x}

    rng = random.Random(31711)
    random_cases = Counter()
    for _ in range(10_000):
        valid = rng.randrange(16)
        pairs = tuple((rng.randrange(4), rng.randrange(4)) for _ in range(SLOTS))
        x = audit_case(valid, pairs)
        random_cases["cases"] += 1
        random_cases["overgrant_cases"] += int(x["overgrant"])
        random_cases["safe_suboptimal_cases"] += int(
            x["safe_grants"] < x["optimal_grants"]
        )
        random_cases["safe_grants_total"] += x["safe_grants"]
        random_cases["optimal_grants_total"] += x["optimal_grants"]
    return {
        "evidence_tier": "SOURCE_LEVEL_PORT_CAPACITY_NOT_RTL_SIM_OR_PHYSICAL",
        "assumptions": {
            "independent_operand_reads": 2,
            "read_ports_per_bank": PORTS,
            "sharing_without_operand_identity": False,
        },
        "frozen": frozen,
        "exhaustive_two_bank": dict(exhaustive),
        "first_witness": witness,
        "first_suboptimal_witness": suboptimal_witness,
        "random_four_bank": dict(random_cases),
    }


if __name__ == "__main__":
    print(json.dumps(sweep(), indent=2, sort_keys=True))
