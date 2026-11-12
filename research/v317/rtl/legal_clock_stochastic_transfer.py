#!/usr/bin/env python3
"""Independent event simulation for V317 frozen legal-clock transfer cases.

Synthetic service opportunities and unbounded shared queue, NOT GPU IPC.
The event loop never calls the separate analytic capacity law.
"""
from __future__ import annotations
import json
import math
import random
from statistics import mean, pstdev

PHYSICAL = {
    '2.050': (7244.78, 6576.58),
    '2.200': (7096.08, 6560.36),
}
BUDGET = 1_170_000
OTHER_TILE_AREA = 40_000
SEEDS = (17, 71, 173, 719, 1723)
WARMUP = 4096
CYCLES = 120_000
TOL = 0.002
# id, normalized bandwidth, pairwise tile-opportunity probability, equal resources?
REGIMES = (
    ('W_frozen_win', 1.10, 1.00, False),
    ('N_frozen_bandwidth_no_win', .95, 1.00, False),
    ('R_frozen_occupancy_reversal', 1.10, .95, False),
    ('H1_unseen_modest_win', 1.07, .97, False),
    ('H2_unseen_occupancy_loss', 1.02, .90, False),
    ('H3_unseen_bandwidth_saturation', .88, .97, False),
    ('H4_unseen_clipped_win', 1.01, .99, False),
    ('E1_equal_resources', 1.10, 1.00, True),
    ('E2_equal_resources_penalty', 1.10, .95, True),
)

def tile_count(controller_area: float) -> int:
    return math.floor(BUDGET / (OTHER_TILE_AREA + controller_area))

def simulate(tiles: int, probability: float, normalized_bandwidth: float,
             seed: int, *, queued: bool = True) -> dict:
    """Independent event execution: local issue opportunities then shared server.

    Each tile emits at most one useful op/cycle, subject to probability.
    The global server accumulates fractional bandwidth credits. The queue
    is unbounded by design, so this is NOT a realizable SRAM/NoC model.
    """
    rng = random.Random(seed)
    backlog = 0
    credit = 0.0
    served = 0
    max_backlog = 0
    total = WARMUP + CYCLES
    for cycle in range(total):
        arrivals = tiles if probability == 1.0 else sum(rng.random() < probability for _ in range(tiles))
        credit += 24.0 * normalized_bandwidth
        allowance = int(credit + 1e-9)
        credit -= allowance
        available = arrivals + (backlog if queued else 0)
        delivered = min(available, allowance)
        backlog = available - delivered if queued else 0
        if cycle >= WARMUP:
            served += delivered
            if backlog > max_backlog:
                max_backlog = backlog
    return {'rate': served / CYCLES, 'final_backlog': backlog, 'max_measured_backlog': max_backlog}

def predicted_ratio(ns: int, np: int, q: float, b: float) -> float:
    """Separate precommitted capacity identity; not used by simulate()."""
    return min(np * q / ns, b) / min(1.0, b)

def run() -> dict:
    counts = {period: {'source': tile_count(s), 'pairwise': tile_count(p)}
              for period, (s,p) in PHYSICAL.items()}
    assert all(c == {'source':24,'pairwise':25} for c in counts.values()), counts
    rows = []
    for name, b, q, equal in REGIMES:
        ns, np = 24, 24 if equal else 25
        predicted = predicted_ratio(ns, np, q, b)
        seed_rows = []
        for seed in SEEDS:
            src = simulate(ns, 1.0, b, seed)
            pair = simulate(np, q, b, seed)
            seed_rows.append({'seed':seed, 'ratio':pair['rate']/src['rate'],
                              'source_rate':src['rate'], 'pairwise_rate':pair['rate'],
                              'source_final_backlog':src['final_backlog'],
                              'pairwise_final_backlog':pair['final_backlog']})
        avg = mean(r['ratio'] for r in seed_rows)
        rows.append({'name':name, 'source_tiles':ns, 'pairwise_tiles':np,
                     'b':b, 'q':q, 'frozen_prediction':predicted,
                     'measured_mean':avg,
                     'abs_error':abs(avg-predicted),
                     'seed_stddev':pstdev(r['ratio'] for r in seed_rows),
                     'pass':abs(avg-predicted) <= TOL,
                     'seeds':seed_rows})
    unqueued = []
    for seed in SEEDS:
        src = simulate(24,.75,.75,seed,queued=False)
        pair = simulate(25,.75,.75,seed,queued=False)
        unqueued.append(pair['rate']/src['rate'])
    return {'evidence_tier':'measured routed controller areas + synthetic workload arrivals and bandwidth',
            'area_counts':counts, 'seeds':SEEDS, 'warmup':WARMUP, 'measured_cycles':CYCLES,
            'tolerance':TOL, 'all_backlogged_pass':all(r['pass'] for r in rows),
            'backlogged':rows, 'unqueued_control':{'b':.75,'source_q':.75,'pairwise_q':.75,
                 'ratio_mean':mean(unqueued),'ratios':unqueued,
                 'warning':'backlogged capacity law does not apply to unqueued arrivals'}}

if __name__ == '__main__':
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result['all_backlogged_pass'], 'FROZEN LAW FALSIFIED; retain results'
