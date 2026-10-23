#!/usr/bin/env python3
"""Independent E0 V292 sector-packer comparator; no electrical claims."""
import random, json
R=random.Random(29220261023)
def overlay(a,b,credits):
    aa=credits>0
    ab=credits>1 and not(a&b)
    return (aa,ab,(a if aa else 0),(b if ab else 0))
def sector_packer(a,b,credits):
    occupancy=0
    accepted=[]
    for m in (a,b):
        if len(accepted)>=credits: break
        if m&occupancy: break
        accepted.append(m)
        occupancy|=m
    return (len(accepted)>0,len(accepted)>1,
            accepted[0] if accepted else 0,
            accepted[1] if len(accepted)>1 else 0)
def check(a,b,credits):
    x=overlay(a,b,credits)
    y=sector_packer(a,b,credits)
    assert x==y,(x,y)
    return int(x[0])+int(x[1])
count=0
for a in range(256):
    for b in range(256):
        check(a,b,2);count+=1
results={}
for name,q,credits in [('sparse',.08,2),('dense',.70,2),('single_credit',.08,1),('train20',.2,2),('train50',.5,2)]:
    total=0
    for _ in range(40000):
        a=sum((R.random()<q)<<i for i in range(32))
        b=sum((R.random()<q)<<i for i in range(32))
        total+=check(a,b,credits)
        count+=1
    results[name]=total/40000
print(json.dumps({'evidence':'E0','checks':count,'mismatches':0,
                  'packets_per_beat':results,'matched_gain':1.0},indent=2))
