#!/usr/bin/env python3
"""Independent V317 exact-law audit; no import of evaluator or law derivation."""
from __future__ import annotations
import json
import math
import random
import sys
from fractions import Fraction
from itertools import product

B=(12,48,64)
S=(4111,5113,6113)
N=12000

def admissible(req, indices):
    used={}
    for index in indices:
        for bank in req[index]:
            used[bank]=used.get(bank,0)+1
    return all(n<=2 for n in used.values())

def solve(req):
    choices=[(0,)]+[(0,j) for j in (1,2,3) if admissible(req,(0,j))]
    def finish(first):
        pending=[i for i in (0,1,2,3) if i not in first]
        if not pending:return len(first)
        second=[(pending[0],)]+[(pending[0],j) for j in pending[1:]
                                  if admissible(req,(pending[0],j))]
        return len(first)+max(len(s) for s in second)
    g=finish(choices[1] if len(choices)>1 else choices[0])
    o=max(finish(c) for c in choices)
    assert o-g in (0,1)
    return g,o

def falling(n,k):
    x=1
    for j in range(k):x*=n-j
    return x if k<=n else 0

def exact(b):
    events=(153*falling(b,3)+212*falling(b,4)+61*falling(b,5)+4*falling(b,6))
    greedy=(2*falling(b,1)+404*falling(b,2)+3511*falling(b,3)
            +6536*falling(b,4)+4139*falling(b,5)+1060*falling(b,6)
            +112*falling(b,7)+4*falling(b,8))
    return Fraction(events,b**8),Fraction(greedy,b**8)

def audit(data):
    assert tuple(data['bank_counts'])==B and tuple(data['seeds'])==S and data['samples_per_seed']==N
    brute={}
    for b in (3,4):
        e=g=0
        for raw in product(range(b),repeat=8):
            req=tuple((raw[2*i],raw[2*i+1]) for i in range(4))
            x,y=solve(req)
            e+=y-x
            g+=x
        pe,pg=exact(b)
        assert Fraction(e,b**8)==pe and Fraction(g,b**8)==pg
        brute[str(b)]={'vectors':b**8,'events':e,'greedy':g}
    for b in B:
        rows=[]
        for seed in S:
            rng=random.Random(seed)
            r={'vectors':0,'greedy':0,'oracle':0,'opportunities':0}
            for _ in range(N):
                req=tuple((rng.randrange(b),rng.randrange(b)) for i in range(4))
                g,o=solve(req)
                r['vectors']+=1
                r['greedy']+=g
                r['oracle']+=o
                r['opportunities']+=o-g
            assert r==data['by_bank'][str(b)]['seeds'][str(seed)]
            rows.append(r)
        totals={k:sum(row[k] for row in rows) for k in rows[0]}
        assert totals==data['by_bank'][str(b)]['total']
        p,mean_g=exact(b)
        assert abs(data['by_bank'][str(b)]['exact_law']['event_probability']-float(p))<1e-15
        assert abs(data['by_bank'][str(b)]['exact_law']['greedy_mean']-float(mean_g))<1e-15
        mu=float(p*3*N)
        sigma=math.sqrt(float(3*N*p*(1-p)))
        assert data['by_bank'][str(b)]['within_five_sigma']==(abs(totals['opportunities']-mu)<=max(2,5*sigma))
        ratio=Fraction(totals['oracle'],totals['greedy'])/Fraction(1005,1000)
        assert data['by_bank'][str(b)]['clock_win']==(ratio>1)
        assert abs(data['by_bank'][str(b)]['conditional_oracle_rate_with_0p5pct_delay']-float(ratio))<1e-14
    assert data['predictions']=={
        'holdouts_within_five_sigma':all(data['by_bank'][str(b)]['within_five_sigma'] for b in B),
        'b12_clock_win':data['by_bank']['12']['clock_win'],
        'b48_b64_clock_no_win':not data['by_bank']['48']['clock_win'] and not data['by_bank']['64']['clock_win'],
        'bandwidth_0p95_kill':all(data['by_bank'][str(b)]['bandwidth_0p95_no_win'] for b in B)}
    return {'status':'PASS','independent_holdout_vectors':len(B)*len(S)*N,
            'exhaustive_cross_checks':brute,'predictions':data['predictions']}

if __name__=='__main__':
    with open(sys.argv[1],encoding='utf8') as f:data=json.load(f)
    print(json.dumps(audit(data),indent=2,sort_keys=True))
