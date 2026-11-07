"""Posthoc strong controls for the frozen V317 streaming falsification.

These controls were added after seeing the frozen three-policy outcome. They
are exploratory and must not be reported as prospectively predicted wins.
"""
from research.v317.rf_streaming_age_falsification import (
    SLOTS, legal, arrivals, simulate
)
import json


def oldest_greedy(valid, pairs, ages):
    """Greedy issue in descending head age; tie by slot ID."""
    grant = 0
    for slot in sorted(range(SLOTS), key=lambda i: (-ages[i], i)):
        if valid & (1 << slot) and legal(grant | (1 << slot), pairs):
            grant |= 1 << slot
    return grant


class RotatingPriority:
    """Simple fairness comparator: rotate starting slot each cycle."""
    def __init__(self):
        self.cycle = 0

    def __call__(self, valid, pairs, ages):
        grant = 0
        for offset in range(SLOTS):
            slot = (self.cycle + offset) % SLOTS
            if valid & (1 << slot) and legal(grant | (1 << slot), pairs):
                grant |= 1 << slot
        self.cycle += 1
        return grant


def sensitivity():
    cases = [
        (0.48, 317111), (0.60, 317260),
        (0.75, 317275), (0.90, 317290),
    ]
    result = {}
    for p, seed in cases:
        stream = arrivals("four_bank", p, seed)
        result[str(p)] = {
            name: simulate(stream, policy)
            for name, policy in [
                ("oldest_greedy", oldest_greedy),
                ("rotating_priority", RotatingPriority()),
            ]
        }
    return {
        "evidence_tier": "POSTHOC_SYNTHETIC_STRONG_CONTROLS",
        "regimes": result,
    }


if __name__ == "__main__":
    print(json.dumps(sensitivity(), indent=2, sort_keys=True))
