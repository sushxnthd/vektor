#!/usr/bin/env python3
"""FP32-CANCEL-015: quantify exact opposite-sign FMA cancellation geometry.

This is a representation/mechanism experiment, not an FMA implementation.
It constructs exact integer significands for finite FP32 a*b and c on a
common binary lattice, then measures exponent separation and cancelled
leading bits. Directed cases force deep cancellation; deterministic random
cases estimate how rarely that regime is entered by unguided traffic.
"""
import json, random

SEED = 0x5090
CASES = 1_000_000

def parts(u):
    sign = u >> 31
    exp = (u >> 23) & 0xff
    frac = u & 0x7fffff
    if exp == 0xff:
        return None
    if exp == 0:
        return sign, frac, -149
    return sign, (1 << 23) | frac, exp - 150

def finite(rng):
    while True:
        u = rng.getrandbits(32)
        if ((u >> 23) & 0xff) != 0xff:
            return u

def geometry(a,b,c):
    pa,pb,pc=parts(a),parts(b),parts(c)
    sa,ma,ea=pa; sb,mb,eb=pb; sc,mc,ec=pc
    if ma == 0 or mb == 0 or mc == 0 or (sa ^ sb) == sc:
        return None
    mp, ep = ma*mb, ea+eb
    # Compare positions of leading 1s before common-lattice expansion.
    lead_p = ep + mp.bit_length() - 1
    lead_c = ec + mc.bit_length() - 1
    lead_delta = abs(lead_p-lead_c)
    base=min(ep,ec)
    x=mp << (ep-base); y=mc << (ec-base)
    top=max(x.bit_length(),y.bit_length())
    r=abs(x-y)
    cancelled = top if r == 0 else top-r.bit_length()
    return lead_delta,cancelled

def main():
    rng=random.Random(SEED)
    # Exact cancellation and adjacent representable values establish that
    # cancellation can expose >=24 low-order bits.
    directed=[
      (0x3f800000,0x3f800000,0xbf800000),
      (0x3f800000,0x3f800000,0xbf7fffff),
      (0x3f800001,0x3f800000,0xbf800000),
      (0x00800000,0x3f800000,0x807fffff),
    ]
    hist_delta={}; hist_cancel={}; joint={}
    eligible=0; deep=0; max_cancel=-1; witness=None
    for i in range(CASES+len(directed)):
        t=directed[i] if i<len(directed) else (finite(rng),finite(rng),finite(rng))
        g=geometry(*t)
        if g is None: continue
        d,k=g; eligible+=1
        db=min(d,64); kb=min(k,64)
        hist_delta[db]=hist_delta.get(db,0)+1
        hist_cancel[kb]=hist_cancel.get(kb,0)+1
        joint[(db,kb)]=joint.get((db,kb),0)+1
        if k>=24: deep+=1
        if k>max_cancel:
            max_cancel=k; witness=[hex(x) for x in t]
    assert geometry(*directed[0])[1] >= 24
    assert geometry(*directed[1])[1] >= 23
    print(json.dumps({
      "experiment":"FP32-CANCEL-015","seed":SEED,"random_cases":CASES,
      "eligible_opposite_sign_nonzero":eligible,
      "deep_cancel_ge24":deep,"max_cancelled_leading_bits":max_cancel,
      "max_witness":witness,
      "lead_delta_hist":dict(sorted(hist_delta.items())),
      "cancel_hist":dict(sorted(hist_cancel.items())),
      "joint_nonzero":[[d,k,n] for (d,k),n in sorted(joint.items())],
    },sort_keys=True))

if __name__=="__main__":
    main()
