"""Exploratory equal-offer V097 sweep; 32/256 random probes."""
from ref_model import Ref
import random,json
from pathlib import Path
def trial(k,cfg,lock):
 n=4;r=random.Random(4000+k)
 a=Ref(n,cfg[0],lock=lock)
 src=[None]*n;done=[0]*n;prev=None;bad=0
 for t in range(1500):
  for i in range(n):
   if src[i] is None and r.random()<cfg[1]:
    src[i]=(int(r.random()<cfg[3]),i+1)
  ready=r.random()<cfg[2] and not(cfg[4] and t%97<cfg[4])
  chosen,grant=a.step(src,ready)
  payload=(chosen,src[chosen]) if chosen is not None else None
  if prev is not None and prev!=payload:bad+=1
  prev=payload if payload is not None and not ready else None
  if grant is not None:src[grant]=None;done[grant]+=1
 return sum(done),bad
if __name__=='__main__':
 totals=[0,0];bad=[0,0];deltas=[];probes=0
 for k in range(256):
  r=random.Random(990000+k)
  probe=k%8==0;probes+=probe
  if probe:
   cfg=(r.choice([1,2,3,7,15,31,63]),r.uniform(.05,1),
        r.uniform(.1,1),r.uniform(0,1),r.randrange(0,35))
  else:
   cfg=([2,4,16,64][k%4],[.35,.75,.98][k%3],
        [.35,.65,.9][k%3],[.1,.5,.9][(k//3)%3],
        [0,12,24][(k//9)%3])
  old=trial(k,cfg,False);new=trial(k,cfg,True)
  totals[0]+=old[0];totals[1]+=new[0]
  bad[0]+=old[1];bad[1]+=new[1]
  deltas.append(new[0]-old[0])
 out={'cases':256,'random_probes':probes,'old_accepts':totals[0],
      'new_accepts':totals[1],'old_stability_violations':bad[0],
      'new_stability_violations':bad[1],
      'improve':sum(d>0 for d in deltas),'tie':sum(d==0 for d in deltas),
      'regress':sum(d<0 for d in deltas)}
 Path(__file__).with_name('sweep_reproduction.json').write_text(
   json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
