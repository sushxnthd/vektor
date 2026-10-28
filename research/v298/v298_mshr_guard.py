#!/usr/bin/env python3
"""Synthetic V298 MSHR credit guard. Not a GPU performance model.

Deterministic event simulator; all policies see identical potential background arrivals.
An MSHR is occupied until completion; one issue per cycle. A critical burst is a
serial chain: the next load becomes ready D cycles after the previous return.
The guard holds the MSHR credit freed by a critical return until the next
known dependent load is issued. No future burst arrival is revealed to it.
"""
import json
import random
import statistics


def simulate(policy, *, seed, cycles=30000, mshr=4, critical_latency=8,
             background_latency=32, gap=240, chain=8, compute_delay=4,
             bg_probability=1.0):
    rng = random.Random(seed)
    active = []  # (completion_time, kind)
    bg_pending = 0
    next_critical_ready = 0
    next_burst_start = 0
    in_burst = False
    chain_issued = 0
    chain_done = 0
    credit_guard = False
    completed_bursts = []
    burst_start_time = None
    background_issued = 0
    background_completed = 0
    critical_issued = 0
    critical_completed = 0
    idle_credit_cycles = 0
    max_bg_pending = 0
    for t in range(cycles):
        if rng.random() < bg_probability:
            bg_pending += 1
        max_bg_pending = max(max_bg_pending, bg_pending)
        remains = []
        for done, kind in active:
            if done > t:
                remains.append((done, kind))
            elif kind == 'bg':
                background_completed += 1
            else:
                critical_completed += 1
                chain_done += 1
                if chain_done == chain:
                    completed_bursts.append(t - burst_start_time)
                    in_burst = False
                    credit_guard = False
                    next_burst_start = t + gap
                else:
                    next_critical_ready = t + compute_delay
                    credit_guard = True
        active = remains
        if not in_burst and t >= next_burst_start:
            in_burst = True
            burst_start_time = t
            chain_issued = 0
            chain_done = 0
            next_critical_ready = t
            credit_guard = False
        critical_pending = (in_burst and chain_issued == chain_done
                            and chain_issued < chain and t >= next_critical_ready)
        free = mshr - len(active)
        if free > 0 and critical_pending:
            active.append((t + critical_latency, 'crit'))
            critical_issued += 1
            chain_issued += 1
            credit_guard = False
        elif free > 0 and bg_pending > 0:
            can_bg = policy != 'fixed_reserve' or len(active) < mshr - 1
            if policy == 'guard' and credit_guard and free <= 1:
                can_bg = False
            if (policy == 'deadline_aware' and credit_guard and free <= 1
                    and t + background_latency > next_critical_ready):
                can_bg = False
            if can_bg:
                active.append((t + background_latency, 'bg'))
                background_issued += 1
                bg_pending -= 1
        if policy == 'guard' and credit_guard and mshr - len(active) > 0:
            idle_credit_cycles += 1
        assert len(active) <= mshr, "MSHR overflow"
        assert chain_done <= chain_issued <= chain, "critical chain duplication"
    return {
        'policy': policy, 'seed': seed, 'cycles': cycles,
        'critical_completed': critical_completed,
        'background_completed': background_completed,
        'background_issued': background_issued,
        'critical_issued': critical_issued,
        'bursts_completed': len(completed_bursts),
        'mean_burst_latency': statistics.mean(completed_bursts) if completed_bursts else None,
        'p95_burst_latency': sorted(completed_bursts)[int(.95 * (len(completed_bursts) - 1))] if completed_bursts else None,
        'guard_credit_cycles': idle_credit_cycles,
        'max_bg_pending': max_bg_pending,
    }


def exploratory_pilot():
    """Pre-protocol exploratory regimes: NEVER treat as prospective evidence."""
    cases = {
        'positive_long_background': dict(background_latency=32, gap=240, chain=8, compute_delay=4, bg_probability=1),
        'negative_short_background': dict(background_latency=4, gap=240, chain=8, compute_delay=4, bg_probability=1),
        'negative_sparse_background': dict(background_latency=32, gap=240, chain=8, compute_delay=4, bg_probability=.025),
        'negative_long_compute': dict(background_latency=32, gap=240, chain=8, compute_delay=40, bg_probability=1),
        'short_chain': dict(background_latency=32, gap=240, chain=2, compute_delay=4, bg_probability=1),
    }
    result = {'description': 'exploratory synthetic finite-MSHR issue; NOT prospective or GPU IPC', 'cases': {}}
    for case, kwargs in cases.items():
        data = {p: [simulate(p, seed=s, **kwargs) for s in [101, 103, 107, 109]]
                for p in ('work_conserving', 'fixed_reserve', 'guard', 'deadline_aware')}
        means = {}
        for p, runs in data.items():
            means[p] = {k: round(statistics.mean(x[k] for x in runs), 6)
                        for k in ('background_completed', 'critical_completed',
                                  'bursts_completed', 'mean_burst_latency',
                                  'p95_burst_latency', 'guard_credit_cycles')}
        result['cases'][case] = {'parameters': kwargs, 'means': means}
    return result


if __name__ == '__main__':
    print(json.dumps(exploratory_pilot(), indent=2, sort_keys=True))
