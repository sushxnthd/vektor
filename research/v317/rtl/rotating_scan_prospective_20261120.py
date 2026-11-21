#!/usr/bin/env python3
"""V317 rotating scan candidate: deterministic paired finite FIFO, synthetic only."""
import random, json, argparse, math
from collections import deque
BANKS=4; PORTS=2; CAP=4; CYCLES=20000; WARMUP=2000
WEIGHTS={'uniform':(.25,)*4,'hot65':(.65,.11666666666666667,.11666666666666667,.11666666666666667),'hot85':(.85,.05,.05,.05)}

def trace(seed, regime, rate, burst=False):
    ar=random.Random(seed*1009+17); br=random.Random(seed*1009+29)
    state=0
    for t in range(CYCLES):
        if burst:
            n=3 if state else 0
            if ar.random() < (.12 if state else .08):state=1-state
        else:n=int(rate)+(ar.random()<rate%1)
        yield [tuple(br.choices(range(BANKS),WEIGHTS[regime],k=2)) for _ in range(n)]

def grants(q, phase, rotating):
    order=(0,2,1,3) if rotating and phase else (0,1,2,3)
    ports=[0]*BANKS; out=[]
    for i in order:
        if i>=len(q):continue
        a,b=q[i][1]
        needed=[0]*BANKS;needed[a]+=1;needed[b]+=1
        if all(ports[j]+needed[j]<=PORTS for j in range(BANKS)):
            out.append(i)
            for j in range(BANKS):ports[j]+=needed[j]
    assert all(x<=PORTS for x in ports)
    return out

def run(arrivals,rotating):
    q=deque(); phase=0; offered=admitted=dropped=completed=0; warm_completed=0; waits=[]; occ=0
    for t,batch in enumerate(arrivals):
        before=list(q); selected=grants(before,phase,rotating); phase^=1
        assert len(selected)==len(set(selected))
        assert 0 in selected if q else not selected
        for i in sorted(selected,reverse=True):
            born,_=q[i];del q[i];completed+=1
            if t>=WARMUP:warm_completed+=1;waits.append(t-born)
        for operands in batch:
            offered+=1
            if len(q)<CAP:q.append((t,operands));admitted+=1
            else:dropped+=1
        occ+=len(q)
        assert offered==admitted+dropped
        assert admitted==completed+len(q)
    return {'throughput':warm_completed/(CYCLES-WARMUP),'completed':completed,'offered':offered,'admitted':admitted,'dropped':dropped,'remaining':len(q),'max_wait':max(waits,default=0),'mean_wait':sum(waits)/max(1,len(waits)),'occupancy':occ/CYCLES}

def evaluate(seeds):
    rows=[]
    for seed in seeds:
        for regime in WEIGHTS:
            for rate in (1.,1.5,2.,2.5,'burst'):
                arrivals=list(trace(seed,regime,rate,rate=='burst'))
                a=run(arrivals,False);b=run(arrivals,True)
                rows.append({'seed':seed,'regime':regime,'rate':rate,'compact':a,'rotating':b,'ratio':b['throughput']/a['throughput']})
    logs=[math.log(r['ratio']) for r in rows]
    return {'n':len(rows),'geomean':math.exp(sum(logs)/len(logs)),'min_ratio':min(r['ratio'] for r in rows),'max_ratio':max(r['ratio'] for r in rows),'rows':rows}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--holdout',action='store_true');p.add_argument('--short',action='store_true');args=p.parse_args()
    seeds=range(20261201,20261217) if args.holdout else range(20261121,20261125)
    r=evaluate(seeds)
    print(json.dumps({k:v for k,v in r.items() if not args.short or k!='rows'},indent=2))
