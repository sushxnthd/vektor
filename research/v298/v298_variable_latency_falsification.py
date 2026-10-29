#!/usr/bin/env python3
"""V298 prospective variable-latency/false-dependency stress test.

Isolated finite-MSHR discrete-event model; NOT GPU IPC or hardware PPA.
All policies see identical exogenous arrival sequences, background service draws,
critical service draws and prediction events. Latencies are bound to request IDs
before policy-dependent admission, avoiding admission-order RNG confounding.
"""
from __future__ import annotations
import argparse
import json
import random
import statistics
from collections import deque

POLICIES = ('work_conserving', 'fixed_reserve', 'guard', 'phase_reserve')
SEEDS = (503, 509, 521, 523)
CYCLES = 40000
M = 4
CASES = {
    'V1_long_stable': dict(bg_lat=(32, 32), bg_q=.30, gap=240, chain=8, D=4, fp=0, fn=0, cancel=4),
    'V2_variable_long': dict(bg_lat=(8, 64), bg_q=.30, gap=240, chain=8, D=4, fp=.15, fn=.10, cancel=8),
    'V3_short_no_win': dict(bg_lat=(4, 12), bg_q=.50, gap=240, chain=8, D=4, fp=0, fn=0, cancel=4),
    'V4_false_positive': dict(bg_lat=(8, 64), bg_q=.30, gap=240, chain=8, D=4, fp=.85, fn=.10, cancel=48),
    'V5_long_cancel': dict(bg_lat=(16, 48), bg_q=.30, gap=240, chain=8, D=4, fp=.50, fn=.05, cancel=96),
    'V6_low_traffic': dict(bg_lat=(8, 64), bg_q=.025, gap=240, chain=8, D=4, fp=.15, fn=.10, cancel=8),
}

def generate(case, seed, cycles=CYCLES):
    """Precompute arrivals and all service times; no policy can affect draws."""
    rng = random.Random(seed)
    nbg = cycles + 500
    arrivals = [rng.random() < case['bg_q'] for _ in range(cycles)]
    bg_service = [rng.randint(*case['bg_lat']) for _ in range(nbg)]
    nburst = cycles // max(1,case['gap']) + 500
    crit_service = [[rng.randint(6, 10) for _ in range(case['chain'])] for _ in range(nburst)]
    false_neg = [[rng.random() < case['fn'] for _ in range(case['chain'])] for _ in range(nburst)]
    false_pos = [rng.random() < case['fp'] for _ in range(nburst)]
    return arrivals, bg_service, crit_service, false_neg, false_pos

def simulate(policy, case, seed, cycles=CYCLES):
    assert policy in POLICIES
    arrivals, bg_service, crit_service, false_neg, false_pos = generate(case, seed, cycles)
    active = []  # (finish, type, burst_id, critical_index)
    bg_queue = deque()
    bg_next = 0
    in_burst = False
    burst_id = -1
    burst_start = 0
    next_start = 0
    issued = done = 0
    crit_ready_at = 0
    guard = False
    cancel_at = None
    latencies = []
    bg_completed = bg_issued = crit_completed = 0
    idle_guard = false_guard_cycles = 0
    max_queue = 0
    for t in range(cycles):
        if arrivals[t]:
            bg_queue.append(bg_next)
            bg_next += 1
        max_queue = max(max_queue, len(bg_queue))
        remaining = []
        for finish, kind, bid, idx in active:
            if finish > t:
                remaining.append((finish, kind, bid, idx))
                continue
            if kind == 'bg':
                bg_completed += 1
            else:
                assert in_burst and bid == burst_id and idx == done
                crit_completed += 1
                done += 1
                if done == case['chain']:
                    latencies.append(t - burst_start)
                    in_burst = False
                    next_start = t + case['gap']
                    if false_pos[bid]:
                        guard = True
                        cancel_at = t + case['cancel']
                    else:
                        guard = False
                        cancel_at = None
                else:
                    crit_ready_at = t + case['D']
                    guard = not false_neg[bid][idx]
                    cancel_at = None
        active = remaining
        if cancel_at is not None and t >= cancel_at:
            guard = False
            cancel_at = None
        if not in_burst and t >= next_start:
            in_burst = True
            burst_id += 1
            burst_start = t
            issued = done = 0
            crit_ready_at = t
        pending_critical = (in_burst and issued == done and issued < case['chain'] and t >= crit_ready_at)
        free = M - len(active)
        if free and pending_critical:
            active.append((t + crit_service[burst_id][issued], 'crit', burst_id, issued))
            issued += 1
            guard = False
            cancel_at = None
        elif free and bg_queue:
            can_bg = True
            if policy == 'fixed_reserve':
                can_bg = free > 1
            elif policy == 'guard':
                can_bg = not (guard and free == 1)
            elif policy == 'phase_reserve':
                can_bg = not (in_burst and free == 1)
            if can_bg:
                req = bg_queue.popleft()
                active.append((t + bg_service[req], 'bg', -1, -1))
                bg_issued += 1
        if policy == 'guard' and guard and M - len(active) > 0:
            idle_guard += 1
            if not in_burst:
                false_guard_cycles += 1
        assert len(active) <= M
        assert 0 <= done <= issued <= case['chain']
    return dict(policy=policy, seed=seed, bursts=len(latencies), mean_burst=statistics.mean(latencies) if latencies else None,
                p95_burst=sorted(latencies)[int(.95*(len(latencies)-1))] if latencies else None,
                bg_completed=bg_completed, bg_issued=bg_issued, crit_completed=crit_completed,
                idle_guard=idle_guard, false_guard_cycles=false_guard_cycles, max_queue=max_queue)

def evaluate():
    output = dict(evidence='synthetic finite-MSHR; no GPU IPC or routed PPA', seeds=SEEDS, cycles=CYCLES, mshr=M, cases={})
    for name, case in CASES.items():
        runs = {p:[simulate(p,case,s) for s in SEEDS] for p in POLICIES}
        means = {p:{k:statistics.mean(r[k] for r in rs) for k in ('mean_burst','p95_burst','bg_completed','bg_issued','bursts','idle_guard','false_guard_cycles')}
                 for p,rs in runs.items()}
        g,w,f,ph = (means[p] for p in ('guard','work_conserving','fixed_reserve','phase_reserve'))
        output['cases'][name] = dict(parameters=case, means=means, runs=runs,
           relative=dict(critical_latency_reduction_vs_work_conserving=1-g['mean_burst']/w['mean_burst'],
                         background_retention_vs_work_conserving=g['bg_completed']/w['bg_completed'],
                         critical_latency_reduction_vs_phase_reserve=1-g['mean_burst']/ph['mean_burst'],
                         background_retention_vs_phase_reserve=g['bg_completed']/ph['bg_completed'],
                         background_vs_fixed=g['bg_completed']/f['bg_completed']))
    return output

def selftest():
    for p in POLICIES:
        x=simulate(p,CASES['V1_long_stable'],503,1000)
        assert x['bg_completed'] <= x['bg_issued']
        assert x['crit_completed'] >= x['bursts']*CASES['V1_long_stable']['chain']
    c={**CASES['V1_long_stable'],'bg_q':0}
    xs=[simulate(p,c,509,2000) for p in POLICIES]
    assert len({(x['mean_burst'],x['crit_completed']) for x in xs})==1
    assert simulate('guard',CASES['V1_long_stable'],509,2000)['false_guard_cycles']==0
    print('SELFTEST PASS: conservation, zero-traffic equivalence, false-positive control')

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--selftest',action='store_true')
    ap.add_argument('--evaluate',action='store_true')
    args=ap.parse_args()
    if args.selftest: selftest()
    if args.evaluate: print(json.dumps(evaluate(),indent=2,sort_keys=True))
