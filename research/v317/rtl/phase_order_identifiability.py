#!/usr/bin/env python3
"""Frozen V317 synthetic phase-order falsification; NOT GPU IPC or RTL."""
import json, random
from collections import deque, Counter
from functools import lru_cache
SEEDS=(137,271,809)
WARMUP=500
MEASURE=3000
FIFO_CAP=8
WINDOW=4
PORTS=2
PHASES=(((3,4),(1,4),(2,4),(0,0)),((3,1),(1,1),(3,3),(4,0)))
REGIMES=('clean','phase_flip_1pct','row_shuffle','phase_random','cap2')
POLICIES=('greedy','reverse','degree','exact_head')

def legal(reqs, mask):
    counts=Counter()
    for i,(a,b) in enumerate(reqs):
        if mask>>i&1:
            counts[a]+=1
            counts[b]+=1
            if counts[a]>PORTS or counts[b]>PORTS:return False
    return True

@lru_cache(maxsize=200000)
def choose(reqs, cap, policy):
    n=len(reqs)
    if not n:return 0
    if policy=='exact_head':
        return max((mask for mask in range(1,1<<n,2) if mask.bit_count()<=cap and legal(reqs,mask)),key=lambda m:(m.bit_count(),tuple(bool(m>>i&1) for i in range(n))))
    mask=1
    if policy=='greedy':order=range(1,n)
    elif policy=='reverse':order=range(n-1,0,-1)
    else:
        def degree(i):
            ai=set(reqs[i]);return sum(bool(ai.intersection(reqs[j])) for j in range(n) if j!=i)
        order=sorted(range(1,n),key=lambda i:(degree(i),i))
    for i in order:
        if mask.bit_count()<cap and legal(reqs,mask|(1<<i)):mask|=1<<i
    assert mask&1 and legal(reqs,mask)
    return mask

def trace_for(regime,seed):
    rng=random.Random(seed)
    out=[]; phases=[]; matches=[]
    for t in range(WARMUP+MEASURE):
        phase=(t+seed%2)%2
        if regime=='phase_flip_1pct' and rng.random()<.01:phase^=1
        if regime=='phase_random':phase=rng.randrange(2)
        row=list(PHASES[phase])
        if regime=='row_shuffle':rng.shuffle(row)
        out.append(tuple(row));phases.append(phase);matches.append(tuple(row)==PHASES[phase])
    same=sum(phases[t]==phases[t-1] for t in range(1,len(phases)))/(len(phases)-1)
    return out,dict(phase_persistence=same,canonical_order_fraction=sum(matches)/len(matches))

def replay(rows,policy,cap):
    fifo=deque(); source=deque();completed=0;offered=0;finished=0;pre=0;stalled=0;post_occ=0;maxwait=0
    for t,row in enumerate(rows):
        for pair in row:source.append((pair,t));offered+=1
        while source and len(fifo)<FIFO_CAP:
            pair,born=source.popleft();fifo.append((pair,born,t))
        if t>=WARMUP and source:stalled+=1
        reqs=tuple(e[0] for e in list(fifo)[:WINDOW]);mask=choose(reqs,cap,policy)
        kept=deque()
        for i,e in enumerate(fifo):
            if i<WINDOW and (mask>>i)&1:
                finished+=1
                if t>=WARMUP:completed+=1;maxwait=max(maxwait,t-e[2])
            else:kept.append(e)
        fifo=kept
        if t==WARMUP-1:pre=finished
        if t>=WARMUP:post_occ+=len(fifo)
        assert len(fifo)<=FIFO_CAP and offered==finished+len(fifo)+len(source)
    assert finished-pre==completed
    return dict(completed=completed,throughput=completed/MEASURE,upstream_pending=len(source),backpressure_cycles=stalled,avg_fifo=post_occ/MEASURE,max_onchip_wait=maxwait,conserved=True)

def run():
    output={}
    for regime in REGIMES:
        cap=2 if regime=='cap2' else 4
        rows=[]
        for seed in SEEDS:
            tr,diagnostic=trace_for(regime,seed)
            rows.append(dict(seed=seed,diagnostic=diagnostic,policies={p:replay(tr,p,cap) for p in POLICIES}))
        totals={p:sum(x['policies'][p]['completed'] for x in rows) for p in POLICIES}
        best=max(POLICIES[:-1],key=lambda p:(totals[p],-POLICIES.index(p)))
        ratio=totals['exact_head']/totals[best]
        output[regime]=dict(cap=cap,totals=totals,strongest_control=best,ratio=ratio,rows=rows)
    return dict(protocol='FROZEN_PHASE_ORDER_IDENTIFIABILITY_20261102.md',evidence_tier='synthetic finite FIFO only; no RTL, physical PPA or GPU IPC',seeds=SEEDS,warmup=WARMUP,measure=MEASURE,regimes=output)
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
