#!/usr/bin/env python3
"""Independent exact leading-one specification for the seven-step search."""
import random

def candidate(v):
    t=v; k=0
    for s in (64,32,16,8,4,2):
        if t >> s:
            t >>= s
            k += s
    if t & 2:
        k += 1
    return k if v else -1

rng=random.Random(152)
values=list(range(1<<16)) + [0,1,(1<<64),(1<<65)-1]
values += [rng.getrandbits(65) for _ in range(100000)]
for i,v in enumerate(values):
    expected=v.bit_length()-1
    actual=candidate(v)
    if actual!=expected:
        raise AssertionError((i,v,expected,actual))
print(f'V152 independent leading-one: {len(values)}/{len(values)} PASS')
