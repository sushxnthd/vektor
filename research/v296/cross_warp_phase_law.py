#!/usr/bin/env python3
"""V296 cross-warp phase synchrony: prospective exact-mixture law and independent oracle.

This is a synthetic admission sub-law, not routed timing, hardware throughput, or
an architectural advantage over the strongest serial control.
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

from four_request_admission_law import exact_expected

BANKS, PORTS, REQUESTS = 16, 2, 4
SEEDS = (20261031, 20261101, 20261102)
BATCHES = 30000
TOLERANCE = 0.035
PREREG_COMMIT = "0b0f51a7260d91e8c60b16172c19d02716714a3b"
REGIMES = (
    ("uniform_control", 0.0, 0.0, 0.0),
    ("uniform_partial_sync", 0.0, 0.0, 0.25),
    ("uniform_strong_sync", 0.0, 0.0, 0.8),
    ("moderate_hotspot_sync", 0.45, 0.2, 0.65),
    ("heavy_hotspot_sync", 0.8, 0.2, 0.95),
)


def check(h, rho, s):
    if any(not isinstance(x, (float, int)) or isinstance(x, bool) or not 0 <= x <= 1
           for x in (h, rho, s)):
        raise ValueError("h, rho, s must be numeric probabilities in [0,1]")


def bank_probabilities(h):
    return [h + (1 - h) / BANKS] + [(1 - h) / BANKS] * (BANKS - 1)


def synchronized_expected(h, rho):
    check(h, rho, 0)
    p = bank_probabilities(h)
    return 2 - (rho + (1 - rho) * sum(v*v for v in p))


def predicted(h, rho, s):
    check(h, rho, s)
    iid = exact_expected(h, rho, REQUESTS)
    sync = synchronized_expected(h, rho)
    return (1 - s) * iid + s * sync


def draw(rng, probabilities):
    u = rng.random()
    for bank, p in enumerate(probabilities):
        u -= p
        if u < 0:
            return bank
    return BANKS - 1


def sample_pairs(rng, p, rho, s):
    synchronized = rng.random() < s
    if synchronized:
        a = draw(rng, p)
        b = a if rng.random() < rho else draw(rng, p)
        return [(a, b)] * REQUESTS
    pairs = []
    for _ in range(REQUESTS):
        a = draw(rng, p)
        b = a if rng.random() < rho else draw(rng, p)
        pairs.append((a, b))
    return pairs


def simulate(h, rho, s, seed, batches, audit=False):
    """Independent event accounting; never uses the analytic transition model."""
    check(h, rho, s)
    if type(batches) is not int or batches <= 0 or type(seed) is not int:
        raise ValueError("invalid batch count or seed")
    rng = random.Random(seed)
    p = bank_probabilities(h)
    total = 0
    for _ in range(batches):
        pairs = sample_pairs(rng, p, rho, s)
        if audit:
            # Independent implementation: count bank demands per candidate,
            # checking against a cumulative admitted-demand map.
            occupied = Counter()
            for a, b in pairs:
                demand = Counter((a, b))
                if all(occupied[k] + v <= PORTS for k, v in demand.items()):
                    occupied.update(demand)
                    total += 1
        else:
            free = [PORTS] * BANKS
            for a, b in pairs:
                if a == b:
                    if free[a] >= 2:
                        free[a] -= 2
                        total += 1
                elif free[a] >= 1 and free[b] >= 1:
                    free[a] -= 1
                    free[b] -= 1
                    total += 1
            assert min(free) >= 0
    return total / batches


def self_test():
    assert synchronized_expected(0, 0) == 1.9375
    assert synchronized_expected(1, 1) == 1
    assert synchronized_expected(1, 0) == 1
    assert abs(predicted(0, 0, 0) - exact_expected(0, 0, 4)) < 1e-12
    assert abs(predicted(0, 0, 1) - 1.9375) < 1e-12
    assert abs(predicted(0.45, 0.2, 0.65) -
               (0.35 * exact_expected(0.45, 0.2, 4) +
                0.65 * synchronized_expected(0.45, 0.2))) < 1e-12
    assert simulate(1, 1, 1, 37, 100) == 1
    for seed in (31, 37):
        for h, rho, s in ((0, 0, 0.8), (0.45, 0.2, 0.65), (1, 1, 1)):
            assert simulate(h, rho, s, seed, 100, False) == simulate(h, rho, s, seed, 100, True)
    for bad in ((-0.1, 0, 0), (0, 1.1, 0), (0, 0, 1.1), (True, 0, 0)):
        try:
            predicted(*bad)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted invalid probability")
    print("V296_CROSS_WARP_PHASE_SELFTEST_PASS")


def evaluate(output):
    self_test()
    rows = []
    for name, h, rho, s in REGIMES:
        iid = exact_expected(h, rho, REQUESTS)
        sync = synchronized_expected(h, rho)
        q = predicted(h, rho, s)
        for seed in SEEDS:
            observed = simulate(h, rho, s, seed, BATCHES)
            independent_audit = simulate(h, rho, s, seed, BATCHES, audit=True)
            rows.append({
                "regime": name, "h": h, "rho": rho, "s": s,
                "seed": seed, "batches": BATCHES,
                "iid_only_prediction": iid,
                "fully_synchronized_prediction": sync,
                "mixture_prediction": q,
                "independent_observed": observed,
                "second_event_accounting_observed": independent_audit,
                "mixture_abs_error": abs(observed - q),
                "iid_abs_error": abs(observed - iid),
                "mixture_pass": abs(observed - q) <= TOLERANCE,
                "independent_audit_pass": observed == independent_audit,
            })
    strong = [r for r in rows if r["regime"] in
              ("uniform_strong_sync", "moderate_hotspot_sync")]
    control = [r for r in rows if r["regime"] == "uniform_control"]
    iid_falsified = all(r["iid_abs_error"] >= 0.25 for r in strong)
    all_pass = (all(r["mixture_pass"] and r["independent_audit_pass"] for r in rows)
                and iid_falsified
                and all(abs(r["mixture_prediction"] - r["iid_only_prediction"]) < 1e-12
                        for r in control))
    result = {
        "evidence_tier": "SYNTHETIC_PROSPECTIVE_CROSS_WARP_CORRELATION_NOT_GPU_HARDWARE",
        "prereg_commit": PREREG_COMMIT,
        "holdout_cells": len(rows),
        "tolerance_admissions_per_batch": TOLERANCE,
        "iid_transfer_falsified_in_strong_sync_regimes": iid_falsified,
        "all_pass": all_pass,
        "physical_signoff": False,
        "v296_vs_serial_throughput_claim": False,
        "limitation": "Mixture law exact only for stated phase generator; s must be known independently; no real GPU traces, physical clocks, or architecture speedup.",
        "rows": rows,
    }
    Path(output).write_text(json.dumps(result, indent=2) + "\n")
    print("V296_CROSS_WARP_PHASE_HOLDOUT_PASS" if all_pass else "V296_CROSS_WARP_PHASE_HOLDOUT_FAIL")
    for name, *_ in REGIMES:
        r = [x for x in rows if x["regime"] == name]
        print(name, "prediction", round(r[0]["mixture_prediction"], 5),
              "mean observed", round(sum(x["independent_observed"] for x in r)/3, 5),
              "max abs error", round(max(x["mixture_abs_error"] for x in r), 5),
              "iid error", round(max(x["iid_abs_error"] for x in r), 5))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--evaluate", action="store_true")
    p.add_argument("--output", default="research/v296/CROSS_WARP_PHASE_HELDOUT_20261027.json")
    a = p.parse_args()
    if a.self_test:
        self_test()
    if a.evaluate:
        if not evaluate(a.output)["all_pass"]:
            raise SystemExit(1)
    if not (a.self_test or a.evaluate):
        p.error("choose --self-test or --evaluate")
