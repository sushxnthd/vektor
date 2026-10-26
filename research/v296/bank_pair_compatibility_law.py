#!/usr/bin/env python3
"""V296 exact two-request RF-bank compatibility law, prospective holdouts.

This is a sub-law for two independent requests, not GPU speedup or physical closure.
Frozen protocol: BANK_PAIR_COMPATIBILITY_PREREG_20261026.md.
"""
import argparse
import json
import random
from pathlib import Path

BANKS = 16
PORTS = 2
REGIMES = (
    ("uniform_independent", 0.0, 0.0),
    ("uniform_correlated", 0.0, 0.7),
    ("moderate_hotspot", 0.45, 0.2),
    ("heavy_hotspot", 0.80, 0.2),
    ("extreme_hotspot", 0.95, 0.7),
)
# Prospective seeds; pilot seeds 271828, 314159, 161803 are excluded.
HOLDOUT_SEEDS = (424243, 515151, 616161)
N_PER_HOLDOUT = 50000


def distribution(h):
    if not 0 <= h <= 1:
        raise ValueError("invalid hotspot")
    return [h+(1-h)/BANKS if k == 0 else (1-h)/BANKS for k in range(BANKS)]


def q(p, rho, a, b):
    return p[a] * (rho * (a == b) + (1-rho)*p[b])


def analytic(p, rho):
    """Closed form O(B^2), no fit or random sampling."""
    if len(p) != BANKS or min(p) < 0 or abs(sum(p)-1) > 1e-10:
        raise ValueError("invalid bank probabilities")
    if not 0 <= rho <= 1:
        raise ValueError("invalid operand-copy probability")
    diagonal = [q(p,rho,a,a) for a in range(BANKS)]
    result = 0.0
    for a in range(BANKS):
        avoid_a = (1-p[a]) * (rho+(1-rho)*(1-p[a]))
        result += diagonal[a]*avoid_a
        for b in range(BANKS):
            if a != b:
                result += q(p,rho,a,b)*(1-diagonal[a]-diagonal[b])
    return result


def exhaustive_reference(p, rho):
    """Independent 16^4 reference: count all four operand bank demands."""
    pairs = [(a,b,q(p,rho,a,b)) for a in range(BANKS) for b in range(BANKS)]
    total = 0.0
    for a,b,pab in pairs:
        for c,d,pcd in pairs:
            counts = {}
            for k in (a,b,c,d):
                counts[k] = counts.get(k,0)+1
            if max(counts.values()) <= PORTS:
                total += pab*pcd
    return total


def draw_bank(rng,p):
    x = rng.random()
    for k,pk in enumerate(p):
        x -= pk
        if x < 0:
            return k
    return BANKS-1


def draw_pair(rng,p,rho):
    a = draw_bank(rng,p)
    return a, a if rng.random() < rho else draw_bank(rng,p)


def observed(p,rho,seed,n):
    rng = random.Random(seed)
    ok = 0
    for _ in range(n):
        a,b = draw_pair(rng,p,rho)
        c,d = draw_pair(rng,p,rho)
        counts = [0]*BANKS
        for k in (a,b,c,d):
            counts[k] += 1
        ok += max(counts) <= PORTS
    return ok/n


def self_test():
    for h,rho in ((0,0),(0,1),(0.45,0.2),(0.8,0.2),(0.95,0.7),(1,1)):
        p = distribution(h)
        prediction = analytic(p,rho)
        reference = exhaustive_reference(p,rho)
        assert abs(prediction-reference) < 1e-10, (h,rho,prediction,reference)
        assert 0 <= prediction <= 1
    assert abs(analytic(distribution(1),0.2)) < 1e-12
    assert analytic(distribution(0),0) > 0.95
    try:
        analytic(distribution(0),1.01)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid rho accepted")
    print("V296_BANK_PAIR_COMPATIBILITY_EXACT_ORACLE_PASS")


def evaluate(output):
    self_test()
    rows = []
    for name,h,rho in REGIMES:
        p = distribution(h)
        predicted = analytic(p,rho)
        independent = exhaustive_reference(p,rho)
        for seed in HOLDOUT_SEEDS:
            actual = observed(p,rho,seed,N_PER_HOLDOUT)
            se = (predicted*(1-predicted)/N_PER_HOLDOUT)**0.5
            tolerance = max(0.005,5*se)
            row = {
                "regime":name, "hotspot":h, "operand_copy_probability":rho,
                "holdout_seed":seed, "n_pairs":N_PER_HOLDOUT,
                "predicted_compatible_probability":predicted,
                "independent_enumeration_probability":independent,
                "observed_compatible_probability":actual,
                "absolute_prediction_error":abs(actual-predicted),
                "frozen_tolerance":tolerance,
                "pass":abs(actual-predicted) <= tolerance
            }
            rows.append(row)
    result = {
        "evidence_tier":"EXACT_TWO_REQUEST_COMPATIBILITY_SYNTHETIC_PROSPECTIVE_HOLDOUT_NOT_GPU_PERFORMANCE",
        "prereg_commit":"ff6b088ab901a88e7751b5abdf0435916af0bae1",
        "pilot_seeds_excluded":[271828,314159,161803],
        "n_heldout_cells":len(rows), "n_samples_per_cell":N_PER_HOLDOUT,
        "parameters_fitted":False,
        "all_pass":all(row["pass"] for row in rows),
        "scope_limit":"Not V296-vs-serial speedup, not scheduler, traffic, power, or routed physical closure.",
        "rows":rows
    }
    Path(output).write_text(json.dumps(result,indent=2)+"\n")
    if not result["all_pass"]:
        raise AssertionError("heldout diagnostic falsified; preserve failed JSON")
    print("V296_BANK_PAIR_COMPATIBILITY_PROSPECTIVE_HOLDOUT_PASS")
    for name,_,_ in REGIMES:
        matching=[r for r in rows if r["regime"]==name]
        print(name,"prediction",round(matching[0]["predicted_compatible_probability"],6),
              "mean_observed",round(sum(r["observed_compatible_probability"] for r in matching)/len(matching),6),
              "max_abs_error",round(max(r["absolute_prediction_error"] for r in matching),6))
    return result


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--evaluate",action="store_true")
    ap.add_argument("--output",default="research/v296/BANK_PAIR_COMPATIBILITY_HELDOUT_20261026.json")
    args=ap.parse_args()
    if args.self_test:self_test()
    if args.evaluate:evaluate(args.output)
    if not (args.self_test or args.evaluate):ap.error("choose --self-test or --evaluate")
