"""Golden model for Vektor-097 (synthetic return arbitration)."""
class Ref:
 def __init__(self,n,guard,lock=True):
  self.n=n;self.guard=guard;self.lock=lock
  self.age=[0]*n;self.rr=0;self.held=None
 def step(self,src,ready):
  active=[i for i,b in enumerate(src) if b is not None]
  if self.lock and self.held is not None:c=self.held
  else:
   overdue=[i for i in active if self.age[i]>=self.guard]
   if overdue:
    c=min(overdue,key=lambda i:(-self.age[i],(i-self.rr)%self.n))
   else:
    finals=[i for i in active if src[i][0]]
    pool=finals or active
    c=min(pool,key=lambda i:(i-self.rr)%self.n) if pool else None
  beat=src[c] if c is not None else None
  grant=c if beat is not None and ready else None
  if self.lock:
   if beat is not None and not ready and self.held is None:self.held=c
   if grant is not None:self.held=None
  if grant is not None:self.rr=(grant+1)%self.n
  self.age=[0 if src[i] is None or grant==i else min(1023,a+1)
            for i,a in enumerate(self.age)]
  return c if beat is not None else None,grant
