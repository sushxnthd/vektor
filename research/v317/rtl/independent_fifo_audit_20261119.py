"""Independent FIFO accounting and selection audit for finite_fifo_oracle_challenge_20261119.py.
Run from same directory as target, no third-party dependencies.
Checks deterministic arrivals, independent subset enumeration, feasible grants, and
full-cycle conservation, including warmup. This is synthetic software evidence only.
"""
import importlib.util
import itertools
from collections import Counter
from pathlib import Path

TARGET=Path(__file__).with_name('finite_fifo_oracle_challenge_20261119.py')
spec=importlib.util.spec_from_file_location('fifo_target',TARGET)
target=importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)

def feasible(window,ids,cap):
    if len(ids)>cap or len(set(ids))!=len(ids) or any(i<0 or i>=len(window) for i in ids):return False
    banks=Counter(b for i in ids for b in window[i][0])
    return all(v<=2 for v in banks.values())

def independent_best(window,cap):
    return max((comb for k in range(min(cap,len(window))+1)
                for comb in itertools.combinations(range(len(window)),k)
                if feasible(window,comb,cap)),key=lambda x:(len(x),tuple(-i for i in x)))

def audit(seed,regime,rate,cap,cycles=22000,warm=2000):
    stream=list(target.arrivals(seed,regime,cycles,rate))
    assert stream==list(target.arrivals(seed,regime,cycles,rate))
    assert all(len(batch)==rate for batch in stream)
    results={}
    for oracle in (False,True):
        q=[];grants=admitted=dropped=0;total_grants=total_admitted=total_dropped=0
        measured_occupancy=0;maximum_age=0
        for t,batch in enumerate(stream):
            window=q[:4]
            ids=target.schedule(q,cap,oracle)
            assert feasible(window,ids,cap),(regime,seed,oracle,t,ids,window)
            if oracle: assert ids==independent_best(window,cap),(regime,seed,t,ids,window)
            if t>=warm:
                grants+=len(ids)
                maximum_age=max(maximum_age,max((t-q[i][1] for i in ids),default=0))
            total_grants+=len(ids)
            for i in sorted(ids,reverse=True):q.pop(i)
            for pair in batch:
                if len(q)<16:
                    q.append((pair,t));total_admitted+=1
                    if t>=warm:admitted+=1
                else:
                    total_dropped+=1
                    if t>=warm:dropped+=1
            assert 0<=len(q)<=16
            assert total_admitted-total_grants==len(q)
            assert total_admitted+total_dropped==(t+1)*rate
            if t>=warm:measured_occupancy+=len(q)
        results['oracle' if oracle else 'greedy']={
            'grants':grants,'admitted':admitted,'dropped':dropped,
            'avg_occupancy':measured_occupancy/(cycles-warm),
            'max_wait_age':maximum_age,'final_occupancy':len(q),'violations':0}
    original=target.run(seed,regime,rate,cap,cycles,warm)
    for policy in ('greedy','oracle'):
        for key,value in results[policy].items():
            assert original[policy][key]==value,(regime,seed,policy,key,original[policy][key],value)
    assert original['ratio']==results['oracle']['grants']/results['greedy']['grants']
    assert original['passes_relevance']==(original['ratio']>=1.02 and results['oracle']['dropped']<=results['greedy']['dropped'])
    return original['ratio'],results['oracle']['dropped']-results['greedy']['dropped']

if __name__=='__main__':
    for regime,rate,cap in [('uniform16',3,4),('uniform4',3,4),('hot65',3,4),('hot65',3,2),('hot65',1,4)]:
        for seed in (11,29,47):
            ratio,drop_delta=audit(seed,regime,rate,cap)
            print(f'PASS {regime} rate={rate} cap={cap} seed={seed} ratio={ratio:.6f} oracle_drop_delta={drop_delta}')
    print('PASS all 15 cases; synthetic checker only')
