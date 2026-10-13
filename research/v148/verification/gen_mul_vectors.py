"""V148 independent integer/dyadic multiplication-stage reference vectors.
The IEEE FMA operation is NOT performed; NaN/Inf are only classified.
"""
from pathlib import Path
import random
r=random.Random(148)
special=[0,0x80000000,1,0x80000001,0x7fffff,0x807fffff,
         0x00800000,0x80800000,0x3f800000,0xbf800000,
         0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,
         0x7fc00001,0xffc00001,0x7f800001,0xff800001]
def sig(x):
    return (x&0x7fffff) | (0x800000 if (x>>23)&255 else 0)
def ex(x):
    e=(x>>23)&255
    return (-149 if e==0 else e-150)&2047
def cls(x):
    e=(x>>23)&255
    m=x&0x7fffff
    if e==255:return 2 if m==0 else (3 if m&0x400000 else 4)
    return 0 if e==0 and m==0 else 1
cases=[]
for i in range(512):
    if i<len(special)**2:
        a=special[i%len(special)]
        b=special[(i//len(special))%len(special)]
        c=special[(i*7+3)%len(special)]
    else:
        a,b,c=[r.getrandbits(32) for _ in range(3)]
    cases.append((a,b,c))
path=Path("build/v148/mul_vectors.hex")
path.parent.mkdir(parents=True,exist_ok=True)
with path.open("w") as f:
    for a,b,c in cases:
        p=sig(a)*sig(b)
        ep=(ex(a)+ex(b))&2047
        ec=ex(c)
        sp=((a^b)>>31)&1
        sc=(c>>31)&1
        cl=cls(a)|(cls(b)<<3)|(cls(c)<<6)
        f.write(f"{a:08x} {b:08x} {c:08x} {p:012x} {ep:03x} {sig(c):06x} {ec:03x} {sp:x} {sc:x} {cl:03x}\n")
print(f"V148 generated {len(cases)} deterministic independent stage vectors: {path}")
