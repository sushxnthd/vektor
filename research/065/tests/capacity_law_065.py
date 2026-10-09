#!/usr/bin/env python3
"""Preregistered H6: mean-occupancy heuristic median error <10%; synthetic only."""
import json
import statistics
from quiescence_065 import simulate

def run():
    records = []
    for seed in (101, 211, 307):
        for tags in (1, 2, 3, 4, 6, 8, 12, 16):
            for dup_p in (0.25, 0.5, 0.75):
                for gap in (4, 16, 64):
                    actual = simulate(seed, tags, 3000, dup_p, gap, 'quiescence', 0.2)['throughput']
                    predicted = min(1.0, tags / (2.5 + dup_p * (gap + 1) / 2))
                    records.append(dict(seed=seed, tags=tags, dup_p=dup_p, gap=gap,
                                        predicted=predicted, actual=actual,
                                        relative_error=abs(actual-predicted)/actual))
    summary = dict(n=len(records), median_relative_error=statistics.median(r['relative_error'] for r in records),
                   max_relative_error=max(r['relative_error'] for r in records),
                   over_10_percent=sum(r['relative_error'] > .1 for r in records),
                   over_20_percent=sum(r['relative_error'] > .2 for r in records))
    assert summary['median_relative_error'] < .1
    with open('research/065/results/capacity_law_065.json', 'w') as f:
        json.dump(dict(preregistered='H6 median relative error below 10%', summary=summary, cases=records), f, indent=2)
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    run()
