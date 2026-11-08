#!/usr/bin/env python3
"""Prospective demand-denominator falsification for V317 trace comparisons.

A grant-only trace is a service log, not a workload description. Two equal-resource
implementations must receive the same offered request IDs and arrival cycles before
their completed-request throughput can be interpreted as a speedup.
This regression deliberately uses the existing checker unchanged and must fail
if it ever begins to claim workload equivalence from grant logs alone.
"""
import csv
import tempfile
from pathlib import Path
from v317_matched_trace_gate import audit, compare

FIELDS = ('cycle','request_id','bank','operand','complete','retained_words')

def write(path, rows):
    with path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        w.writerows(rows)

def run():
    with tempfile.TemporaryDirectory() as d:
        a, b = Path(d)/'baseline.csv', Path(d)/'candidate.csv'
        # Same nominal clock and hardware. Baseline receives two jobs and
        # finishes one. Candidate's trace silently omits the second job.
        # Without an independently frozen demand manifest, both audit summaries
        # report 1 completion and a misleading ratio of 1.0.
        write(a, [(0,0,0,0,0,1),(1,0,1,1,1,0),
                  (2,1,0,0,0,1)])
        write(b, [(0,0,0,0,0,1),(1,0,1,1,1,0)])
        k = dict(period_ns=3,bank_count=2,bank_ports=1,return_ports=1,
                 word_budget=2,max_cycles=4,retention_mode='registered')
        base, cand = audit(a,**k), audit(b,**k)
        assert base['completed'] == cand['completed'] == 1
        assert compare(base,cand)['ratio'] == 1
        # The demand manifests below are intentionally unequal.
        base_offered = {(0,0),(1,2)}
        cand_offered = {(0,0)}
        assert base_offered != cand_offered
        assert 'offered_requests' not in base and 'offered_requests' not in cand
        print('FALSIFIED: equal-resource grant traces do not certify equal offered workloads')
        print('NEEDED: immutable arrival manifest, matching request IDs, censoring/queue state,')
        print('        end-of-horizon pending requests, and identical warmup/drain policy')
        print('NO CLAIM: physical RTL speedup, synthesis closure, or GPU IPC')
if __name__ == '__main__':
    run()
