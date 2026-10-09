#!/usr/bin/env python3
import random
from pathlib import Path
def choose(v,r,a,p):
    ids=[i for i in range(8) if v[i]]
    if not ids:return -1
    if p==0:return ids[0]
    if p in (2,3):
        urgent=[i for i in ids if a[i]>=4]
        if urgent:return min(urgent,key=lambda i:(-a[i],i)) if p==2 else urgent[0]
    return min(ids,key=lambda i:(r[i],i))
def pack(values,w):
    return sum(x<<(w*i) for i,x in enumerate(values))
if __name__=="__main__":
    rng=random.Random(570957)
    out=Path("research/057/build")
    out.mkdir(parents=True,exist_ok=True)
    for p in range(4):
        with (out/f"vectors_p{p}.txt").open("w") as f:
            for n in range(4096):
                v=[rng.randrange(2) for _ in range(8)]
                r=[rng.randrange(1,4) for _ in range(8)]
                a=[rng.randrange(64) for _ in range(8)]
                if n<8:
                    v=[0]*8
                    if n:v[n-1]=1
                if 8<=n<16:
                    v=[1]*8;a=[0,3,4,4,6,5,2,1];r=[3,1,3,2,3,1,1,2]
                if p==3:a.sort(reverse=True)
                f.write(f"{pack(v,1):02x} {pack(r,2):04x} {pack(a,6):012x} {choose(v,r,a,p)}\n")
    for line in (out/"vectors_p3.txt").read_text().splitlines():
        v,r,a,_=line.split();v=int(v,16);r=int(r,16);a=int(a,16)
        vv=[(v>>i)&1 for i in range(8)]
        rr=[(r>>(2*i))&3 for i in range(8)]
        aa=[(a>>(6*i))&63 for i in range(8)]
        assert choose(vv,rr,aa,2)==choose(vv,rr,aa,3)
    assert choose([1,1]+[0]*6,[2,2]+[1]*6,[4,9]+[0]*6,2)!=choose([1,1]+[0]*6,[2,2]+[1]*6,[4,9]+[0]*6,3)
    print("16384 oracle vectors and 4096 order-invariant equivalence checks")
