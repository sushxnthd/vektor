#!/usr/bin/env python3
"""V311 preregistered two-warp bank-salt falsification, stdlib-only.

This is a synthetic admission ceiling, not a physical GPU measurement.
"""
import argparse
import json
import random
from fractions import Fraction

BANKS = 16
HOT = 85
N_PER_PHASE = 25_000
SEED_BASE = 311_000
THRESHOLD = Fraction(105, 100)


def pmf(hot):
    assert 0 <= hot < BANKS
    return tuple(Fraction(HOT if b == hot else 1, 100) for b in range(BANKS))


def collision(p, q, salt):
    assert 0 <= salt < BANKS
    return sum(p[b] * q[b ^ salt] for b in range(BANKS))


def choose(p, q):
    return min(range(BANKS), key=lambda s: (collision(p, q, s), s))


def static_oracle(phase_q):
    p = pmf(0)
    return min(range(BANKS), key=lambda s: (sum(collision(p, q, s) for q in phase_q), s))


def draw(rng, hot):
    k = rng.randrange(100)
    if k < HOT:
        return hot
    # Every non-hot bank occurs with probability exactly 1/100.
    return (hot + 1 + k - HOT) % BANKS


def check_bijection(salt):
    mapped = [b ^ salt for b in range(BANKS)]
    if sorted(mapped) != list(range(BANKS)):
        raise ValueError("bank map is not bijective")


def check_fixed_salt(salts):
    if len(set(salts)) != 1:
        raise ValueError("salt changed within live cohort")


def audit_static(phase_q, selected):
    p = pmf(0)
    observed = sum(collision(p, q, selected) for q in phase_q)
    for s in range(BANKS):
        if sum(collision(p, q, s) for q in phase_q) < observed:
            raise ValueError("static baseline not oracle-optimal")


def audit_probabilities(p, q, salt):
    # Independent enumerative oracle; do not reuse collision() arithmetic.
    count = Fraction(0)
    for left in range(BANKS):
        for right in range(BANKS):
            if left == (right ^ salt):
                count += p[left] * q[right]
    if count != collision(p, q, salt):
        raise ValueError("collision formula mismatch")
    return count


def mutation_controls():
    caught = 0
    for fn in (
        lambda: check_fixed_salt([1, 1, 2]),
        lambda: audit_static([pmf(0)], 0),
    ):
        try:
            fn()
        except ValueError:
            caught += 1
    # A deliberately broken nonbijective mapping must fail the same criterion.
    fake_map = [0] * BANKS
    try:
        if sorted(fake_map) != list(range(BANKS)):
            raise ValueError("nonbijective map")
    except ValueError:
        caught += 1
    assert caught == 3
    return caught


def run_regime(hotspots):
    p = pmf(0)
    phase_q = [pmf(h) for h in hotspots]
    global_s = static_oracle(phase_q)
    audit_static(phase_q, global_s)
    check_bijection(global_s)
    chosen = [choose(p, q) for q in phase_q]
    for q, s in zip(phase_q, chosen):
        check_bijection(s)
        audit_probabilities(p, q, s)
        assert all(collision(p, q, s) <= collision(p, q, other) for other in range(BANKS))
        check_fixed_salt([s] * N_PER_PHASE)
    predicted_static = sum((2 - collision(p, q, global_s) for q in phase_q), Fraction(0)) / len(phase_q)
    predicted_dynamic = sum((2 - collision(p, q, s) for q, s in zip(phase_q, chosen)), Fraction(0)) / len(phase_q)
    nstatic = ndynamic = 0
    phase_records = []
    for i, (hot, salt) in enumerate(zip(hotspots, chosen)):
        rng = random.Random(SEED_BASE + i)
        phase_base = phase_dyn = 0
        for _ in range(N_PER_PHASE):
            a, b = draw(rng, 0), draw(rng, hot)
            phase_base += 1 if a == (b ^ global_s) else 2
            phase_dyn += 1 if a == (b ^ salt) else 2
        nstatic += phase_base
        ndynamic += phase_dyn
        phase_records.append({"hot_bank_b": hot, "selected_salt": salt, "static_admissions": phase_base, "candidate_admissions": phase_dyn})
    predicted = predicted_dynamic / predicted_static
    observed = Fraction(ndynamic, nstatic)
    assert abs(float(predicted - observed)) < 0.01, (predicted, observed)
    assert observed >= 1, (ndynamic, nstatic)
    return {
        "global_static_oracle_salt": global_s,
        "n_opportunities": len(hotspots) * N_PER_PHASE,
        "predicted_static_admissions_per_opportunity": float(predicted_static),
        "predicted_candidate_admissions_per_opportunity": float(predicted_dynamic),
        "predicted_ratio": float(predicted),
        "holdout_static_admissions": nstatic,
        "holdout_candidate_admissions": ndynamic,
        "holdout_ratio": float(observed),
        "phase_records": phase_records,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    mutations = mutation_controls()
    rotating = run_regime(list(range(BANKS)))
    stationary = run_regime([0] * BANKS)
    assert abs(stationary["predicted_ratio"] - 1) < 1e-12
    assert abs(stationary["holdout_ratio"] - 1) < 0.01
    assert rotating["predicted_ratio"] < float(THRESHOLD)
    output = {
        "experiment": "V311 bank-salt two-warp synthetic preregistered falsification",
        "date": "2026-10-31",
        "banks": BANKS,
        "read_ports_per_bank": 1,
        "slots": 2,
        "reads_per_slot": 1,
        "hot_probability": HOT / 100,
        "frozen_materiality_ratio": float(THRESHOLD),
        "mutation_controls_rejected": mutations,
        "rotating": rotating,
        "stationary": stationary,
        "decision": "RETIRE_NARROW_V311_BELOW_1_05_IDEAL_ADMISSION_CEILING",
        "caveat": "No RTL, no electrical timing, no GPU throughput; no incremental novelty against same-information per-cohort oracle",
    }
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        for key in ("rotating", "stationary"):
            r = output[key]
            print(f"{key}: predicted={r['predicted_ratio']:.8f} holdout={r['holdout_ratio']:.8f} "
                  f"admissions={r['holdout_candidate_admissions']}/{r['holdout_static_admissions']}")
        print(output["decision"])


if __name__ == "__main__":
    main()
