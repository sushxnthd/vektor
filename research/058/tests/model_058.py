from dataclasses import dataclass
N=4;MAX_AGE=15;AGE_LIMIT=3
@dataclass
class Entry:
 tag:int
 data:int
 rem:int
 age:int=0
class Queue:
 def __init__(self):
  self.q=[];self.locked_tag=None;self.accepted=[];self.served=[];self.stalled_last=None
 def select(self):
  if not self.q:return None
  if self.locked_tag is not None:
   matches=[i for i,e in enumerate(self.q) if e.tag==self.locked_tag]
   assert len(matches)==1
   return matches[0]
  for i,e in enumerate(self.q):
   if e.age>=AGE_LIMIT:return i
  return min(range(len(self.q)),key=lambda i:self.q[i].rem)
 def observe(self,enq_valid,out_ready):
  idx=self.select();out_valid=idx is not None
  pop=out_valid and out_ready
  in_ready=len(self.q)<N or pop
  e=self.q[idx] if out_valid else None
  return (int(in_ready),int(out_valid),e.tag if e else 0,e.data if e else 0,len(self.q))
 def step(self,enq_valid,tag,data,rem,out_ready):
  obs=self.observe(enq_valid,out_ready)
  in_ready,out_valid,otag,odata,_=obs
  idx=self.select()
  if self.stalled_last is not None:
   assert (out_valid,otag,odata)==self.stalled_last
  if out_valid and not out_ready:
   self.locked_tag=otag;self.stalled_last=(out_valid,otag,odata)
  else:self.stalled_last=None
  if out_valid and out_ready:
   e=self.q.pop(idx)
   assert e.tag==otag and e.data==odata
   self.served.append(e.tag);self.locked_tag=None
  for e in self.q:e.age=min(MAX_AGE,e.age+1)
  if enq_valid and in_ready:
   assert tag not in [e.tag for e in self.q]
   self.q.append(Entry(tag,data,rem));self.accepted.append(tag)
  assert len(self.q)<=N
  assert all(self.q[i].age>=self.q[i+1].age for i in range(len(self.q)-1))
  assert len(set(e.tag for e in self.q))==len(self.q)
  assert len(set(self.served))==len(self.served)
  assert set(self.served).issubset(set(self.accepted))
  return obs
