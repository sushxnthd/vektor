#!/usr/bin/env python3
"""Pre-outcome, iid bank-equality moment law for V309; NOT GPU throughput.

Frozen protocol: BANK_EQUALITY_MOMENT_LAW_PREREG_20261031.md.
No fitted parameters. The independent Monte Carlo reference is imported from
factored_issue_law_holdout.py, not the partition evaluator below.
"""
from collections import Counter
from functools import lru_cache
from math import factorial, fsum
import hashlib
import json
import random
import sys

from factored_issue_law_holdout import (
    greedy as independent_greedy,
    oracle as independent_oracle,
    feasible as independent_feasible,
)

N = 100_000
REGIMES = (
    ("uniform8", 0x309E, "uniform8", 1.007648758273677, "lt", 1.01),
    ("hot2", 0x309F, "hot2", 1.0973483338585934, "gt", 1.07),
)


def partitions(n):
    """Restricted-growth strings: one representative of each set partition."""
    def rec(prefix, highest):
        if len(prefix) == n:
            yield tuple(prefix)
            return
        for label in range(highest + 2):
            yield from rec(prefix + [label], max(highest, label))
    if n < 1:
        yield ()
    else:
        yield from rec([0], 0)


@lru_cache(None)
def coarsenings(k):
    return tuple(partitions(k))


@lru_cache(None)
def exact_pattern_mass(sizes, power_sums):
    """Möbius inversion: assign DISTINCT bank labels to equality blocks."""
    terms = []
    for grouping in coarsenings(len(sizes)):
        groups = {}
        for i, label in enumerate(grouping):
            groups.setdefault(label, []).append(i)
        product_term = 1.0
        for members in groups.values():
            r = sum(sizes[i] for i in members)
            product_term *= ((-1) ** (len(members) - 1) *
                             factorial(len(members) - 1) * power_sums[r])
        terms.append(product_term)
    return fsum(terms)


def pattern_grants(labels):
    """Independent canonical-pattern policy evaluator, no RTL or holdout data."""
    a, b = labels[::2], labels[1::2]
    k = max(labels) + 1
    demand = [0] * k
    greedy_mask = 0
    for i in range(4):
        x, y = a[i], b[i]
        if demand[x] + 1 + int(x == y) > 2:
            continue
        if x != y and demand[y] + 1 > 2:
            continue
        demand[x] += 1
        demand[y] += 1
        greedy_mask |= 1 << i

    for mask in sorted(range(16), key=lambda x: (-x.bit_count(), x)):
        counts = [0] * k
        for i in range(4):
            if mask & (1 << i):
                counts[a[i]] += 1
                counts[b[i]] += 1
        if max(counts) <= 2:
            return greedy_mask.bit_count(), mask.bit_count()
    raise AssertionError("empty subset must be feasible")


def marginal(mode):
    if mode == "uniform8":
        return (1 / 8,) * 8 + (0.0,) * 8
    if mode == "hot2":
        return (0.95 / 2 + 0.05 / 16,) * 2 + (0.05 / 16,) * 14
    raise ValueError(mode)


def analytic_prediction(q):
    if len(q) != 16 or any(x < 0 for x in q) or abs(fsum(q) - 1) > 1e-12:
        raise ValueError("invalid bank distribution")
    powers = (0.0,) + tuple(fsum(x ** r for x in q) for r in range(1, 9))
    masses, weighted_g, weighted_m, weighted_loss = [], [], [], []
    count = 0
    for labels in partitions(8):
        count += 1
        sizes = tuple(sorted(labels.count(i) for i in set(labels)))
        mass = exact_pattern_mass(sizes, powers)
        if mass < -1e-10:
            raise AssertionError(f"negative exact pattern probability: {mass}")
        g, m = pattern_grants(labels)
        if m - g not in (0, 1):
            raise AssertionError("single-admission bound failed")
        masses.append(mass)
        weighted_g.append(mass * g)
        weighted_m.append(mass * m)
        weighted_loss.append(mass * (m > g))
    total, g, m, p = map(fsum, (masses, weighted_g, weighted_m, weighted_loss))
    if count != 4140 or abs(total - 1) > 1e-9 or abs(m - g - p) > 1e-9:
        raise AssertionError(f"partition normalization or identity failure: {count=} {total=} {g=} {m=} {p=}")
    return dict(partitions=count, probability_mass=total,
                predicted_greedy_mean=g, predicted_exact_max_mean=m,
                predicted_conflict_loss_probability=p,
                predicted_issue_ratio=m / g,
                exact_law_residual=m - g - p,
                optimistic_min_frequency_retention=g / m)


def draw_bank(rng, mode):
    if mode == "uniform8":
        return rng.randrange(8)
    if mode == "hot2":
        return rng.randrange(2) if rng.random() < 0.95 else rng.randrange(16)
    raise ValueError(mode)


def independent_holdout(mode, seed):
    rng = random.Random(seed)
    digest = hashlib.sha256()
    hist = Counter()
    sum_g = sum_m = 0
    for _ in range(N):
        a, b = [], []
        for _slot in range(4):
            a.append(draw_bank(rng, mode))
            b.append(draw_bank(rng, mode))
        digest.update(bytes([15, *a, *b]))
        gm = independent_greedy(15, a, b)
        mm = independent_oracle(15, a, b)
        if not independent_feasible(gm, 15, a, b) or not independent_feasible(mm, 15, a, b):
            raise AssertionError("bank-port violation")
        g, m = gm.bit_count(), mm.bit_count()
        if m - g not in (0, 1):
            raise AssertionError("invalid admission difference")
        hist[f"{g}->{m}"] += 1
        sum_g += g
        sum_m += m
    return dict(n=N, sample_sha256=digest.hexdigest(),
                observed_greedy_mean=sum_g / N,
                observed_exact_max_mean=sum_m / N,
                observed_issue_ratio=sum_m / sum_g,
                joint_histogram=dict(sorted(hist.items())))


def main():
    results = []
    for name, seed, mode, frozen, relation, threshold in REGIMES:
        prediction = analytic_prediction(marginal(mode))
        value = prediction["predicted_issue_ratio"]
        if abs(value - frozen) > 1e-10:
            raise AssertionError(f"frozen analytical prediction drift for {name}: {value}")
        holdout = independent_holdout(mode, seed)
        observed = holdout["observed_issue_ratio"]
        directional = observed < threshold if relation == "lt" else observed > threshold
        error = abs(observed - value)
        results.append(dict(name=name, seed=hex(seed),
                            frozen_predicted_ratio=frozen,
                            frozen_direction=f"{relation} {threshold}",
                            prediction=prediction, holdout=holdout,
                            absolute_prediction_error=error,
                            frozen_direction_pass=directional,
                            frozen_absolute_error_limit=0.015,
                            frozen_error_gate_pass=error < 0.015))
    out = dict(evidence_tier="synthetic_iid_issue_prediction_not_gpu_throughput",
               protocol="research/v309/BANK_EQUALITY_MOMENT_LAW_PREREG_20261031.md",
               model_uses_holdout_outcomes=False,
               physical_speedup_claimed=False, results=results,
               all_frozen_gates_pass=all(
                   r["frozen_direction_pass"] and r["frozen_error_gate_pass"]
                   for r in results))
    print(json.dumps(out, indent=2, sort_keys=True))
    if not out["all_frozen_gates_pass"]:
        sys.exit("FROZEN_IID_PREDICTION_GATE_FAIL")


if __name__ == "__main__":
    main()
