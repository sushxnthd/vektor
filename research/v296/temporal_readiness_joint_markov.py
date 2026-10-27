#!/usr/bin/env python3
"""V296 finite-token temporal readiness falsification; synthetic, not GPU data.

Exact joint token/readiness Markov chain versus independent bank-index Monte Carlo.
Both architectures use identical admission rules, so this is a workload law,
not a V296 speedup claim.
"""
import argparse
import json
import random
from collections import defaultdict

B, S, P, RHO, REFILL, CAPACITY = 4, 3, 2, 0.2, 1, 2
P_LOW, P_HIGH = 0.05, 0.95
SEEDS = (90211, 90217)
TOL = 0.025
CYCLES, BURN = 150000, 10000


def kernel(p, available):
    """Independent bank-index DP, exactly enumerates each read-pair outcome."""
    states = {((0,) * B, 0): 1.0}
    for _ in range(S):
        nxt = defaultdict(float)
        for (loads, accepted), mass in states.items():
            nxt[(loads, accepted)] += mass * (1 - p)
            for a in range(B):
                for b in range(B):
                    weight = mass * p * ((RHO / B if a == b else 0) + (1 - RHO) / (B * B))
                    new = list(loads)
                    new[a] += 1
                    new[b] += 1
                    if accepted < available and max(new) <= P:
                        nxt[(tuple(new), accepted + 1)] += weight
                    else:
                        nxt[(loads, accepted)] += weight
        states = nxt
    q = [0.0] * (min(S, available) + 1)
    for (_, k), weight in states.items():
        q[k] += weight
    assert abs(sum(q) - 1) < 1e-10
    return q


def exact(stay):
    """State (post-cycle tokens, mode); next mode is chosen after the cycle."""
    assert 0 < stay < 1
    states = [(x, m) for x in range(CAPACITY + 1) for m in range(2)]
    kernels = {(m, t): kernel((P_LOW, P_HIGH)[m], t)
               for m in range(2) for t in range(1, CAPACITY + 1)}
    M = [[0.0] * len(states) for _ in states]
    rewards = [0.0] * len(states)
    for i, (x, m) in enumerate(states):
        t = min(CAPACITY, x + REFILL)
        for k, prob in enumerate(kernels[(m, t)]):
            rewards[i] += k * prob
            for next_m in range(2):
                j = states.index((t - k, next_m))
                M[i][j] += prob * (stay if next_m == m else 1 - stay)
        assert abs(sum(M[i]) - 1) < 1e-10
    pi = [1 / len(states)] * len(states)
    for it in range(20000):
        nxt = [sum(pi[i] * M[i][j] for i in range(len(states))) for j in range(len(states))]
        if max(abs(a - b) for a, b in zip(nxt, pi)) < 1e-14:
            pi = nxt
            break
        pi = nxt
    else:
        raise AssertionError('stationary chain did not converge')
    residual = max(abs(sum(pi[i] * M[i][j] for i in range(len(states))) - pi[j])
                   for j in range(len(states)))
    assert residual < 1e-11
    return sum(a * b for a, b in zip(pi, rewards)), residual


def iid():
    """Stationary token chain with independent per-cycle ready p = 0.5."""
    k = {t: kernel((P_LOW + P_HIGH) / 2, t) for t in range(1, CAPACITY + 1)}
    states = list(range(CAPACITY + 1))
    M = [[0.0] * len(states) for _ in states]
    rewards = [0.0] * len(states)
    for x in states:
        t = min(CAPACITY, x + REFILL)
        for admitted, prob in enumerate(k[t]):
            M[x][t - admitted] += prob
            rewards[x] += admitted * prob
    pi = [1 / len(states)] * len(states)
    for _ in range(10000):
        nxt = [sum(pi[i] * M[i][j] for i in states) for j in states]
        if max(abs(a - b) for a, b in zip(nxt, pi)) < 1e-14:
            pi = nxt
            break
        pi = nxt
    return sum(a * b for a, b in zip(pi, rewards))


def simulate(stay, seed):
    rng = random.Random(seed)
    tokens, mode, total = 0, rng.randrange(2), 0
    for cycle in range(CYCLES):
        tokens = min(CAPACITY, tokens + REFILL)
        used = [0] * B
        for _ in range(S):
            if rng.random() >= (P_LOW, P_HIGH)[mode]:
                continue
            a = rng.randrange(B)
            b = a if rng.random() < RHO else rng.randrange(B)
            if tokens and used[a] + 1 + (a == b) <= P and (a == b or used[b] + 1 <= P):
                used[a] += 1
                used[b] += 1
                tokens -= 1
                if cycle >= BURN:
                    total += 1
        if rng.random() > stay:
            mode = 1 - mode
    return total / (CYCLES - BURN)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output')
    args = ap.parse_args()
    iid_q = iid()
    rows = []
    for stay in (0.5, 0.9, 0.98):
        prediction, residual = exact(stay)
        observed = [simulate(stay, seed) for seed in SEEDS]
        rows.append({'stay': stay, 'exact_q': prediction,
                     'independent_iid_mean_p_prediction': iid_q,
                     'observed': observed,
                     'max_abs_error': max(abs(x - prediction) for x in observed),
                     'stationary_residual': residual})
    assert all(row['max_abs_error'] < TOL for row in rows)
    # stay=.5 is independent MODE each cycle, but shared-mode slot
    # readiness remains correlated within a cycle. Not iid-equivalent.
    assert rows[-1]['exact_q'] < iid_q
    result = {'tier': 'synthetic exact joint Markov + independent Monte Carlo',
              'configuration': {'banks': B, 'slots': S, 'ports_per_bank': P,
                                'rho': RHO, 'refill': REFILL, 'capacity': CAPACITY,
                                'p_low': P_LOW, 'p_high': P_HIGH,
                                'cycles': CYCLES, 'burn': BURN,
                                'seeds': SEEDS, 'tolerance': TOL},
              'rows': rows, 'all_pass': True,
              'architectural_speedup_claim': False}
    print(json.dumps(result, indent=2))
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
            f.write('\n')


if __name__ == '__main__':
    main()
