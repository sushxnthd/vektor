#!/usr/bin/env python3
import random
from pathlib import Path
def choose(v,r,a,p):
    ids=[i for i in range(8) if v[i]]
    if not ids:return -1
    if p==0:return ids[0]
    if p==2:
        urgent=[i for i in ids if a[i]>=4]
        if urgent:return min(urgent,key=lambda i:(-a[i],i))
    return min(ids,key=lambda i:(r[i],i))
def pack(values,w):
    return sum(x<<(w*i) for i,x in enumerate(values))
if __name__=="__main__":
    rng=random.Random(570957)
    out=Path("research/057/build")
    out.mkdir(parents=True,exist_ok=True)
    for p in range(3):
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
                f.write(f"{pack(v,1):02x} {pack(r,2):04x} {pack(a,6):012x} {choose(v,r,a,p)}\n")
    print("12288 deterministic vectors generated")
