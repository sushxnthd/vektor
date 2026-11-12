#!/usr/bin/env python3
"""Prospective periodic-bank conflict transfer; synthetic queue service, NOT GPU IPC.

The periodic positive example was discovered by exploratory search. Holdout seeds,
noise and negative regimes were frozen before this evaluator was committed.
"""
import json
import random
from collections import Counter, deque
from functools import lru_cache

SEEDS = (4919, 7351, 10657)
WARMUP = 1000
MEASURE = 5000
CAPACITY = 8
WINDOW = 4
PORTS = 2
PATTERN = (((3, 4), (1, 4), (2, 4), (0, 0)),
           ((3, 1), (1, 1), (3, 3), (4, 0)))
POLICIES = ("greedy", "reverse", "least_overlap", "bestfit", "exact_head")
REGIMES = ("periodic_clean", "periodic_noise1", "periodic_noise5",
           "periodic_cap2", "uniform16")


def fits(reqs, mask):
    used = Counter()
    for i, (a, b) in enumerate(reqs):
        if mask & (1 << i):
            used[a] += 1
            used[b] += 1
            if used[a] > PORTS or used[b] > PORTS:
                return False
    return True


@lru_cache(maxsize=250000)
def choose(reqs, cap, policy):
    n = len(reqs)
    if not n:
        return 0
    if policy == "exact_head":
        return max((m for m in range(1, 1 << n, 2)
                    if m.bit_count() <= cap and fits(reqs, m)),
                   key=lambda m: (m.bit_count(),
                                  tuple(bool(m & (1 << i)) for i in range(n))))
    if policy == "greedy":
        order = range(n)
        mask = 0
    else:
        order = range(n - 1, 0, -1) if policy == "reverse" else ()
        mask = 1
    for i in order:
        if mask.bit_count() < cap and fits(reqs, mask | (1 << i)):
            mask |= 1 << i
    if policy in ("least_overlap", "bestfit"):
        while mask.bit_count() < cap:
            options = [i for i in range(1, n)
                       if not mask & (1 << i) and fits(reqs, mask | (1 << i))]
            if not options:
                break
            counts = Counter(v for j, pair in enumerate(reqs)
                             if mask & (1 << j) for v in pair)
            if policy == "least_overlap":
                key = lambda i: (len(set(reqs[i]) & set(counts)), i)
            else:
                def key(i):
                    trial = counts.copy()
                    trial.update(reqs[i])
                    return (sum(v * v for v in trial.values()), i)
            mask |= 1 << min(options, key=key)
    assert mask & 1 and mask.bit_count() <= cap and fits(reqs, mask)
    return mask


def make_trace(regime, seed):
    rng = random.Random(seed)
    rows = []
    noise = {"periodic_noise1": .01, "periodic_noise5": .05}.get(regime, 0)
    for t in range(WARMUP + MEASURE):
        if regime == "uniform16":
            row = tuple((rng.randrange(16), rng.randrange(16)) for _ in range(4))
        else:
            row = PATTERN[(t + seed % 2) % 2]
            if noise:
                row = tuple(tuple(rng.randrange(5) if rng.random() < noise else x
                                  for x in pair) for pair in row)
        rows.append(row)
    return rows


def replay(trace, policy, cap):
    fifo, source = deque(), deque()
    offered = admitted = finished = pre = 0
    measured = 0
    post_occ = 0
    waits = []
    stalled = 0
    for t, row in enumerate(trace):
        for pair in row:
            source.append((pair, t))
            offered += 1
        while source and len(fifo) < CAPACITY:
            pair, born = source.popleft()
            fifo.append((pair, born, t))
            admitted += 1
        if t >= WARMUP and source:
            stalled += 1
        reqs = tuple(e[0] for e in list(fifo)[:WINDOW])
        mask = choose(reqs, cap, policy)
        assert not fifo or mask & 1
        kept = deque()
        for i, entry in enumerate(fifo):
            if i < WINDOW and mask & (1 << i):
                finished += 1
                if t >= WARMUP:
                    measured += 1
                    waits.append(t - entry[2])
            else:
                kept.append(entry)
        fifo = kept
        assert len(fifo) <= CAPACITY
        assert offered == finished + len(fifo) + len(source)
        if t >= WARMUP:
            post_occ += len(fifo)
        else:
            pre = finished
    assert admitted == finished + len(fifo)
    assert finished - pre == measured
    assert max(waits, default=0) <= CAPACITY - 1
    return dict(completed=measured, throughput=measured / MEASURE,
                post_queue=post_occ / MEASURE, max_onchip_wait=max(waits, default=0),
                backpressure_cycles=stalled, upstream_pending=len(source),
                fifo_residual=len(fifo), admitted=admitted,
                conserved=offered == finished + len(fifo) + len(source))


def run():
    regimes = {}
    for regime in REGIMES:
        cap = 2 if regime == "periodic_cap2" else 4
        rows = []
        for seed in SEEDS:
            trace = make_trace(regime, seed)
            rows.append(dict(seed=seed, policies={
                policy: replay(trace, policy, cap) for policy in POLICIES}))
        sums = {p: sum(row["policies"][p]["completed"] for row in rows)
                for p in POLICIES}
        strongest = max(POLICIES[:-1], key=lambda p: (sums[p], -POLICIES.index(p)))
        ratio = sums["exact_head"] / sums[strongest]
        regimes[regime] = dict(cap=cap, rows=rows, totals=sums,
                               strongest_control=strongest, ratio=ratio)
    return dict(protocol="FROZEN_PERIODIC_BANK_PHASE_TRANSFER_20261102.md",
                evidence_tier="synthetic selected periodic trace; independent holdouts, not RTL or GPU IPC",
                seeds=SEEDS, warmup=WARMUP, measured_cycles=MEASURE,
                regimes=regimes)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
