#!/usr/bin/env python3
"""Independent exhaustive B=2,3 audit of V317 degree-control claim.
No import of RTL, evaluator, or comparator implementations.
Combinational only; not a workload, area, timing or GPU IPC result.
"""
import json
from collections import Counter
from itertools import product

def feasible(req, subset):
    ports = {}
    for idx, pair in enumerate(req):
        if subset & (1 << idx):
            for bank in pair:
                ports[bank] = ports.get(bank, 0) + 1
                if ports[bank] > 2:
                    return False
    return True

def grant(req, valid, kind):
    order = [0, 1, 2, 3]
    if kind == 'degree':
        overlap = lambda i,j: any(x == y for x in req[i] for y in req[j])
        order[1:] = sorted(order[1:], key=lambda i: (sum(bool(valid & (1 << j)) and overlap(i,j) for j in range(4) if i != j), i))
    mask = 0
    for i in order:
        if (valid & (1 << i)) and feasible(req, mask | (1 << i)):
            mask |= 1 << i
    return mask

def optimum(req, valid):
    return max((m for m in range(16) if not (m & ~valid) and (not (valid & 1) or m & 1) and feasible(req,m)),key=lambda m:(m.bit_count(),tuple(bool(m & (1 << i)) for i in range(4))))

def run():
    out = {}
    for banks in (2,3):
        c = Counter();examples={}
        for valid in range(16):
            for x in product(range(banks), repeat=8):
                req = tuple(zip(x[::2],x[1::2]))
                g = grant(req,valid,'greedy')
                d = grant(req,valid,'degree')
                e = optimum(req,valid)
                assert feasible(req,g) and feasible(req,d) and feasible(req,e)
                assert (g & ~valid) == 0 and (d & ~valid) == 0
                assert not (valid & 1) or (g & d & e & 1)
                assert d.bit_count() <= e.bit_count() and g.bit_count() <= e.bit_count()
                c['cases']+=1
                for k,m in [('greedy_grants',g),('degree_grants',d),('exact_head_grants',e)]:c[k]+=m.bit_count()
                for k,condition in [('degree_wins',d.bit_count()>g.bit_count()),('degree_losses',d.bit_count()<g.bit_count()),('degree_below_exact',d.bit_count()<e.bit_count())]:
                    if condition:
                        c[k]+=1
                        if k not in examples:examples[k]=dict(valid=valid,requests=req,greedy=g,degree=d,exact_head=e)
        out[str(banks)]={'counts':dict(c),'first_counterexamples':examples}
    assert out['2']['counts']==dict(cases=4096,greedy_grants=5210,degree_grants=5226,exact_head_grants=5258,degree_wins=16,degree_below_exact=32)
    assert out['3']['counts']==dict(cases=104976,greedy_grants=158409,degree_grants=158529,exact_head_grants=159225,degree_wins=216,degree_losses=96,degree_below_exact=696)
    return {'evidence_tier':'exhaustive combinational small-bank model only; no RTL PPA or sustained GPU throughput', 'head_required_if_valid':True, 'ports_per_bank':2,'results':out}

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
