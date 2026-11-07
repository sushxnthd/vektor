#!/usr/bin/env python3
"""Independent recursive checker: no imports from the primary evaluator."""
import itertools,json,random,sys
def recursive_opt(reqs,valid,ports=2):
 counts=[0]*(max(max(a,b) for a,b in reqs)+1)
 def rec(i):
  if i==4:return 0
  best=rec(i+1);a,b=reqs[i]
  if valid>>i&1 and counts[a]+(a==b)<ports and counts[b]+(a==b)<ports:
   counts[a]+=1;counts[b]+=1
   best=max(best,1+rec(i+1))
   counts[a]-=1;counts[b]-=1
  return best
 return rec(0)
def greedy_count(reqs,valid,ports=2):
 counts={};out=0
 for i,(a,b) in enumerate(reqs):
  if not(valid>>i&1):continue
  need=2 if a==b else 1
  if counts.get(a,0)+need>ports or counts.get(b,0)+need>ports:continue
  counts[a]=counts.get(a,0)+1;counts[b]=counts.get(b,0)+1;out+=1
 return out
def run(path):
 x=json.load(open(path))
 assert x['seeds']==[1103,2207,3301] and x['batches_per_seed']==20000
 for name,v in x['regimes'].items():
  assert v['batches']==60000
  assert 0<=v['greedy_grants']<=v['oracle_grants']<=240000
  assert abs(v['mean_greedy']-v['greedy_grants']/60000)<1e-12
  assert abs(v['mean_oracle']-v['oracle_grants']/60000)<1e-12
  assert abs(v['oracle_over_greedy']-v['oracle_grants']/v['greedy_grants'])<1e-12
  assert abs(v['improvement_probability']-v['improved_batches']/60000)<1e-12
  assert abs(v['conditional_extra_grants']*v['improved_batches']-(v['oracle_grants']-v['greedy_grants']))<1e-9
 fixed={'win':([(0,1),(0,0),(1,1),(2,2)],4,(2,3)),
  'disjoint':([(0,0),(1,1),(2,2),(3,3)],4,(4,4)),
  'cap2':([(0,1),(0,0),(1,1),(2,2)],2,(2,2)),
  'onebank':([(0,0)]*4,4,(1,1))}
 for name,(reqs,cap,exp) in fixed.items():
  got=(min(cap,greedy_count(reqs,15)),min(cap,recursive_opt(reqs,15)))
  assert got==exp and got==(x['frozen'][name]['greedy'],x['frozen'][name]['oracle']),(name,got)
 n=improved=0
 for seq in itertools.product(range(2),repeat=8):
  reqs=list(zip(seq[::2],seq[1::2]))
  g=greedy_count(reqs,15);o=recursive_opt(reqs,15)
  assert o>=g and o-g<=1
  n+=1;improved+=(o>g)
 assert x['exhaustive_B2']==dict(batches=n,improved_batches=improved)
 configs=[('uniform16',16,'uniform',4,1.0),('uniform4',4,'uniform',4,1.0),
  ('hot65_16',16,'hot65',4,1.0),('hot65_16_cap2',16,'hot65',2,1.0),
  ('samebank70_16',16,'samebank70',4,1.0),('uniform16_valid60',16,'uniform',4,0.6)]
 holdout={}
 for j,(name,B,kind,cap,p) in enumerate(configs):
  rng=random.Random(900001+j);gs=os=0
  for _ in range(1000):
   def bank():
    if kind=='hot65':return 0 if rng.random()<0.65 else rng.randrange(1,B)
    return rng.randrange(B)
   reqs=[]
   for i in range(4):
    a=bank();b=a if kind=='samebank70' and rng.random()<0.70 else bank()
    reqs.append((a,b))
   valid=sum(1<<i for i in range(4) if rng.random()<p)
   gs+=min(cap,greedy_count(reqs,valid));os+=min(cap,recursive_opt(reqs,valid))
  assert os>=gs
  holdout[name]=dict(batches=1000,greedy_grants=gs,oracle_grants=os,ratio=os/gs)
 return dict(exhaustive_B2_batches=n,exhaustive_B2_improved=improved,holdout=holdout,
  decision='PASS: independent recursion and summary arithmetic; not physical signoff')
if __name__=='__main__':print(json.dumps(run(sys.argv[1]),sort_keys=True,indent=2))
