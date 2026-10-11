"""Bounded enumeration of legal ready/valid traces; not formal RTL proof."""
import itertools,json
from pathlib import Path
from ref_model import Ref
def run():
 counts=[0,0];accepted=[0,0];example=None
 for seq in itertools.product(range(8),repeat=5):
  for mode in range(2):
   a=Ref(2,2,lock=bool(mode));src=[None,None];prev=None
   for t,action in enumerate(seq):
    ready=bool(action&4)
    for i in range(2):
     if src[i] is None and action&(1<<i):src[i]=(int(i==0),i+1)
    chosen,grant=a.step(src,ready)
    payload=(chosen,src[chosen]) if chosen is not None else None
    if prev is not None and payload!=prev:
     counts[mode]+=1
     if example is None and mode==0:
      example={'actions':seq,'cycle':t,'old':str(prev),'new':str(payload)}
    prev=payload if payload is not None and not ready else None
    if grant is not None:src[grant]=None;accepted[mode]+=1
 assert counts[0]>0 and counts[1]==0
 report={'traces':32768,'legacy_stability_violations':counts[0],
         'locked_stability_violations':counts[1],
         'legacy_acceptances':accepted[0],
         'locked_acceptances':accepted[1],
         'counterexample':example}
 Path(__file__).with_name('exhaustive_results.json').write_text(
   json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':run()
