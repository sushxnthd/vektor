#!/usr/bin/env python3
"""Independent control-equivalence gate. Python model only, not RTL or PPA."""
from itertools import product
import json, random

def proposed(valid_mask, addresses, tag_valid, tag):
    grant = forwarded = reads = 0
    for i, addr in enumerate(addresses):
        if not (valid_mask >> i) & 1: continue
        if tag_valid and addr == tag:
            grant |= 1 << i
            forwarded |= 1 << i
        elif reads < 2:
            grant |= 1 << i
            reads += 1
    return grant, forwarded, reads

def standard_operand_cache(valid_mask, addresses, cache_valid, cache_tag):
    hits = [bool(cache_valid and cache_tag == a) for a in addresses]
    misses = [i for i in range(4) if ((valid_mask >> i) & 1) and not hits[i]]
    selected = set(misses[:2])
    granted = [i for i in range(4) if ((valid_mask >> i) & 1) and (hits[i] or i in selected)]
    forwarded = [i for i in granted if hits[i]]
    return sum(1 << i for i in granted), sum(1 << i for i in forwarded), len(selected)

n = 0
for addresses in product(range(4), repeat=4):
    for mask in range(16):
        for valid in range(2):
            for tag in range(4):
                assert proposed(mask, addresses, valid, tag) == standard_operand_cache(mask, addresses, valid, tag)
                n += 1
rng = random.Random(28838)
for _ in range(100000):
    addresses = [rng.randrange(4096) for _ in range(4)]
    mask, valid = rng.randrange(16), rng.randrange(2)
    tag = rng.choice(addresses) if rng.random() < .6 else rng.randrange(4096)
    assert proposed(mask, addresses, valid, tag) == standard_operand_cache(mask, addresses, valid, tag)
print(json.dumps({"mechanism":"V288","evidence":"E0 independent Python control equivalence","exhaustive_AW2_cases":n,"random_AW12_cases":100000,"mismatches":0,"control":"same-budget one-entry write-through operand cache"},indent=2))
