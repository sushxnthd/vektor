#!/usr/bin/env python3
"""Vektor-065: deterministic abstract transaction-fabric model; NOT RTL/GPU data.

Transport assumptions: all replicas are registered at injection; a terminal event
arrives for every replica (delivered or dropped); no replication after close;
ACK is non-replaying and cannot overtake terminal events; primary is delivered.
"""
import argparse
import heapq
import itertools
import json
import random
import statistics


def simulate(seed, tags, count, dup_probability, max_gap, policy, loss_probability=0.0):
    assert policy in ('first_delivery', 'quiescence')
    assert 0 <= dup_probability <= 1 and 0 <= loss_probability <= 1
    rng = random.Random(seed)
    pending = []  # due, order, tag, immutable owner, deliver
    live = {}  # tag -> owner, remaining, seen
    free = set(range(tags))
    serial = 0
    injected = 0
    terminal = 0
    good_credits = 0
    false_credits = 0
    stale = 0
    retired = 0
    max_live = 0
    for cycle in range(200000):
        while pending and pending[0][0] <= cycle:
            _, _, tag, owner, deliver = heapq.heappop(pending)
            terminal += 1
            rec = live.get(tag)
            if rec is not None and rec['owner'] == owner:
                rec['remaining'] -= 1
                assert rec['remaining'] >= 0
            if deliver:
                if rec is None:
                    stale += 1
                elif not rec['seen']:
                    rec['seen'] = True
                    if rec['owner'] == owner:
                        good_credits += 1
                    else:
                        false_credits += 1
                elif rec['owner'] != owner:
                    stale += 1
        for tag, rec in list(live.items()):
            if rec['seen'] and (policy == 'first_delivery' or rec['remaining'] == 0):
                del live[tag]
                free.add(tag)
                retired += 1
        if serial < count and free:
            tag = min(free)
            free.remove(tag)
            serial += 1
            base = rng.randint(1, 4)
            copies = [(cycle + base, True)]
            if rng.random() < dup_probability:
                copies.append((cycle + base + rng.randint(1, max_gap),
                               rng.random() >= loss_probability))
            live[tag] = {'owner': serial, 'remaining': len(copies), 'seen': False}
            for due, deliver in copies:
                injected += 1
                heapq.heappush(pending, (due, injected, tag, serial, deliver))
        max_live = max(max_live, len(live))
        assert len(free) + len(live) == tags
        if serial == count and not live and not pending:
            return dict(policy=policy, seed=seed, tags=tags, transactions=count,
                        cycles=cycle + 1, throughput=retired / (cycle + 1),
                        issued=serial, retired=retired, good_credits=good_credits,
                        false_credits=false_credits, stale=stale,
                        injected=injected, terminal=terminal, max_live=max_live)
    raise AssertionError('simulation exceeded horizon')


def exhaustive_quiescence(max_copies=4):
    """Enumerate delivery/drop ordering for small, closed replica sets."""
    states = safe_acks = weak_unsafe = no_delivery = 0
    for n in range(1, max_copies + 1):
        for deliveries in itertools.product((False, True), repeat=n):
            for ordering in itertools.permutations(range(n)):
                seen = False
                remaining = n
                for index in ordering:
                    seen |= deliveries[index]
                    remaining -= 1
                    states += 1
                    strong = seen and remaining == 0
                    weak = seen
                    if strong:
                        safe_acks += 1
                        assert not remaining
                    if weak and remaining:
                        weak_unsafe += 1
                if not any(deliveries):
                    no_delivery += 1
    return dict(states=states, strong_ack_safe_states=safe_acks,
                weak_ack_unsafe_states=weak_unsafe,
                no_delivery_permutations=no_delivery)


def run():
    prereg = {
        'H1': 'With all replicas accounted for, quiescence retirement yields zero false credits across the holdout suite.',
        'H2': 'First-delivery retirement produces false credits when replicas arrive after tag reuse.',
        'H3': 'Quiescence reduces throughput in high-delay duplicate regimes; quantify cost instead of hiding it.',
        'H4': 'Without guaranteed delivery or bounded retry, the strong protocol is safe but not live.',
        'H5': 'The mechanism requires replication accounting at the last copy-generating point; hidden replicas invalidate it.'
    }
    exhaustive = exhaustive_quiescence()
    cases = []
    for seed in (11, 23, 37, 53):
        for tags in (1, 2, 4, 8):
            for p in (0.0, 0.25, 0.75):
                for gap in (2, 8, 32):
                    for policy in ('first_delivery', 'quiescence'):
                        r = simulate(seed, tags, 800, p, gap, policy, 0.25)
                        cases.append(dict(dup_p=p, max_gap=gap, **r))
                        assert r['issued'] == r['retired'] == 800
                        assert r['injected'] == r['terminal']
                        if policy == 'quiescence':
                            assert r['false_credits'] == 0
    rng = random.Random(65065)
    probes = []
    for i in range(18):  # 12.5% of paired structured comparisons
        seed = rng.randrange(1000000)
        tags = rng.randint(1, 12)
        p = rng.random()
        gap = rng.randint(1, 100)
        loss = rng.random()
        for policy in ('first_delivery', 'quiescence'):
            r = simulate(seed, tags, 800, p, gap, policy, loss)
            probes.append(dict(probe=i, dup_p=p, max_gap=gap, loss_p=loss, **r))
            if policy == 'quiescence':
                assert r['false_credits'] == 0
    pairs = []
    for a, b in zip(cases[::2], cases[1::2]):
        assert a['policy'] == 'first_delivery' and b['policy'] == 'quiescence'
        assert a['seed'] == b['seed'] and a['tags'] == b['tags']
        pairs.append(dict(seed=a['seed'], tags=a['tags'], dup_p=a['dup_p'],
                          gap=a['max_gap'], weak_false=a['false_credits'],
                          strong_false=b['false_credits'],
                          weak_rate=a['throughput'], strong_rate=b['throughput'],
                          strong_to_weak_rate=b['throughput'] / a['throughput']))
    summary = dict(structured_runs=len(cases), exploratory_runs=len(probes),
                   paired_cases=len(pairs), exhaustive=exhaustive,
                   weak_cases_with_false_credit=sum(p['weak_false'] > 0 for p in pairs),
                   total_weak_false_credits=sum(p['weak_false'] for p in pairs),
                   total_strong_false_credits=sum(p['strong_false'] for p in pairs),
                   median_strong_to_weak_rate=statistics.median(p['strong_to_weak_rate'] for p in pairs),
                   min_strong_to_weak_rate=min(p['strong_to_weak_rate'] for p in pairs),
                   max_strong_to_weak_rate=max(p['strong_to_weak_rate'] for p in pairs))
    return dict(preregistered=prereg, summary=summary, pairs=pairs, probes=probes)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='research/065/results/quiescence_065.json')
    args = ap.parse_args()
    result = run()
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result['summary'], indent=2))
