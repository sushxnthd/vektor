#!/usr/bin/env python3
"""Combinational grant-cardinality invariant for V289 and age control."""
from itertools import product
import json
def select(valid, banks, critical, use_critical):
    grant=0
    for b in (0,1):
        candidates=[i for i in range(4) if ((valid>>i)&1) and banks[i]==b]
        if candidates:
            i=min(candidates,key=lambda x:(-((critical>>x)&1),x)) if use_critical else min(candidates)
            grant |= 1<<i
    return grant
n=0;different=0
for valid in range(16):
 for banks in product((0,1),repeat=4):
  for critical in range(16):
   g0=select(valid,banks,critical,False);g1=select(valid,banks,critical,True)
   occupied=sum(any(((valid>>i)&1) and banks[i]==b for i in range(4)) for b in (0,1))
   assert g0.bit_count()==g1.bit_count()==occupied
   assert all(not (((g1>>i)&1) and ((g1>>j)&1) and banks[i]==banks[j]) for i in range(4) for j in range(i+1,4))
   different+=g0!=g1;n+=1
print(json.dumps({"cases":n,"grant_cardinality_mismatches":0,"selection_differences":different,"evidence":"E0 independent Python model; no DAG throughput or physical evidence"},indent=2))
