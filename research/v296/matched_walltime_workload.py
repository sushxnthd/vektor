#!/usr/bin/env python3
"""V296/serial matched-walltime synthetic bank+memory stress; NOT GPU evidence."""
import argparse
import itertools
import json
import math
import random
from collections import deque

BANKS, SLOTS, PORTS, DEPTH, COST = 16, 4, 2, 8, 8
DURATION, BURN = 60000, 12000


def events(seed, probability=.95, hotspot=.35, persistence=.90):
    rng = random.Random(seed)
    hot = rng.randrange(BANKS)
    out = []
    for t in range(0, DURATION, 4):
        if rng.random() > persistence:
            hot = rng.randrange(BANKS)
        for lane in range(SLOTS):
            if rng.random() > probability:
                continue
            a = hot if rng.random() < hotspot else rng.randrange(BANKS)
            b = hot if rng.random() < hotspot else rng.randrange(BANKS)
            out.append((t + 4 * rng.random(), lane, (a, b, COST)))
    return sorted(out)


def greedy(heads, tokens):
    used = [0] * BANKS
    yes = [False] * SLOTS
    for i, request in enumerate(heads):
        if request is None:
            continue
        a, b, cost = request
        if tokens + 1e-9 < cost or used[a] + 1 + (a == b) > PORTS or (a != b and used[b] + 1 > PORTS):
            continue
        yes[i] = True
        used[a] += 1
        used[b] += 1
        tokens -= cost
    return tuple(yes)


def oracle(heads, tokens):
    feasible = []
    for bits in itertools.product((False, True), repeat=SLOTS):
        counts = [0] * BANKS
        cost = 0
        for selected, request in zip(bits, heads):
            if selected:
                if request is None:
                    break
                a, b, price = request
                counts[a] += 1
                counts[b] += 1
                cost += price
        else:
            if max(counts) <= PORTS and cost <= tokens + 1e-9:
                feasible.append(bits)
    return max(feasible)


def replay(workload, period_ns, bandwidth_gbs, bucket=64):
    if not all(math.isfinite(x) and x > 0 for x in (period_ns, bandwidth_gbs, bucket)) or bucket < COST:
        raise ValueError('Invalid clock, bandwidth or bucket')
    fifo = [deque() for _ in range(SLOTS)]
    tokens = 0.
    cursor = 0
    all_offered = all_dropped = all_issued = 0
    offered = dropped = issued = traffic = 0
    for cycle in range(int(DURATION / period_ns)):
        end = (cycle + 1) * period_ns
        tokens = min(bucket, tokens + bandwidth_gbs * period_ns)
        new = lost = 0
        while cursor < len(workload) and workload[cursor][0] < end - 1e-9:
            _, lane, request = workload[cursor]
            cursor += 1
            new += 1
            if len(fifo[lane]) == DEPTH:
                lost += 1
            else:
                fifo[lane].append(request)
        heads = tuple(q[0] if q else None for q in fifo)
        chosen = greedy(heads, tokens)
        if chosen != oracle(heads, tokens):
            raise AssertionError('Greedy vs exhaustive priority mismatch')
        spent = 0
        for i, selected in enumerate(chosen):
            if selected:
                spent += fifo[i].popleft()[2]
        tokens -= spent
        if tokens < -1e-7:
            raise AssertionError('Bandwidth overspend')
        all_offered += new
        all_dropped += lost
        all_issued += sum(chosen)
        if end > BURN + 1e-9:
            offered += new
            dropped += lost
            issued += sum(chosen)
            traffic += spent
    if all_offered != all_dropped + all_issued + sum(map(len, fifo)):
        raise AssertionError('FIFO conservation')
    elapsed = DURATION - BURN
    if traffic / elapsed > bandwidth_gbs + 1e-9:
        raise AssertionError('Bandwidth violation')
    return dict(offered_per_ns=offered/elapsed, issued_per_ns=issued/elapsed,
                dropped_per_ns=dropped/elapsed, traffic_gbs=traffic/elapsed,
                bandwidth_utilization=traffic/elapsed/bandwidth_gbs,
                independent_oracle=True, fifo_conservation=True)


def case(seed, bandwidth, bucket=64, probability=.95):
    workload = events(seed, probability)
    serial = replay(workload, 4., bandwidth, bucket)
    candidate = replay(workload, 3., bandwidth, bucket)
    if serial['offered_per_ns'] != candidate['offered_per_ns']:
        raise AssertionError('Unmatched real-time workload')
    return dict(seed=seed, bandwidth_gbs=bandwidth, bucket_bytes=bucket,
                valid_probability=probability, serial=serial, candidate=candidate,
                throughput_ratio=candidate['issued_per_ns']/serial['issued_per_ns'])


def self_test():
    requests = (None, (0, 0, COST), (0, 1, COST), (1, 1, COST))
    for heads in itertools.product(requests, repeat=SLOTS):
        for credits in (0, 8, 16, 24, 32):
            assert greedy(heads, credits) == oracle(heads, credits)
    workload = events(296444)
    for bandwidth in (1., 20.):
        a = replay(workload, 4., bandwidth)
        assert a == replay(workload, 4., bandwidth)
        assert a['fifo_conservation'] and a['independent_oracle']
    print('V296_MATCHED_WALLTIME_SELFTEST_PASS: 1280 exhaustive subset checks, FIFO/bandwidth conservation')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--evaluate', choices=['calibration', 'prospective'])
    args = p.parse_args()
    if args.self_test:
        self_test()
    if args.evaluate:
        configs = ([(296101,20.,64,.95),(296102,1.,64,.95),(296103,2.5,16,.95),(296104,2.5,128,.95)]
                   if args.evaluate == 'calibration' else
                   [(296201,20.,64,.95),(296202,1.,64,.95),(296203,2.5,16,.95),(296204,2.5,128,.95)])
        rows = [case(*config) for config in configs]
        print(json.dumps(dict(evidence='SYNTHETIC_NOT_GPU', experiment=args.evaluate,
            original_integrated_gate='BOTH_INFEASIBLE', assumed_tile_periods_ns=[4.,3.],
            banks=BANKS, slots=SLOTS, ports_per_bank=PORTS, fifo_depth=DEPTH,
            cost_bytes_per_wave=COST, duration_ns=DURATION, burn_ns=BURN,
            workload_hotspot=.35, hotspot_persistence=.90,
            holdouts='EXISTING_GPU_HOLDOUTS_UNTOUCHED', cases=rows),indent=2))
    if not args.self_test and not args.evaluate:
        p.error('Select --self-test or --evaluate')

if __name__ == '__main__':
    main()
