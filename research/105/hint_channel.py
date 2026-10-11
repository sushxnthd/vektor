from collections import defaultdict
from random import Random
from sector_incidence import workload,sector_incidence
def grouped(lanes,q,seed):
 r=Random(seed); bins=defaultdict(list)
 for l in lanes:
  truth=l.address//128
  options=sorted({x.address//128 for x in lanes if x.path==l.path and x.address//128!=truth})
  hint=truth if r.random()<q else r.choice(options)
  bins[l.path].append((hint,l))
 out=[]
 for p in sorted(bins):
  x=sorted(bins[p],key=lambda z:(z[0],z[1].warp,z[1].lane))
  out.extend([[a[1] for a in x[i:i+32]] for i in range(0,len(x),32)])
 return out
def main():
 lanes=workload('shared_sector')
 for q in (0,.25,.75,1):
  counts=[sector_incidence(grouped(lanes,q,seed+21000)) for seed in range(505000,505032)]
  print(q,sum(counts)/32,min(counts),max(counts))
  if q==0: assert sum(counts)/32<32
  if q==.25: assert all(x==32 for x in counts)
  if q==1: assert all(x==8 for x in counts)
if __name__=='__main__':main()
