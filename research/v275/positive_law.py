#!/usr/bin/env python3
"""V275 E1 training-only model. Does not inspect frozen holdouts."""
import random,json
from collections import deque
from pathlib import Path
class Join:
 def __init__(self,indexed,latency=12):
  self.indexed=indexed;self.latency=latency;self.slots=[None]*4
  self.accept=0;self.walks=0;self.merges=0;self.stalls=0;self.completed=0;self.cmp=0
 def step(self,t,key):
  retired=False
  for i,s in enumerate(self.slots):
   if s and s[2]<=t:
    self.completed+=s[1];self.slots[i]=None;retired=True;break
  if key is None:return True
  if retired:self.stalls+=1;return False
  allowed=range(2*(key&1),2*(key&1)+2) if self.indexed else range(4)
  self.cmp+=len(allowed)
  for i in allowed:
   s=self.slots[i]
   if s and s[0]==key:
    if s[1]>=15:self.stalls+=1;return False
    self.slots[i]=(key,s[1]+1,s[2]);self.merges+=1;self.accept+=1;return True
  for i in allowed:
   if self.slots[i] is None:
    self.slots[i]=(key,1,t+self.latency);self.walks+=1;self.accept+=1;return True
  self.stalls+=1;return False

def simulate(seed,pattern,cycles=20000,arrival=0.7):
 r=random.Random(seed);idx=Join(True);cam=Join(False);queues=[deque(),deque()]
 for t in range(cycles):
  if r.random()<arrival:
   if pattern=='reuse': key=r.choice([0,1,2,3]) if r.random()<0.85 else r.randrange(256)
   elif pattern=='collision': key=2*r.randrange(128)
   elif pattern=='balanced':key=r.randrange(256)
   else:raise ValueError(pattern)
   for q in queues:q.append(key)
  for model,q in zip((idx,cam),queues):
   ok=model.step(t,q[0] if q else None)
   if ok and q:q.popleft()
 return {name:{'accepted':m.accept,'walks':m.walks,'merges':m.merges,'stalls':m.stalls,'full_tag_comparisons':m.cmp,'queued':len(q),'completed':m.completed} for name,m,q in [('indexed',idx,queues[0]),('cam',cam,queues[1])]}

def main():
 out={'evidence':'E1 training-only, no RTL simulation, no PPA','mechanism':'V275 two-set two-way in-flight page join','traces':{f'{p}_arrival_{a}':simulate(27500+i,p,arrival=a) for i,(p,a) in enumerate([(p,a) for p in ('reuse','balanced','collision') for a in (0.1,0.2,0.4,0.7)])},'holdouts_evaluated':False}
 for x in out['traces'].values():
  assert x['indexed']['walks']<=x['indexed']['accepted']
  assert x['cam']['walks']<=x['cam']['accepted']
 Path(__file__).with_name('training_results.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
