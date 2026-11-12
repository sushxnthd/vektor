#!/usr/bin/env python3
"""Exact four-slot 2R bank-service headroom; an unfair oracle, not a scheduler."""
import itertools, json, random
from collections import Counter
SEEDS=(1103,2207,3301)
N=20000
SCENARIOS=(
 ('uniform16',16,'uniform',4,1.0),('uniform4',4,'uniform',4,1.0),
 ('hot65_16',16,'hot65',4,1.0),('hot65_16_cap2',16,'hot65',2,1.0),
 ('samebank70_16',16,'samebank70',4,1.0),('uniform16_valid60',16,'uniform',4,0.6))
FROZEN={
 'win':([(0,1),(0,0),(1,1),(2,2)],4,(2,3)),
 'disjoint':([(0,0),(1,1),(2,2),(3,3)],4,(4,4)),
 'cap2':([(0,1),(0,0),(1,1),(2,2)],2,(2,2)),
 'onebank':([(0,0)]*4,4,(1,1))}
def fits(reqs,mask,valid=15):
 used=Counter()
 for i in range(4):
  if mask>>i&1:
   if not(valid>>i&1):return False
   a,b=reqs[i];used[a]+=1;used[b]+=1
   if used[a]>2 or used[b]>2:return False
 return True
def greedy(reqs,valid=15):
 selected=0
 for i in range(4):
  if valid>>i&1 and fits(reqs,selected|(1<<i),valid):selected|=1<<i
 return selected
def oracle(reqs,valid=15):
 return max((m for m in range(16) if fits(reqs,m,valid)),
  key=lambda m:(m.bit_count(),tuple(bool(m>>i&1) for i in range(4))))
def sample(rng,B,kind,validity):
 def bank():
  if kind=='hot65' and rng.random()<0.65:return 0
  if kind=='hot65':return rng.randrange(1,B)
  return rng.randrange(B)
 reqs=[]
 for _ in range(4):
  a=bank();b=a if kind=='samebank70' and rng.random()<0.70 else bank()
  reqs.append((a,b))
 valid=sum(1<<i for i in range(4) if rng.random()<validity)
 return reqs,valid
def score(pairs,cap):
 gs=ms=events=delta=0
 for reqs,valid in pairs:
  g=min(cap,greedy(reqs,valid).bit_count())
  m=min(cap,oracle(reqs,valid).bit_count())
  assert m>=g and m-g<=1,(reqs,valid,g,m)
  gs+=g;ms+=m
  if m>g:events+=1;delta+=m-g
 n=len(pairs)
 return dict(batches=n,greedy_grants=gs,oracle_grants=ms,
  mean_greedy=gs/n,mean_oracle=ms/n,
  oracle_over_greedy=ms/gs if gs else None,
  improvement_probability=events/n,
  conditional_extra_grants=delta/events if events else 0,
  improved_batches=events)
def run():
 frozen={}
 for key,(reqs,cap,expected) in FROZEN.items():
  g=min(cap,greedy(reqs).bit_count());m=min(cap,oracle(reqs).bit_count())
  assert(g,m)==expected,(key,g,m)
  frozen[key]=dict(greedy=g,oracle=m,gain=m/g)
 regimes={}
 for j,(name,B,kind,cap,validity) in enumerate(SCENARIOS):
  pairs=[]
  for seed in SEEDS:
   rng=random.Random(seed*100+j)
   pairs.extend(sample(rng,B,kind,validity) for _ in range(N))
  regimes[name]=score(pairs,cap)
 exhaustive=improved=0
 for z in itertools.product(range(2),repeat=8):
  q=list(zip(z[::2],z[1::2]))
  g=greedy(q).bit_count();m=oracle(q).bit_count()
  assert m>=g and m-g<=1
  exhaustive+=1;improved+=(m>g)
 return dict(protocol='FROZEN_FOUR_SLOT_BANK_SERVICE_HEADROOM_20261102.md',
  evidence_tier='synthetic instantaneous bank-service oracle; not RTL or GPU IPC',
  seeds=list(SEEDS),batches_per_seed=N,frozen=frozen,regimes=regimes,
  exhaustive_B2=dict(batches=exhaustive,improved_batches=improved))
if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
