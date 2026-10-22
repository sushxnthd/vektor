#!/usr/bin/env python3
"""V277 deterministic training, no holdouts imported."""
import json
class Cache:
 def __init__(self,policy):self.policy=policy;self.tag=None;self.conf=0;self.hits=0;self.misses=0
 def access(self,t):
  if t==self.tag:
   self.hits+=1
   if self.policy=='confidence':self.conf=min(3,self.conf+1)
  else:
   self.misses+=1
   if self.policy=='confidence' and self.conf>=2:self.conf-=1
   else:self.tag=t;self.conf=0
def trace(R,K,phases=40):
 for p in range(phases):
  for e in range(K):
   for _ in range(R):yield 100000+p
   yield 200000+p*K+e
def run(R,K):
 a=Cache('confidence');b=Cache('lru')
 for t in trace(R,K):a.access(t);b.access(t)
 return {'R':R,'K':K,'confidence_misses':a.misses,'lru_misses':b.misses,'saved_reads':b.misses-a.misses,'read_reduction':(b.misses-a.misses)/b.misses}
if __name__=='__main__':
 out=[run(R,K) for R in (1,2,3,4,6,8,12) for K in (1,2,3,4,8,16,32)]
 assert next(x for x in out if x['R']==4 and x['K']==8)['saved_reads']==241
 assert next(x for x in out if x['R']==4 and x['K']==1)['saved_reads']==-20
 print(json.dumps(out,indent=2))
