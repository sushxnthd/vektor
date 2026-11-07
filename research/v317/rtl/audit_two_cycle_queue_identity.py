#!/usr/bin/env python3
"""Independent V317 two-cycle queue-identity audit; does not import evaluator."""
import json
import random
import sys
from itertools import product

SEEDS = (503, 907, 1201)
N = 40000

def feasible(batch, indices, B):
    demands = [0] * B
    for index in indices:
        for bank in batch[index]:
            demands[bank] += 1
    return max(demands, default=0) <= 2

def policy(batch, B, name):
    if not batch:
        return ()
    if name == 'compact':
        priorities = list(range(len(batch)))
    else:
        adj = []
        for i, pair in enumerate(batch):
            score = 0
            for j, other in enumerate(batch):
                if i != j and (pair[0] in other or pair[1] in other):
                    score += 1
            adj.append(score)
        priorities = [0] + sorted(range(1, len(batch)), key=lambda i: (adj[i], i))
    selected = []
    for index in priorities:
        if len(selected) != 2 and feasible(batch, selected + [index], B):
            selected.append(index)
    return tuple(selected)

def two_round(batch, B, name):
    first = policy(batch, B, name)
    remainder = tuple(x for i, x in enumerate(batch) if i not in first)
    second = policy(remainder, B, name)
    return len(first), len(first) + len(second), remainder

def check(batch, B, out):
    a1, a2, ar = two_round(batch, B, 'compact')
    b1, b2, br = two_round(batch, B, 'degree')
    assert a1 == b1
    ia = int(len(ar) == 2 and not feasible(ar, range(2), B))
    ib = int(len(br) == 2 and not feasible(br, range(2), B))
    assert b2 - a2 == ia - ib
    out['cases'] += 1
    out['first_equal'] += 1
    out['greedy'] += a2
    out['degree'] += b2
    out['degree_wins'] += b2 > a2
    out['degree_losses'] += b2 < a2
    out['residual_conflicts_greedy'] += ia
    out['residual_conflicts_degree'] += ib
    out['identity_pass'] += 1

def blank():
    return dict.fromkeys(('cases','first_equal','greedy','degree','degree_wins','degree_losses',
                          'residual_conflicts_greedy','residual_conflicts_degree','identity_pass'), 0)

def audit(report):
    retrospective = blank()
    for raw in product(range(3), repeat=8):
        check(tuple((raw[i], raw[i+1]) for i in range(0,8,2)), 3, retrospective)
    assert retrospective == report['retrospective_b3']
    total = blank()
    for seed in SEEDS:
        rng = random.Random(seed)
        row = blank()
        for _ in range(N):
            batch = tuple((rng.randrange(4), rng.randrange(4)) for _ in range(4))
            check(batch, 4, row)
        assert row == report['prospective_b4_by_seed'][str(seed)]
        for k in total:
            total[k] += row[k]
    assert total == report['prospective_b4_total']
    assert abs(total['degree']/total['greedy']-report['prospective_ratio']) < 1e-15
    assert report['frozen_predictions'] == dict(
        first_cycle_equal=True, degree_ratio_at_most_0p995=total['degree']/total['greedy']<=.995,
        residual_identity_exact=True)
    return dict(status='PASS', independent_replays=retrospective['cases']+total['cases'],
                b3=retrospective, b4=total, ratio=total['degree']/total['greedy'])

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        report=json.load(f)
    print(json.dumps(audit(report), sort_keys=True, indent=2))
