#!/usr/bin/env python3
"""V312 prospective two-choice synthetic issue-admission screen. No GPU speedup claim."""
import itertools, json, random
from functools import lru_cache

N=4
SEEDS={"hotspot":312031,"disjoint":312032,"transfer":312033}
TRIALS=100000

def feasible(head,backup,choice):
    ports=[0]*16
    for i,c in enumerate(choice):
        if not c: continue
        pair=head[i] if c==1 else backup[i]
        if pair is None: return False
        for b in pair: ports[b]+=1
        if max(ports)>2: return False
    return True

def greedy(head,backup,use_backup):
    ports=[0]*16; choice=[]
    for i in range(N):
        found=0
        for c in ((1,2) if use_backup else (1,)):
            pair=head[i] if c==1 else backup[i]
            if pair is None: continue
            p=ports.copy()
            for b in pair: p[b]+=1
            if max(p)<=2:
                found=c; ports=p; break
        choice.append(found)
    return tuple(choice)

@lru_cache(maxsize=None)
def oracle(head,backup):
    best=(-1,-1,())
    for choice in itertools.product((0,1,2),repeat=N):
        if not feasible(head,backup,choice): continue
        key=(sum(c!=0 for c in choice),sum(c==1 for c in choice),choice)
        if key>best: best=key
    return best[2]

def generate(regime,rng):
    if regime=="hotspot":
        return ((0,1),)*4,tuple((2+2*i,3+2*i) if rng.random()<.95 else None for i in range(4))
    if regime=="disjoint":
        return tuple((2*i,2*i+1) for i in range(4)),tuple((8+2*i,9+2*i) for i in range(4))
    pairs=((10,11),(12,13),(14,15),(2,3))
    return (tuple((0,1) if rng.random()<.75 else (2+2*i,3+2*i) for i in range(4)),
            tuple(pairs[i] if rng.random()<.75 else None for i in range(4)))

def states(regime):
    if regime=="disjoint":
        h,b=generate(regime,random.Random(0)); yield h,b,1.; return
    if regime=="hotspot":
        for ready in itertools.product((False,True),repeat=4):
            h=((0,1),)*4
            b=tuple((2+2*i,3+2*i) if ready[i] else None for i in range(4))
            yield h,b,.95**sum(ready)*.05**(4-sum(ready))
        return
    for hot in itertools.product((False,True),repeat=4):
        for ready in itertools.product((False,True),repeat=4):
            h=tuple((0,1) if hot[i] else (2+2*i,3+2*i) for i in range(4))
            pairs=((10,11),(12,13),(14,15),(2,3))
            b=tuple(pairs[i] if ready[i] else None for i in range(4))
            k=sum(hot)+sum(ready)
            yield h,b,.75**k*.25**(8-k)

def admissions(h,b):
    a=greedy(h,b,False); c=greedy(h,b,True); o=oracle(h,b)
    assert all(feasible(h,b,x) for x in (a,c,o))
    v=tuple(sum(z!=0 for z in x) for x in (a,c,o))
    assert v[2]>=v[1]>=v[0]
    return v

def main():
    out={"trials":TRIALS,"model":"4 slots, 16 banks, 2 ports/bank, 2 reads/instruction","regimes":{}}
    for name in SEEDS:
        predicted=[0.]*3; mass=0.; n=0
        # Analytical finite-state expectation is calculated before opening holdout RNG.
        for h,b,p in states(name):
            v=admissions(h,b)
            for i in range(3): predicted[i]+=p*v[i]
            mass+=p; n+=1
        assert abs(mass-1)<1e-10
        rng=random.Random(SEEDS[name]); totals=[0]*3
        for _ in range(TRIALS):
            v=admissions(*generate(name,rng))
            for i in range(3): totals[i]+=v[i]
        observed=[x/TRIALS for x in totals]
        gp=predicted[1]/predicted[0]; go=observed[1]/observed[0]
        op=predicted[1]/predicted[2]; oo=observed[1]/observed[2]
        assert abs(gp-go)<.02 and abs(op-oo)<.02
        if name=="hotspot": assert go>1.50 and oo>=.90
        if name=="disjoint": assert go==1 and oo==1
        out["regimes"][name]={"seed":SEEDS[name],"states":n,"predicted":predicted,"observed":observed,
                              "predicted_gain":gp,"observed_gain":go,
                              "predicted_oracle_fraction":op,"observed_oracle_fraction":oo}
    r,a,c=.35,.75,.8
    out["single_late_slot_law"]={"rejection":r,"backup_ready_conditional":a,"backup_compatible_conditional":c,
                                  "predicted_gain":1+r*a*c/(1-r)}
    print(json.dumps(out,sort_keys=True,indent=2))

if __name__=="__main__": main()
