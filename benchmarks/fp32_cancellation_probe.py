"""FP32-FMA-002 negative control: pre-subtraction sticky compression.

This is deliberately NOT a production FMA.  It asks whether replacing all discarded
low bits by one sticky bit before an opposite-sign subtraction preserves the exact
post-cancellation integer.  A counterexample falsifies that compression rule.
"""
from __future__ import annotations
import random
from sim.vektor.fp32_stage_contract import classify, sig24, qexp

def exact_terms(a:int,b:int,c:int):
    ep=qexp(a)+qexp(b); ec=qexp(c)
    p=sig24(a)*sig24(b); cs=sig24(c)
    e=min(ep,ec)
    return p << (ep-e), cs << (ec-e), e

def compress_sticky(x:int, keep:int):
    n=x.bit_length()
    if n<=keep: return x,0
    sh=n-keep
    hi=x>>sh
    sticky=1 if (x & ((1<<sh)-1)) else 0
    # Deliberately naive: encode all discarded information as the LSB.
    return (hi|sticky)<<sh,sh

def find_counterexample(seed=0x5090, trials=200000, keep=52):
    rng=random.Random(seed)
    for i in range(trials):
        a,b,c=(rng.getrandbits(32) for _ in range(3))
        if any(classify(x) not in ("zero","finite") for x in (a,b,c)): continue
        if (((a>>31)^(b>>31)) == (c>>31)): continue
        p,cv,e=exact_terms(a,b,c)
        pc,_=compress_sticky(p,keep); cc,_=compress_sticky(cv,keep)
        exact=p-cv; naive=pc-cc
        if exact != naive:
            return {"trial":i,"a":a,"b":b,"c":c,"common_exp":e,
                    "exact":exact,"naive":naive,
                    "exact_bits":abs(exact).bit_length(),"naive_bits":abs(naive).bit_length()}
    return None

def main():
    r=find_counterexample()
    if r is None: raise SystemExit("no counterexample found")
    print("COUNTEREXAMPLE", " ".join(f"{k}={v:#x}" if isinstance(v,int) and k in {"a","b","c"} else f"{k}={v}" for k,v in r.items()))

if __name__=="__main__": main()
