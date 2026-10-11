"""Deterministic held-valid producer vectors for V097 RTL equivalence."""
from ref_model import Ref
from pathlib import Path
import random,json
def run(n,guard,seed,cycles=4096):
 rng=random.Random(seed);a=Ref(n,guard)
 src=[None]*n;generation=[0]*n;prev=None
 accepted=0;stalls=0
 dest=Path(__file__).with_name(f'vectors_s{n}_g{guard}_seed{seed}.txt')
 with dest.open('w') as f:
  for t in range(cycles):
   for i in range(n):
    if src[i] is None and rng.random()<(.82 if i%2 else .64):
     src[i]=(int(rng.random()<(.15 if i%2 else .65)),
             (generation[i]*n+i)&15)
   ready=int(rng.random()<(.35 if t%97<24 else .82))
   chosen,grant=a.step(src,ready)
   payload=(chosen,src[chosen]) if chosen is not None else None
   if prev is not None:assert payload==prev
   prev=payload if payload is not None and not ready else None
   accepted+=int(grant is not None)
   stalls+=int(payload is not None and not ready)
   valid=sum(1<<i for i,b in enumerate(src) if b is not None)
   final=sum(1<<i for i,b in enumerate(src) if b and b[0])
   tags=sum((b[1] if b else 0)<<(4*i) for i,b in enumerate(src))
   outfinal=src[chosen][0] if chosen is not None else 0
   outtag=src[chosen][1] if chosen is not None else 0
   row=(valid,final,tags,ready,int(chosen is not None),
        outfinal,outtag,chosen if chosen is not None else 0,
        (1<<grant) if grant is not None else 0)
   f.write(' '.join(f'{v:x}' for v in row)+'\n')
   if grant is not None:src[grant]=None;generation[grant]+=1
 return {'sources':n,'guard':guard,'seed':seed,'cycles':cycles,
         'stalls':stalls,'accepted':accepted}
if __name__=='__main__':
 cfg=[(2,2,97),(4,4,1097),(4,16,2097),(4,4,3097)]
 result=[run(*args) for args in cfg]
 Path(__file__).with_name('vectors_summary.json').write_text(
   json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
