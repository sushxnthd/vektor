#!/usr/bin/env python3
"""Generate deterministic 10k-cycle trace from the indexed-ring model."""
import csv
from random import Random
from model_071 import Ring
rng=Random(71371);m=Ring(4)
with open('research/071/model/trace_071.csv','w',newline='') as f:
    w=csv.writer(f)
    w.writerow('d_uid,d_clone,d_drop,d_stall,d_ready,a_uid,a_clone,a_drop,a_stall,a_ready,d_accept,d_pop,a_accept,a_pop,d_count,a_count,d_admit_total,a_admit_total,cycle'.split(','))
    for i in range(10000):
        u=[None if rng.randrange(4)==0 else rng.randrange(4) for _ in range(2)]
        c=[rng.randrange(2) for _ in range(2)]
        d=[rng.randrange(5)==0 for _ in range(2)]
        s=[rng.randrange(4)==0 for _ in range(2)]
        r=[rng.randrange(2)==0 for _ in range(2)]
        actions=[(u[k],c[k],d[k],s[k],r[k]) for k in range(2)]
        out=m.step(actions)
        w.writerow([u[0] if u[0] is not None else -1,c[0],int(d[0]),int(s[0]),int(r[0]),
          u[1] if u[1] is not None else -1,c[1],int(d[1]),int(s[1]),int(r[1]),
          int(out[0][0]),int(out[0][1]),int(out[1][0]),int(out[1][1]),
          m.n[0],m.n[1],m.admit[0],m.admit[1],i])
print('generated 10000 deterministic cycles')
