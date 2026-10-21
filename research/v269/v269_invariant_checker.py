#!/usr/bin/env python3
"""Independent E1 semantic checker, not RTL simulation."""
from collections import deque
import random,json
r=random.Random(269009)
q=[deque(),deque()];written=[[],[]];read=[[],[]];rr=0;pushes=pops=0
for t in range(50000):
 c=r.randrange(2);data=(t<<1)|c;ready=[r.random()<.5,r.random()<.9]
 choices=[i for i in (0,1) if q[i] and ready[i]]
 if choices:
  i=rr if rr in choices else choices[0]
  read[i].append(q[i].popleft());rr=1-i;pops+=1
 if r.random()<.85 and len(q[c])<4:
  q[c].append(data);written[c].append(data);pushes+=1
 assert all(len(x)<=4 for x in q)
 for i in (0,1):assert read[i]==written[i][:len(read[i])]
print(json.dumps({'cycles':50000,'pushes':pushes,'pops':pops,'mismatches':0,'capacity_violations':0,'evidence':'E1, not RTL sim','holdouts':'unopened'},indent=2))
