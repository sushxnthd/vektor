#!/usr/bin/env python3
"""Exhaustive matched-placement discriminator; no frozen holdouts read."""
import itertools,json
from pathlib import Path
out={"states":0,"legal":0,"same_full_comparisons":0,"cam_only_admissions":0,"indexed_only_admissions":0}
for occ in itertools.product((0,1),repeat=4):
 for tag in itertools.product((0,1),repeat=4):
  for reqset in (0,1):
   out["states"]+=1
   if any(occ[j] and tag[j]!=j//2 for j in range(4)):continue
   out["legal"]+=1
   ix=[j for j in range(4) if j//2==reqset]
   a=sum(occ[j] for j in ix)
   b=sum(occ[j] and tag[j]==reqset for j in range(4))
   assert a==b
   out["same_full_comparisons"]+=1
   i=any(not occ[j] for j in ix)
   c=any(not v for v in occ)
   out["cam_only_admissions"]+=int(c and not i)
   out["indexed_only_admissions"]+=int(i and not c)
assert out["legal"]==out["same_full_comparisons"]
assert out["indexed_only_admissions"]==0
Path(__file__).with_name("run22_equal_resource.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
