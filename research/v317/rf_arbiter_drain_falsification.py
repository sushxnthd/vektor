"""Finite-queue falsification of the V317 RF arbiter's single-cycle gap.

No arrivals, no dependencies, no collector latency. Both schedulers have
identical banks, ports, and pending requests. Results are NOT GPU IPC.
"""
from collections import Counter
from functools import lru_cache
from itertools import product
import json
import random

from research.v317.rf_arbiter_port_audit import (
    legal, optimal_grant, rtl_priority_model,
)


def drain_cycles(valid, pairs, selector):
    """Count issue cycles until all initially valid requests complete."""
    cycles = 0
    while valid:
        grant = selector(valid, pairs)
        if not grant or not legal(grant, valid, pairs):
            raise AssertionError("invalid or non-progressing scheduler")
        valid &= ~grant
        cycles += 1
    return cycles


def independent_legal(grant, valid, pairs):
    """A second capacity oracle: count physical reads without arbiter state."""
    if grant & ~valid:
        return False
    for bank in range(16):
        reads = sum(
            int(x == bank)
            for i, pair in enumerate(pairs) if grant & (1 << i)
            for x in pair
        )
        if reads > 2:
            return False
    return True


def optimal_multicycle(valid, pairs):
    """Dynamic program over all legal issue subsets, not greedy cardinality."""
    @lru_cache(None)
    def solve(pending):
        if pending == 0:
            return 0
        return 1 + min(
            solve(pending & ~grant)
            for grant in range(1, 16)
            if (grant & pending) and independent_legal(grant, pending, pairs)
        )
    return solve(valid)


def case(valid, pairs):
    priority = drain_cycles(valid, pairs, rtl_priority_model)
    exact = drain_cycles(valid, pairs, optimal_grant)
    optimum = optimal_multicycle(valid, pairs)
    if priority < optimum or exact < optimum:
        raise AssertionError("multi-cycle oracle lower bound violated")
    return priority, exact, optimum


def summarize(iterator):
    counts = Counter()
    first_exact_worse = None
    first_exact_better = None
    for valid, pairs in iterator:
        priority, exact, optimum = case(valid, pairs)
        counts["cases"] += 1
        counts["priority_cycles"] += priority
        counts["exact_cycles"] += exact
        counts["optimal_cycles"] += optimum
        counts["exact_better"] += int(exact < priority)
        counts["exact_worse"] += int(exact > priority)
        counts["exact_tie"] += int(exact == priority)
        counts["greedy_suboptimal"] += int(priority > optimum)
        counts["exact_suboptimal"] += int(exact > optimum)
        if exact > priority and first_exact_worse is None:
            first_exact_worse = {
                "valid": valid, "pairs": pairs,
                "priority_cycles": priority, "exact_cycles": exact,
                "optimal_cycles": optimum,
            }
        if exact < priority and first_exact_better is None:
            first_exact_better = {
                "valid": valid, "pairs": pairs,
                "priority_cycles": priority, "exact_cycles": exact,
                "optimal_cycles": optimum,
            }
    return {
        "counts": dict(counts),
        "first_exact_worse": first_exact_worse,
        "first_exact_better": first_exact_better,
    }


def sweep():
    win_pairs = ((0, 0), (0, 1), (0, 1), (0, 0))
    no_win_pairs = ((0, 0), (1, 1), (0, 0), (0, 0))
    two_bank = (
        (valid, tuple((flat[2*i], flat[2*i+1]) for i in range(4)))
        for valid in range(16)
        for flat in product(range(2), repeat=8)
    )
    rng = random.Random(31711)
    four_bank = (
        (rng.randrange(16), tuple(
            (rng.randrange(4), rng.randrange(4)) for _ in range(4)
        ))
        for _ in range(10_000)
    )
    return {
        "evidence_tier": "SYNTHETIC_FINITE_BATCH_SERVICE_CYCLES_NOT_GPU_IPC",
        "frozen_predicted_first_cycle_win": {
            "priority_grant": rtl_priority_model(7, win_pairs),
            "exact_grant": optimal_grant(7, win_pairs),
            "drain_cycles": case(7, win_pairs),
        },
        "frozen_predicted_no_win": {
            "priority_grant": rtl_priority_model(3, no_win_pairs),
            "exact_grant": optimal_grant(3, no_win_pairs),
            "drain_cycles": case(3, no_win_pairs),
        },
        "exhaustive_two_bank": summarize(two_bank),
        "fixed_seed_four_bank_transfer": summarize(four_bank),
        "assumptions": {
            "bank_count": 16,
            "read_ports_per_bank": 2,
            "requests": 4,
            "independent_reads_per_request": 2,
            "new_arrivals": False,
            "dependencies": False,
            "collector_and_memory_latency": False,
        },
    }


if __name__ == "__main__":
    print(json.dumps(sweep(), indent=2, sort_keys=True))
