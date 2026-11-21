#!/usr/bin/env python3
"""V317 finite-buffer prospective stress gate; synthetic, not RTL/physical evidence.
Policies: strict scan greedy and oldest-protected max-cardinality (zero-cost oracle).
Both have identical FIFO capacity, two reads/request, two ports/bank.
"""
import itertools, random, json
from collections import deque

BANKS=4; CAP=4; PORTS=2; CYCLES=20000; WARMUP=2000
SEEDS=(20261121,20261122,20261123,20261124)
REGIMES={'uniform':(0.25,0.25,0.25,0.25),'hot65':(0.65,0.11666666666666667,0.11666666666666667,0.11666666666666667),'hot85':(0.85,0.05,0.05,0.05)}

def feasible(q, selected):
    count=[0]*BANKS
    for i in selected:
        for b in q[i][1]:
            count[b]+=1
            if count[b]>PORTS:return False
    return True

def choose(q, policy):
    if not q:return ()
    if policy=='greedy':
        out=[]
        for i in range(len(q)):
            if feasible(q,out+[i]):out.append(i)
        return tuple(out)
    if policy=='protected':
        valid=(x for n in range(1,len(q)+1) for x in itertools.combinations(range(len(q)),n) if 0 in x and feasible(q,x))
        return max(valid,key=lambda x:(len(x),tuple(-i for i in x)))
    raise ValueError(policy)

def simulate(seed, regime, policy, arrival_rate):
    rng=random.Random(seed); q=deque(); completed=0; dropped=0; waits=[]; offered=0
    weights=REGIMES[regime]; arrivals=[]
    for t in range(CYCLES):
        n=int(arrival_rate)+(rng.random() < arrival_rate%1)
        arrivals.append([tuple(rng.choices(range(BANKS),weights,k=2)) for _ in range(n)])
    for t, batch in enumerate(arrivals):
        selected=choose(list(q),policy)
        for i in reversed(selected):
            born,_=q[i]
            del q[i]
            if t>=WARMUP:
                completed+=1;waits.append(t-born)
        for operands in batch:
            if t>=WARMUP:offered+=1
            if len(q)<CAP:q.append((t,operands))
            elif t>=WARMUP:dropped+=1
    assert all(x>=0 for x in waits)
    return {'throughput':completed/(CYCLES-WARMUP),'drop_rate':dropped/max(1,offered),'max_wait':max(waits,default=0),'mean_wait':sum(waits)/max(1,len(waits))}

def main():
    rows=[]
    for regime in REGIMES:
        for rate in (1.0,1.5,2.0,2.5):
            for seed in SEEDS:
                g=simulate(seed,regime,'greedy',rate)
                p=simulate(seed,regime,'protected',rate)
                rows.append({'regime':regime,'arrival_rate':rate,'seed':seed,'greedy':g,'protected':p,'ratio':p['throughput']/g['throughput'] if g['throughput'] else None})
    print(json.dumps({'protocol':{'banks':BANKS,'capacity':CAP,'ports':PORTS,'cycles':CYCLES,'warmup':WARMUP,'seeds':SEEDS,'regimes':REGIMES,'rates':(1.0,1.5,2.0,2.5)},'results':rows},indent=2))
if __name__=='__main__':main()
