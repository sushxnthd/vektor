#!/usr/bin/env python3
"""Independent V317 phase-order audit; deliberately does not import evaluator."""
import itertools,json,random,sys
from collections import defaultdict
PATTERNS=(((3,4),(1,4),(2,4),(0,0)),((3,1),(1,1),(3,3),(4,0)))
REGIMES=('clean','phase_flip_1pct','row_shuffle','phase_random','cap2')
SEEDS=(137,271,809)
POLICIES=('greedy','reverse','degree','exact_head')

def feasible(pairs,ids):
    loads=defaultdict(int)
    for i in ids:
        for b in pairs[i]:
            loads[b]+=1
            if loads[b]>2:return False
    return True

def independent_pick(pairs,cap,mode):
    n=len(pairs)
    if n==0:return set()
    if mode=='exact_head':
        opts=[]
        for k in range(1,min(cap,n)+1):
            for combo in itertools.combinations(range(1,n),k-1):
                ids={0,*combo}
                if feasible(pairs,ids):opts.append(ids)
        return max(opts,key=lambda ids:(len(ids),tuple(i in ids for i in range(n))))
    chosen={0}
    if mode=='greedy':order=list(range(1,n))
    elif mode=='reverse':order=list(range(n-1,0,-1))
    else:
        def rank(i):
            return (sum(bool(set(pairs[i])&set(pairs[j])) for j in range(n) if j!=i),i)
        order=sorted(range(1,n),key=rank)
    for i in order:
        if len(chosen)<cap and feasible(pairs,chosen|{i}):chosen.add(i)
    return chosen

def make_rows(kind,seed):
    rng=random.Random(seed)
    rows=[]
    for t in range(3500):
        phase=(t+seed%2)%2
        if kind=='phase_flip_1pct' and rng.random()<0.01:phase=1-phase
        if kind=='phase_random':phase=rng.randrange(2)
        row=list(PATTERNS[phase])
        if kind=='row_shuffle':rng.shuffle(row)
        rows.append(tuple(row))
    return rows

def replay(rows,policy,cap):
    buffer=[];backlog=[];done=0;offered=0;finished=0
    for t,row in enumerate(rows):
        backlog.extend(row);offered+=len(row)
        while backlog and len(buffer)<8:buffer.append(backlog.pop(0))
        candidates=buffer[:4]
        chosen=independent_pick(candidates,cap,policy)
        assert not candidates or 0 in chosen
        buffer=[v for i,v in enumerate(buffer) if i>=4 or i not in chosen]
        finished+=len(chosen)
        if t>=500:done+=len(chosen)
        assert offered==finished+len(buffer)+len(backlog)
    return done

def check(path):
    obj=json.load(open(path))
    assert obj['seeds']==list(SEEDS) and obj['measure']==3000
    for kind in REGIMES:
        r=obj['regimes'][kind]
        cap=2 if kind=='cap2' else 4
        for row in r['rows']:
            tr=make_rows(kind,row['seed'])
            for policy in POLICIES:
                got=replay(tr,policy,cap)
                assert got==row['policies'][policy]['completed'],(kind,row['seed'],policy,got)
        total={p:sum(row['policies'][p]['completed'] for row in r['rows']) for p in POLICIES}
        assert total==r['totals']
        assert abs(r['ratio']-total['exact_head']/max(total[p] for p in POLICIES[:-1]))<1e-12
    count=0
    for flat in itertools.product(range(3),repeat=8):
        pairs=tuple((flat[i],flat[i+1]) for i in range(0,8,2))
        for cap in (2,4):
            oracle=independent_pick(pairs,cap,'exact_head')
            assert 0 in oracle and feasible(pairs,oracle)
            for policy in POLICIES[:-1]:
                control=independent_pick(pairs,cap,policy)
                assert 0 in control and feasible(pairs,control)
                assert len(oracle)>=len(control)
        count+=1
    print(json.dumps({'audit':'PASS','independent_trace_replays':60,'exhaustive_3bank_snapshots':count,'no_gpu_ipc_claim':True}))
if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else 'research/v317/PHASE_ORDER_IDENTIFIABILITY_RESULTS_20261102.json')
