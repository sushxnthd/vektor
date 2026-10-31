#!/usr/bin/env python3
"""V315 prospective optimistic RF/ALU capacity envelope.

This is NOT cycle-accurate IPC, RTL, a real GPU workload, or a novel
rematerialization implementation. All phase predictions are frozen in
PREREG_20261031.md before this script was added.
"""
import argparse
import bisect
import json
import random

W, P, A = 4, 2, 4
N = 100_000
REGIMES = {
    "win": (315801, (1.6, 0.6), 0.65, 1),
    "no_win": (315802, (1.8, 1.8), 0.65, 1),
    "transfer": (315803, (1.4, 0.7), 0.65, 1),
    "sensitivity": (315804, (1.6, 0.6), 0.20, 2),
}


def f_star(d, q, cost):
    if d <= 0 or q <= 0:
        return 0.
    return max(0., min(1., (A*d-P)/(q*d*(P*cost+A))))


def predicted_cycles(d, f, q, cost, n=N):
    bank = n*d*(1-q*f)
    alu = n*(1+cost*d*q*f)
    return max(n/W, bank/P, alu/A)


def phase_sample(rng, d, q):
    """One independent physical-register read per hot operand.

    Each instruction has two operands; eligible reads are a subset of hot reads.
    A shared selection uniform lets all policies see the same offered workload.
    """
    total = 0
    eligible_thresholds = []
    for _ in range(N):
        for _ in range(2):
            if rng.random() < d/2:
                total += 1
                if rng.random() < q:
                    eligible_thresholds.append(rng.random())
    eligible_thresholds.sort()
    return (total, eligible_thresholds)


def actual_cycles(phase, f, cost):
    hot_total, thresholds = phase
    remat = bisect.bisect_left(thresholds, f)
    # The ALU cost and RF read removal are charged to the SAME operand.
    return max(N/W, (hot_total-remat)/P, (N+cost*remat)/A)


def best_global(phases, cost, measured):
    options = [i/1000 for i in range(1001)]
    if measured:
        key = lambda f: sum(actual_cycles(p, f, cost) for p in phases)
    else:
        raise ValueError("Only measured global optimum used here")
    return min(options, key=key)


def evaluate(name):
    seed, ds, q, cost = REGIMES[name]
    fs = [f_star(d, q, cost) for d in ds]
    expected_static = min((i/1000 for i in range(1001)),
                          key=lambda f: sum(predicted_cycles(d, f, q, cost) for d in ds))
    predicted_dynamic = sum(predicted_cycles(d, f, q, cost) for d, f in zip(ds, fs))
    predicted_static = sum(predicted_cycles(d, expected_static, q, cost) for d in ds)
    rng = random.Random(seed)
    phases = [phase_sample(rng, d, q) for d in ds]
    # Hindsight global-static control is strictly stronger than the frozen
    # expected-global-static control.
    hindsight_static = best_global(phases, cost, True)
    measured_dynamic = sum(actual_cycles(p, f, cost) for p, f in zip(phases, fs))
    measured_static = sum(actual_cycles(p, expected_static, cost) for p in phases)
    measured_hindsight = sum(actual_cycles(p, hindsight_static, cost) for p in phases)
    phase_oracle = sum(min(actual_cycles(p, i/1000, cost)
                           for i in range(1001)) for p in phases)
    # A phase-aware compiler with identical phase information and f choices
    # performs exactly the same rematerializations as the candidate.
    strong_same_info = measured_dynamic
    ratio = measured_hindsight/measured_dynamic
    frozen_intervals = {
        "win": (1.06, 1.09), "no_win": (0.995, 1.005),
        "transfer": (1.045, 1.075),
    }
    lo, hi = frozen_intervals.get(name, (0., float("inf")))
    return {
        "seed": seed, "mean_hot_reads_per_instruction": list(ds),
        "eligibility_q": q, "remat_alu_cost": cost,
        "frozen_f_star": fs, "expected_global_static_f": expected_static,
        "hindsight_global_static_f": hindsight_static,
        "predicted_gain_vs_expected_static": predicted_static/predicted_dynamic,
        "sampled_hot_reads": [p[0] for p in phases],
        "sampled_eligible_reads": [len(p[1]) for p in phases],
        "measured_resource_cycles_dynamic": measured_dynamic,
        "measured_resource_cycles_static": measured_static,
        "measured_resource_cycles_hindsight_static": measured_hindsight,
        "measured_resource_cycles_phase_oracle": phase_oracle,
        "observed_gain_vs_hindsight_static": ratio,
        "incremental_gain_vs_equal_information_phase_aware": strong_same_info/measured_dynamic,
        "within_frozen_interval": lo <= ratio <= hi if name in frozen_intervals else None,
        "novelty_gate_pass": strong_same_info/measured_dynamic >= 1.02,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--regime", choices=[*REGIMES, "all"], default="all")
    args = p.parse_args()
    names = list(REGIMES) if args.regime == "all" else [args.regime]
    rows = {name: evaluate(name) for name in names}
    for name in ("win", "no_win", "transfer"):
        if name in rows:
            assert rows[name]["within_frozen_interval"], (name, rows[name])
    for row in rows.values():
        assert row["measured_resource_cycles_phase_oracle"] <= row["measured_resource_cycles_dynamic"] + 1e-8
        assert row["measured_resource_cycles_hindsight_static"] <= row["measured_resource_cycles_static"] + 1e-8
        assert row["incremental_gain_vs_equal_information_phase_aware"] == 1.
        assert not row["novelty_gate_pass"]
    print(json.dumps({
        "evidence_tier": "sampled optimistic resource lower bound; NOT measured GPU IPC",
        "prereg": "research/v315/PREREG_20261031.md",
        "decision": "RETIRE V315 as incremental mechanism vs equally informed phase-aware compiler",
        "regimes": rows,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
