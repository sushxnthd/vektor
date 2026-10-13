#!/usr/bin/env python3
"""Independent libc fenv validation of V150 finite IEEE exception flags."""
import ctypes,random,struct
from research.v147.fma_oracle import fma_bits
lib=ctypes.CDLL('libm.so.6')
lib.fmaf.argtypes=[ctypes.c_float]*3
lib.fmaf.restype=ctypes.c_float
lib.feclearexcept.argtypes=[ctypes.c_int]
lib.fetestexcept.argtypes=[ctypes.c_int]
lib.fetestexcept.restype=ctypes.c_int
f32=lambda x:struct.unpack('<f',struct.pack('<I',x))[0]
r=random.Random(1212)
n=0
for _ in range(20000):
 a,b,c=(r.getrandbits(32) for j in range(3))
 if any((x&0x7f800000)==0x7f800000 for x in (a,b,c)):continue
 expected,flags=fma_bits(a,b,c)
 lib.feclearexcept(0x3d)
 lib.fmaf(ctypes.c_float(f32(a)),ctypes.c_float(f32(b)),ctypes.c_float(f32(c)))
 exc=lib.fetestexcept(0x3d)
 observed=(16 if exc&1 else 0)|(4 if exc&8 else 0)|(2 if exc&16 else 0)|(1 if exc&32 else 0)
 assert flags==observed,(a,b,c,flags,observed)
 n+=1
print(f'V150 libc fenv PASS: {n} finite flag comparisons')
