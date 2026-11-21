#!/usr/bin/env python3
"""Exact exchangeable-uniform-bank two-cycle opportunity via set partitions.

Enumerates all 4,140 equivalence partitions of eight source positions, then
weights each k-class partition by (B)_k labeled bank assignments. Exact for
independent uniform bank assignments; no GPU claim.
"""
from __future__ import annotations
import json
from fractions import Fraction
from math import prod

def partitions(n):
    def walk(seq, k):
        if len(seq) == n:
            yield tuple(seq)
            return
        for j in range(k + 1):
            seq.append(j)
            yield from walk(seq, max(k, j+1))
            seq.pop()
    yield from walk([0],1)

def legal(requests, ids):
    bins = {}
    for i in ids:
        for b in requests[i]:
            bins[b] = bins.get(b,0) + 1
            if bins[b]>2:
                return False
    return True

def evaluate(mapping):
    requests = tuple(mapping[2*i:2*i+2] for i in range(4))
    first = [(0,)] + [(0,i) for i in range(1,4) if legal(requests,(0,i))]
    def completion(choice):
        rem = [i for i in range(4) if i not in choice]
        if not rem: return len(choice)
        return len(choice)+1+int(any(legal(requests,(rem[0],i)) for i in rem[1:]))
    greedy = completion(first[1] if len(first)>1 else (0,))
    oracle = max(completion(choice) for choice in first)
    assert oracle-greedy in (0,1)
    return oracle-greedy, greedy

def falling(b,k):
    return prod(range(b-k+1,b+1)) if k<=b else 0

def coefficients():
    by_k={str(k):{'partitions':0,'events':0,'greedy_completions':0} for k in range(1,9)}
    for mapping in partitions(8):
        k=max(mapping)+1
        event,greedy=evaluate(mapping)
        r=by_k[str(k)]
        r['partitions']+=1
        r['events']+=event
        r['greedy_completions']+=greedy
    assert sum(x['partitions'] for x in by_k.values())==4140
    return by_k

def predict(b,by_k):
    n=b**8
    opportunities=sum(row['events']*falling(b,int(k)) for k,row in by_k.items())
    greedy=sum(row['greedy_completions']*falling(b,int(k)) for k,row in by_k.items())
    assert sum(row['partitions']*falling(b,int(k)) for k,row in by_k.items())==n
    return {'banks':b,'event_probability':float(Fraction(opportunities,n)),
            'greedy_mean':float(Fraction(greedy,n)),
            'oracle_gain':float(Fraction(opportunities,greedy)),
            'event_fraction':str(Fraction(opportunities,n)),
            'gain_fraction':str(Fraction(opportunities,greedy))}

def run():
    c=coefficients()
    return {'schema':'vektor.v317.exact_bank_opportunity_polynomial.v1',
            'evidence_tier':'exact combinatorial synthetic iid-uniform-bank model; not physical bank mapping or measured GPU IPC',
            'coefficients_by_occupied_bank_classes':c,
            'leading_event_coefficient_b_inverse_square':c['6']['events'],
            'predictions':{str(b):predict(b,c) for b in (8,12,16,24,32,48,64)},
            'unseen_validation_required':True}

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
