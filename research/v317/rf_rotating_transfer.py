"""V317 preregistered strong-control holdouts; synthetic bank-service only."""
import json
from research.v317.rf_streaming_age_falsification import (
    arrivals, simulate, priority, age_aware, CYCLES, WARMUP
)
from research.v317.rf_streaming_strong_controls import (
    RotatingPriority, oldest_greedy
)

REGIMES = (
    ("unseen_stable_no_win", "four_bank", 0.52, 317952),
    ("unseen_stressed_possible_win", "four_bank", 0.60, 317960),
    ("unseen_private_negative_control", "private", 0.55, 317955),
)


def evaluate():
    out = {}
    for label, kind, p, seed in REGIMES:
        trace = arrivals(kind, p, seed)
        policies = {
            "fixed_priority": priority,
            "rotating_priority": RotatingPriority(),
            "oldest_first_greedy": oldest_greedy,
            "age_aware_exact": age_aware,
        }
        results = {name: simulate(trace, policy) for name, policy in policies.items()}
        base = results["fixed_priority"]["completed_after_warmup"]
        rot = results["rotating_priority"]["completed_after_warmup"]
        out[label] = {
            "kind": kind, "p_per_slot": p, "seed": seed,
            "rotation_over_fixed_completed_ratio": round(rot/base, 8),
            "results": results,
        }
    return {
        "evidence_tier": "FROZEN_SYNTHETIC_FOUR_SLOT_BANK_SERVICE_NOT_GPU_IPC",
        "cycles": CYCLES, "warmup": WARMUP,
        "regimes": out,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
