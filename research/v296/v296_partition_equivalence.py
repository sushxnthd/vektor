#!/usr/bin/env python3
"""Exact V296/V295 four-slot bank-admission certificate; Python stdlib only."""
import json, random
from collections import Counter
from math import comb
from fractions import Fraction

B, W = 16, 4

def partitions(n=8):
    def go(a, high):
        if len(a) == n:
            yield tuple(a)
        else:
            for x in range(high+2):
                yield from go(a+[x], max(high,x))
    yield from go([0], 0)

def pairwise(o, valid):
    g = 0
    for i in range(W):
        if not valid & (1<<i): continue
        a,b = o[2*i:2*i+2]
        ha = sum(o[2*j+k] == a for j in range(i) if g&(1<<j) for k in range(2))
        hb = sum(o[2*j+k] == b for j in range(i) if g&(1<<j) for k in range(2))
        if (a == b and ha == 0) or (a != b and ha < 2 and hb < 2): g |= 1<<i
    return g

def serial(o, valid):
    g=once=twice=0
    for i in range(W):
        if not valid&(1<<i): continue
        a,b = 1<<o[2*i],1<<o[2*i+1]
        fit = not (once&a) if a&b else not ((twice&a)|(twice&b))
        if fit:
            g |= 1<<i
            if a&b: once |= a; twice |= a
            else: twice |= once&(a|b); once |= a|b
    return g

def feasible(o,mask):
    c=Counter(o[2*i+j] for i in range(W) if mask&(1<<i) for j in range(2))
    return max(c.values(),default=0)<=2

def audit():
    total=B**8; counts=[0]*16; optcounts=[0]*16; sub=[0]*16
    mismatch=port_errors=weighted=patterns=0; witness=None; max_regret=0
    hist=Counter()
    for o in partitions():
        patterns+=1; k=max(o)+1; mult=1
        for i in range(k): mult*=B-i
        weighted+=mult
        for valid in range(16):
            g=pairwise(o,valid); s=serial(o,valid)
            mismatch+=g!=s
            port_errors+=not feasible(o,g) or bool(g&~valid)
            n=g.bit_count()
            optimum=max(x.bit_count() for x in range(16) if not x&~valid and feasible(o,x))
            counts[valid]+=mult*n; optcounts[valid]+=mult*optimum
            sub[valid]+=mult*(n<optimum)
            if optimum-n>max_regret:
                max_regret=optimum-n
                witness={'banks':list(o),'valid_mask':valid,'greedy_mask':g,'optimal_count':optimum}
            if valid==15: hist[n]+=mult
    assert patterns==4140 and weighted==total and mismatch==0 and port_errors==0
    polynomial=[sum(counts[m]*comb(W-m.bit_count(),d-m.bit_count())*(-1)**(d-m.bit_count())
                    for m in range(16) if d>=m.bit_count()) for d in range(5)]
    assert sum(polynomial)==counts[15]
    def expectation(arr,q):
        return sum(Fraction(arr[m],total)*q**m.bit_count()*(1-q)**(W-m.bit_count()) for m in range(16))
    sweep={}
    for q in (Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)):
        g=expectation(counts,q); o=expectation(optcounts,q)
        sweep[str(q)]={'greedy':round(float(g),9),'optimal':round(float(o),9),
                       'oracle_headroom_pct':round(float((o/g-1)*100),6),
                       'suboptimal_probability':round(float(expectation(sub,q)),9)}
    unseen={}
    for seed,q in ((296101,0.33),(296102,0.87)):
        r=random.Random(seed); observed=0
        for _ in range(100000):
            o=tuple(r.randrange(B) for _ in range(8))
            valid=sum(1<<i for i in range(W) if r.random()<q)
            observed+=serial(o,valid).bit_count()
        observed/=100000
        pred=sum(polynomial[d]*q**d for d in range(5))/total
        assert abs(pred-observed)<0.025
        unseen[str(q)]={'seed':seed,'predicted':round(pred,8),'observed':round(observed,8),
                        'abs_error':round(abs(pred-observed),8)}
    r=random.Random(2961028)
    for _ in range(100000):
        o=tuple(r.randrange(B) for _ in range(8)); v=r.randrange(16)
        assert pairwise(o,v)==serial(o,v) and feasible(o,pairwise(o,v))
    return {'patterns':patterns,'validity_cases':patterns*16,'concrete_bank_maps':total,
            'mismatches':mismatch,'port_errors':port_errors,'random_equivalence_tests':100000,
            'iid_polynomial_numerator':polynomial,'iid_polynomial_denominator':total,
            'full_valid_grant_distribution':{str(k):round(v/total,9) for k,v in sorted(hist.items())},
            'sweep':sweep,'unseen_q':unseen,'max_greedy_regret':max_regret,'witness':witness,
            'scope':'COMBINATIONAL_ADMISSION_ONLY_NO_RTL_TIMING_OR_GPU_PERFORMANCE_CLAIM'}

if __name__=='__main__':
    assert len(list(partitions(4)))==15
    assert pairwise((0,)*8,15)==serial((0,)*8,15)==1
    assert pairwise(tuple(range(8)),15)==serial(tuple(range(8)),15)==15
    print(json.dumps(audit(),indent=2,sort_keys=True))
