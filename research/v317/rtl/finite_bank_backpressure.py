#!/usr/bin/env python3
"""V317 frozen finite-buffer bank-port falsification.

This is synthetic traffic, not GPU RTL or GPU IPC. Do not fit after outcomes.
"""
from __future__ import annotations
from collections import deque
from statistics import mean, pstdev
import json
import random

SEEDS = (17, 71, 173)
WARMUP = 2048
MEASURED = 30000
LOCAL_DEPTH = 4
OUTPUT_DEPTH = 8
TOL = 0.015
REGIMES = (
    ("W_ports", 32, 32, 1.0),
    ("N_ports", 4, 4, 1.0),
    ("R_eligibility", 32, 32, 0.85),
    ("N_bandwidth", 32, 12, 1.0),
    ("H_marginal", 32, 32, 0.95),
)
FROZEN_RATIOS = {
    "W_ports": 1.0273525341549115,
    "N_ports": 1.0002510997707081,
    "R_eligibility": 0.9185977952901293,
    "N_bandwidth": 1.000014520112589,
    "H_marginal": 0.9924918555270553,
    "E_equal_resource": 1.0,
}

def independent_head_rate(tiles: int, banks: int, q: float, capacity: int) -> float:
    """Exact occupancy distribution for independent heads; not called by simulate."""
    probs = [1.0] + [0.0] * banks
    for _ in range(tiles):
        nxt = [0.0] * (banks + 1)
        for occupied, prob in enumerate(probs):
            nxt[occupied] += prob * (1.0 - q + q * occupied / banks)
            if occupied < banks:
                nxt[occupied + 1] += prob * q * (banks - occupied) / banks
        probs = nxt
    assert abs(sum(probs) - 1) < 1e-10
    return sum(prob * min(occupied, capacity) for occupied, prob in enumerate(probs))

def simulate(tiles: int, banks: int, capacity: int, q: float, seed: int) -> dict:
    """Explicit FIFO heads, one-port banks, rotating arbitration, finite output buffer."""
    rng = random.Random(seed)
    queues = [deque() for _ in range(tiles)]
    last_grant = [-1] * banks
    output_backlog = 0
    served = blocked_admissions = bank_stalls = output_stalls = 0
    max_local = max_output = 0
    for cycle in range(WARMUP + MEASURED):
        measuring = cycle >= WARMUP
        for tile in range(tiles):
            if len(queues[tile]) < LOCAL_DEPTH:
                queues[tile].append(rng.randrange(banks))
            elif measuring:
                blocked_admissions += 1
        contenders = [[] for _ in range(banks)]
        for tile in range(tiles):
            if queues[tile] and rng.random() < q:
                contenders[queues[tile][0]].append(tile)
        winners = []
        for bank, candidates in enumerate(contenders):
            if not candidates:
                continue
            after = (last_grant[bank] + 1) % tiles
            winner = min(candidates, key=lambda tile: (tile - after) % tiles)
            winners.append((bank, winner))
            if measuring:
                bank_stalls += len(candidates) - 1
        # Work-conserving same-cycle output bypass. Buffer never exceeds 8.
        available = max(0, OUTPUT_DEPTH + capacity - output_backlog)
        if len(winners) > available:
            # Rotate bank preference to avoid fixed-bank starvation.
            first = cycle % banks
            winners.sort(key=lambda x: (x[0] - first) % banks)
        accepted = winners[:available]
        if measuring:
            output_stalls += len(winners) - len(accepted)
        for bank, tile in accepted:
            assert queues[tile][0] == bank
            queues[tile].popleft()
            last_grant[bank] = tile
        output_backlog += len(accepted)
        delivered = min(capacity, output_backlog)
        output_backlog -= delivered
        assert 0 <= output_backlog <= OUTPUT_DEPTH
        if measuring:
            served += delivered
            max_output = max(max_output, output_backlog)
            max_local = max(max_local, *(len(q_) for q_ in queues))
    return {
        "rate": served / MEASURED,
        "completed": served,
        "blocked_admissions": blocked_admissions,
        "bank_stalls": bank_stalls,
        "output_stalls": output_stalls,
        "max_local_fifo": max_local,
        "max_output_fifo": max_output,
        "final_output_backlog": output_backlog,
    }

def run() -> dict:
    rows = []
    for name, banks, capacity, pair_q in REGIMES + (("E_equal_resource", 32, 32, 1.0),):
        src_tiles = 24
        pair_tiles = 24 if name == "E_equal_resource" else 25
        pred = independent_head_rate(pair_tiles, banks, pair_q, capacity) / independent_head_rate(src_tiles, banks, 1.0, capacity)
        assert abs(pred - FROZEN_RATIOS[name]) < 1e-10
        samples = []
        for seed in SEEDS:
            source = simulate(src_tiles, banks, capacity, 1.0, seed)
            pair = simulate(pair_tiles, banks, capacity, pair_q, seed)
            samples.append({"seed": seed, "ratio": pair["rate"] / source["rate"], "source": source, "pairwise": pair})
        avg = mean(s["ratio"] for s in samples)
        rows.append({"regime": name, "banks": banks, "bandwidth": capacity, "pairwise_q": pair_q,
                     "predicted_independent_head_ratio": pred, "finite_fifo_ratio_mean": avg,
                     "absolute_error": abs(avg - pred), "falsified": abs(avg - pred) > TOL,
                     "stddev": pstdev(s["ratio"] for s in samples), "samples": samples})
    return {"evidence_tier": "synthetic finite FIFO, bank ports and output backpressure; measured controller area only in external tile-count assumption",
            "source_tiles": 24, "pairwise_tiles": 25, "seeds": SEEDS,
            "warmup_cycles": WARMUP, "measured_cycles": MEASURED,
            "local_fifo_depth": LOCAL_DEPTH, "output_fifo_depth": OUTPUT_DEPTH,
            "falsification_threshold": TOL, "rows": rows,
            "any_independent_head_falsified": any(r["falsified"] for r in rows)}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
