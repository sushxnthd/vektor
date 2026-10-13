#!/usr/bin/env python3
"""V149 modeled workload probe: CLOSE-eligible fraction, not GPU trace/performance."""
import ctypes,random,struct,json
r=random.Random(149901)
lib=ctypes.CDLL("libm.so.6")
lib.fmaf.argtypes=[ctypes.c_float]*3
lib.fmaf.restype=ctypes.c_float
def bits(x):return struct.unpack("<I",struct.pack("<f",float(x)))[0]
def value(x):return struct.unpack("<f",struct.pack("<I",x))[0]
def fma(a,b,c):
 return bits(lib.fmaf(ctypes.c_float(value(a)),ctypes.c_float(value(b)),ctypes.c_float(value(c))))
def close(a,b,c):
 def sigexp(x):
  e=(x>>23)&255;f=x&0x7fffff
  if e==255:return None
  return (f|((1<<23) if e else 0)),(-149 if e==0 else e-150)
 aa=sigexp(a);bb=sigexp(b);cc=sigexp(c)
 if None in (aa,bb,cc):return False
 p=aa[0]*bb[0];v=cc[0]
 if not p or not v:return False
 return bool(((a^b^c)>>31)&1) and abs(aa[1]+bb[1]+p.bit_length()-1-(cc[1]+v.bit_length()-1))<=1
def normal():return bits(r.uniform(-1.5,1.5))
def pos():return bits(r.uniform(0.5,1.5))
streams={}
streams["vector_positive"]=[(pos(),pos(),pos()) for _ in range(8192)]
streams["vector_signed"]=[(normal(),normal(),normal()) for _ in range(8192)]
gemm=[]
for _ in range(128):
 acc=bits(0.0)
 for k in range(64):
  a,b=normal(),normal()
  gemm.append((a,b,acc));acc=fma(a,b,acc)
streams["gemm_fragments"]=gemm
streams["cancellation_control"]=[(bits(1.0),b,b^0x80000000) for b in (pos() for _ in range(8192))]
divergent=[]
for _ in range(16384):
 if r.randrange(2):divergent.append((normal(),normal(),normal()))
streams["divergent_active"]=divergent
summary={}
for name,v in streams.items():
 n=len(v);k=sum(close(*x) for x in v)
 summary[name]={"active_fma":n,"close_eligible":k,"fraction":round(k/n,6)}
print(json.dumps({"seed":149901,"evidence":"software modeled operand streams, not GPU traces","workloads":summary},indent=2))
