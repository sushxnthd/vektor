#!/usr/bin/env python3
"""Exact K-request bank-port admission law and independent prospective simulator.

See FOUR_REQUEST_ADMISSION_LAW_PREREG_20261027.md. Synthetic sub-law only;
no V296-vs-serial speedup or physically feasible GPU clock is established.
"""
import argparse
import json
import random
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

BANKS, PORTS, REQUESTS = 16, 2, 4
REGIMES = (
    ("uniform_independent", 0.0, 0.0),
    ("uniform_correlated", 0.0, 0.7),
    ("moderate_hotspot", 0.45, 0.2),
    ("heavy_hotspot", 0.80, 0.2),
    ("extreme_hotspot_correlated", 0.95, 0.7),
)
HOLDOUT_SEEDS = (717171, 818181, 919191)
SAMPLES = 30000


def bank_distribution(h):
    if not 0 <= h <= 1:
        raise ValueError("hotspot outside [0,1]")
    return (h + (1 - h) / BANKS,) + ((1 - h) / BANKS,) * (BANKS - 1)


def pair_weight(p, rho, a, b):
    return p[a] * ((rho if a == b else 0.0) + (1 - rho) * p[b])


def state_ports(state):
    hot, c0, c1, c2 = state
    if not (0 <= hot <= PORTS and c0 + c1 + c2 == BANKS - 1 and min(c0, c1, c2) >= 0):
        raise ValueError("invalid compressed port state")
    return (hot,) + (0,) * c0 + (1,) * c1 + (2,) * c2


def advance(state, a, b):
    used = list(state_ports(state))
    if used[a] + (1 + (a == b)) > PORTS or (a != b and used[b] + 1 > PORTS):
        return state, 0
    used[a] += 1
    used[b] += 1
    return (used[0], used[1:].count(0), used[1:].count(1), used[1:].count(2)), 1


def exact_expected(h, rho, k=REQUESTS):
    """Finite-state recurrence over hot-bank ports and cold-bank occupancy counts."""
    if not 0 <= rho <= 1 or not 0 <= k <= REQUESTS:
        raise ValueError("invalid rho or number of requests")
    p = bank_distribution(h)
    initial = (0, BANKS - 1, 0, 0)

    @lru_cache(maxsize=None)
    def transitions(state):
        weights = defaultdict(float)
        for a in range(BANKS):
            for b in range(BANKS):
                next_state, admitted = advance(state, a, b)
                weights[(next_state, admitted)] += pair_weight(p, rho, a, b)
        assert abs(sum(weights.values()) - 1.0) < 1e-11
        return tuple((s, admit, prob) for (s, admit), prob in weights.items())

    states = {initial: 1.0}
    expected = 0.0
    for _ in range(k):
        nxt = defaultdict(float)
        for state, mass in states.items():
            for new_state, admitted, prob in transitions(state):
                nxt[new_state] += mass * prob
                expected += mass * prob * admitted
        states = nxt
        assert abs(sum(states.values()) - 1.0) < 1e-9
    assert 0 <= expected <= k + 1e-9
    return expected


def draw_bank(rng, p):
    u = rng.random()
    for i, pi in enumerate(p):
        u -= pi
        if u < 0:
            return i
    return BANKS - 1


def simulate_independent(h, rho, seed, batches, k=REQUESTS):
    """Independent event oracle with explicit 16-bank port counters."""
    p = bank_distribution(h)
    rng = random.Random(seed)
    admitted_total = 0
    for _ in range(batches):
        free = [PORTS] * BANKS
        for _ in range(k):
            a = draw_bank(rng, p)
            b = a if rng.random() < rho else draw_bank(rng, p)
            demand_a = 1 + (a == b)
            if free[a] >= demand_a and (a == b or free[b] >= 1):
                free[a] -= 1
                free[b] -= 1
                admitted_total += 1
        assert min(free) >= 0
    return admitted_total / batches


def exact_pair_compatibility_reference(h, rho):
    """Independent 16^4 event enumeration for the K=2 identity."""
    p = bank_distribution(h)
    pairs = [(a, b, pair_weight(p, rho, a, b)) for a in range(BANKS) for b in range(BANKS)]
    total = 0.0
    for a, b, x in pairs:
        for c, d, y in pairs:
            demands = [0] * BANKS
            for i in (a, b, c, d):
                demands[i] += 1
            if max(demands) <= PORTS:
                total += x * y
    return total


def self_test():
    for h, rho in ((0, 0), (0, 0.7), (0.45, 0.2), (0.8, 0.2), (1, 1)):
        p2 = exact_pair_compatibility_reference(h, rho)
        assert abs(exact_expected(h, rho, 2) - (1 + p2)) < 1e-9
        values = [exact_expected(h, rho, k) for k in range(1, 5)]
        assert values[0] == 1.0 or abs(values[0] - 1.0) < 1e-12
        assert all(values[i] <= values[i + 1] <= values[i] + 1 + 1e-9 for i in range(3))
    assert exact_expected(1, 1, 4) == 1.0
    for args in ((-0.1, 0.2), (0.3, 1.1), (0.3, 0.2, 5)):
        try:
            exact_expected(*args)
        except ValueError:
            continue
        raise AssertionError("invalid inputs accepted")
    print("V296_FOUR_REQUEST_EXACT_DP_INDEPENDENT_K2_ORACLE_PASS")


def evaluate(output):
    self_test()
    rows = []
    for name, h, rho in REGIMES:
        pred = exact_expected(h, rho, REQUESTS)
        pair = exact_pair_compatibility_reference(h, rho)
        naive = 1 + 3 * pair
        for seed in HOLDOUT_SEEDS:
            actual = simulate_independent(h, rho, seed, SAMPLES)
            rows.append(dict(regime=name, hotspot=h, operand_copy_probability=rho,
                             holdout_seed=seed, batches=SAMPLES,
                             exact_predicted_admissions_per_batch=pred,
                             independent_observed_admissions_per_batch=actual,
                             absolute_prediction_error=abs(actual - pred),
                             naive_pair_extrapolation=naive,
                             naive_absolute_error=abs(actual - naive),
                             pass_gate=abs(actual - pred) <= 0.025))
    result = dict(evidence_tier="EXACT_FOUR_REQUEST_SYNTHETIC_PROSPECTIVE_NOT_GPU_SPEEDUP",
                  prereg_commit="873c0b3e397ab6421dcadf680ad3773ed5c83e03",
                  fitted_parameters=False, frozen_tolerance=0.025,
                  holdout_cells=len(rows), all_pass=all(x["pass_gate"] for x in rows),
                  scope_limit="Instantaneous independent ready requests; no queues, clock, area, occupancy, power, memory, or routed feasibility.",
                  rows=rows)
    Path(output).write_text(json.dumps(result, indent=2) + "\n")
    for name, _, _ in REGIMES:
        subset = [x for x in rows if x["regime"] == name]
        print(name, "prediction", round(subset[0]["exact_predicted_admissions_per_batch"], 6),
              "mean_observed", round(sum(x["independent_observed_admissions_per_batch"] for x in subset)/3, 6),
              "max_error", round(max(x["absolute_prediction_error"] for x in subset), 6),
              "naive", round(subset[0]["naive_pair_extrapolation"], 6))
    print("V296_FOUR_REQUEST_PROSPECTIVE_PASS" if result["all_pass"] else "V296_FOUR_REQUEST_PROSPECTIVE_FAIL")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--evaluate", action="store_true")
    ap.add_argument("--output", default="research/v296/FOUR_REQUEST_ADMISSION_HELDOUT_20261027.json")
    args = ap.parse_args()
    if args.self_test:
        self_test()
    if args.evaluate:
        result = evaluate(args.output)
        if not result["all_pass"]:
            raise SystemExit(1)
    if not (args.self_test or args.evaluate):
        ap.error("choose --self-test or --evaluate")
