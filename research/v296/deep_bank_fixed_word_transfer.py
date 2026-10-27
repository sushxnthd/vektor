#!/usr/bin/env python3
"""V296 two-static-word deep-bank transfer falsification.
Frozen protocol: DEEP_BANK_FIXED_WORD_TRANSFER_PREREG_20261027.md.
No GPU performance, physical closure, or deep-SRAM equivalence claim.
"""
import argparse
import itertools
import json
import math
import random

SEEDS = (927611, 927613, 927617)
N = 100000
TOL = .012

def regimes():
    return [(f'uniform_D{d}', [1/d]*d, .2, target)
            for d, target in [(2,1.), (4,.3), (8,.1), (16,.0375), (32,.015625)]] + [
        ('skew_D16_rho02', [.55,.25]+[.2/14]*14, .2, .672),
        ('skew_D16_rho08', [.90,.05]+[.05/14]*14, .8, .9405),
        ('skew_D16_mid', [.50,.25]+[.25/14]*14, .8, .7125)]

def validate(p,rho):
    if len(p)<2 or any(not math.isfinite(x) or x<0 for x in p):
        raise ValueError('invalid distribution')
    if not math.isclose(sum(p),1,rel_tol=0,abs_tol=1e-12):
        raise ValueError('distribution must sum to one')
    if not math.isfinite(rho) or not 0<=rho<=1:
        raise ValueError('invalid copy probability')

def optimal_static_words(p):
    return tuple(sorted(range(len(p)),key=lambda i:(-p[i],i))[:2])

def analytic_coverage(p,rho,selected):
    validate(p,rho)
    if len(set(selected))!=2 or any(i not in range(len(p)) for i in selected):
        raise ValueError('select two distinct words')
    m=sum(p[i] for i in selected)
    return rho*m+(1-rho)*m*m

def independent_weighted_enumeration(p,rho,selected):
    total=0.
    for a in range(len(p)):
        for b in range(len(p)):
            weight=(1-rho)*p[a]*p[b]
            if a==b: weight+=rho*p[a]
            if a in selected and b in selected: total+=weight
    return total

def independent_sample(p,rho,selected,seed,n=N):
    rng=random.Random(seed)
    edges=list(itertools.accumulate(p))
    def draw():
        u=rng.random()
        for i,edge in enumerate(edges):
            if u<edge: return i
        return len(p)-1
    hits=0
    for _ in range(n):
        a=draw()
        b=a if rng.random()<rho else draw()
        hits+=(a in selected and b in selected)
    return hits/n

def adversarial_counterexample(d,selected):
    words=tuple(13*(i+1) for i in range(d))
    missing=next((i for i in range(d) if i not in selected),None)
    if missing is None: return None
    return {'requested_pair':[missing,missing],
            'static_word_indices':list(selected),
            'dynamic_values':[words[missing],words[missing]],
            'available_static_values':[words[i] for i in selected],
            'mismatch_for_every_static_choice':all(words[missing]!=words[i] for i in selected)}

def evaluate(samples=True):
    out=[]
    for name,p,rho,target in regimes():
        selected=optimal_static_words(p)
        pred=analytic_coverage(p,rho,selected)
        exact=independent_weighted_enumeration(p,rho,selected)
        assert abs(pred-target)<=1e-12,(name,pred,target)
        assert abs(exact-pred)<=1e-12,(name,exact,pred)
        best=max(independent_weighted_enumeration(p,rho,s)
                 for s in itertools.combinations(range(len(p)),2))
        assert abs(best-pred)<=1e-12
        counter=adversarial_counterexample(len(p),selected)
        assert (counter is None)==(len(p)==2)
        if counter: assert counter['mismatch_for_every_static_choice']
        trials=[]
        if samples:
            for seed in SEEDS:
                observed=independent_sample(p,rho,selected,seed)
                assert abs(observed-pred)<=TOL,(name,seed,observed,pred)
                trials.append({'seed':seed,'observed':observed,
                               'absolute_error':abs(observed-pred)})
        out.append({'regime':name,'depth':len(p),'rho':rho,
                    'best_static_words':list(selected),
                    'top_two_mass':sum(p[i] for i in selected),
                    'predicted_coverage':pred,
                    'exact_enumerated_coverage':exact,
                    'predicted_uncovered_fraction':1-pred,
                    'counterexample':counter,'prospective_trials':trials})
    assert all(row['predicted_coverage']<1 for row in out if row['depth']>2)
    proof={}
    for d in (2,3,4,8,16,32):
        covered=sum(a in (0,1) and b in (0,1)
                    for a,b in itertools.product(range(d),repeat=2))
        assert covered==4
        proof[str(d)]={'total_ordered_pairs':d*d,'covered_pairs':covered,
                       'all_pairs_covered':covered==d*d,
                       'adversarial_example':adversarial_counterexample(d,(0,1))}
    return {'evidence_tier':'ANALYTICAL_AND_SYNTHETIC; NOT_PHYSICAL_OR_GPU',
            'decision':'FIXED_TWO_STATIC_WORD_READOUT_NOT_GENERALIZABLE_TO_DEPTH_GT_2',
            'parent_architecture':'V296_PAIRWISE_BANK_ADMISSION_PROVISIONAL',
            'real_workload_holdouts':'SEALED',
            'seeds':list(SEEDS),'trials_per_regime_per_seed':N,
            'absolute_error_gate':TOL,'regimes':out,
            'exhaustive_address_proof':proof}

def self_test():
    assert abs(analytic_coverage([.5,.5],.2,(0,1))-1)<1e-12
    assert abs(analytic_coverage([.5,.25,.25],0,(0,1))-.5625)<1e-12
    assert adversarial_counterexample(2,(0,1)) is None
    assert adversarial_counterexample(3,(0,1))['mismatch_for_every_static_choice']
    for p,r in [([.5,.5],-.1),([.2,.2],.2),([.5,float('nan')],.2)]:
        try: analytic_coverage(p,r,(0,1))
        except ValueError: pass
        else: raise AssertionError('invalid input accepted')
    print('DEEP_BANK_FIXED_WORD_SELF_TEST_PASS')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--evaluate',action='store_true')
    args=parser.parse_args()
    if args.self_test: self_test()
    if args.evaluate: print(json.dumps(evaluate(),indent=2,sort_keys=True))
    if not (args.self_test or args.evaluate):
        parser.error('choose --self-test or --evaluate')
