#!/usr/bin/env python3
"""Independent periodic bank queue audit: no imports from the evaluator."""
import json
import random
import sys
from collections import deque
from itertools import product

SEEDS = (4919, 7351, 10657)
N = 6000
PHASES = (((3, 4), (1, 4), (2, 4), (0, 0)),
          ((3, 1), (1, 1), (3, 3), (4, 0)))
POLICIES = ("greedy", "reverse", "least_overlap", "bestfit", "exact_head")
REGIMES = ("periodic_clean", "periodic_noise1", "periodic_noise5",
           "periodic_cap2", "uniform16")


def legal(reqs, selected):
    usage = {}
    for i in range(len(reqs)):
        if selected >> i & 1:
            for b in reqs[i]:
                usage[b] = usage.get(b, 0) + 1
                if usage[b] > 2:
                    return False
    return True


def select(reqs, cap, policy):
    n = len(reqs)
    if not n:
        return 0
    if policy == "exact_head":
        valid = []
        # Independent recursion, not the evaluator's bitmask enumeration.
        def visit(i, mask):
            if i == n:
                if mask & 1:
                    valid.append(mask)
                return
            visit(i + 1, mask)
            m = mask | (1 << i)
            if m.bit_count() <= cap and legal(reqs, m):
                visit(i + 1, m)
        visit(0, 0)
        assert valid
        return max(valid, key=lambda m: (m.bit_count(),
                   tuple(int(bool(m >> j & 1)) for j in range(n))))
    mask = 0 if policy == "greedy" else 1
    if policy == "greedy":
        order = list(range(n))
    elif policy == "reverse":
        order = list(range(n - 1, 0, -1))
    else:
        order = []
    for i in order:
        m = mask | (1 << i)
        if m.bit_count() <= cap and legal(reqs, m):
            mask = m
    if policy in ("least_overlap", "bestfit"):
        while mask.bit_count() < cap:
            opts = [i for i in range(1, n) if not mask >> i & 1
                    and legal(reqs, mask | (1 << i))]
            if not opts:
                break
            occupancy = {}
            for i in range(n):
                if mask >> i & 1:
                    for b in reqs[i]:
                        occupancy[b] = occupancy.get(b, 0) + 1
            if policy == "least_overlap":
                pick = min(opts, key=lambda i: (
                    sum(int(b in occupancy) for b in set(reqs[i])), i))
            else:
                def imbalance(i):
                    loads = dict(occupancy)
                    for b in reqs[i]:
                        loads[b] = loads.get(b, 0) + 1
                    return sum(v ** 2 for v in loads.values()), i
                pick = min(opts, key=imbalance)
            mask |= 1 << pick
    assert mask & 1 and legal(reqs, mask) and mask.bit_count() <= cap
    return mask


def offers(regime, seed):
    rng = random.Random(seed)
    noise = .01 if regime == "periodic_noise1" else (
            .05 if regime == "periodic_noise5" else 0)
    for t in range(N):
        if regime == "uniform16":
            yield tuple((rng.randrange(16), rng.randrange(16)) for _ in range(4))
        else:
            phase = PHASES[(t + seed % 2) % 2]
            if not noise:
                yield phase
            else:
                yield tuple(tuple(rng.randrange(5) if rng.random() < noise else b
                                  for b in pair) for pair in phase)


def audit_replay(regime, seed, policy, cap):
    fifo = deque()
    upstream = deque()
    offered = admitted = completed = pre = 0
    waits = []
    occupancy = stalled = 0
    for t, batch in enumerate(offers(regime, seed)):
        for req in batch:
            upstream.append((req, t))
            offered += 1
        while upstream and len(fifo) < 8:
            req, born = upstream.popleft()
            fifo.append((req, born, t))
            admitted += 1
        if t >= 1000 and upstream:
            stalled += 1
        front = tuple(item[0] for item in list(fifo)[:4])
        decision = select(front, cap, policy)
        kept = deque()
        for i, item in enumerate(fifo):
            if i < 4 and decision >> i & 1:
                completed += 1
                if t >= 1000:
                    waits.append(t - item[2])
            else:
                kept.append(item)
        fifo = kept
        assert len(fifo) <= 8
        assert offered == completed + len(fifo) + len(upstream)
        if t >= 1000:
            occupancy += len(fifo)
        else:
            pre = completed
    assert admitted == completed + len(fifo)
    assert max(waits, default=0) <= 7
    return dict(completed=completed - pre, throughput=len(waits) / 5000,
                post_queue=occupancy / 5000, max_onchip_wait=max(waits, default=0),
                backpressure_cycles=stalled, upstream_pending=len(upstream),
                fifo_residual=len(fifo), admitted=admitted, conserved=True)


def audit(path):
    with open(path) as f:
        data = json.load(f)
    assert tuple(data["seeds"]) == SEEDS
    assert data["warmup"] == 1000 and data["measured_cycles"] == 5000
    assert set(data["regimes"]) == set(REGIMES)
    checked = 0
    for regime in REGIMES:
        result = data["regimes"][regime]
        cap = 2 if regime == "periodic_cap2" else 4
        assert result["cap"] == cap
        assert len(result["rows"]) == 3
        for row in result["rows"]:
            seed = row["seed"]
            assert seed in SEEDS
            for policy in POLICIES:
                expected = audit_replay(regime, seed, policy, cap)
                recorded = row["policies"][policy]
                for k, v in expected.items():
                    if isinstance(v, float):
                        assert abs(v - recorded[k]) < 1e-10, (regime, seed, policy, k, v, recorded[k])
                    else:
                        assert v == recorded[k], (regime, seed, policy, k, v, recorded[k])
                checked += 1
        totals = {p: sum(r["policies"][p]["completed"] for r in result["rows"])
                  for p in POLICIES}
        assert result["totals"] == totals
        best = max(POLICIES[:-1], key=lambda p: (totals[p], -POLICIES.index(p)))
        assert result["strongest_control"] == best
        assert abs(result["ratio"] - totals["exact_head"] / totals[best]) < 1e-12
    # Exhaustive small-domain feasibility check and dominance of exact head.
    cases = 0
    for x in product(range(3), repeat=8):
        q = tuple(zip(x[::2], x[1::2]))
        optimum = select(q, 4, "exact_head").bit_count()
        for p in POLICIES[:-1]:
            assert select(q, 4, p).bit_count() <= optimum
        cases += 1
    return dict(status="PASS", full_trace_policy_replays=checked,
                exhaustive_three_bank_cases=cases, conservation=True,
                oldest_request_preserved=True)


if __name__ == "__main__":
    print(json.dumps(audit(sys.argv[1]), sort_keys=True, indent=2))
