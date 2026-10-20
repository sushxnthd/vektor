#!/usr/bin/env python3
"""V246: reproducible structural test, not PPA."""
import heapq, random, math
C,R,G=128,8,8
bits=R*G*(math.ceil(math.log2(C))+1)
h=math.ceil(bits/128)
def peak(xs):
    ev=sorted([(a,1) for a,b in xs]+[(b,-1) for a,b in xs],key=lambda x:(x[0],x[1]))
    n=m=0
    for _,d in ev: n+=d; m=max(m,n)
    assert n==0
    return m
def color(xs):
    active=[]; free=[]; used=0; slots={}
    for i in sorted(range(len(xs)),key=lambda j:xs[j]):
        a,b=xs[i]
        while active and active[0][0]<=a: heapq.heappush(free,heapq.heappop(active)[1])
        s=heapq.heappop(free) if free else used
        if s==used: used+=1
        slots[i]=s; heapq.heappush(active,(b,s))
    for i,(a,b) in enumerate(xs):
        for j,(c,d) in enumerate(xs[:i]):
            if a<d and c<b: assert slots[i]!=slots[j]
    assert used==peak(xs)
    return used
def positive(seed):
    rng=random.Random(seed)
    anchors={(r,rng.randrange(8)) for r in range(8)}
    ids=[(r,g) for r in range(8) for g in range(8)]
    others=[x for x in ids if x not in anchors]
    rng.shuffle(others)
    phase={x:(0 if k<20 else 1 if k<41 else 2) for k,x in enumerate(others)}
    return [(0,3) if x in anchors else (phase[x],phase[x]+1) for x in ids]
p=positive(246101); n=[(0,3)]*64
for label,xs in [('positive',p),('negative',n)]:
    live=peak(xs)
    whole=8*peak([(min(a for a,b in xs[r*8:(r+1)*8]),max(b for a,b in xs[r*8:(r+1)*8])) for r in range(8)])
    assert color(xs)==live
    print(label,dict(peak=live,whole_bound=C//whole,dynamic_bound=C//(live+h),static_bound=C//live,h=h))
rng=random.Random(246103)
for _ in range(1024):
    xs=[]
    for j in range(64):
        a=rng.randrange(16); xs.append((a,rng.randrange(a+1,17)))
    color(xs)
print('PASS 1024 randomized interval-coloring tests')
