import random,sys
W,B,P,out=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
O=3; PORTS=2; BW=max(1,(B-1).bit_length()); pointer=0
rng=random.Random(520052)
with open(out,"w") as f:
 for t in range(1000):
  pending=accepted=packed=0
  slots=[0,1,2,3,W*O,rng.randrange(W*O+1)][t%6]
  for i in range(W*O):
   state=rng.randrange(3)
   if t%13==0: state=1
   if t%17==0: state=0
   if state==1: pending|=1<<i
   if state==2: accepted|=1<<i
   bank=0 if t%7==0 else rng.randrange(B)
   packed|=bank<<(i*BW)
  used=[0]*B; grant=0; first=None
  order=[(pointer+k)%W for k in range(W)]
  if P==2:
   order=sorted(order,key=lambda w:-((accepted>>(w*O))&7).bit_count())
  for w in order:
   for o in range(O):
    i=w*O+o
    if not ((pending>>i)&1) or ((accepted>>i)&1): continue
    bank=(packed>>(i*BW))&((1<<BW)-1)
    if grant.bit_count()<slots and used[bank]<PORTS:
     used[bank]+=1; grant|=1<<i
     if first is None: first=w
  assert grant&accepted==0 and grant&~pending==0
  if P==0: pointer=(pointer+1)%W
  elif first is not None: pointer=(first+1)%W
  f.write(f"{pending:x} {accepted:x} {packed:x} {slots:x} {grant:x} {grant.bit_count():x} {pointer:x}\n")
print("Generated",1000,"vectors",W,B,P)
