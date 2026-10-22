import itertools,json
P=list(itertools.permutations(range(4)))
C=(3,0,1,2)
def salt(w,p):
 return sum(((w>>p[i])&1)<<i for i in range(4))
def grant(rs):
 u=[0]*16;n=0
 for a,b in rs:
  need={a:2} if a==b else {a:1,b:1}
  if all(u[k]+v<=2 for k,v in need.items()):
   for k,v in need.items():u[k]+=v
   n+=1
 return n
def regs(ids,m):
 if m=="wave":return [(w,(w+1)&15) for w in ids]
 if m=="perm":return [(salt(w,C),(salt(w,C)+1)&15) for w in ids]
 return [(0,0) if m=="hot" else (0,1) for _ in ids]
def eval(ids,rs,p):
 if p=="identity":return grant(rs)
 if p=="add":return grant([((a+w)&15,(b+w)&15) for w,(a,b) in zip(ids,rs)])
 return grant([(a^salt(w,p),b^salt(w,p)) for w,(a,b) in zip(ids,rs)])
if __name__=="__main__":
 modes=["wave","perm","hot","pair"]; controls=["identity","add"]+P
 out={str(p):{m:0 for m in modes} for p in controls}
 for ids in itertools.combinations(range(16),4):
  for m in modes:
   r=regs(ids,m)
   for p in controls:out[str(p)][m]+=eval(ids,r,p)
 print(json.dumps(out,indent=2))
