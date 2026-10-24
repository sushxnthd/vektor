#!/usr/bin/env python3
"""Independent full-physical-tag checker, not a substitute for RTL/STA."""
import json
import random
from collections import Counter

def reference(valid, tags):
    active = [i for i in range(4) if (valid >> i) & 1]
    if not active:
        return False, 0, 0
    chosen = tags[active[0]]
    served = sum(1 << i for i in active if tags[i] == chosen)
    return True, chosen, served

def multicast(valid, tags):
    if not valid:
        return False, 0, 0
    leader = next(i for i in range(4) if valid & (1 << i))
    t = tags[leader]
    return True, t, sum(1 << i for i in range(4) if (valid & (1 << i)) and tags[i] == t)

rng = random.Random(29120261023)
stats = Counter()
for v in range(16):
    for p in range(256):
        tags = [(p >> (2*i)) & 3 for i in range(4)]
        assert reference(v,tags) == multicast(v,tags)
        stats["exhaustive"] += 1
for _ in range(100000):
    v = rng.randrange(16)
    tags = [rng.randrange(65536) for _ in range(4)]
    if rng.random() < .4: tags[1] = tags[0]
    if rng.random() < .4: tags[2] = tags[0]
    if rng.random() < .4: tags[3] = tags[0]
    if rng.random() < .2: tags[1] = tags[0] ^ 0x0100
    assert reference(v,tags) == multicast(v,tags)
    stats["random"] += 1
    stats["duplicate_grants"] += int(multicast(v,tags)[2].bit_count() > 1)
print(json.dumps({"mechanism":"V291","status":"equal-budget functional identity",
                  "exhaustive":stats["exhaustive"],"random":stats["random"],
                  "random_duplicate_grants":stats["duplicate_grants"],
                  "mismatches":0,"seed":29120261023},indent=2))
