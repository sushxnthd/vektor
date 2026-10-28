#!/usr/bin/env python3
"""V296 counterfactual routed-area tile packing and shared-port falsification.

D4 serial FAILS routed setup/hold; these are measured areas but NOT two
physically feasible controls. No GPU throughput, energy or signoff claim.
"""
import argparse
import json
import random
from decimal import Decimal, getcontext
from itertools import product

getcontext().prec = 35
PAIR_AREA = Decimal("19543.01964701699")
SERIAL_AREA = Decimal("21914.943")
L, N = 2, 8
SEEDS = (3201, 3209, 3217)
CYCLES = 12000
REGIMES = (
    ("capacity_win", "40000", 8, 1.0, 0.0, "win_gt_1p5"),
    ("shared_port_no_win", "40000", 1, 1.0, 0.0, "exact_no_win"),
    ("equal_slice_no_win", "30000", 8, 1.0, 0.0, "exact_no_win"),
    ("capacity_fragility", "40000", 8, 1.0, 0.0, "lost_at_delta_500"),
    ("unseen_mixed", "40000", 5, 0.60, 0.40, "prospective_no_fit"),
)

def slices(budget, area, added=Decimal(0)):
    assert area > 0 and budget >= 0 and added >= 0
    return int(budget // (area + added))

def serial(valid, banks):
    once = twice = 0
    grants = []
    for v, (a, b) in zip(valid, banks):
        ma, mb = 1 << a, 1 << b
        ok = bool(v) and ((once & ma) == 0 if a == b else
                          (twice & ma) == 0 and (twice & mb) == 0)
        grants.append(bool(ok))
        if ok:
            if a == b:
                once |= ma
                twice |= ma
            else:
                twice |= once & (ma | mb)
                once |= ma | mb
    return tuple(grants)

def pairwise(valid, banks):
    grants = []
    for i, (a, b) in enumerate(banks):
        ca = cb = 0
        for j, (x, y) in enumerate(banks[:i]):
            if grants[j]:
                ca += (a == x) + (a == y)
                cb += (b == x) + (b == y)
        grants.append(bool(valid[i]) and
                      (ca == 0 if a == b else ca < 2 and cb < 2))
    return tuple(grants)

def assert_ports(grants, banks):
    counts = [0] * 16
    for g, (a, b) in zip(grants, banks):
        if g:
            counts[a] += 1
            counts[b] += 1
    assert max(counts) <= 2

def bank_pair(rng, hot):
    return tuple(0 if rng.random() < hot else rng.randrange(16)
                 for _ in range(2))

def simulate(architecture, k, B, q, hot, seed, cycles=CYCLES):
    """Synthetic closed-loop issue with shared cap and accepted-only cursor."""
    rng = random.Random(seed)
    ready_after = [[0] * N for _ in range(k)]
    cursor = [0] * k
    admitted = 0
    by_slice = [0] * k
    for cycle in range(cycles):
        budget = B
        for j in range(k):
            s = (cycle + j) % k
            eligible = []
            for offset in range(N):
                w = (cursor[s] + offset) % N
                if ready_after[s][w] <= cycle and rng.random() < q:
                    eligible.append(w)
            chosen = eligible[:4]
            banks = [bank_pair(rng, hot) for _ in chosen]
            grants = (pairwise if architecture == "pairwise" else serial)(
                [1] * len(chosen), banks)
            assert_ports(grants, banks)
            for w, g in zip(chosen, grants):
                if g and budget > 0:
                    budget -= 1
                    admitted += 1
                    by_slice[s] += 1
                    ready_after[s][w] = cycle + L
                    cursor[s] = (w + 1) % N
    return {"waves_per_cycle": admitted / cycles, "accepted_by_slice": by_slice}

def evaluate():
    rows = []
    for name, budget_s, B, q, hot, prediction in REGIMES:
        budget = Decimal(budget_s)
        kp, ks = slices(budget, PAIR_AREA), slices(budget, SERIAL_AREA)
        assert kp >= 1 and ks >= 1
        per_seed = []
        for seed in SEEDS:
            a = simulate("pairwise", kp, B, q, hot, seed)
            b = simulate("serial", ks, B, q, hot, seed)
            per_seed.append({
                "seed": seed, "candidate": a["waves_per_cycle"],
                "serial": b["waves_per_cycle"],
                "ratio": a["waves_per_cycle"] / b["waves_per_cycle"]})
        mean = sum(r["ratio"] for r in per_seed) / len(per_seed)
        passed = (mean > 1.5 if prediction == "win_gt_1p5" else
                  all(r["ratio"] == 1.0 for r in per_seed)
                  if prediction == "exact_no_win" else
                  slices(budget, PAIR_AREA, Decimal(500)) == ks
                  if prediction == "lost_at_delta_500" else None)
        rows.append({
            "name": name, "budget_um2": budget_s, "global_B": B,
            "readiness_q": q, "bank0_hot_probability": hot,
            "candidate_slices": kp, "serial_slices": ks,
            "prediction": prediction, "prediction_pass": passed,
            "mean_ratio": mean, "seeds": per_seed})
    delta = Decimal("40000") / 2 - PAIR_AREA
    return {
        "evidence_tier": "CONDITIONAL_SYNTHETIC_CAPACITY_MODEL_NOT_PHYSICAL_THROUGHPUT",
        "source_routed_run": 40646515864,
        "candidate_area_um2": str(PAIR_AREA),
        "serial_area_um2": str(SERIAL_AREA),
        "serial_D4_physical_status": "SETUP_AND_HOLD_FAIL",
        "candidate_D4_physical_status": "ROUTED_METRIC_PASS",
        "candidate_delta_before_two_slice_loss_um2": str(delta),
        "candidate_delta_before_two_slice_loss_pct": float(100 * delta / PAIR_AREA),
        "conditional_two_slice_budget_window_um2":
            [str(2 * PAIR_AREA), str(2 * SERIAL_AREA)],
        "cycle_count": CYCLES, "seeds": SEEDS,
        "resident_warps_per_slice": N, "operand_latency_cycles": L,
        "results": rows, "matched_feasible_GPU_gain_proven": False,
        "physical_power_proven": False}

def self_test():
    cases = 0
    for valid in product((0, 1), repeat=4):
        for a in product((0, 1, 2), repeat=8):
            banks = tuple(zip(a[::2], a[1::2]))
            p, s = pairwise(valid, banks), serial(valid, banks)
            assert p == s
            assert_ports(p, banks)
            cases += 1
    assert cases == 104976
    assert slices(Decimal(40000), PAIR_AREA) == 2
    assert slices(Decimal(40000), SERIAL_AREA) == 1
    assert slices(Decimal(30000), PAIR_AREA) == slices(Decimal(30000), SERIAL_AREA) == 1
    assert slices(Decimal(40000), PAIR_AREA, Decimal(500)) == 1
    for seed in (11, 13):
        assert simulate("pairwise", 2, 1, 1., 0., seed, 1000)["waves_per_cycle"] == 1
        assert simulate("serial", 1, 1, 1., 0., seed, 1000)["waves_per_cycle"] == 1
    print("V296_CAPACITY_BOUNDARY_SELFTEST_PASS", cases)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--run", action="store_true")
    p.add_argument("--output")
    a = p.parse_args()
    if a.self_test:
        self_test()
    elif a.run:
        data = json.dumps(evaluate(), indent=2, sort_keys=True) + "\n"
        if a.output:
            with open(a.output, "w") as f:
                f.write(data)
        else:
            print(data)
    else:
        p.error("select --self-test or --run")
