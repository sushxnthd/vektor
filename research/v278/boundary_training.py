"""V278: exact eight-register balanced allocation training sweep (not RTL PPA)."""
import itertools,random,json
N=8
parity=[sum(1<<r for r in range(N) if (r&m).bit_count()%2) for m in range(1,8)]
balanced=[sum(1<<r for r in s) for s in itertools.combinations(range(1,N),4)]
assert len(balanced)==35
def conflict(edges,mask):
 return sum(w for u,v,w in edges if (((mask>>u)^(mask>>v))&1)==0)
def evaluate(edges,ceil):
 total=sum(w for _,_,w in edges)
 cp=min(conflict(edges,p) for p in parity)/total
 co=min(conflict(edges,p) for p in balanced)/total
 b=min(ceil,1/(1+cp));a=min(ceil,1/(1+co))
 return dict(conflict_base=cp,conflict_opt=co,rate_base=b,rate_opt=a,gain=a/b)
rng=random.Random(27801)
rows=[]
for i in range(240):
 edges=[(u,v,rng.randint(1,12)) for u in range(N) for v in range(u+1,N) if rng.random()<0.65]
 if not edges: continue
 for ceiling in (1.0,0.5,0.25):
  rows.append(dict(id=i,ceiling=ceiling,**evaluate(edges,ceiling)))
for ceiling in (1.0,0.5,0.25):
 sub=[r for r in rows if r["ceiling"]==ceiling]
 print(ceiling,len(sub),sum(r["gain"]>1.000001 for r in sub),max(r["gain"] for r in sub))
