#!/usr/bin/env python3
"""Independent recursive audit of finite age-head service; does not import evaluator."""
import json, random, sys
from collections import deque
from itertools import product

EXPECTED_SEEDS=(42011,42013,42017)
REGIMES=(('uniform16',16,'uniform',4,4),('hot65_16',16,'hot65',4,4),
         ('structured4',4,'structured',4,4),('structured4_cap2',4,'structured',2,4),
         ('uniform16_lowload',16,'uniform',4,1))

def exact(q,k):
    # Independent recursion over skip/take decisions, with bank usage array.
    n=len(q);banks=max(max(x) for x in q)+1 if n else 0
    counts=[0]*banks
    masks=[]
    def recurse(i,mask):
        if i==n:
            masks.append(mask);return
        recurse(i+1,mask)
        a,b=q[i]
        if mask.bit_count()>=k or counts[a]+(2 if a==b else 1)>2 or (a!=b and counts[b]>=2):return
        counts[a]+=1;counts[b]+=1
        recurse(i+1,mask|(1<<i))
        counts[a]-=1;counts[b]-=1
    recurse(0,0)
    g=0
    for i,(a,b) in enumerate(q):
        candidate=g|(1<<i)
        if candidate in masks:g=candidate
    if not n:return 0,0
    valid=[m for m in masks if m&1]
    assert valid
    best=max(valid,key=lambda m:(m.bit_count(),tuple(bool(m>>i&1) for i in range(n))))
    return g,best

def make_trace(B,kind,arr,seed,cycles):
    rng=random.Random(seed)
    if kind=='structured':
        pat=((0,0),(1,1),(1,2),(1,2))
        return [[pat[(t*arr+j)%4] for j in range(arr)] for t in range(cycles)]
    def bank():
        if kind=='hot65':return 0 if rng.random()<.65 else rng.randrange(1,B)
        return rng.randrange(B)
    return [[(bank(),bank()) for _ in range(arr)] for _ in range(cycles)]

def replay(trace,k,which):
    fifo=deque();src=deque();total_offered=total_admitted=total_completed=0
    measured=0;pre=0;post_occupancy=0;waits=[];e2e=[];stalled=0;idle=0
    for t,offers in enumerate(trace):
        for pair in offers:src.append((pair,t));total_offered+=1
        while src and len(fifo)<8:
            pair,born=src.popleft();fifo.append((pair,born,t));total_admitted+=1
        if t>=3000 and src:stalled+=1
        q=[e[0] for e in list(fifo)[:4]]
        g,h=exact(q,k);mask=g if which=='greedy' else h
        assert not fifo or mask&1
        new=deque()
        for i,item in enumerate(fifo):
            if i<4 and mask>>i&1:
                total_completed+=1
                if t>=3000:
                    measured+=1;waits.append(t-item[2]);e2e.append(t-item[1])
            else:new.append(item)
        fifo=new
        assert len(fifo)<=8
        if t>=3000:
            post_occupancy+=len(fifo)
            idle+=int(mask==0)
        else:pre=total_completed
        assert total_offered==total_completed+len(fifo)+len(src)
    assert total_admitted==total_completed+len(fifo)
    assert max(waits,default=0)<=7
    def p99(xs):return sorted(xs)[min(len(xs)-1,int(.99*len(xs)))] if xs else 0
    return dict(completed=total_completed-pre,throughput=measured/12000,
      accepted=total_admitted,backpressure_cycles=stalled,queue_residual=len(fifo),
      upstream_pending=len(src),mean_post_service_queue=post_occupancy/12000,
      mean_wait=sum(waits)/len(waits) if waits else 0,p99_wait=p99(waits),
      max_wait=max(waits,default=0),p99_e2e_wait=p99(e2e),idle_cycles=idle,
      conservation_ok=True)

def audit(path):
    data=json.load(open(path));assert tuple(data['seeds'])==EXPECTED_SEEDS
    assert data['warmup']==3000 and data['measured_cycles']==12000
    # Complete independent exhaustive combinational audit, 65,536 B4 cases.
    counts={}
    for k in (2,4):
        totals=[0,0];cases=0
        for x in product(range(4),repeat=8):
            q=list(zip(x[::2],x[1::2]))
            g,h=exact(q,k)
            assert g.bit_count()<=h.bit_count()
            totals[0]+=g.bit_count();totals[1]+=h.bit_count();cases+=1
        counts[str(k)]=dict(cases=cases,greedy=totals[0],head=totals[1])
    assert counts['2']['greedy']==counts['2']['head']
    validated={}
    for name,B,kind,k,arr in REGIMES:
        row=data['regimes'][name]
        assert len(row['rows'])==3
        for entry in row['rows']:
            seed=entry['seed'];assert seed in EXPECTED_SEEDS
            trace=make_trace(B,kind,arr,seed,15000)
            for which in ('greedy','head'):
                got=replay(trace,k,which)
                want=entry[which]
                for key in got:
                    if isinstance(got[key],float):assert abs(got[key]-want[key])<1e-9,(name,seed,which,key,got[key],want[key])
                    else:assert got[key]==want[key],(name,seed,which,key,got[key],want[key])
        g=sum(x['greedy']['completed'] for x in row['rows']);h=sum(x['head']['completed'] for x in row['rows'])
        assert row['greedy_completed']==g and row['head_completed']==h
        assert abs(row['ratio']-h/g)<1e-12
        validated[name]=dict(greedy=g,head=h,ratio=h/g)
    return dict(audit='PASS: independent full-trace replay, conservation, 65536-case exact recursion, on-chip wait <=7',exact=counts,regimes=validated)

if __name__=='__main__':print(json.dumps(audit(sys.argv[1]),indent=2,sort_keys=True))
