#!/usr/bin/env python3
"""Prospective decoded-area V296 matched-budget synthetic replay.

Preregistered at 47395ad9df837871c50c6a92eb157306854337c6.
Uses the existing port-exact replay plus its independently implemented
reference; this experiment isolates area packing and clock/bandwidth
boundaries, NOT different arbitration policies or physical performance.
"""
import argparse
from decimal import Decimal
import json
from pathlib import Path

from joint_occupancy_area_packing import bank_streams, simulate, reference

SERIAL_AREA = Decimal("10143.112")
PAIRWISE_AREA = Decimal("10426.402")
SERIAL_SLICES = 17
PAIRWISE_SLICES = 16
LATENCY = 2
WARMUP = 500
MEASURE = 4000
SEEDS = (61719, 61743)
# (name, resident warps, hotspot, shared waves per serial-clock interval, period ratio)
CELLS = (
    ("predicted_no_win_equal_clock", 180, 0.0, None, 1.00),
    ("predicted_win_hypothetical_clock", 180, 0.0, None, 0.90),
    ("predicted_no_win_shared_cap", 180, 0.0, 25.0, 0.90),
    ("boundary_period_0p94", 180, 0.0, None, 0.94),
    ("low_occupancy_equal", 32, 0.0, None, 1.00),
    ("low_occupancy_clock", 32, 0.0, None, 0.90),
    ("high_occupancy_equal", 256, 0.0, None, 1.00),
    ("hotspot_80pct_equal", 180, 0.8, None, 1.00),
)

def exact_area_floor():
    budget = SERIAL_AREA * SERIAL_SLICES
    assert PAIRWISE_AREA * PAIRWISE_SLICES <= budget
    assert PAIRWISE_AREA * (PAIRWISE_SLICES + 1) > budget
    assert budget // PAIRWISE_AREA == PAIRWISE_SLICES
    return budget

def gain(qs, qp, period_ratio, shared_cap):
    if min(qs, qp, period_ratio) <= 0:
        raise ValueError("nonpositive admission/period")
    serial_rate = qs
    pairwise_rate = qp / period_ratio
    if shared_cap is not None:
        if shared_cap <= 0:
            raise ValueError("nonpositive shared cap")
        # External shared capacity is per PHYSICAL time, not per local cycle.
        serial_rate = min(serial_rate, shared_cap)
        pairwise_rate = min(pairwise_rate, shared_cap)
    return pairwise_rate / serial_rate - 1, serial_rate, pairwise_rate

def self_test():
    exact_area_floor()
    # Independently implemented reference state machine: compare full per-cycle
    # admissions for 2-cycle dependency, variable warp counts and bank hotspots.
    for seed in (3, 5):
        for warps in (7, 13):
            for slices in (2, 3):
                streams = bank_streams(seed, warps, 0.35, 90)
                fast = simulate(streams, slices, LATENCY, cycles=60, trace=True)
                slow = reference(streams, slices, LATENCY, cycles=60)
                assert fast["history"] == slow
    g, qs, qp = gain(40, 38, 0.90, 25)
    assert (g, qs, qp) == (0, 25, 25)
    # A faulty cycle-domain cap before frequency conversion predicts a gain:
    faulty = min(38, 25) / min(40, 25) / 0.90 - 1
    assert faulty > 0.10 and g == 0
    assert gain(68, 64, 1.0, None)[0] < 0
    assert gain(68, 64, 0.90, None)[0] > 0
    assert gain(68, 64, 64/68, None)[0] == 0
    print("V296_DECODED_AREA_INDEPENDENT_CHECK_PASS")

def evaluate(output):
    budget = exact_area_floor()
    results = []
    for seed in SEEDS:
        for name, W, hotspot, shared_cap, period in CELLS:
            streams = bank_streams(seed, W, hotspot)
            s = simulate(streams, SERIAL_SLICES, LATENCY)
            p = simulate(streams, PAIRWISE_SLICES, LATENCY)
            qs, qp = s["issued_per_cycle"], p["issued_per_cycle"]
            g, sr, pr = gain(qs, qp, period, shared_cap)
            assert qs <= min(4*SERIAL_SLICES, W/LATENCY) + 1e-9
            assert qp <= min(4*PAIRWISE_SLICES, W/LATENCY) + 1e-9
            row = dict(seed=seed, regime=name, total_warps=W,
                       hotspot=hotspot, candidate_period_ratio=period,
                       shared_cap_waves_per_serial_period=shared_cap,
                       serial_admissions_per_cycle=qs,
                       candidate_admissions_per_cycle=qp,
                       observed_clock_period_break_even=qp/qs,
                       serial_useful_per_serial_period=sr,
                       candidate_useful_per_serial_period=pr,
                       gain_fraction=g)
            results.append(row)
            print(seed, name, "q_s", round(qs, 5), "q_p",
                  round(qp, 5), "gain_pct", round(g*100, 5))
    for seed in SEEDS:
        d = {r["regime"]: r for r in results if r["seed"] == seed}
        assert d["predicted_no_win_equal_clock"]["gain_fraction"] < 0
        assert d["predicted_win_hypothetical_clock"]["gain_fraction"] > 0
        assert abs(d["predicted_no_win_shared_cap"]["gain_fraction"]) < 1e-12
        assert d["high_occupancy_equal"]["gain_fraction"] < 0
    payload = {
        "evidence_tier": "PREREGISTERED_SYNTHETIC_MATCHED_MAPPED_AREA_NOT_PHYSICAL",
        "prereg_commit": "47395ad9df837871c50c6a92eb157306854337c6",
        "mapped_area_source_run": 40337484954,
        "mapped_area_source_artifact_sha256": "0cafd08a8a4cbd2164336c9f2ad11e6037c3fac02aa42243ebd1a7641d704ba2",
        "serial_slices": SERIAL_SLICES,
        "pairwise_slices": PAIRWISE_SLICES,
        "shared_budget_um2": str(budget),
        "serial_mapped_area_um2": str(SERIAL_AREA),
        "pairwise_mapped_area_um2": str(PAIRWISE_AREA),
        "same_scheduler_model_both_contestants": True,
        "both_latency_cycles": LATENCY,
        "warmup_cycles": WARMUP,
        "measured_cycles": MEASURE,
        "ideal_saturated_break_even_period_ratio": PAIRWISE_SLICES / SERIAL_SLICES,
        "results": results
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    print("V296_DECODED_AREA_FROZEN_REPLAY_PASS")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--evaluate", action="store_true")
    ap.add_argument("--output", default="research/v296/DECODED_AREA_REPLAY_RESULTS_20261026.json")
    args = ap.parse_args()
    if args.self_test:
        self_test()
    if args.evaluate:
        evaluate(args.output)
    if not (args.self_test or args.evaluate):
        ap.error("select --self-test or --evaluate")
