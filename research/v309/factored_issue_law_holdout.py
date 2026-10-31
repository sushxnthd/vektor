#!/usr/bin/env python3
"""V309 prospective, synthetic issue-admission holdout; NOT GPU throughput.

Protocol frozen before held-out seeds were evaluated:
research/v309/FACTORED_SUBSET_ISSUE_LAW_PREREG_20261031.md

Independent Python exact-subset oracle and greedy controller. The exact law
E[M] = E[G] + P(M>G) is a conservation identity, not a novel speedup law.
"""
from collections import Counter
import hashlib
import json
import os
import random
import sys

N = 20_000
MASK_ORDER = tuple(sorted(range(16), key=lambda m: (-m.bit_count(), m)))
REGIMES = (
    ("uniform16_predicted_no_win", 0x309C, 0.0, "lt", 1.01),
    ("hot3_predicted_win", 0x309D, 0.8, "gt", 1.02),
)


def feasible(mask, valid, a, b):
    if mask & ~valid:
        return False
    demand = [0] * 16
    for i in range(4):
        if mask & (1 << i):
            demand[a[i]] += 1
            if demand[a[i]] > 2:
                return False
            demand[b[i]] += 1
            if demand[b[i]] > 2:
                return False
    return True


def oracle(valid, a, b):
    for mask in MASK_ORDER:
        if feasible(mask, valid, a, b):
            return mask
    raise AssertionError("empty subset must always be feasible")


def greedy(valid, a, b):
    demand = [0] * 16
    mask = 0
    for i in range(4):
        if not (valid & (1 << i)):
            continue
        x, y = a[i], b[i]
        if demand[x] + 1 + int(x == y) > 2:
            continue
        if x != y and demand[y] + 1 > 2:
            continue
        demand[x] += 1
        demand[y] += 1
        mask |= 1 << i
    return mask


def directed_controls():
    a, b = (0, 0, 1, 2), (1, 0, 1, 2)
    assert greedy(15, a, b) == 0x9
    assert oracle(15, a, b) == 0xE
    a, b = (0, 2, 4, 6), (1, 3, 5, 7)
    assert greedy(15, a, b) == oracle(15, a, b) == 0xF
    a = b = (15, 15, 15, 15)
    assert oracle(15, a, b) == 0x1
    for valid in range(16):
        assert feasible(oracle(valid, a, b), valid, a, b)


def bank(rng, hot_prob):
    # Consume the Bernoulli draw even for the uniform16 no-win regime.
    if rng.random() < hot_prob:
        return rng.randrange(3)
    return rng.randrange(16)


def run_regime(name, seed, hot_prob, relation, threshold):
    rng = random.Random(seed)
    hist = Counter()
    gsum = msum = loss = 0
    sample_digest = hashlib.sha256()
    for _ in range(N):
        a, b = [], []
        for _slot in range(4):
            a.append(bank(rng, hot_prob))
            b.append(bank(rng, hot_prob))
        valid = 0xF
        sample_digest.update(bytes([valid, *a, *b]))
        gmask = greedy(valid, a, b)
        mmask = oracle(valid, a, b)
        assert feasible(gmask, valid, a, b)
        assert feasible(mmask, valid, a, b)
        g, m = gmask.bit_count(), mmask.bit_count()
        if m - g not in (0, 1):
            raise AssertionError(f"4-slot delta bound falsified: {g=} {m=} {a=} {b=}")
        gsum += g
        msum += m
        loss += (m > g)
        hist[f"{g}->{m}"] += 1
    mean_g, mean_m, p_loss = gsum / N, msum / N, loss / N
    assert mean_g > 0
    ratio = mean_m / mean_g
    residual = mean_m - mean_g - p_loss
    assert abs(residual) < 1e-12
    gate = (ratio < threshold) if relation == "lt" else (ratio > threshold)
    return {
        "name": name,
        "seed": hex(seed),
        "n": N,
        "hot_probability": hot_prob,
        "hot_bank_set": [0, 1, 2],
        "valid_requests_per_opportunity": 4,
        "sample_sha256": sample_digest.hexdigest(),
        "greedy_mean_admissions": mean_g,
        "exact_max_mean_admissions": mean_m,
        "probability_greedy_loses_one": p_loss,
        "admission_ratio": ratio,
        "exact_law_residual": residual,
        "joint_histogram": dict(sorted(hist.items())),
        "frozen_prediction": f"admission_ratio {relation} {threshold}",
        "frozen_prediction_pass": gate,
    }


def main():
    directed_controls()
    rows = [run_regime(*spec) for spec in REGIMES]
    result = {
        "source_commit": os.environ.get("GITHUB_SHA", "local_unpinned"),
        "evidence_tier": "synthetic_issue_admission_only_not_gpu_throughput",
        "pre_registered_protocol": "research/v309/FACTORED_SUBSET_ISSUE_LAW_PREREG_20261031.md",
        "previous_pilot_disclosed": True,
        "holdouts": rows,
        "all_frozen_predictions_pass": all(r["frozen_prediction_pass"] for r in rows),
        "hardware_frequency_area_power_or_tile_gain_claimed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["all_frozen_predictions_pass"]:
        sys.exit("FROZEN_ISSUE_LAW_PREDICTION_FAIL")


if __name__ == "__main__":
    main()
