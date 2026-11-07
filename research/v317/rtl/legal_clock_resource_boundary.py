#!/usr/bin/env python3
"""Exact conditional tile-reinvestment boundary from measured legal-clock area.

Deterministic capacity accounting, not GPU IPC or an architectural novelty claim.
Areas are from the independent audit of Actions run 41387898294.
"""
import argparse
import json
import math

PHYSICAL = {
    "2.050": {"source_area": 7244.78, "pair_area": 6576.58},
    "2.200": {"source_area": 7096.08, "pair_area": 6560.36},
}

def tile_counts(budget_um2, other_area_um2, source_area, pair_area):
    assert budget_um2 >= 0 and other_area_um2 >= 0
    assert 0 < pair_area < source_area
    return (math.floor(budget_um2 / (other_area_um2 + source_area)),
            math.floor(budget_um2 / (other_area_um2 + pair_area)))

def service_ratio(source_tiles, pair_tiles, occupancy_ratio, bandwidth_ratio):
    """Persistent-backlog throughput ratio, equal clock and RF port resources.

    occupancy_ratio = pairwise per-tile useful service / source per-tile service,
    including control overhead. bandwidth_ratio = shared sustainable capacity /
    source unconstrained aggregate service. Does not model stochastic unqueued bins.
    """
    assert source_tiles > 0 and pair_tiles > 0
    assert occupancy_ratio >= 0 and bandwidth_ratio > 0
    offered_ratio = pair_tiles * occupancy_ratio / source_tiles
    return min(offered_ratio, bandwidth_ratio) / min(1.0, bandwidth_ratio)

def scenarios(other_area_um2=40000, budget_um2=1170000):
    result = []
    for period, areas in PHYSICAL.items():
        ns, np = tile_counts(budget_um2, other_area_um2, areas["source_area"], areas["pair_area"])
        assert ns > 0
        result.append({
            "clock_ns": period, "source_tiles": ns, "pairwise_tiles": np,
            "tile_area_reduction_pct": 100 * (areas["source_area"] - areas["pair_area"]) / (other_area_um2 + areas["source_area"]),
            "frozen_win_backlogged_b1_10_q1": service_ratio(ns, np, 1.0, 1.10),
            "frozen_no_win_backlogged_b0_95_q1": service_ratio(ns, np, 1.0, 0.95),
            "frozen_occupancy_penalty_b1_10_q0_95": service_ratio(ns, np, 0.95, 1.10),
            "break_even_pairwise_occupancy_ratio_when_unconstrained": ns / np,
        })
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--other-area", type=float, default=40000)
    p.add_argument("--budget", type=float, default=1170000)
    a = p.parse_args()
    print(json.dumps(scenarios(a.other_area, a.budget), indent=2))
    assert service_ratio(24, 25, 1, 1.10) == 25 / 24
    assert service_ratio(24, 25, 1, 0.95) == 1
    assert math.isclose(service_ratio(24, 25, .95, 1.10), 25*.95/24)
    assert all(row["source_tiles"] == 24 and row["pairwise_tiles"] == 25 for row in scenarios())
    assert all(row["source_tiles"] == 24 and row["pairwise_tiles"] == 24 for row in scenarios(40000, 1150000))
