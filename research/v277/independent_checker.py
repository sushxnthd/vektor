#!/usr/bin/env python3
import json,random
class Cache:
 def __init__(self,confidence):self.c=confidence;self.tag=None;self.val=None;self.conf=0;self.reads=0
 def invalidate(self,t):
  if self.tag==t:self.tag=None;self.conf=0
 def access(self,t,mem):
  if self.tag==t:
   v=self.val
   if self.c:self.conf=min(3,self.conf+1)
  else:
   self.reads+=1;v=mem[t]
   if self.c and self.conf>=2:self.conf-=1
   else:self.tag=t;self.val=v;self.conf=0
  assert v==mem[t]
  return v
r=random.Random(277770);mem={i:r.getrandbits(32) for i in range(32)}
a=Cache(True);b=Cache(False);checks=0;writes=0
for i in range(100000):
 t=r.randrange(32)
 if r.random()<.06:
  mem[t]=r.getrandbits(32);a.invalidate(t);b.invalidate(t);writes+=1
 else:
  assert a.access(t,mem)==b.access(t,mem)==mem[t];checks+=1
print(json.dumps({'reads_checked':checks,'writes':writes,'stale_reads':0,'candidate_rf_reads':a.reads,'lru_rf_reads':b.reads}))
