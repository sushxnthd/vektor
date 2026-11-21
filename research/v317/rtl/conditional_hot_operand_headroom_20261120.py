#!/usr/bin/env python3
"""Exact conditional service headroom by hot-bank operand count; synthetic oracle only."""
from itertools import product, combinations

def legal(q, subset):
    count = {}
    for i in subset:
        for bank in q[i]:
            count[bank] = count.get(bank, 0) + 1
            if count[bank] > 2:
                return False
    return True

def greedy(q):
    chosen = ()
    for i in range(4):
        if legal(q, chosen + (i,)):
            chosen += (i,)
    return chosen

def oldest_protected(q):
    return max((s for k in range(1, 5)
                for s in combinations(range(4), k)
                if 0 in s and legal(q, s)),
               key=lambda s: (len(s), tuple(-i for i in s)))

def audit(banks=4):
    buckets = {h: [0, 0, 0] for h in range(9)}
    for operands in product(range(banks), repeat=8):
        q = [operands[2*i:2*i+2] for i in range(4)]
        g, p = greedy(q), oldest_protected(q)
        assert legal(q, g) and legal(q, p) and 0 in p
        delta = len(p) - len(g)
        assert 0 <= delta <= 1
        bucket = buckets[operands.count(0)]
        bucket[0] += 1
        bucket[1] += len(g)
        bucket[2] += delta
    assert sum(x[0] for x in buckets.values()) == banks**8
    assert sum(x[1] for x in buckets.values()) == 171076
    assert sum(x[2] for x in buckets.values()) == 2496
    for hot, (cases, base, extra) in buckets.items():
        print(hot, cases, base, extra, f"{1+extra/base:.9f}")
    assert buckets[3] == [13608, 36246, 816]
    assert all(buckets[h][2] == 0 for h in (5,6,7,8))
    print("PASS exact conditional enumeration")

if __name__ == "__main__":
    audit()
