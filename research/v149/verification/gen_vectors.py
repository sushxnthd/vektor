#!/usr/bin/env python3
"""V149: independent exact-dyadic FP32 RNE oracle, cross-checked with libc fmaf."""
import ctypes,random,struct,pathlib
R=random.Random(149)
lib=ctypes.CDLL("libm.so.6")
lib.fmaf.argtypes=[ctypes.c_float,ctypes.c_float,ctypes.c_float]
lib.fmaf.restype=ctypes.c_float
def f32(x):return struct.unpack("<f",struct.pack("<I",x))[0]
def bits(x):return struct.unpack("<I",struct.pack("<f",x))[0]
def parts(x):
 e=(x>>23)&255
 return (x&0x7fffff)|((1<<23) if e else 0),(-149 if e==0 else e-150)
def rne(mag,ex,sign):
 if not mag:return sign<<31,0
 h=mag.bit_length()-1;top=ex+h
 if top>127:return (sign<<31)|0x7f800000,5
 if top>=-126:
  shift=h-23
  if shift<=0:q=mag<<(-shift);rem=0
  else:q=mag>>shift;rem=mag&((1<<shift)-1)
  if shift>0 and (rem*2>(1<<shift) or (rem*2==(1<<shift) and q&1)):q+=1
  nx=bool(rem)
  if q==1<<24:q>>=1;top+=1
  if top>127:return (sign<<31)|0x7f800000,5
  return (sign<<31)|((top+127)<<23)|(q&0x7fffff),int(nx)
 shift=-149-ex
 if shift<=0:q=mag<<(-shift);rem=0
 else:q=mag>>shift;rem=mag&((1<<shift)-1)
 if shift>0 and (rem*2>(1<<shift) or (rem*2==(1<<shift) and q&1)):q+=1
 nx=bool(rem)
 if q>=1<<23:return (sign<<31)|0x00800000,int(nx)
 return (sign<<31)|q,(3 if nx else 0)
def oracle(a,b,c):
 sa,ea=parts(a);sb,eb=parts(b);sc,ec=parts(c)
 p=sa*sb;pe=ea+eb;ps=((a^b)>>31)&1;cs=c>>31
 lp=p.bit_length()-1;lc=sc.bit_length()-1
 if not (p and sc and ps!=cs and abs(pe+lp-ec-lc)<=1):return None
 base=min(pe,ec)
 vp=p<<(pe-base);vc=sc<<(ec-base)
 sm=(-vp if ps else vp)+(-vc if cs else vc)
 return (ps,cs,pe,ec,p,sc,*rne(abs(sm),base,sm<0))
cases=[
 (0x00000001,0x3f000000,0x80000001),
 (0x80000001,0x3f000000,0x00000001),
 (0x00000003,0x3f000000,0x80000001),
 (0x00000005,0x3f000000,0x80000002),
 (0x3f800001,0x3f800001,0xbf800000),
 (0xbf800001,0x3f800001,0x3f800000),
 (0x3f800000,0x3f800000,0xbf800000),
 (0x3f800000,0x3f800000,0xbf7fffff),
 (0x3f800000,0x00000001,0x80000001),
 (0x3f800000,0x007fffff,0x807fffff),
 (0x00800000,0x3f800000,0x80800000),
 (0xbf800000,0x3f800000,0x3f800000)]
for _ in range(20000):
 ea=R.randint(10,242);eb=R.randint(10,242)
 a=(ea<<23)|R.getrandbits(23);b=(eb<<23)|R.getrandbits(23)
 if R.randrange(2):a|=1<<31
 if R.randrange(2):b|=1<<31
 sa,qa=parts(a);sb,qb=parts(b)
 p=sa*sb;pe=qa+qb;lead=pe+p.bit_length()-1
 cexp=lead+127+R.choice([-1,0,0,0,1])
 if not (1<=cexp<=254):continue
 c=(cexp<<23)|R.getrandbits(23)
 if (((a^b)>>31)&1)==0:c|=1<<31
 cases.append((a,b,c))
out=[];seen=set()
for a,b,c in cases:
 v=oracle(a,b,c)
 if v is None or (a,b,c) in seen:continue
 seen.add((a,b,c))
 f=bits(lib.fmaf(ctypes.c_float(f32(a)),ctypes.c_float(f32(b)),ctypes.c_float(f32(c))))
 assert f==v[-2],f"independent libc mismatch {a:08x} {b:08x} {c:08x} {f:08x} {v[-2]:08x}"
 out.append(v)
 if len(out)>=3072:break
assert len(out)==3072,len(out)
path=pathlib.Path("build/v149/close_vectors.txt")
path.parent.mkdir(parents=True,exist_ok=True)
with path.open("w") as f:
 for ps,cs,pe,ce,p,sc,res,flags in out:
  f.write(f"{ps:x} {cs:x} {pe:d} {ce:d} {p:012x} {sc:06x} {res:08x} {flags:02x}\n")
print(f"V149 ORACLE PASS: {len(out)} real-FP32 CLOSE cases, libc fmaf result match, seed 149")
