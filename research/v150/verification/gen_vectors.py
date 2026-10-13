#!/usr/bin/env python3
"""V150 frozen exact-integer binary32 FMA vectors; finite cases cross-check libc fmaf."""
import ctypes,random,struct,pathlib
from research.v147.fma_oracle import fma_bits,decode
r=random.Random(1502026)
lib=ctypes.CDLL('libm.so.6')
lib.fmaf.argtypes=[ctypes.c_float]*3;lib.fmaf.restype=ctypes.c_float
def f32(x):return struct.unpack('<f',struct.pack('<I',x))[0]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def cl(x):
 e=(x>>23)&255;f=x&0x7fffff
 return (2 if not f else (3 if f&0x400000 else 4)) if e==255 else (0 if x&0x7fffffff==0 else 1)
def fields(a,b,c):
 sa,_,_,_,_,ma,qa=decode(a);sb,_,_,_,_,mb,qb=decode(b);sc,_,_,_,_,mc,qc=decode(c)
 return (sa^sb,sc,qa+qb,qc,ma*mb,mc,(cl(c)<<6)|(cl(b)<<3)|cl(a))
special=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x80800000,0x3f800000,0xbf800000,0x3f800001,0xbf800001,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc00000,0xffc00001,0x7f800001]
triples=[]
for a in special:
 for b in special:
  for c in [0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x7f800000,0xff800000,0x7fc00000]:
   triples.append((a,b,c))
for _ in range(10000):triples.append(tuple(r.getrandbits(32) for _ in range(3)))
for _ in range(4000):
 a=(r.randrange(1,254)<<23)|r.getrandbits(23)
 b=(r.randrange(1,254)<<23)|r.getrandbits(23)
 sa,_,_,_,_,ma,qa=decode(a);sb,_,_,_,_,mb,qb=decode(b)
 lead=qa+qb+(ma*mb).bit_length()-1
 e=max(1,min(254,lead+127+r.choice([-1,0,1])))
 c=(1<<31)|(e<<23)|r.getrandbits(23)
 triples.append((a,b,c))
path=pathlib.Path('build/v150/full_vectors.txt');path.parent.mkdir(parents=True,exist_ok=True)
finite_libc=0;special_count=0
with path.open('w') as f:
 for a,b,c in triples:
  expected,flags=fma_bits(a,b,c)
  if all((x&0x7f800000)!=0x7f800000 for x in (a,b,c)):
   actual=bits(lib.fmaf(ctypes.c_float(f32(a)),ctypes.c_float(f32(b)),ctypes.c_float(f32(c))))
   assert actual==expected,(hex(a),hex(b),hex(c),hex(actual),hex(expected))
   finite_libc+=1
  else:special_count+=1
  ps,cs,pe,ce,p,cm,classes=fields(a,b,c)
  f.write(f'{ps:x} {cs:x} {pe:d} {ce:d} {p:012x} {cm:06x} {classes:03x} {expected:08x} {flags:02x}\n')
assert len(triples)==16916
print(f'V150 ORACLE PASS: {len(triples)} vectors, {finite_libc} finite libc fmaf matches, {special_count} special cases')
