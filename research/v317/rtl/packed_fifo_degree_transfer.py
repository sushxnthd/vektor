#!/usr/bin/env python3
"""V317 preregistered packed-FIFO cardinality and four-bank transfer.
Combinational grant counts only: NOT GPU IPC, timing, or power.
"""
import json
import random
from collections import defaultdict
from itertools import product

SEEDS = (191, 409, 733)
SAMPLES = 40000
CAPS = (2, 3, 4)
PREFIX = {1, 3, 7, 15}

def count_bits(mask):
    return mask.bit_count()

def legal(req, mask, banks):
    uses = [0] * banks
    for i, (a, b) in enumerate(req):
        if mask & (1 << i):
            uses[a] += 1
            uses[b] += 1
            if uses[a] > 2 or uses[b] > 2:
                return False
    return True

def choose(req, valid, cap, banks, policy):
    order = list(range(4))
    if policy == 'degree':
        def overlap(i, j):
            return bool(set(req[i]) & set(req[j]))
        order[1:] = sorted(order[1:], key=lambda i: (
            sum(bool(valid & (1 << j)) and overlap(i, j)
                for j in range(4) if j != i), i))
    mask = 0
    for i in order:
        candidate = mask | (1 << i)
        if valid & (1 << i) and count_bits(mask) < cap and legal(req, candidate, banks):
            mask = candidate
    return mask

def exact(req, valid, cap, banks):
    feasible = [m for m in range(16)
                if not m & ~valid and (not valid & 1 or m & 1)
                and count_bits(m) <= cap and legal(req, m, banks)]
    return max(feasible, key=count_bits)

def row():
    return dict(cases=0, greedy=0, degree=0, degree_wins=0,
                degree_losses=0, exact=0, exact_above_degree=0)

def add(dst, req, valid, cap, banks, with_exact=False):
    g = choose(req, valid, cap, banks, 'greedy')
    d = choose(req, valid, cap, banks, 'degree')
    assert legal(req, g, banks) and legal(req, d, banks)
    if valid & 1:
        assert g & 1 and d & 1
    gc, dc = count_bits(g), count_bits(d)
    dst['cases'] += 1
    dst['greedy'] += gc
    dst['degree'] += dc
    dst['degree_wins'] += dc > gc
    dst['degree_losses'] += dc < gc
    if with_exact:
        ec = count_bits(exact(req, valid, cap, banks))
        assert ec >= gc and ec >= dc
        dst['exact'] += ec
        dst['exact_above_degree'] += ec > dc

def run():
    b3 = defaultdict(row)
    for raw in product(range(3), repeat=8):
        req = tuple(zip(raw[::2], raw[1::2]))
        for valid in range(16):
            for cap in CAPS:
                add(b3[f'all_cap{cap}'], req, valid, cap, 3)
                add(b3[f'head_{bool(valid & 1)}_cap{cap}'], req, valid, cap, 3)
                if valid in PREFIX:
                    add(b3[f'packed_cap{cap}'], req, valid, cap, 3)
                    if valid == 15:
                        add(b3[f'full_cap{cap}'], req, valid, cap, 3)
    assert b3['all_cap4']['greedy'] == 158409
    assert b3['all_cap4']['degree'] == 158529
    assert b3['head_True_cap2']['greedy'] == b3['head_True_cap2']['degree']
    assert b3['packed_cap2']['greedy'] == b3['packed_cap2']['degree']
    b4 = {}
    for seed in SEEDS:
        rng = random.Random(seed)
        per_cap = {cap: row() for cap in CAPS}
        for _ in range(SAMPLES):
            raw = [rng.randrange(4) for _ in range(8)]
            req = tuple(zip(raw[::2], raw[1::2]))
            for cap in CAPS:
                add(per_cap[cap], req, 15, cap, 4, with_exact=True)
        b4[str(seed)] = {str(cap): per_cap[cap] for cap in CAPS}
    total = {str(cap): row() for cap in CAPS}
    for seed in b4.values():
        for cap in CAPS:
            for key, value in seed[str(cap)].items():
                total[str(cap)][key] += value
    assert total['2']['greedy'] == total['2']['degree'] == total['2']['exact']
    return dict(evidence_tier='combinational synthetic bank-port model only; no finite FIFO, RTL PPA or GPU IPC',
                frozen_protocol='FROZEN_PACKED_FIFO_DEGREE_TRANSFER_20261103.md',
                bank_ports=2, reads_per_request=2, slots=4,
                seeds=SEEDS, samples_per_seed=SAMPLES,
                b3_exhaustive=dict(b3), b4_holdout_by_seed=b4, b4_holdout_total=total,
                prospective_prediction=dict(cap2_no_win=total['2']['degree'] == total['2']['greedy'],
                  cap3_small_gain=total['3']['degree'] < 1.005 * total['3']['greedy'],
                  cap4_small_gain=total['4']['degree'] < 1.005 * total['4']['greedy']))

if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
