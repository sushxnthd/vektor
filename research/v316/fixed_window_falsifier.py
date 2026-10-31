#!/usr/bin/env python3
"""V316: independently reproducible fixed-window bank-reservation novelty kill.

Synthetic opportunity-level experiment, NOT GPU IPC. No external dependencies.
Run: python3 research/v316/fixed_window_falsifier.py
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
import json
import random

BANKS = 2
WINDOW = 3
N = 100_000

@dataclass(frozen=True)
class Request:
    sources: tuple[int | None, ...]
    ready: bool = True

def can_reserve(reservations: tuple[tuple[int, ...], ...],
                request: Request, horizon: int = WINDOW) -> bool:
    """Exact deterministic earliest-slot assignment, with independent bank ports."""
    if not request.ready:
        return False
    taken = [list(row) for row in reservations]
    if horizon > len(taken):
        taken.extend([[0] * BANKS for _ in range(horizon - len(taken))])
    for bank in request.sources:
        if bank is None:  # RFC hit, consumes no RF bank read
            continue
        if bank not in range(BANKS):
            raise ValueError("invalid bank")
        for cycle in range(horizon):
            if not taken[cycle][bank]:
                taken[cycle][bank] = 1
                break
        else:
            return False
    return True

def head_only(reservations, requests):
    return 0 if requests and can_reserve(reservations, requests[0]) else None

def strong_equal_information(reservations, requests):
    # Existing all-ready-warp scan, identical resources and priority.
    for i, req in enumerate(requests):
        if can_reserve(reservations, req):
            return i
    return None

def v316_backup(reservations, requests):
    # Candidate's explicit primary/backup decision, independent implementation.
    if requests and can_reserve(reservations, requests[0]):
        return 0
    if len(requests) > 1 and can_reserve(reservations, requests[1]):
        return 1
    return None

def exhaustive():
    cases = 0
    # 64 reservation patterns x 9^2 two-source requests x 4 ready masks.
    options = [Request(tuple(x)) for x in product((0, 1, None), repeat=2)]
    for bits in product((0, 1), repeat=BANKS * WINDOW):
        reservations = tuple(tuple(bits[t * BANKS:(t + 1) * BANKS])
                             for t in range(WINDOW))
        for a, b in product(options, repeat=2):
            for ready_a, ready_b in product((False, True), repeat=2):
                reqs = (Request(a.sources, ready_a), Request(b.sources, ready_b))
                assert v316_backup(reservations, reqs) == strong_equal_information(
                    reservations, reqs), (reservations, reqs)
                cases += 1
    assert cases == 20_736
    return cases

def trial(seed, hot_fraction, primary_hot, backup_cold):
    rng = random.Random(seed)
    counts = {"head": 0, "strong": 0, "candidate": 0, "primary_blocked": 0,
              "backup_given_block": 0}
    for _ in range(N):
        hot = rng.random() < hot_fraction
        reservations = ((1, 0), (1, 0), (1, 0)) if hot else (
            (0, 0), (0, 0), (0, 0))
        primary_bank = 0 if rng.random() < primary_hot else 1
        backup_bank = 1 if rng.random() < backup_cold else 0
        requests = (Request((primary_bank,)), Request((backup_bank,)))
        h = head_only(reservations, requests)
        s = strong_equal_information(reservations, requests)
        c = v316_backup(reservations, requests)
        counts["head"] += h is not None
        counts["strong"] += s is not None
        counts["candidate"] += c is not None
        if h is None:
            counts["primary_blocked"] += 1
            counts["backup_given_block"] += can_reserve(reservations, requests[1])
    p = hot_fraction * primary_hot
    q = backup_cold
    predicted = 1 + p * q / (1 - p)
    measured = counts["candidate"] / counts["head"]
    # Fixed prospective tolerance; 100k independent opportunities.
    assert abs(predicted - measured) < 0.025, (predicted, measured)
    assert counts["candidate"] == counts["strong"]
    return {"seed": seed, "N": N, "hot_fraction": hot_fraction,
            "primary_hot": primary_hot, "backup_cold": backup_cold,
            "predicted_vs_head": predicted, "measured_vs_head": measured,
            "incremental_vs_strong": counts["candidate"] / counts["strong"],
            "counts": counts}

def main():
    n = exhaustive()
    win = trial(31601, 0.55, 0.90, 0.90)
    no_win = trial(31602, 0.0, 0.90, 0.90)
    transfer = trial(31603, 0.25, 0.70, 0.75)
    assert win["measured_vs_head"] >= 1.10
    assert no_win["measured_vs_head"] == 1.0
    # Buffered-collector counterexample: reads may be served after 3-cycle window.
    full_hot = ((1, 0), (1, 0), (1, 0))
    blocked = Request((0,))
    assert not can_reserve(full_hot, blocked, WINDOW)
    assert can_reserve(full_hot, blocked, WINDOW + 1)
    result = {"exhaustive_parity_cases": n, "win": win, "no_win": no_win,
              "transfer": transfer,
              "fixed_vs_buffered_counterexample": {
                  "reservation": full_hot, "sources": blocked.sources,
                  "fixed_window_feasible": False, "four_cycle_feasible": True},
              "decision": "KILL_V316_INCREMENTAL_NOVELTY",
              "evidence_tier": "synthetic-opportunity-level, no RTL/physical/GPU"}
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
