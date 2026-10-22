#!/usr/bin/env python3
"""Training-only, independent lane-mask admission oracle. Holdouts unopened."""
import json, random
rng=random.Random(29220261023)
def dut(a,b,credits,ma,mb):
    accept_a=bool(a and credits>0)
    accept_b=bool(accept_a and b and credits>=2 and not (ma&mb))
    return accept_a,accept_b
def oracle(a,b,credits,ma,mb):
    if not a or credits==0:return False,False
    if not b or credits==1:return True,False
    for lane in range(32):
        if (ma>>lane)&1 and (mb>>lane)&1:return True,False
    return True,True
for i in range(50000):
    a=rng.randrange(2);b=rng.randrange(2);credits=rng.randrange(3)
    ma=rng.getrandbits(32);mb=rng.getrandbits(32)
    if i%5==0:mb=(~ma)&0xffffffff
    assert dut(a,b,credits,ma,mb)==oracle(a,b,credits,ma,mb)
print(json.dumps({"kernel":"V292","random_checks":50000,"mismatches":0,
 "holdouts_evaluated":False,"evidence":"E0 combinational functional only"}))
