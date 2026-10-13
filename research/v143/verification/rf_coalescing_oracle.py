#!/usr/bin/env python3
"""Independent exhaustive combinational 3-source request/response oracle."""
import itertools
def req(tags,missing,valid):
 return tuple(bool(valid and missing[i] and all(not missing[j] or tags[j]!=tags[i] for j in range(i))) for i in range(3))
def rsp(tags,missing,return_mask,values):
 return tuple(next((values[j] for j in range(3) if return_mask[j] and tags[j]==tags[i]),None) if missing[i] else None for i in range(3))
count=0
for tags in itertools.product(range(3),repeat=3):
 for m in itertools.product((0,1),repeat=3):
  for v in (0,1):
   q=req(tags,m,v)
   assert sum(q)==(len({tags[i] for i in range(3) if m[i]}) if v else 0)
   for ret in itertools.product((0,1),repeat=3):
    values=[100,200,300]
    a=rsp(tags,m,ret,values)
    for i in range(3):
     matches=[j for j in range(3) if ret[j] and tags[j]==tags[i]]
     assert a[i]==(values[matches[0]] if matches and m[i] else None)
    count+=1
print("V143 PASS:",count,"independent abstract request/response cases")
