#!/usr/bin/env python3
"""Frozen, unopened V268 workload generator. Outputs only active masks."""
import random, sys, json
seed = int(sys.argv[1])
assert seed in (268101,268102,268103)
r = random.Random(seed)
if seed == 268101:
    masks = [((1 << r.randint(1,8)) - 1) << (8*r.randrange(4)) for _ in range(4096)]
elif seed == 268102:
    masks = [(1 << 32)-1 for _ in range(4096)]
else:
    masks = [sum(1 << (8*i + r.randrange(8)) for i in range(4)) for _ in range(4096)]
print(json.dumps({"seed":seed,"masks":masks},separators=(',',':')))
