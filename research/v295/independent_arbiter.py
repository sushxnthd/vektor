#!/usr/bin/env python3
"""Independent bank-port occupancy oracle; E0 only, not STA."""
import itertools,json,random
def baseline(req):
    once=twice=grant=0
    for s,(v,a,b) in enumerate(req):
        if not v: continue
        x,y=1<<a,1<<b
        ok=not (once&x) if a==b else not (twice&x or twice&y)
        if not ok: continue
        grant|=1<<s
        if a==b: once|=x;twice|=x
        else:
            if once&x: twice|=x
            else: once|=x
            if once&y: twice|=y
            else: once|=y
    return grant
def onehot(req):
    once=twice=grant=0
    for s,(v,a,b) in enumerate(req):
        if not v: continue
        x,y=1<<a,1<<b
        fit=not (once&x) if x&y else not (twice&x or twice&y)
        if not fit: continue
        grant|=1<<s
        if x&y: once|=x;twice|=x
        else: twice|=once&(x|y);once|=x|y
    return grant
def main():
    n=bad=0
    for a,b,c,d in itertools.product(range(16),repeat=4):
        req=[(1,a,b),(1,c,d),(0,0,0),(0,0,0)]
        n+=1;bad+=baseline(req)!=onehot(req)
    r=random.Random(295)
    for _ in range(100000):
        req=[(r.getrandbits(1),r.randrange(16),r.randrange(16)) for s in range(4)]
        n+=1;bad+=baseline(req)!=onehot(req)
    print(json.dumps({"seed":295,"exhaustive_two_slot":65536,
        "random_four_slot":100000,"total":n,"mismatches":bad,
        "evidence":"E0 Python model only"},indent=2))
    assert bad==0
if __name__=="__main__":main()
