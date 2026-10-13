#!/usr/bin/env python3
"""V149 isolated wildcard: cancellation-path coverage vs synthetic GEMM reduction depth."""
import random,ctypes,struct,json
r=random.Random(149902)
lib=ctypes.CDLL("libm.so.6")
lib.fmaf.argtypes=[ctypes.c_float]*3
lib.fmaf.restype=ctypes.c_float
def bits(x):return struct.unpack("<I",struct.pack("<f",float(x)))[0]
def val(x):return struct.unpack("<f",struct.pack("<I",x))[0]
def fma(a,b,c):return bits(lib.fmaf(ctypes.c_float(val(a)),ctypes.c_float(val(b)),ctypes.c_float(val(c))))
def close(a,b,c):
 def se(x):
  e=(x>>23)&255
  return ((x&0x7fffff)|((1<<23) if e else 0),(-149 if e==0 else e-150))
 sa,ea=se(a);sb,eb=se(b);sc,ec=se(c);p=sa*sb
 return bool(p and sc and (((a^b^c)>>31)&1) and abs(ea+eb+p.bit_length()-1-ec-sc.bit_length()+1)<=1)
result=[]
for k in [2,4,8,16,32,64,128,256,512]:
 n=0;count=0;late=0;late_n=0
 for _ in range(8192//k):
  acc=bits(0.0)
  for t in range(k):
   a=bits(r.uniform(-1.5,1.5));b=bits(r.uniform(-1.5,1.5))
   hit=close(a,b,acc);count+=hit;n+=1
   if t>=k//2:late+=hit;late_n+=1
   acc=fma(a,b,acc)
 result.append({"K":k,"active":n,"close":count,"fraction":round(count/n,6),"last_half_fraction":round(late/late_n,6)})
print(json.dumps({"seed":149902,"evidence":"modeled synthetic GEMM accumulator stream","results":result},indent=2))
