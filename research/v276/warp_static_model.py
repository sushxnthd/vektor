#!/usr/bin/env python3
"""Deterministic warp-static boundary, no unseen holdout imports."""
import json
from pathlib import Path
def bank(a,m): return (a&3)^(((a>>2)&3) if m else 0)
def score(warps,mode):
 return sum(1+(bank(a,mode(w))!=bank(b,mode(w))) for w in warps for a,b in w['pairs'])
def make(kind):
 ws=[]
 for w in range(400):
  if kind=='mixed': types=[0,1]*32; hint=w&1; kernel=0
  elif kind=='pure_one_kernel': types=[w&1]*64; hint=w&1; kernel=0
  elif kind=='pure_two_kernels': types=[w&1]*64; hint=w&1; kernel=w&1
  elif kind=='majority': types=([1]*48+[0]*16) if w&1 else ([1]*16+[0]*48); hint=w&1; kernel=0
  else: raise ValueError(kind)
  ws.append({'hint':hint,'kernel':kernel,'pairs':[(16*(w*64+i+1),16*(w*64+i+1)+(4 if t else 5)) for i,t in enumerate(types)]})
 return ws
def evaluate(kind):
 ws=make(kind)
 d=score(ws,lambda w:0); x=score(ws,lambda w:1); a=score(ws,lambda w:w['hint'])
 km={}
 for k in {w['kernel'] for w in ws}:
  g=[w for w in ws if w['kernel']==k]
  km[k]=int(score(g,lambda w:1)>score(g,lambda w:0))
 pk=score(ws,lambda w:km[w['kernel']])
 purity=sum(abs(sum((b-a)==4 for a,b in w['pairs'])/64-.5) for w in ws)/len(ws)
 pb=sum(sum((b-a)==4 for a,b in w['pairs']) for w in ws)/(len(ws)*64)
 law=(1.5+purity)/(1.5+abs(pb-.5))
 return {'pairs':len(ws)*64,'direct_reads':d,'xor_reads':x,'hinted_reads':a,'per_kernel_reads':pk,'best_global_reads':max(d,x),'hinted_gain_vs_global':a/max(d,x),'hinted_gain_vs_per_kernel':a/pk,'per_warp_oracle_gain_law':law,'pbar':pb,'mean_warp_purity':purity,'clock_retention_threshold':max(d,x)/a}
if __name__=='__main__':
 results={k:evaluate(k) for k in ('mixed','pure_one_kernel','pure_two_kernels','majority')}
 assert results['mixed']['hinted_gain_vs_global']==1.0
 assert results['pure_one_kernel']['hinted_gain_vs_global']==4/3
 assert results['pure_two_kernels']['hinted_gain_vs_per_kernel']==1.0
 Path('research/v276/run23_corrected_training.json').write_text(json.dumps({'evidence':'E1 only','holdouts_opened':False,'results':results},indent=2)+'\n')
 print(json.dumps(results,indent=2))
