#!/usr/bin/env python3
"""Frozen v151 boundary corpus: exact oracle; deterministic seed; no API spend."""
import pathlib,random,sys
sys.path.insert(0,'.')
from research.v147.fma_oracle import fma_bits,decode
def cl(x):
 e=(x>>23)&255;f=x&0x7fffff
 return (2 if not f else (3 if f&0x400000 else 4)) if e==255 else (0 if x&0x7fffffff==0 else 1)
def fields(a,b,c):
 sa,_,_,_,_,ma,qa=decode(a);sb,_,_,_,_,mb,qb=decode(b);sc,_,_,_,_,mc,qc=decode(c)
 return sa^sb,sc,qa+qb,qc,ma*mb,mc,(cl(c)<<6)|(cl(b)<<3)|cl(a)
edge=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,
 0x3f7fffff,0x3f800000,0x3f800001,0x3f800002,0x3f000000,
 0x40000000,0x7f7fffff,0xff7fffff,0x7f800000,0x7fc00000]
cs=[0xbf800000,0x3f800000,0xbf7fffff,0xbf800001,
 0x80000001,0x00000001,0x80800000,0x00800000,0x7f800000]
cases=[(a,b,c) for a in edge for b in edge for c in cs]
r=random.Random(1512026)
for i in range(5000):
 a,b,c=(r.getrandbits(32) for _ in range(3))
 if i%4==0:c=r.choice(cs)
 if i%4==1:a=r.choice(edge)
 if i%4==2:b=r.choice(edge)
 cases.append((a,b,c))
dst=pathlib.Path('build/v151/full_vectors.txt');dst.parent.mkdir(parents=True,exist_ok=True)
base=pathlib.Path('build/v150/full_vectors.txt').read_text()
with dst.open('w') as f:
 f.write(base)
 for a,b,c in cases:
  ps,cs,pe,ce,p,cm,classes=fields(a,b,c)
  exp,flags=fma_bits(a,b,c)
  f.write(f'{ps:x} {cs:x} {pe:d} {ce:d} {p:012x} {cm:06x} {classes:03x} {exp:08x} {flags:02x}\n')
print(f'V151 corpus: {len(base.splitlines())} original + {len(cases)} boundary = {len(base.splitlines())+len(cases)}')
