#!/usr/bin/env python3
"""Independent V296 bank-admission oracle; E0 only."""
import itertools,json,random
def baseline(req):
    once=twice=grants=0
    for i,(valid,a,b) in enumerate(req):
        if not valid:continue
        x,y=1<<a,1<<b
        fit=not(once&x) if a==b else not(twice&x or twice&y)
        if not fit:continue
        grants|=1<<i
        if a==b:once|=x;twice|=x
        else:
            if once&x:twice|=x
            else:once|=x
            if once&y:twice|=y
            else:once|=y
    return grants
def pairwise(req):
    grants=0
    for i,(valid,a,b) in enumerate(req):
        if not valid:continue
        ha=hb=0
        for j,(_,pa,pb) in enumerate(req[:i]):
            if grants&(1<<j):
                ha+=(pa==a)+(pb==a)
                hb+=(pa==b)+(pb==b)
        if (ha==0 if a==b else ha<2 and hb<2):grants|=1<<i
    return grants
r=random.Random(296)
n=bad=0
for a,b,c,d in itertools.product(range(16),repeat=4):
    req=[(1,a,b),(1,c,d),(0,0,0),(0,0,0)]
    n+=1;bad+=baseline(req)!=pairwise(req)
for _ in range(100000):
    req=[(r.getrandbits(1),r.randrange(16),r.randrange(16)) for _ in range(4)]
    n+=1;bad+=baseline(req)!=pairwise(req)
print(json.dumps(dict(seed=296,exhaustive_two_slot=65536,random_four_slot=100000,
    total=n,mismatches=bad,evidence="E0 independent Python"),indent=2))
assert bad==0
