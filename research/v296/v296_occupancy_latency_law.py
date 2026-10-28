#!/usr/bin/env python3
"""Finite-population latency/occupancy law for V296 retiming triage.

Abstract closed-loop model only. NOT RTL, bank traces, routed evidence, or
measured GPU performance. q is independent per-ready-wave eligibility;
B is a global issue/bandwidth cap; L is cycles before a granted wave is ready.
"""
import argparse
import itertools
import json
import random
from collections import defaultdict


def advance(state, eligible, B, L):
    ready = [i for i, c in enumerate(state) if c == 0 and i in eligible]
    granted = set(ready[:B])
    nxt = tuple((L-1 if i in granted else max(0, c-1)) for i,c in enumerate(state))
    return nxt, len(granted)


def exact(N, B, L, q, tolerance=1e-13):
    if not (1 <= N <= 4 and 1 <= B <= N and 1 <= L <= 4 and 0 < q < 1):
        raise ValueError('Unsupported finite-state parameters')
    states = list(itertools.product(range(L), repeat=N))
    idx = {s:i for i,s in enumerate(states)}
    rows=[]
    for s in states:
        ready=[i for i,c in enumerate(s) if c==0]
        row=defaultdict(float)
        reward=0.0
        for mask in range(1<<len(ready)):
            chosen={ready[k] for k in range(len(ready)) if mask & (1<<k)}
            p=q**len(chosen)*(1-q)**(len(ready)-len(chosen))
            t,g=advance(s,chosen,B,L)
            row[idx[t]]+=p
            reward+=p*g
        assert abs(sum(row.values())-1)<1e-12
        rows.append((tuple(row.items()),reward))
    pi=[0.0]*len(states);pi[idx[(0,)*N]]=1.0
    for iterations in range(1,20001):
        nxt=[0.0]*len(states)
        for i,(edges,_) in enumerate(rows):
            if pi[i]:
                for j,p in edges:nxt[j]+=pi[i]*p
        error=sum(abs(x-y) for x,y in zip(nxt,pi))
        pi=nxt
        if error<tolerance:break
    else: raise ArithmeticError('Stationary distribution did not converge')
    return sum(pi[i]*row[1] for i,row in enumerate(rows)),iterations,error


def simulate(N,B,L,q,seed,cycles):
    rng=random.Random(seed)
    c=[0]*N
    grants=0
    for _ in range(cycles):
        # Independent simulator: mutate readiness after selecting eligible.
        eligible=[i for i in range(N) if c[i]==0 and rng.random()<q]
        winners=set(eligible[:B])
        grants+=len(winners)
        for i in range(N):
            if i in winners:c[i]=L-1
            elif c[i]:c[i]-=1
    return grants/cycles


def selftest():
    for q in (.2,.55,.9):
        for L in (1,2,3,4):
            t,_,_=exact(1,1,L,q)
            assert abs(t-q/(1+q*(L-1)))<1e-11,(q,L,t)
    assert abs(exact(4,1,1,.55)[0]-(1-(1-.55)**4))<1e-11
    assert abs(exact(4,4,1,.55)[0]-4*.55)<1e-11
    assert advance((0,1),{0},1,3)==((2,0),1)
    assert advance((0,0),{0,1},1,2)==((1,0),1)
    print('V296_OCCUPANCY_LATENCY_LAW_SELFTEST_PASS')


def evaluate():
    # Preselected exploratory regimes; synthetic independent Bernoulli eligibility.
    regimes=[
        ('low_population',1,1,3,.55),
        ('occupancy_limited',2,2,3,.90),
        ('bandwidth_saturated',4,1,2,.90),
        ('eligibility_sparse',4,2,2,.20),
        ('balanced',4,2,3,.55),
        ('deep_latency',4,2,4,.85),
        ('single_cycle_control',4,1,1,.55),
        ('port_rich_control',4,4,1,.55),
    ]
    out=[]
    for name,N,B,L,q in regimes:
        predicted,it,err=exact(N,B,L,q)
        observed=[simulate(N,B,L,q,seed,200000) for seed in (101,911)]
        bound=min(B,N/L,N*q)
        row=dict(name=name,N=N,B=B,L=L,q=q,exact=predicted,
                 naive_upper_bound=bound,naive_overprediction=bound-predicted,
                 monte_carlo=observed,max_absolute_error=max(abs(x-predicted) for x in observed),
                 stationary_iterations=it,stationary_l1_error=err)
        assert predicted<=bound+1e-10,row
        assert row['max_absolute_error']<=.012,row
        out.append(row)
    pairs=[]
    for name,N,B,q in [('scarce_occupancy',2,2,.9),('shared_bandwidth',4,1,.9),('sparse_eligibility',4,2,.2),('balanced',4,2,.55)]:
        a=exact(N,B,1,q)[0];b=exact(N,B,2,q)[0]
        pairs.append(dict(name=name,N=N,B=B,q=q,L1=a,L2=b,ratio=b/a,loss_percent=100*(1-b/a),necessary_clock_ratio_for_no_regression=a/b))
        assert b<=a+1e-12
    return dict(evidence_tier='exact finite-state model plus independently seeded synthetic Monte Carlo',
                model='closed-loop fixed-priority independent per-ready-wave Bernoulli eligibility',
                single_wave_law='T=q/(1+q*(L-1))',
                clock_break_even='f_new/f_old > T_L1/T_L2 to gain absolute work per second',
                necessary_bound='T <= min(B,N/L,N*q)',
                regimes=out,retiming_pairs=pairs,
                gate='No candidate timing/area repair established; no retiming throughput gain claimed',
                holdouts='existing GPU trace holdouts SEALED',
                physical=False,rtl=False,matched=False,gpu_speedup=False)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--output')
    args=p.parse_args()
    if args.self_test:selftest()
    if args.output or not args.self_test:
        data=evaluate();payload=json.dumps(data,indent=2,sort_keys=True)+'\n'
        if args.output:
            with open(args.output,'w') as f:f.write(payload)
        else:print(payload)

if __name__=='__main__':main()
