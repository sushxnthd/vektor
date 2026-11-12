#!/usr/bin/env python3
"""Independent audit: no imports from the V317 evaluator or RTL.
Checks oldest-valid K=2 theorem and B<=3 port ceiling exhaustively,
then replays the prospectively frozen four-bank holdout with a separate selector.
"""
import json
import random
import sys
from itertools import product

SEEDS = (191, 409, 733)
SAMPLES = 40000

def legal(mask, raw, banks):
    ports = [0] * banks
    for slot in range(4):
        if mask & (1 << slot):
            ports[raw[2 * slot]] += 1
            ports[raw[2 * slot + 1]] += 1
    return max(ports) <= 2

def scan(raw, valid, cap, banks, degree):
    slots = [0, 1, 2, 3]
    if degree:
        def n_overlap(i):
            a, b = raw[2 * i], raw[2 * i + 1]
            total = 0
            for j in range(4):
                if i == j or not valid & (1 << j):
                    continue
                c, d = raw[2 * j], raw[2 * j + 1]
                total += a == c or a == d or b == c or b == d
            return total
        slots[1:] = sorted(slots[1:], key=lambda i: (n_overlap(i), i))
    selected = 0
    for i in slots:
        trial = selected | (1 << i)
        if valid & (1 << i) and selected.bit_count() < cap and legal(trial, raw, banks):
            selected = trial
    return selected.bit_count()

def oracle(raw, valid, cap, banks):
    return max(mask.bit_count() for mask in range(16)
               if mask & ~valid == 0 and (not valid & 1 or mask & 1)
               and mask.bit_count() <= cap and legal(mask, raw, banks))

def audit(result):
    for banks in (2, 3):
        cases = 0
        for raw in product(range(banks), repeat=8):
            for valid in range(1, 16, 2):
                g = scan(raw, valid, 2, banks, False)
                d = scan(raw, valid, 2, banks, True)
                e = oracle(raw, valid, 2, banks)
                assert g == d == e, (banks, raw, valid, g, d, e)
                cases += 1
            if banks == 3:
                for valid in range(16):
                    assert oracle(raw, valid, 3, banks) == oracle(raw, valid, 4, banks)
        assert cases == (banks ** 8) * 8
    for seed in SEEDS:
        rng = random.Random(seed)
        sums = {str(cap): {'greedy': 0, 'degree': 0, 'exact': 0,
                            'degree_wins': 0, 'degree_losses': 0,
                            'exact_above_degree': 0} for cap in (2, 3, 4)}
        for _ in range(SAMPLES):
            raw = tuple(rng.randrange(4) for _ in range(8))
            for cap in (2, 3, 4):
                g = scan(raw, 15, cap, 4, False)
                d = scan(raw, 15, cap, 4, True)
                e = oracle(raw, 15, cap, 4)
                s = sums[str(cap)]
                s['greedy'] += g
                s['degree'] += d
                s['exact'] += e
                s['degree_wins'] += d > g
                s['degree_losses'] += d < g
                s['exact_above_degree'] += e > d
        for cap in ('2', '3', '4'):
            observed = result['b4_holdout_by_seed'][str(seed)][cap]
            for key, value in sums[cap].items():
                assert observed[key] == value, (seed, cap, key, observed[key], value)
    return {'independent_audit': 'PASS', 'exhaustive_b2_b3_head_valid_k2': True,
            'exhaustive_b3_cap3_equals_cap4': True,
            'b4_seeded_full_holdout_reproduced': True,
            'b4_samples': len(SEEDS) * SAMPLES,
            'scope': 'synthetic instantaneous grant counts, not RTL PPA or GPU throughput'}

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        result = json.load(f)
    print(json.dumps(audit(result), indent=2, sort_keys=True))
