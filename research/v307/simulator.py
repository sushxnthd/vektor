"""V307 cheap next-bank-pressure tie-break. Synthetic issue model only.

No GPU IPC, area, or timing claims. Run --pilot only after protocol freeze.
"""
from __future__ import annotations
import argparse, json, random
from statistics import mean

WARPS, LENGTH, BANKS, ISSUE = 5, 48, 8, 3

def program(seed, regime):
    if regime not in ('W1', 'N1', 'N2'): raise ValueError(regime)
    rng = random.Random(seed)
    pairs = ((0,1), (2,3), (4,5), (6,7))
    out = []
    for w in range(WARPS):
        q = []
        for j in range(LENGTH):
            if regime == 'N1' and rng.random() < .95:
                pair = pairs[(j%4+w)%4]
            elif regime == 'N2':
                pair = (w%4*2, w%4*2+1)
            else:
                pair = tuple(rng.sample(range(BANKS),2))
            q.append((1<<pair[0])|(1<<pair[1]))
        out.append(tuple(q))
    return tuple(out)

def legal(head, queues):
    out=[]
    for s in range(1<<len(queues)):
        if s.bit_count()>ISSUE: continue
        used=0
        for w,q in enumerate(queues):
            if not (s>>w)&1: continue
            if head[w]>=len(q) or used&q[head[w]]: break
            used|=q[head[w]]
        else: out.append(s)
    return out

def advance(head,s):
    return tuple(x+((s>>w)&1) for w,x in enumerate(head))

def next_pressure(head,queues):
    counts=[0]*BANKS
    for w,q in enumerate(queues):
        if head[w]>=len(q): continue
        mask=q[head[w]]
        for b in range(BANKS): counts[b]+=((mask>>b)&1)
    return sum(max(0,c-1) for c in counts)

def priority(s): return tuple((s>>w)&1 for w in range(WARPS))

def select(head,queues,policy):
    opts=legal(head,queues)
    if policy not in ('max_now','pressure','future_tie'): raise ValueError(policy)
    best=max(s.bit_count() for s in opts)
    opts=[s for s in opts if s.bit_count()==best]
    if policy=='max_now': return max(opts,key=priority)
    if policy=='pressure':
        return max(opts,key=lambda s:(-next_pressure(advance(head,s),queues),priority(s)))
    return max(opts,key=lambda s:(max(t.bit_count() for t in legal(advance(head,s),queues)),priority(s)))

def simulate(queues,policy):
    head=(0,)*WARPS; issued=0; cycles=0; total=sum(map(len,queues))
    while issued<total:
        s=select(head,queues,policy)
        assert s and s in legal(head,queues)
        head=advance(head,s); issued+=s.bit_count(); cycles+=1
        assert cycles<=total
    assert all(head[w]==len(queues[w]) for w in range(WARPS))
    return {'cycles':cycles,'issued':issued,'rate':issued/cycles}

def experiment(seeds=(31,32,33,34)):
    data={}
    for regime in ('W1','N1','N2'):
        rows=[]
        for seed in seeds:
            q=program(seed,regime)
            d={p:simulate(q,p) for p in ('max_now','pressure','future_tie')}
            d['seed']=seed
            d['pressure_vs_future_pct']=100*(d['future_tie']['cycles']/d['pressure']['cycles']-1)
            d['pressure_vs_max_pct']=100*(d['max_now']['cycles']/d['pressure']['cycles']-1)
            rows.append(d)
        data[regime]={'rows':rows,'mean_cycles':{p:mean(r[p]['cycles'] for r in rows) for p in ('max_now','pressure','future_tie')},'mean_vs_future_pct':mean(r['pressure_vs_future_pct'] for r in rows),'mean_vs_max_pct':mean(r['pressure_vs_max_pct'] for r in rows)}
    # Freeze: >= 95% future-tie throughput, >=10% over max-now on W1; N1 <=2% regression to future-tie.
    data['survival']=(data['W1']['mean_vs_future_pct']>=-5 and data['W1']['mean_vs_max_pct']>=10 and data['N1']['mean_vs_future_pct']>=-2)
    return data

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--pilot',action='store_true');a.add_argument('--seeds',nargs='*',type=int,default=[31,32,33,34]);args=a.parse_args()
    if not args.pilot: a.error('Explicit --pilot required; holdouts not automatic')
    print(json.dumps(experiment(tuple(args.seeds)),indent=2,sort_keys=True))
