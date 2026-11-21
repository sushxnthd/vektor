#!/usr/bin/env python3
"""Prospective V317 head-preserving output-port ceiling sweep. Not GPU IPC."""
from __future__ import annotations
from collections import Counter
from itertools import product
import json, random

SEEDS = (20261103, 20261107, 20261111)
BATCHES_PER_SEED = 8000
REGIMES = (("uniform16", 16, "uniform"), ("uniform4", 4, "uniform"),
           ("hot65_16", 16, "hot65"), ("samebank70_16", 16, "samebank70"))
WIDTHS = (2, 3, 4)

def feasible(reqs: list[tuple[int, int]], mask: int) -> bool:
    usage = Counter()
    for i, (a, b) in enumerate(reqs):
        if mask & (1 << i):
            usage[a] += 1
            usage[b] += 1
            if usage[a] > 2 or usage[b] > 2:
                return False
    return True

def service(reqs: list[tuple[int, int]]) -> tuple[int, int]:
    assert len(reqs) == 4
    chosen = 0
    for i in range(4):
        trial = chosen | (1 << i)
        if feasible(reqs, trial):
            chosen = trial
    valid = (mask for mask in range(1, 16) if mask & 1 and feasible(reqs, mask))
    return chosen.bit_count(), max(mask.bit_count() for mask in valid)

def sample(rng: random.Random, banks: int, kind: str) -> list[tuple[int, int]]:
    def bank():
        if kind == "hot65":
            return 0 if rng.random() < 0.65 else rng.randrange(1, banks)
        return rng.randrange(banks)
    reqs = []
    for _ in range(4):
        a = bank()
        b = a if kind == "samebank70" and rng.random() < 0.70 else bank()
        reqs.append((a, b))
    return reqs

def summarize(pairs: list[tuple[int, int]]) -> dict:
    result = {}
    for width in WIDTHS:
        greedy = sum(min(width, g) for g, h in pairs)
        optimal = sum(min(width, h) for g, h in pairs)
        gain_events = sum(min(width, h) > min(width, g) for g, h in pairs)
        saturated = sum(g >= width for g, h in pairs)
        assert greedy > 0 and optimal >= greedy
        result[str(width)] = {
            "greedy_grants": greedy,
            "head_optimal_grants": optimal,
            "ratio": optimal / greedy,
            "gain_events": gain_events,
            "gain_probability": gain_events / len(pairs),
            "greedy_output_saturated_probability": saturated / len(pairs),
            "exact_identity": 1 + (optimal - greedy) / greedy,
        }
    return result

def run() -> dict:
    exhaustive = {}
    for banks in (2, 4):
        pairs = []
        for operands in product(range(banks), repeat=8):
            q = list(zip(operands[::2], operands[1::2]))
            pairs.append(service(q))
        exhaustive[str(banks)] = {"batches": len(pairs), "widths": summarize(pairs)}
    regimes = {}
    for index, (name, banks, kind) in enumerate(REGIMES):
        pairs = []
        for seed in SEEDS:
            rng = random.Random(seed * 100 + index)
            pairs.extend(service(sample(rng, banks, kind)) for _ in range(BATCHES_PER_SEED))
        regimes[name] = {"batches": len(pairs), "widths": summarize(pairs)}
    decisions = {
        "cap2_universal_test_pass": all(
            row["widths"]["2"]["ratio"] == 1
            for row in list(regimes.values()) + list(exhaustive.values())
        ),
        "cap3_uniform16_no_material_gain": regimes["uniform16"]["widths"]["3"]["ratio"] < 1.02,
        "cap3_hot65_no_material_gain": regimes["hot65_16"]["widths"]["3"]["ratio"] < 1.02,
        "cap4_uniform4_small_win": regimes["uniform4"]["widths"]["4"]["ratio"] > 1.01,
        "cap4_hot65_no_material_gain": regimes["hot65_16"]["widths"]["4"]["ratio"] < 1.02,
        "monotone_ratios": all(
            row["widths"]["2"]["ratio"] <= row["widths"]["3"]["ratio"] <= row["widths"]["4"]["ratio"]
            for row in list(regimes.values()) + list(exhaustive.values())
        ),
    }
    return {"protocol": "FROZEN_OUTPUT_PORT_CEILING_THEOREM_20261102.md",
            "evidence_tier": "synthetic combinational head-preserving bank-service upper bound; not RTL/IPC",
            "seeds": list(SEEDS), "batches_per_seed": BATCHES_PER_SEED,
            "regimes": regimes, "exhaustive": exhaustive, "decisions": decisions}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
