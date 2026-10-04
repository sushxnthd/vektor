from __future__ import annotations
import random
from pathlib import Path
from sim.vektor.fp32_stage_contract import classify, sig24, qexp

CLASS={"zero":0,"finite":1,"inf":2,"qnan":3,"snan":4}
def expected(a,b,c):
    return ((a>>31)^(b>>31), qexp(a)+qexp(b), sig24(a)*sig24(b),
            (c>>31)&1,qexp(c),sig24(c),CLASS[classify(a)],CLASS[classify(b)],CLASS[classify(c)])
def main():
    rng=random.Random(0x5090)
    directed=[0,0x80000000,1,0x007fffff,0x00800000,0x3f800000,0x7f7fffff,0x7f800000,0xff800000,0x7fc00000,0x7f800001]
    triples=[]
    for i,x in enumerate(directed): triples.append((x,directed[(i*3+1)%len(directed)],directed[(i*7+2)%len(directed)]))
    triples += [(rng.getrandbits(32),rng.getrandbits(32),rng.getrandbits(32)) for _ in range(10000)]
    out=Path("verification/fp32/mul_stage_vectors.hex")
    with out.open("w") as f:
        for a,b,c in triples:
            sp,ep,sigp,sc,ec,sigc,ca,cb,cc=expected(a,b,c)
            f.write(f"{a:08x} {b:08x} {c:08x} {sp:x} {ep & 0x7ff:03x} {sigp:012x} {sc:x} {ec & 0x7ff:03x} {sigc:06x} {ca:x} {cb:x} {cc:x}\n")
    print(f"generated {len(triples)} bounded multiply-stage vectors")
if __name__=="__main__": main()
