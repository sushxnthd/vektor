#!/usr/bin/env python3
"""V317 frozen K=2 finite-batch queue identity challenge. Synthetic only."""
import json
import random
from collections import Counter
from itertools import product

SEEDS = (503, 907, 1201)
N = 40000

def legal(reqs, selected, banks):
    uses = [0] * banks
    for i in selected:
        a, b = reqs[i]
        uses[a] += 1
        uses[b] += 1
        if uses[a] > 2 or uses[b] > 2:
            return False
    return True

def select(reqs, banks, mode):
    if not reqs:
        return ()
    order = list(range(len(reqs)))
    if mode == 'degree':
        order[1:] = sorted(order[1:], key=lambda i: (
            sum(bool(set(reqs[i]) & set(reqs[j])) for j in range(len(reqs)) if j != i), i))
    chosen = []
    for i in order:
        if len(chosen) < 2 and legal(reqs, chosen + [i], banks):
            chosen.append(i)
    assert 0 in chosen
    return tuple(sorted(chosen))

def outcome(reqs, banks, mode):
    first = select(reqs, banks, mode)
    rest = tuple(req for i, req in enumerate(reqs) if i not in first)
    second = select(rest, banks, mode)
    return len(first), len(first) + len(second), rest

def stats():
    return dict(cases=0, first_equal=0, greedy=0, degree=0,
                degree_wins=0, degree_losses=0, residual_conflicts_greedy=0,
                residual_conflicts_degree=0, identity_pass=0)

def update(row, reqs, banks):
    gf, g, gr = outcome(reqs, banks, 'greedy')
    df, d, dr = outcome(reqs, banks, 'degree')
    assert gf == df
    assert len(gr) == len(dr)
    ig = int(len(gr) == 2 and not legal(gr, (0, 1), banks))
    id_ = int(len(dr) == 2 and not legal(dr, (0, 1), banks))
    assert d - g == ig - id_
    row['cases'] += 1
    row['first_equal'] += gf == df
    row['greedy'] += g
    row['degree'] += d
    row['degree_wins'] += d > g
    row['degree_losses'] += d < g
    row['residual_conflicts_greedy'] += ig
    row['residual_conflicts_degree'] += id_
    row['identity_pass'] += 1

def run():
    exhaustive = stats()
    for raw in product(range(3), repeat=8):
        update(exhaustive, tuple(zip(raw[::2], raw[1::2])), 3)
    by_seed = {}
    total = stats()
    for seed in SEEDS:
        rng = random.Random(seed)
        row = stats()
        for _ in range(N):
            raw = [rng.randrange(4) for _ in range(8)]
            update(row, tuple(zip(raw[::2], raw[1::2])), 4)
        by_seed[str(seed)] = row
        for key in total:
            total[key] += row[key]
    ratio = total['degree'] / total['greedy']
    return dict(schema='vektor.v317.two_cycle_queue_identity.v1',
                evidence_tier='synthetic all-valid 4-request two-cycle batch; no dynamic GPU trace or RTL PPA',
                protocol='FROZEN_TWO_CYCLE_QUEUE_IDENTITY_20261103.md',
                banks=4, ports_per_bank=2, reads_per_request=2, issue_cap=2,
                seeds=SEEDS, samples_per_seed=N,
                retrospective_b3=exhaustive, prospective_b4_by_seed=by_seed,
                prospective_b4_total=total, prospective_ratio=ratio,
                frozen_predictions=dict(first_cycle_equal=total['first_equal']==total['cases'],
                    degree_ratio_at_most_0p995=ratio <= .995,
                    residual_identity_exact=total['identity_pass']==total['cases']))

if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
