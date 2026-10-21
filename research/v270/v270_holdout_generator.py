#!/usr/bin/env python3
"""Frozen unopened holdout generator for V270; do not run before mapped-PPA prediction lock."""
import random
import json
import sys

def gen(seed,kind,n=512):
    rng=random.Random(seed)
    for _ in range(n):
        if kind=='positive': a,b=rng.choice([(6,2),(2,6)])
        elif kind=='negative': a,b=rng.choice([(5,3),(3,5)])
        elif kind=='divergent': a,b=rng.choice([(4,4),(6,2),(5,3)])
        else: raise ValueError(kind)
        op0=rng.randrange(4)
        op1=op0 if kind!='divergent' or rng.random()<0.4 else (op0+rng.randrange(1,4))%4
        yield {'a':a,'b':b,'op0':op0,'op1':op1}

if __name__=='__main__':
    kind=sys.argv[1]
    seed={'positive':270101,'negative':270102,'divergent':270103}[kind]
    print(json.dumps(list(gen(seed,kind))))
