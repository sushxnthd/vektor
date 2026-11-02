#!/usr/bin/env python3
"""Independent audit: enumerates masks and bank usage; imports no evaluator code."""
import json
import random
import sys
from itertools import product

SEEDS=(1603,2603,3603)
N=12000

def legal(batch,ids):
    bank_use={}
    for i in ids:
        for b in batch[i]:
            bank_use[b]=bank_use.get(b,0)+1
            if bank_use[b]>2: return False
    return True

def admissible(batch,indices):
    head=indices[0]
    return [(head,)]+[(head,i) for i in indices[1:] if legal(batch,(head,i))]

def best_second(batch,first):
    remaining=tuple(i for i in range(4) if i not in first)
    if not remaining: return 0
    return max(map(len,admissible(batch,remaining)))

def compute(batch):
    feasible=admissible(batch,tuple(range(4)))
    greedy=next((s for s in feasible[1:]),(0,))
    conflict=[]
    for i in range(1,4):
        degree=sum(any(b in batch[j] for b in batch[i]) for j in range(4) if j!=i)
        conflict.append((degree,i))
    degree=(0,)
    for _,i in sorted(conflict):
        if legal(batch,(0,i)):
            degree=(0,i)
            break
    g=len(greedy)+best_second(batch,greedy)
    d=len(degree)+best_second(batch,degree)
    o=max(len(s)+best_second(batch,s) for s in feasible)
    tail=greedy
    for s in feasible[1:]:
        remaining=[i for i in range(4) if i not in s]
        if legal(batch,remaining):
            tail=s
            break
    t=len(tail)+best_second(batch,tail)
    opportunity=int(o>g)
    assert o-g==opportunity and t==o and o>=d
    return g,d,t,o,opportunity

def empty():
    return {k:0 for k in ('vectors','greedy','degree','tail','oracle','opportunities',
                          'degree_wins','degree_losses','degree_ties','identities_passed')}

def append(row,batch):
    g,d,t,o,p=compute(batch)
    row['vectors']+=1
    row['greedy']+=g
    row['degree']+=d
    row['tail']+=t
    row['oracle']+=o
    row['opportunities']+=p
    row['degree_wins']+=int(d>g)
    row['degree_losses']+=int(d<g)
    row['degree_ties']+=int(d==g)
    row['identities_passed']+=1

def audit(result):
    for b in (3,4,5):
        row=empty()
        for raw in product(range(b),repeat=8):
            append(row,tuple((raw[i],raw[i+1]) for i in range(0,8,2)))
        assert row==result['exhaustive'][str(b)],('exhaustive',b)
    combined=empty()
    for seed in SEEDS:
        row=empty()
        rng=random.Random(seed)
        for _ in range(N):
            append(row,tuple((rng.randrange(16),rng.randrange(16)) for i in range(4)))
        assert row==result['uniform_b16_by_seed'][str(seed)],('holdout',seed)
        for k in combined: combined[k]+=row[k]
    assert combined==result['uniform_b16_total']
    assert result['predictions']==dict(exact_opportunity_identity=True,tail_equals_oracle=True,
       b5_gain_ge_0p1pct=result['exhaustive']['5']['oracle']>=1.001*result['exhaustive']['5']['greedy'],
       b16_gain_le_1pct=combined['oracle']<=1.01*combined['greedy'])
    return dict(status='PASS',independent_vectors=sum(x['vectors'] for x in result['exhaustive'].values())+combined['vectors'],
                b5_gain=result['exhaustive']['5']['oracle']/result['exhaustive']['5']['greedy'],
                b16_gain=combined['oracle']/combined['greedy'])

if __name__=='__main__':
    with open(sys.argv[1]) as f: data=json.load(f)
    print(json.dumps(audit(data),sort_keys=True,indent=2))
