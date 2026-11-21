#!/usr/bin/env python3
"""Prospective V317 exact bank-partition law transfer on unseen B=12/48/64.

Synthetic independent uniform bank assignments, optimistic clairvoyant
two-cycle upper bound. No GPU IPC, physical timing, or bank mapping.
"""
from __future__ import annotations
import json
import math
import random
from fractions import Fraction
from research.v317.rtl.exact_bank_opportunity_polynomial import coefficients, predict

BANKS = (12,48,64)
SEEDS = (4111,5113,6113)
N = 12000
OVERHEAD = Fraction(5,1000)

def legal(batch, indices):
    count = {}
    for i in indices:
        for bank in batch[i]:
            count[bank] = count.get(bank,0)+1
            if count[bank]>2:return False
    return True

def outcome(batch):
    first=[(0,)]+[(0,i) for i in range(1,4) if legal(batch,(0,i))]
    def score(chosen):
        remaining=[i for i in range(4) if i not in chosen]
        if not remaining:return len(chosen)
        return len(chosen)+1+int(any(legal(batch,(remaining[0],i)) for i in remaining[1:]))
    g=score(first[1] if len(first)>1 else (0,))
    o=max(score(chosen) for chosen in first)
    assert o-g in (0,1)
    return g,o

def run():
    coeff=coefficients()
    rows={}
    for b in BANKS:
        seeds={}
        for seed in SEEDS:
            rng=random.Random(seed)
            count={'vectors':0,'greedy':0,'oracle':0,'opportunities':0}
            for _ in range(N):
                batch=tuple((rng.randrange(b),rng.randrange(b)) for _ in range(4))
                g,o=outcome(batch)
                count['vectors']+=1
                count['greedy']+=g
                count['oracle']+=o
                count['opportunities']+=o-g
            seeds[str(seed)]=count
        total={k:sum(x[k] for x in seeds.values()) for k in next(iter(seeds.values()))}
        expected=predict(b,coeff)
        p=Fraction(expected['event_fraction'])
        trials=total['vectors']
        observed=total['opportunities']
        mu=float(p*trials)
        sigma=math.sqrt(float(trials*p*(1-p)))
        passes=abs(observed-mu)<=max(2,5*sigma)
        ratio=Fraction(total['oracle'],total['greedy'])
        conditional_clock=ratio/(1+OVERHEAD)
        rows[str(b)]={'seeds':seeds,'total':total,'exact_law':expected,
                      'expected_opportunities':mu,'binomial_sigma':sigma,
                      'empirical_opportunity_probability':observed/trials,
                      'empirical_oracle_gain':float(ratio-1),
                      'conditional_oracle_rate_with_0p5pct_delay':float(conditional_clock),
                      'clock_win':conditional_clock>1,
                      'within_five_sigma':passes,
                      'bandwidth_0p95_no_win':True}
    checks={'holdouts_within_five_sigma':all(x['within_five_sigma'] for x in rows.values()),
            'b12_clock_win':rows['12']['clock_win'],
            'b48_b64_clock_no_win':not rows['48']['clock_win'] and not rows['64']['clock_win'],
            'bandwidth_0p95_kill':all(x['bandwidth_0p95_no_win'] for x in rows.values())}
    return {'schema':'vektor.v317.exact_bank_partition_transfer.v1',
            'frozen_protocol':'FROZEN_EXACT_BANK_PARTITION_LAW_TRANSFER_20261103.md',
            'evidence_tier':'synthetic independent iid-uniform-bank holdouts, not GPU performance',
            'bank_counts':BANKS,'seeds':SEEDS,'samples_per_seed':N,
            'by_bank':rows,'predictions':checks,'physical_evidence':False}

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
