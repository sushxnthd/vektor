#!/usr/bin/env python3
"""Frozen four-slot age-head-preserving oracle; combinational bound, not GPU IPC."""
import itertools, json, random
from collections import Counter
SEEDS=(4127,6151,8111)
N=10000
SCENARIOS=(('uniform16',16,'uniform',4),('uniform4',4,'uniform',4),('hot65_16',16,'hot65',4),('hot65_16_cap2',16,'hot65',2),('samebank70_16',16,'samebank70',4))
CONTROLS={'head_blocker':([(0,1),(0,0),(1,1),(2,2)],4,(2,2,3)), 'disjoint':([(0,0),(1,1),(2,2),(3,3)],4,(4,4,4))}
def fits(reqs,mask):
    usage=Counter()
    for i,(a,b) in enumerate(reqs):
        if (mask>>i)&1:
            usage[a]+=1;usage[b]+=1
            if usage[a]>2 or usage[b]>2: return False
    return True
def service(reqs,cap):
    greedy=0
    for i in range(4):
        if fits(reqs,greedy|(1<<i)): greedy|=1<<i
    possible=[m for m in range(16) if fits(reqs,m)]
    head=max((m.bit_count() for m in possible if m&1))
    unbounded=max(m.bit_count() for m in possible)
    return min(cap,greedy.bit_count()),min(cap,head),min(cap,unbounded)
def sample(rng,B,kind):
    def bank():
        if kind=='hot65': return 0 if rng.random()<.65 else rng.randrange(1,B)
        return rng.randrange(B)
    req=[]
    for _ in range(4):
        a=bank(); b=a if kind=='samebank70' and rng.random()<.70 else bank()
        req.append((a,b))
    return req
def aggregate(rows):
    gs=hs=us=head_bypass=improved=0
    for g,h,u in rows:
        assert 0<=g<=h<=u<=4,(g,h,u)
        gs+=g;hs+=h;us+=u
        head_bypass+=int(u>h)
        improved+=int(h>g)
    n=len(rows)
    return dict(batches=n,greedy_grants=gs,head_preserving_grants=hs,unrestricted_grants=us,
      head_over_greedy=hs/gs,unrestricted_over_greedy=us/gs,
      head_gain_probability=improved/n,unrestricted_head_bypass_probability=head_bypass/n,
      exact_head_gain_identity=1+(hs-gs)/gs)
def run():
    controls={}
    for name,(q,k,expected) in CONTROLS.items():
        got=service(q,k)
        assert got==expected,(name,got,expected)
        controls[name]=dict(greedy=got[0],head_preserving=got[1],unrestricted=got[2])
    regimes={}
    for j,(name,B,kind,cap) in enumerate(SCENARIOS):
        rows=[]
        for seed in SEEDS:
            rng=random.Random(seed*100+j)
            rows.extend(service(sample(rng,B,kind),cap) for _ in range(N))
        regimes[name]=aggregate(rows)
    exhaustive={}
    for B in (2,4):
        rows=[]
        for x in itertools.product(range(B),repeat=8):
            q=list(zip(x[::2],x[1::2]))
            rows.append(service(q,4))
        exhaustive['B'+str(B)]=aggregate(rows)
    return dict(protocol='FROZEN_HEAD_PRESERVING_BANK_SERVICE_20261102.md',seeds=list(SEEDS),batches_per_seed=N,
       evidence_tier='synthetic age-head-preserving combinational oracle, not starvation-free RTL or GPU IPC',
       controls=controls,regimes=regimes,exhaustive=exhaustive)
if __name__=='__main__': print(json.dumps(run(),sort_keys=True,indent=2))
