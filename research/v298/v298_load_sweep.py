#!/usr/bin/env python3
"""Post-hoc V298 offered-load sensitivity. EXPLORATORY, not prospective."""
from __future__ import annotations
import statistics
from v298_variable_latency_falsification import CASES, SEEDS, POLICIES, simulate

def mean(runs, key):
    return statistics.mean(r[key] for r in runs)

def main():
    print('q,guard_critical_improvement_pct,guard_vs_phase_latency_pct,guard_vs_phase_background_pct,guard_max_queue')
    for q in (.05, .08, .10, .12, .14):
        case = {**CASES['V1_long_stable'], 'bg_q': q}
        runs = {p: [simulate(p, case, s) for s in SEEDS] for p in POLICIES}
        g, w, ph = (runs[p] for p in ('guard', 'work_conserving', 'phase_reserve'))
        print(f"{q:.2f},{100*(1-mean(g,'mean_burst')/mean(w,'mean_burst')):.4f},"
              f"{100*(mean(g,'mean_burst')/mean(ph,'mean_burst')-1):.4f},"
              f"{100*(mean(g,'bg_completed')/mean(ph,'bg_completed')-1):.4f},"
              f"{mean(g,'max_queue'):.2f}")

if __name__ == '__main__':
    main()
