"""Subcritical synthetic bank-port queue falsification; not GPU throughput."""
import random,json
def simulate(seed,skew,policy,cycles=40000,warmup=5000,cap=256):
 rng=random.Random(seed);q=[];done=lost=wait=0
 for t in range(cycles+warmup):
  for _ in range(4):
   if rng.random()<.25:
    bs=tuple(0 if rng.random()<skew else rng.randrange(3) for _ in range(2))
    if len(q)<cap:q.append((t,bs))
    elif t>=warmup:lost+=1
  demand=[0]*3
  for _,bs in q:
   for b in bs:demand[b]+=1
  order=range(len(q)) if policy=="fifo" else sorted(range(len(q)),key=lambda i:(sum(demand[b] for b in q[i][1]) if policy=="weighted" else max(demand[b] for b in q[i][1]),i))
  used=[0]*3; chosen=[]
  for i in order:
   req=[q[i][1].count(b) for b in range(3)]
   if all(used[b]+req[b]<=2 for b in range(3)):
    chosen.append(i)
    for b in range(3):used[b]+=req[b]
  for i in sorted(chosen,reverse=True):
   born,_=q.pop(i)
   if t>=warmup:done+=1;wait+=t-born
 return {"served":done,"lost":lost,"mean_wait":round(wait/done,3),"remaining":len(q)}
if __name__=="__main__":
 out={name:{str(seed):{p:simulate(seed,h,p) for p in ("fifo","mincontention","weighted")} for seed in (11,23,37)} for name,h in (("uniform",0),("moderate",.3),("severe",.7))}
 print(json.dumps(out,indent=2))
