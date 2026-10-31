#!/usr/bin/env python3
"""V317 exact atomic multi-bank coissue counterexample, synthetic only.

The candidate's eliminated read is hypothetical, not a demonstrated GPU
mechanism. These are optimal finite-workload cycles, NOT measured GPU IPC.
"""
from __future__ import annotations
from functools import lru_cache
from itertools import product
from math import ceil
import json

BASE = (0b011, 0b110, 0b101)  # AB, BC, CA
CANDIDATE = (0b001, 0b110, 0b101)  # hypothetical AB -> A
BANKS = 3


def schedule_cycles(counts: tuple[int, ...], masks: tuple[int, ...],
                    ports: tuple[int, ...] = (1, 1, 1), issue: int = 2) -> int:
    """Exact globally optimal atomic issue schedule; equal-resource baseline."""
    if not counts or len(counts) != len(masks) or len(ports) != BANKS:
        raise ValueError("mismatched nonempty workload dimensions")
    if any(not isinstance(x, int) or x < 0 for x in counts):
        raise ValueError("counts must be nonnegative integers")
    if any(not isinstance(x, int) or x < 0 or x >= 1 << BANKS for x in masks):
        raise ValueError("invalid bank mask")
    if any(not isinstance(p, int) or p <= 0 for p in ports) or issue <= 0:
        raise ValueError("positive integral ports and issue required")

    @lru_cache(None)
    def solve(state: tuple[int, ...]) -> int:
        if not any(state):
            return 0
        best = sum(state)

        def choices(i: int, remaining: int, uses: tuple[int, ...],
                    chosen: tuple[int, ...]) -> None:
            nonlocal best
            if i == len(state) or remaining == 0:
                if any(chosen):
                    padded = chosen + (0,) * (len(state) - len(chosen))
                    nxt = tuple(s - c for s, c in zip(state, padded))
                    best = min(best, 1 + solve(nxt))
                return
            for n in range(min(state[i], remaining) + 1):
                new_uses = tuple(uses[b] + (n if masks[i] & (1 << b) else 0)
                                 for b in range(BANKS))
                if all(new_uses[b] <= ports[b] for b in range(BANKS)):
                    choices(i + 1, remaining - n, new_uses, chosen + (n,))

        choices(0, issue, (0,) * BANKS, ())
        return best

    return solve(counts)


def mean_capacity_lower_bound(counts: tuple[int, ...], masks: tuple[int, ...],
                              ports: tuple[int, ...] = (1, 1, 1),
                              issue: int = 2) -> int:
    if not any(counts):
        return 0
    demands = [sum(n for n, m in zip(counts, masks) if m & (1 << b))
               for b in range(BANKS)]
    return max(ceil(sum(counts) / issue),
               *(ceil(d / p) for d, p in zip(demands, ports)))


def analyze(counts: tuple[int, int, int]) -> dict:
    if not any(counts):
        raise ValueError("empty workload has undefined gain")
    before = schedule_cycles(counts, BASE)
    after = schedule_cycles(counts, CANDIDATE)
    before_bound = mean_capacity_lower_bound(counts, BASE)
    after_bound = mean_capacity_lower_bound(counts, CANDIDATE)
    # Exact compatibility law for this fixed three-class single-port model:
    # baseline masks pairwise intersect; only candidate A and BC can coissue.
    matching = min(counts[0], counts[1])
    assert before == sum(counts)
    assert after == sum(counts) - matching
    assert before_bound <= before and after_bound <= after
    return {
        "counts_AB_BC_CA": list(counts),
        "baseline_optimal_cycles": before,
        "candidate_optimal_cycles": after,
        "baseline_mean_bound_cycles": before_bound,
        "candidate_mean_bound_cycles": after_bound,
        "exact_gain": f"{before}/{after}",
        "gain": before / after,
        "mean_bound_gain": before_bound / after_bound,
        "compatible_pair_count": matching,
        "mean_predicts_no_win_but_exact_gain_gt_1p02":
            before_bound == after_bound and 50 * before > 51 * after,
    }


def report() -> dict:
    frozen = {
        "predicted_win": (2, 2, 2),
        "predicted_no_win": (0, 3, 3),
        "prospective_transfer": (2, 1, 3),
    }
    cases = {name: analyze(counts) for name, counts in frozen.items()}
    worlds = [analyze(x) for x in product(range(5), repeat=3) if any(x)]
    return {
        "schema": "vektor.v317.atomic_bank_coissue_hypergraph.v1",
        "evidence_tier": "synthetic_exact_atomic_issue_schedule",
        "physical_gpu_measurements": False,
        "baseline_masks_AB_BC_CA": list(BASE),
        "candidate_masks_A_BC_CA": list(CANDIDATE),
        "physical_ports_per_bank": [1, 1, 1],
        "issue_slots": 2,
        "frozen": cases,
        "sweep_total_worlds": len(worlds),
        "sweep_mean_false_no_win_worlds": sum(
            x["mean_predicts_no_win_but_exact_gain_gt_1p02"] for x in worlds),
        "sweep_min_gain": min(x["gain"] for x in worlds),
        "sweep_max_gain": max(x["gain"] for x in worlds),
        "law": "N/(N-min(n_AB,n_BC)) for one port per bank, issue width 2",
        "limitations": ("Hypothetical read removal; no real binary, dynamic RF "
                        "cache, bank mapping, RTL, timing, power, or measured IPC."),
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
