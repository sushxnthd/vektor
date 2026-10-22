#!/usr/bin/env python3
"""V286 independent E0 grant-count training and frozen holdout evaluator."""
import random,json,sys
B=16
def greedy(reqs):
    counts=[0]*B;grants=0
    for a,b in reqs:
        if counts[a]+(a==b)<2 and counts[b]<2:
            counts[a]+=1;counts[b]+=1;grants+=1
    return grants
def draw(rng,mode):
    ids=rng.sample(range(16),4)
    if mode=='hot_same':regs=[(0,0)]*4
    elif mode=='hot_pair':regs=[(0,1)]*4
    elif mode=='independent':regs=[(rng.randrange(16),rng.randrange(16)) for _ in range(4)]
    elif mode=='perwarp_pair':regs=[(i,(i+1)%16) for i in ids]
    elif mode=='withinwarp_collision':regs=[(rng.randrange(16),)*2 for _ in range(4)]
    elif mode=='phase_shifted':regs=[(i%4,(i+1)%4) for i in ids]
    else:raise ValueError(mode)
    return ids,regs
def mapped(ids,regs,kind):
    if kind=='identity':return regs
    if kind=='xor':return [((a^w)&15,(b^w)&15) for w,(a,b) in zip(ids,regs)]
    if kind=='add':return [((a+w)&15,(b+w)&15) for w,(a,b) in zip(ids,regs)]
    raise ValueError(kind)
def run(mode,seed,n):
    rng=random.Random(seed);total={k:0 for k in ('identity','xor','add')}
    for _ in range(n):
        ids,regs=draw(rng,mode)
        for k in total:total[k]+=greedy(mapped(ids,regs,k))
    return {'mode':mode,'seed':seed,'n':n,'totals':total,'gain_add_over_xor':total['add']/total['xor']}
if __name__=='__main__':
    if '--holdout' in sys.argv:
        tests=[('perwarp_pair',986001,10000,1.95,2.05),('hot_same',986002,10000,1,1),('independent',986003,10000,.99,1.01),('hot_pair',986004,10000,1,1)]
    else:tests=[(m,286001+i,10000,0,float('inf')) for i,m in enumerate(('hot_same','hot_pair','independent','perwarp_pair','withinwarp_collision','phase_shifted'))]
    out=[]
    for mode,seed,n,lo,hi in tests:
        row=run(mode,seed,n);row['pass']=lo<=row['gain_add_over_xor']<=hi;out.append(row)
    print(json.dumps(out,indent=2))
