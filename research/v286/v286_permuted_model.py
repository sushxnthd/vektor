#!/usr/bin/env python3
"""V286 bit-permuted warp bank mapping; deterministic E0 workloads."""
import random,json,sys
PERM=(3,0,1,2)
def salt(w):
    return sum(((w>>PERM[i])&1)<<i for i in range(4))
def greedy(reqs):
    used=[0]*16;grants=0
    for a,b in reqs:
        if used[a]+(a==b)<2 and used[b]<2:
            used[a]+=1;used[b]+=1;grants+=1
    return grants
def draw(rng,mode):
    ids=rng.sample(range(16),4)
    if mode=='logical_wave':regs=[(w,(w+1)%16) for w in ids]
    elif mode=='logical_perm':regs=[(salt(w),(salt(w)+1)%16) for w in ids]
    elif mode=='hot_same':regs=[(0,0)]*4
    elif mode=='hot_pair':regs=[(0,1)]*4
    elif mode=='independent':regs=[(rng.randrange(16),rng.randrange(16)) for _ in ids]
    else:raise ValueError(mode)
    return ids,regs
def run(mode,seed,n):
    rng=random.Random(seed);total={'identity':0,'xor':0,'permuted':0,'add':0}
    for _ in range(n):
        ids,regs=draw(rng,mode)
        total['identity']+=greedy(regs)
        total['xor']+=greedy([((a^w)&15,(b^w)&15) for w,(a,b) in zip(ids,regs)])
        total['permuted']+=greedy([((a^salt(w))&15,(b^salt(w))&15) for w,(a,b) in zip(ids,regs)])
        total['add']+=greedy([((a+w)&15,(b+w)&15) for w,(a,b) in zip(ids,regs)])
    return {'mode':mode,'seed':seed,'n':n,'totals':total,'permuted_over_xor':total['permuted']/total['xor']}
if __name__=='__main__':
    if '--holdout' in sys.argv:
        cases=[('logical_wave',986101,10000,1.95,2.01),('logical_perm',986102,10000,.49,.52),('hot_same',986103,10000,1,1),('independent',986104,10000,.995,1.005)]
    else:
        cases=[('logical_wave',286090,10000,0,10),('logical_perm',286091,10000,0,10),('hot_same',286092,10000,0,10),('independent',286093,10000,0,10),('hot_pair',286094,10000,0,10)]
    results=[]
    for mode,seed,n,lo,hi in cases:
        x=run(mode,seed,n);x['pass']=lo<=x['permuted_over_xor']<=hi;results.append(x)
    print(json.dumps(results,indent=2))
