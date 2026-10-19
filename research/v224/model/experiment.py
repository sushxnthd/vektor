#!/usr/bin/env python3
import random,json
from collections import deque
from pathlib import Path
def make(seed,n,kind):
 r=random.Random(seed); out=[]
 for _ in range(n):
  if kind=="two_zero": keep=set(r.sample(range(4),2))
  elif kind=="nonzero": keep=set(range(4))
  elif kind=="allzero": keep=set()
  else: keep={i for i in range(4) if r.random()<.5}
  out.append(tuple((r.getrandbits(32) or 1) if i in keep else 0 for i in range(4)))
 return out
def sim(lines,mode,interval,credits=128,latency=4):
 sizes=[1+(sum(v!=0 for v in line) if mode=="sector" else 4*int(any(line))) for line in lines]
 n=len(lines);sub=fin=link=left=t=next_finish=0;done=deque()
 while fin<n:
  if sub<n and sub-fin<credits: sub+=1
  if left==0 and link<sub: left=sizes[link]
  if left:
   left-=1
   if left==0: done.append(t+latency);link+=1
  if done and done[0]<=t and t>=next_finish:
   done.popleft();fin+=1;next_finish=t+interval
  t+=1
  assert t<n*(max(sizes)+interval+latency+3)*3
 return dict(cycles=t,flits=sum(sizes),lines=n,rate=n/t)
def main():
 cfg=[("frozen_positive",22419,"two_zero",1),("frozen_negative",22420,"nonzero",1),
      ("completion_limited",22419,"two_zero",10),("divergent",22421,"divergent",1),
      ("allzero",22422,"allzero",1),("compute_limited",22419,"two_zero",20)]
 rows=[]
 for name,seed,kind,interval in cfg:
  lines=make(seed,4096,kind);b=sim(lines,"line",interval);s=sim(lines,"sector",interval)
  rows.append(dict(workload=name,seed=seed,kind=kind,completion_interval=interval,
                   baseline=b,candidate=s,gain=b["cycles"]/s["cycles"]-1))
 assert rows[0]["gain"]>.60
 assert abs(rows[1]["gain"])<.001
 assert abs(rows[2]["gain"])<.01
 assert all(r["candidate"]["flits"]<=r["baseline"]["flits"] for r in rows)
 p=Path("research/v224/evidence/results.json");p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(rows,indent=2)+"\n")
 for r in rows: print(r["workload"],round(100*r["gain"],4),r["candidate"]["flits"],r["baseline"]["flits"])
if __name__=="__main__": main()
