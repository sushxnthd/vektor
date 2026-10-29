"""V305 finite-MSHR admission experiment. Synthetic timing, not GPU IPC.

No future arrival information is available to any policy. All requests are conserved.
Run: python3 research/v305/simulator.py --pilot
"""
from __future__ import annotations
import argparse
from collections import deque
from dataclasses import dataclass
import json
import random
from statistics import mean

@dataclass(frozen=True)
class Request:
    ident: int
    release: int
    partition: int


def make_trace(seed: int, regime: str, duration: int = 1200):
    rng = random.Random(seed)
    if regime == 'W1':
        weights, latency, offer = (.70, .10, .10, .10), (48, 12, 12, 12), .87
    elif regime == 'N1':
        weights, latency, offer = (.25,) * 4, (24,) * 4, .87
    else:
        raise ValueError(regime)
    trace = []
    for t in range(duration):
        burst = (t % 83) < 20
        for _ in range(2):
            if rng.random() < min(.99, offer * (1.13 if burst else .93)):
                p = rng.choices(range(4), weights=weights)[0]
                trace.append(Request(len(trace), t, p))
    return trace, latency


def simulate(trace, latency, policy: str, mshr: int = 12, ingress: int = 32,
             response_bw: int = 1, admission_bw: int = 2):
    if policy not in ('fifo', 'rr', 'fixed', 'shortest', 'guard'):
        raise ValueError(policy)
    waiting = [deque() for _ in range(4)]
    source = [deque(r for r in trace if r.partition == p) for p in range(4)]
    inflight = [[] for _ in range(4)]
    occupancy = [0] * 4
    admitted = set()
    completed = set()
    blocked = [0] * 4
    end_to_end = [[] for _ in range(4)]
    peak_pending = 0
    rr_ptr = 0
    t = 0
    last_release = max((r.release for r in trace), default=0)
    while len(completed) < len(trace):
        if t > last_release + len(trace) * max(latency) + 100:
            raise RuntimeError('No forward progress')
        for p in range(4):
            ready = [x for x in inflight[p] if x[0] <= t]
            ready.sort(key=lambda x: (x[0], x[1].ident))
            for _, req in ready[:response_bw]:
                inflight[p].remove((_, req))
                assert req.ident not in completed
                completed.add(req.ident)
                occupancy[p] -= 1
                end_to_end[p].append(t - req.release + 1)
        for p in range(4):
            while source[p] and source[p][0].release <= t and len(waiting[p]) < ingress:
                waiting[p].append(source[p].popleft())
            if source[p] and source[p][0].release <= t and len(waiting[p]) == ingress:
                blocked[p] += 1
        for _ in range(admission_bw):
            if sum(occupancy) >= mshr:
                break
            candidates = [p for p in range(4) if waiting[p]]
            if policy == 'fixed':
                candidates = [p for p in candidates if occupancy[p] < mshr // 4]
            if policy == 'guard':
                candidates = [p for p in candidates if
                              (mshr - sum(occupancy) >
                               sum(1 for q in range(4) if q != p and waiting[q] and occupancy[q] == 0))]
            if not candidates:
                break
            if policy == 'rr' or policy == 'guard':
                p = min(candidates, key=lambda q: ((q - rr_ptr) % 4))
            elif policy == 'shortest':
                p = min(candidates, key=lambda q: (latency[q], waiting[q][0].release, q))
            else:
                p = min(candidates, key=lambda q: (waiting[q][0].release, waiting[q][0].ident))
            req = waiting[p].popleft()
            assert req.ident not in admitted
            admitted.add(req.ident)
            occupancy[p] += 1
            inflight[p].append((t + latency[p], req))
            rr_ptr = (p + 1) % 4
        peak_pending = max(peak_pending, sum(len(q) for q in waiting))
        assert sum(occupancy) == sum(len(q) for q in inflight)
        assert sum(occupancy) <= mshr
        t += 1
    assert len(admitted) == len(trace) == len(completed)
    assert not any(source) and not any(waiting) and not any(inflight)
    lat = sorted(x for part in end_to_end for x in part)
    percentile = lambda values, q: sorted(values)[min(len(values)-1, int(q*(len(values)-1)))] if values else 0
    return {'cycles': t, 'completed': len(completed), 'rate': len(completed)/t if t else 0.0,
            'p95': percentile(lat, .95), 'p99': percentile(lat, .99),
            'partition_p99': [percentile(x, .99) for x in end_to_end],
            'partition_completed': [len(x) for x in end_to_end],
            'blocked_source_cycles': blocked, 'peak_ingress_pending': peak_pending}


def evaluate(seeds, regimes=('W1','N1')):
    out = {}
    for regime in regimes:
        rows = []
        for seed in seeds:
            trace, latency = make_trace(seed, regime)
            results = {policy: simulate(trace, latency, policy) for policy in
                       ('fifo','rr','fixed','shortest','guard')}
            assert len({r['completed'] for r in results.values()}) == 1
            rows.append(results)
        means = {policy: {key: mean(row[policy][key] for row in rows)
                          for key in ('cycles','rate','p95','p99','peak_ingress_pending')}
                 for policy in rows[0]}
        best = max((p for p in means if p != 'guard'), key=lambda p: means[p]['rate'])
        gain = means['guard']['rate'] / means[best]['rate'] - 1
        out[regime] = {'seeds': list(seeds), 'means': means, 'best_control': best,
                       'guard_vs_best_percent': 100*gain,
                       'per_seed': rows}
    return out


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--pilot', action='store_true')
    group.add_argument('--holdout', action='store_true')
    args = parser.parse_args()
    seeds = range(1,5) if args.pilot else range(101,121)
    print(json.dumps(evaluate(seeds), sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
