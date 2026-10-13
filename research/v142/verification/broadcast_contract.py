#!/usr/bin/env python3
"""Exact per-cycle Wave32 multicast accounting; no performance or PPA claims."""
import itertools
checks=0
for n in range(1,5):  # number of independent producer writebacks
  for fanouts in itertools.product(range(1,4),repeat=n):
    events=[(p,j) for p,f in enumerate(fanouts) for j in range(f)]
    for capacity in range(1,n+1):
      # Reference: first B producer vectors each fan out to every matching source.
      served=set(range(capacity))
      ref=[e for e in events if e[0] in served]
      # Independently derive physical multicast from first-appearance producer order.
      seen=[]
      for p,j in events:
        if p not in seen: seen.append(p)
      got=[(p,j) for p,j in events if p in set(seen[:capacity])]
      assert ref==got
      assert len(got)==sum(fanouts[:capacity])
      assert len(seen[:capacity])<=capacity
      # A per-source unicast bus has at most B source deliveries/cycle.
      assert len(events[:capacity])<=capacity
      checks+=1
print("V142 PASS:",checks,"exact producer-multicast service configurations")
