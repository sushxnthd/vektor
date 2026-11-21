#!/usr/bin/env python3
"""Frozen V317 two-cycle clairvoyant opportunity ceiling; synthetic bank-port model."""
import json
import random
from itertools import product

SEEDS=(1603,2603,3603)
SAMPLES=12000

def compatible(a,b):
    counts={}
    for bank in (*a,*b):
        counts[bank]=counts.get(bank,0)+1
        if counts[bank]>2: return False
    return True

def first_choice(batch,mode):
    if mode=='degree':
        degrees=[sum(bool(set(x)&set(y)) for j,y in enumerate(batch) if i!=j) for i,x in enumerate(batch)]
        order=sorted(range(1,4),key=lambda i:(degrees[i],i))
    else:
        order=list(range(1,4))
    if mode=='tail':
        for i in range(1,4):
            remaining=[j for j in range(1,4) if j!=i]
            if compatible(batch[0],batch[i]) and compatible(batch[remaining[0]],batch[remaining[1]]):
                return (0,i)
    for i in order:
        if compatible(batch[0],batch[i]): return (0,i)
    return (0,)

def second_count(batch,first):
    rem=[batch[i] for i in range(4) if i not in first]
    if len(rem)==2: return 1+int(compatible(rem[0],rem[1]))
    if len(rem)==3: return 1+int(any(compatible(rem[0],x) for x in rem[1:]))
    return min(len(rem),2)

def outcome(batch,mode):
    first=first_choice(batch,mode)
    return len(first)+second_count(batch,first),first

def oracle(batch):
    choices=[(0,)]+[(0,i) for i in range(1,4) if compatible(batch[0],batch[i])]
    return max(len(s)+second_count(batch,s) for s in choices)

def opportunity(batch,first):
    if len(first)!=2: return 0
    rest=[j for j in range(4) if j not in first]
    if compatible(batch[rest[0]],batch[rest[1]]): return 0
    return int(any(compatible(batch[0],batch[i]) and
                   compatible(batch[[j for j in range(1,4) if j!=i][0]],
                              batch[[j for j in range(1,4) if j!=i][1]])
                   for i in range(1,4)))

def empty():
    return dict(vectors=0,greedy=0,degree=0,tail=0,oracle=0,opportunities=0,
                degree_wins=0,degree_losses=0,degree_ties=0,identities_passed=0)

def add(row,batch):
    g,first=outcome(batch,'greedy')
    d,_=outcome(batch,'degree')
    t,_=outcome(batch,'tail')
    o=oracle(batch)
    opp=opportunity(batch,first)
    assert o-g==opp,(batch,g,o,opp)
    assert t==o,(batch,t,o)
    assert o>=d and o>=g
    row['vectors']+=1
    row['greedy']+=g
    row['degree']+=d
    row['tail']+=t
    row['oracle']+=o
    row['opportunities']+=opp
    row['degree_wins']+=int(d>g)
    row['degree_losses']+=int(d<g)
    row['degree_ties']+=int(d==g)
    row['identities_passed']+=1

def run():
    exhaustive={}
    for banks in (3,4,5):
        row=empty()
        for raw in product(range(banks),repeat=8):
            add(row,tuple((raw[2*i],raw[2*i+1]) for i in range(4)))
        exhaustive[str(banks)]=row
    random_holdout={}
    for seed in SEEDS:
        row=empty()
        rng=random.Random(seed)
        for _ in range(SAMPLES):
            add(row,tuple((rng.randrange(16),rng.randrange(16)) for _ in range(4)))
        random_holdout[str(seed)]=row
    totals=empty()
    for row in random_holdout.values():
        for k,v in row.items(): totals[k]+=v
    return dict(schema='vektor.v317.two_cycle_clairvoyant_ceiling.v1',
        evidence_tier='exact synthetic four-request two-cycle batch ceiling, not RTL or GPU IPC',
        frozen_protocol='FROZEN_TWO_CYCLE_CLAIRVOYANT_CEILING_20261103.md',
        ports_per_bank=2,issue_cap=2,cycles=2,request_count=4,
        exhaustive=exhaustive,uniform_b16_seeds=SEEDS,
        uniform_b16_samples_per_seed=SAMPLES,uniform_b16_by_seed=random_holdout,
        uniform_b16_total=totals,
        predictions=dict(exact_opportunity_identity=True,tail_equals_oracle=True,
          b5_gain_ge_0p1pct=exhaustive['5']['oracle']>=1.001*exhaustive['5']['greedy'],
          b16_gain_le_1pct=totals['oracle']<=1.01*totals['greedy']))

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
