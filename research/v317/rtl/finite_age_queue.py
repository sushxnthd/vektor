#!/usr/bin/env python3
"""Finite FIFO age-head bank-port scheduling: synthetic service study, not RTL or GPU IPC.

The two controllers consume the same *offered* trace, each with independent finite
backpressure. They differ only in selecting an age-head-containing feasible subset
of the oldest four resident requests. Deterministic oldest-first tie-breaking.
"""
import json, random
from collections import Counter, deque

WINDOW=4
PORTS=2
QUEUE=8
WARMUP=3000
MEASURE=12000
SEEDS=(42011,42013,42017)
SCENARIOS=(
    ('uniform16',16,'uniform',4,4),
    ('hot65_16',16,'hot65',4,4),
    ('structured4',4,'structured',4,4),
    ('structured4_cap2',4,'structured',2,4),
    ('uniform16_lowload',16,'uniform',4,1),
)

def feasible(reqs,mask):
    usage=Counter()
    for i,(a,b) in enumerate(reqs):
        if mask>>i & 1:
            usage[a]+=1;usage[b]+=1
            if usage[a]>PORTS or usage[b]>PORTS:return False
    return True

def choose(reqs,cap,mode):
    n=len(reqs)
    if not n:return 0
    if mode=='greedy':
        mask=0
        for i in range(n):
            if mask.bit_count()>=cap:break
            if feasible(reqs,mask|(1<<i)):mask|=1<<i
        return mask
    best=0
    for mask in range(1,1<<n,2):
        if mask.bit_count()>cap or not feasible(reqs,mask):continue
        if mask.bit_count()>best.bit_count() or (mask.bit_count()==best.bit_count() and tuple(bool(mask>>i&1) for i in range(n))>tuple(bool(best>>i&1) for i in range(n))):
            best=mask
    assert best & 1
    return best

def offered_trace(name,B,kind,arrival,seed,cycles):
    rng=random.Random(seed)
    if kind=='structured':
        pattern=((0,0),(1,1),(1,2),(1,2))
        return [[pattern[(t*arrival+j)%4] for j in range(arrival)] for t in range(cycles)]
    def bank():
        if kind=='hot65':return 0 if rng.random()<.65 else rng.randrange(1,B)
        return rng.randrange(B)
    return [[(bank(),bank()) for _ in range(arrival)] for _ in range(cycles)]

def simulate(trace,cap,mode):
    q=deque();upstream=deque();accepted=completed=blocked=0
    warm_completed=0;waits=[];e2e_waits=[];occ=0;idle=0;grants=0
    for t,arrivals in enumerate(trace):
        # A common offered trace feeds each scheduler's separate upstream backlog.
        # A full FIFO blocks admission rather than dropping requests. The external
        # backlog is not hardware and is never counted as on-chip buffering.
        for req in arrivals: upstream.append((req,t))
        while upstream and len(q)<QUEUE:
            req,offered_t=upstream.popleft();q.append((req,offered_t,t));accepted+=1
        if t>=WARMUP and upstream:blocked+=1
        heads=[x[0] for x in list(q)[:WINDOW]]
        mask=choose(heads,cap,mode)
        selected=[i for i in range(len(heads)) if mask>>i&1]
        if not selected and q:raise AssertionError('no progress')
        retained=deque()
        for i,item in enumerate(q):
            if i in selected:
                completed+=1
                if t>=WARMUP:
                    waits.append(t-item[2]);e2e_waits.append(t-item[1])
            else:retained.append(item)
        q=retained
        assert len(q)<=QUEUE
        if t>=WARMUP:
            occ+=len(q);grants+=len(selected)
            if not selected:idle+=1
        else:warm_completed=completed
    assert accepted==completed+len(q)
    return dict(completed=completed-warm_completed,throughput=grants/MEASURE,
        accepted=accepted,backpressure_cycles=blocked,queue_residual=len(q),
        upstream_pending=len(upstream),
        mean_post_service_queue=occ/MEASURE,
        mean_wait=sum(waits)/len(waits) if waits else 0,
        p99_wait=sorted(waits)[min(len(waits)-1,int(.99*len(waits))) ] if waits else 0,
        max_wait=max(waits) if waits else 0,
        p99_e2e_wait=sorted(e2e_waits)[min(len(e2e_waits)-1,int(.99*len(e2e_waits)))] if e2e_waits else 0,
        idle_cycles=idle,
        conservation_ok=(accepted==completed+len(q)))

def run():
    out={}
    for name,B,kind,cap,arrival in SCENARIOS:
        rows=[]
        for seed in SEEDS:
            trace=offered_trace(name,B,kind,arrival,seed,WARMUP+MEASURE)
            g=simulate(trace,cap,'greedy');h=simulate(trace,cap,'head')
            rows.append(dict(seed=seed,greedy=g,head=h))
        gsum=sum(r['greedy']['completed'] for r in rows)
        hsum=sum(r['head']['completed'] for r in rows)
        out[name]=dict(rows=rows,ratio=hsum/gsum,greedy_completed=gsum,head_completed=hsum,
            max_p99_wait_increase=max(r['head']['p99_wait']-r['greedy']['p99_wait'] for r in rows),
            max_head_wait=max(r['head']['max_wait'] for r in rows))
    return dict(model='finite eight-entry FIFO with four-head window; upstream holds blocked requests (unbounded offered workload source, not hardware); synthetic not RTL',
        seeds=SEEDS,warmup=WARMUP,measured_cycles=MEASURE,regimes=out)

if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
