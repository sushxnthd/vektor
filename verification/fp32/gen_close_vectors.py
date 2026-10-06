"""Generate deterministic real-FP32 close-path accumulator vectors."""
from __future__ import annotations
import random
from pathlib import Path
from sim.vektor.fp32_stage_contract import classify, sig24, qexp

N=20000
SEED=0xC105E5090

def main():
    rng=random.Random(SEED); rows=[]; tries=0
    while len(rows)<N and tries<N*500:
        tries+=1
        a,b,c=(rng.getrandbits(32) for _ in range(3))
        if any(classify(x) not in ("zero","finite") for x in (a,b,c)): continue
        ps=((a>>31)^(b>>31))&1; cs=(c>>31)&1
        pm=sig24(a)*sig24(b); cm=sig24(c)
        if not pm or not cm: continue
        pe=qexp(a)+qexp(b); ce=qexp(c)
        lp=pm.bit_length()-1; lc=cm.bit_length()-1
        close=abs((pe+lp)-(ce+lc))<=1
        if not close: continue
        base=min(pe,ce); p=pm<<(pe-base); cv=cm<<(ce-base)
        assert p.bit_length()<=49 and cv.bit_length()<=49
        if ps==cs: mag=p+cv; ss=ps
        elif p>cv: mag=p-cv; ss=ps
        elif cv>p: mag=cv-p; ss=cs
        else: mag=0; ss=0
        # Same-sign addition can require bit 49; the current 49-bit close accumulator
        # is intended for cancellation/opposite-sign use only. Record only its contract.
        if ps==cs: continue
        assert mag.bit_length()<=49
        rows.append((ps,cs,pe,ce,pm,cm,ss,int(mag==0),mag))
    if len(rows)!=N: raise SystemExit(f"only generated {len(rows)} close vectors")
    out=Path("build/rtl/close_vectors.txt"); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w") as f:
        for r in rows:
            ps,cs,pe,ce,pm,cm,ss,z,mag=r
            f.write(f"{ps:x} {cs:x} {pe} {ce} {pm:012x} {cm:06x} {ss:x} {z:x} {mag:013x}\n")
    print(f"PASS generated {len(rows)} real-FP32 opposite-sign close vectors seed={SEED:#x} tries={tries}")
if __name__=="__main__": main()
