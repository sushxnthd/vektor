"""V306 deterministic bank-aware warp-issue falsification model.

Synthetic throughput only: no measured GPU IPC or physical timing.
Run: python3 research/v306/simulator.py --pilot
"""
from __future__ import annotations
import argparse
import json
import random
from dataclasses import dataclass
from statistics import mean

WARPS = 5
PROGRAM_LEN = 48
BANKS = 8
ISSUE = 3


def program(seed: int, regime: str, warps: int = WARPS, length: int = PROGRAM_LEN):
    if regime not in ('W1', 'N1'):
        raise ValueError(regime)
    rng = random.Random(seed)
    pairs = ((0, 1), (2, 3), (4, 5), (6, 7))
    result = []
    for w in range(warps):
        warp = []
        for j in range(length):
            if regime == 'N1' and rng.random() < .95:
                pair = pairs[(j % 4 + w) % 4]
            else:
                pair = tuple(rng.sample(range(BANKS), 2))
            assert pair[0] != pair[1]
            warp.append((1 << pair[0]) | (1 << pair[1]))
        result.append(tuple(warp))
    return tuple(result)


def legal_subsets(head, queues, issue=ISSUE):
    """Return feasible subsets encoded as warp bitsets, including zero."""
    n = len(queues)
    out = []
    for s in range(1 << n):
        if s.bit_count() > issue:
            continue
        used = 0
        for w in range(n):
            if not (s >> w) & 1:
                continue
            if head[w] >= len(queues[w]):
                break
            banks = queues[w][head[w]]
            if used & banks:
                break
            used |= banks
        else:
            out.append(s)
    return out


def next_head(head, s):
    return tuple(v + ((s >> w) & 1) for w, v in enumerate(head))


def priority_key(s, n):
    return tuple((s >> w) & 1 for w in range(n))


def select(head, queues, policy):
    opts = legal_subsets(head, queues)
    n = len(queues)
    if policy == 'priority':
        used = 0
        out = 0
        for w in range(n):
            if head[w] >= len(queues[w]) or out.bit_count() >= ISSUE:
                continue
            m = queues[w][head[w]]
            if not used & m:
                out |= 1 << w
                used |= m
        return out
    if policy == 'max_now':
        return max(opts, key=lambda s: (s.bit_count(), priority_key(s, n)))
    if policy not in ('future_tie', 'lookahead'):
        raise ValueError(policy)
    def key(s):
        second = max(t.bit_count() for t in legal_subsets(next_head(head, s), queues))
        if policy == 'future_tie':
            return (s.bit_count(), second, priority_key(s, n))
        return (s.bit_count() + second, s.bit_count(), priority_key(s, n))
    return max(opts, key=key)


@dataclass(frozen=True)
class Result:
    cycles: int
    issued: int
    utilization: float
    idle_slots: int
    max_now_capacity: int
    lookahead_downgrades: int


def simulate(queues, policy):
    n = len(queues)
    h = tuple(0 for _ in queues)
    total = sum(map(len, queues))
    cycles = 0
    issued = 0
    max_now_capacity = 0
    downgrades = 0
    while issued < total:
        best_now = max(s.bit_count() for s in legal_subsets(h, queues))
        s = select(h, queues, policy)
        assert s in legal_subsets(h, queues)
        assert s.bit_count() > 0, 'deadlock'
        assert s.bit_count() <= ISSUE
        if s.bit_count() < best_now:
            downgrades += 1
        max_now_capacity += best_now
        issued += s.bit_count()
        h = next_head(h, s)
        cycles += 1
        assert cycles <= total, 'no forward progress'
    assert all(h[w] == len(queues[w]) for w in range(n))
    return Result(cycles, issued, issued / (cycles * ISSUE),
                  cycles * ISSUE - issued, max_now_capacity, downgrades)


def pilot(seeds=(21, 22, 23, 24)):
    policies = ('priority', 'max_now', 'future_tie', 'lookahead')
    data = {}
    for regime in ('W1', 'N1'):
        rows = []
        for seed in seeds:
            q = program(seed, regime)
            result = {p: vars(simulate(q, p)) for p in policies}
            baseline = result['future_tie']['cycles']
            candidate = result['lookahead']['cycles']
            result['relative_throughput_gain_pct'] = 100 * (baseline / candidate - 1)
            result['seed'] = seed
            rows.append(result)
        data[regime] = {
            'rows': rows,
            'mean_gain_pct': mean(x['relative_throughput_gain_pct'] for x in rows),
            'mean_cycles': {p: mean(x[p]['cycles'] for x in rows) for p in policies},
            'max_seed_regression_pct': min(x['relative_throughput_gain_pct'] for x in rows),
        }
    w = data['W1']
    n = data['N1']
    data['survival'] = (w['mean_gain_pct'] >= 5 and w['max_seed_regression_pct'] >= -2
                        and abs(n['mean_gain_pct']) <= 2)
    return data


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true')
    ap.add_argument('--seeds', nargs='*', type=int, default=[21,22,23,24])
    args = ap.parse_args()
    if not args.pilot:
        ap.error('Specify --pilot; holdouts must not be opened automatically')
    print(json.dumps(pilot(tuple(args.seeds)), sort_keys=True, indent=2))
