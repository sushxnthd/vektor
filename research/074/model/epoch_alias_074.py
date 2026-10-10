#!/usr/bin/env python3
"""Vektor-074 finite epoch alias witness. Synthetic protocol model, not RTL."""
import json
import random
from pathlib import Path

def first_alias(bits, limit, drain=False):
    if drain: return None  # An old copy is retained; gate must stall.
    for generation in range(1, limit + 1):
        if generation % (1 << bits) == 0:
            return generation
    return None

def lease_case(bits, quarantine, lifetime):
    wrap_age = quarantine * (1 << bits)
    return dict(bits=bits, quarantine=quarantine, lifetime=lifetime,
                first_wrap_age=wrap_age, unsafe=wrap_age < lifetime)

def main():
    widths=[]
    for bits in range(1, 9):
        observed=first_alias(bits, (1 << bits) + 1)
        assert observed == 1 << bits
        assert first_alias(bits, (1 << bits)-1) is None
        assert first_alias(bits, (1 << bits)+1, drain=True) is None
        widths.append(dict(bits=bits, prediction=1 << bits,
                           observation=observed, residual=0,
                           reset_alias_if_old_packet_survives=True))
    leases=[]
    for bits in range(1,7):
        for q in (1,2,4,8):
            for lifetime in (2,5,17,65):
                r=lease_case(bits,q,lifetime)
                assert r['unsafe'] == (r['first_wrap_age'] < lifetime)
                leases.append(r)
    rng=random.Random(74011)
    exploratory=[]
    for _ in range(16):
        bits=rng.randrange(1,10)
        q=rng.randrange(1,15)
        lifetime=rng.randrange(1,2000)
        retained=bool(rng.randrange(2))
        exploratory.append(dict(**lease_case(bits,q,lifetime),
                                old_packet_retained_across_reset=retained,
                                reset_alias=retained))
    result=dict(scope="one UID, physical old packet held at independent replay source",
                predictions=["first alias at 2**bits",
                             "complete drain prevents reuse while packet survives",
                             "volatile epoch reset aliases if old packet survives",
                             "certified lifetime boundary Q*2**bits >= L"],
                widths=widths, leases=leases, exploratory=exploratory,
                counts=dict(widths=len(widths), lease_cases=len(leases),
                            exploratory=len(exploratory)))
    Path(__file__).with_name("results_074.json").write_text(json.dumps(result,indent=2)+"\n")
    print("V074_MODEL_PASS",result['counts'])

if __name__=="__main__":
    main()
