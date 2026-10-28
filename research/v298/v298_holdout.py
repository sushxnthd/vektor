#!/usr/bin/env python3
"""Frozen V298 holdout runner. PROTOCOL.md committed at cfcbbc6436492afe67e514d1874b083786080ee6 before execution."""
import json
import statistics
from v298_mshr_guard import simulate

SEEDS = (211, 223, 227, 229)
CASES = {
    'H1_predicted_win': dict(background_latency=32, bg_probability=.30, gap=240, chain=8, compute_delay=4),
    'H2_predicted_win': dict(background_latency=24, bg_probability=.18, gap=180, chain=8, compute_delay=3),
    'H3_predicted_no_win': dict(background_latency=8, bg_probability=.50, gap=240, chain=8, compute_delay=4),
    'H4_predicted_no_win': dict(background_latency=32, bg_probability=.025, gap=240, chain=8, compute_delay=4),
    'H5_short_chain': dict(background_latency=32, bg_probability=.30, gap=240, chain=2, compute_delay=4),
    'H6_oracle_advantage': dict(background_latency=32, bg_probability=.50, gap=240, chain=8, compute_delay=40),
}
POLICIES = ('work_conserving', 'fixed_reserve', 'guard', 'deadline_aware')


def evaluate():
    output = {'protocol': 'research/v298/PROTOCOL.md', 'cycles_per_run': 30000,
              'seeds': SEEDS, 'results': {}}
    for name, params in CASES.items():
        runs = {p: [simulate(p, seed=s, **params) for s in SEEDS] for p in POLICIES}
        summary = {
            p: {metric: round(statistics.mean(run[metric] for run in runs[p]), 6)
                for metric in ('background_completed', 'critical_completed',
                               'bursts_completed', 'mean_burst_latency',
                               'p95_burst_latency')}
            for p in POLICIES
        }
        wc, fixed, guard = (summary[p] for p in POLICIES[:3])
        positive = (
            guard['mean_burst_latency'] <= .9 * wc['mean_burst_latency']
            and guard['background_completed'] >= .9 * wc['background_completed']
            and guard['background_completed'] >= 1.1 * fixed['background_completed']
            and guard['mean_burst_latency'] <= 1.05 * fixed['mean_burst_latency']
        )
        output['results'][name] = {'parameters': params, 'means': summary,
                                   'gate_pass': positive, 'individual_runs': runs}
    return output


if __name__ == '__main__':
    print(json.dumps(evaluate(), sort_keys=True, indent=2))
