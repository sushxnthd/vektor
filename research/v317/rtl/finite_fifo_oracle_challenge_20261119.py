"""Frozen finite-FIFO bank-service challenge. See FROZEN_FINITE_FIFO_ORACLE_CHALLENGE_20261119.md.
An unfair zero-cost oracle is NOT implementable RTL, a GPU IPC result or a legal tile.
"""
import random, itertools, json
SEEDS=(11,29,47)

def schedule(queue, outcap, oracle):
    window=queue[:4]
    if oracle:
        best=()
        for n in range(min(outcap,len(window))+1):
            for ids in itertools.combinations(range(len(window)),n):
                use={}
                for i in ids:
                    for b in window[i][0]: use[b]=use.get(b,0)+1
                if all(v<=2 for v in use.values()) and len(ids)>len(best):best=ids
        return best
    use={}; selected=[]
    for i,(pair,_) in enumerate(window):
        counts=use.copy()
        for b in pair: counts[b]=counts.get(b,0)+1
        if len(selected)<outcap and all(v<=2 for v in counts.values()):
            selected.append(i);use=counts
    return tuple(selected)

def arrivals(seed,regime,cycles,rate):
    rng=random.Random(seed)
    for _ in range(cycles):
        batch=[]
        for _ in range(rate):
            if regime=='uniform16':pair=(rng.randrange(16),rng.randrange(16))
            elif regime=='uniform4':pair=(rng.randrange(4),rng.randrange(4))
            else:
                def draw():return 0 if rng.random()<.65 else 1+rng.randrange(3)
                pair=(draw(),draw())
            batch.append(pair)
        yield batch

def run(seed,regime,rate=3,outcap=4,cycles=22000,warm=2000):
    stream=list(arrivals(seed,regime,cycles,rate));results={}
    for oracle in (False,True):
        queue=[];grants=drop=admitted=0;occup=0;maxage=0;violations=0
        for t,batch in enumerate(stream):
            ids=schedule(queue,outcap,oracle)
            chosen=[queue[i] for i in ids]
            use={}
            for pair,_ in chosen:
                for b in pair:use[b]=use.get(b,0)+1
            if any(v>2 for v in use.values()) or len(ids)>outcap:violations+=1
            if t>=warm:
                grants+=len(ids)
                maxage=max(maxage,*(t-time for _,time in chosen)) if chosen else maxage
            for i in reversed(ids):queue.pop(i)
            for pair in batch:
                if len(queue)<16:
                    queue.append((pair,t))
                    if t>=warm:admitted+=1
                elif t>=warm:drop+=1
            if t>=warm:occup+=len(queue)
            assert len(queue)<=16
        results['oracle' if oracle else 'greedy']={'grants':grants,'dropped':drop,'admitted':admitted,'avg_occupancy':occup/(cycles-warm),'max_wait_age':maxage,'final_occupancy':len(queue),'violations':violations}
    a,b=results['greedy'],results['oracle']
    results['ratio']=b['grants']/a['grants'] if a['grants'] else None
    results['passes_relevance']=results['ratio']>=1.02 and b['dropped']<=a['dropped']
    return results

def main():
    cases=[('uniform16',3,4),('uniform4',3,4),('hot65',3,4),('hot65',3,2),('hot65',1,4)]
    for regime,rate,outcap in cases:
        for seed in SEEDS:
            r=run(seed,regime,rate,outcap)
            print(json.dumps({'regime':regime,'rate':rate,'outcap':outcap,'seed':seed,**r},sort_keys=True))
if __name__=='__main__':main()
