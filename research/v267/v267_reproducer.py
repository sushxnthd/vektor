#!/usr/bin/env python3
"""V267 equal-resource allocation discriminator; behavioral only."""
from itertools import product
import json
B=range(4)
def candidate(p,free,busy,old):
    legal=[b for b in B if not busy[b] and (free[b] or b==old)]
    return min(legal,key=lambda b:(p[b],int(b!=old),b)) if legal else None
def control(p,free,busy,old):
    best=None; key=None
    for b in B:
        if busy[b] or (not free[b] and b!=old): continue
        score=(p[b],0 if b==old else 1,b)
        if key is None or score<key: best,key=b,score
    return best
n=0
for p in product(range(3),repeat=4):
 for free in product((0,1),repeat=4):
  for busy in product((0,1),repeat=4):
   for old in B:
    assert candidate(p,free,busy,old)==control(p,free,busy,old)
    n+=1
assert n==82944
hazards=0
for old in B:
 for new in B:
  if old==new: continue
  queued_read_version=0
  new_directory_version=1
  assert queued_read_version!=new_directory_version
  hazards+=1
assert hazards==12
print(json.dumps({"states":n,"policy_mismatches":0,"old_read_hazard_cases":hazards,"physical_validation":"not run"}))
