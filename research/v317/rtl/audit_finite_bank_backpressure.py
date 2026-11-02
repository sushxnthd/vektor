#!/usr/bin/env python3
"""Independent JSON-only audit of frozen V317 finite-buffer experiment.

Does not import or call the event simulator.
"""
from __future__ import annotations
import json
import math
import sys
from statistics import mean

FROZEN = {
    'W_ports': (32, 32, 1.0, 25, 1.0273525341549115),
    'N_ports': (4, 4, 1.0, 25, 1.0002510997707081),
    'R_eligibility': (32, 32, 0.85, 25, 0.9185977952901293),
    'N_bandwidth': (32, 12, 1.0, 25, 1.000014520112589),
    'H_marginal': (32, 32, 0.95, 25, 0.9924918555270553),
    'E_equal_resource': (32, 32, 1.0, 24, 1.0),
}

def independent_rate(n, b, q, c):
    # Separate DP on active-bank count; does not access simulator.
    dist = {0: 1.0}
    for _ in range(n):
        nxt = {}
        for k, p in dist.items():
            nxt[k] = nxt.get(k, 0) + p * (1 - q * (b - k) / b)
            nxt[k + 1] = nxt.get(k + 1, 0) + p * q * (b - k) / b
        dist = nxt
    return sum(min(k, c) * p for k, p in dist.items())

def audit(data):
    assert data['source_tiles'] == 24 and data['pairwise_tiles'] == 25
    assert data['local_fifo_depth'] == 4 and data['output_fifo_depth'] == 8
    assert data['measured_cycles'] == 30000 and data['warmup_cycles'] == 2048
    assert data['seeds'] == [17, 71, 173]
    assert data['falsification_threshold'] == 0.015
    rows = data['rows']
    assert {r['regime'] for r in rows} == set(FROZEN) and len(rows) == len(FROZEN)
    failures = []
    for r in rows:
        name = r['regime']
        b, c, q, np, frozen = FROZEN[name]
        assert (r['banks'], r['bandwidth'], r['pairwise_q']) == (b, c, q)
        pred = independent_rate(np, b, q, c) / independent_rate(24, b, 1.0, c)
        assert math.isclose(pred, frozen, abs_tol=1e-10)
        assert math.isclose(pred, r['predicted_independent_head_ratio'], abs_tol=1e-10)
        assert [s['seed'] for s in r['samples']] == [17, 71, 173]
        ratios = []
        for s in r['samples']:
            for label, n in [('source', 24), ('pairwise', np)]:
                x = s[label]
                assert x['completed'] <= c * 30000
                assert math.isclose(x['rate'], x['completed']/30000, abs_tol=1e-12)
                assert 0 <= x['max_local_fifo'] <= 4
                assert 0 <= x['max_output_fifo'] <= 8
                assert 0 <= x['final_output_backlog'] <= 8
                for field in ['blocked_admissions','bank_stalls','output_stalls']:
                    assert isinstance(x[field], int) and x[field] >= 0
                # Arrival conservation up to initial/final finite buffer contents.
                assert abs(n*30000 - x['blocked_admissions'] - x['completed']) <= 4*n + 8
            ratio = s['pairwise']['rate']/s['source']['rate']
            assert math.isclose(ratio, s['ratio'], abs_tol=1e-12)
            ratios.append(ratio)
        avg = mean(ratios)
        error = abs(avg - frozen)
        assert math.isclose(avg, r['finite_fifo_ratio_mean'], abs_tol=1e-12)
        assert math.isclose(error, r['absolute_error'], abs_tol=1e-12)
        assert r['falsified'] == (error > 0.015)
        if r['falsified']:
            failures.append(name)
    assert data['any_independent_head_falsified'] == bool(failures)
    assert 'R_eligibility' in failures, 'expected prospective falsification missing'
    return failures

if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as f:
        data = json.load(f)
    failures = audit(data)
    print('PASS: independent structural, conservation and prediction audit; falsified:', ', '.join(failures))
