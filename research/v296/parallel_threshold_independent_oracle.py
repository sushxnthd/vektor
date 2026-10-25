#!/usr/bin/env python3
"""Independent occupancy oracle for the V296 parallel-threshold topology.

Checks greedy two-read-port resource accounting against the proposed hit
threshold formulation, without using the Verilog implementation. This is a
software semantics test, not evidence of physical timing or power.
"""
import itertools
import random


def occupancy(valid, a, b):
    counts = [0] * 16
    grant = 0
    for i in range(4):
        if not (valid >> i) & 1:
            continue
        x, y = a[i], b[i]
        fit = counts[x] == 0 if x == y else counts[x] < 2 and counts[y] < 2
        if fit:
            grant |= 1 << i
            counts[x] += 1
            counts[y] += 1
    return grant


def threshold(valid, a, b):
    grant = 0
    for i in range(4):
        hits_x = []
        hits_y = []
        for j in range(i):
            if (grant >> j) & 1:
                hits_x.extend((a[j] == a[i], b[j] == a[i]))
                hits_y.extend((a[j] == b[i], b[j] == b[i]))
        if a[i] == b[i]:
            fit = not any(hits_x)
        else:
            fit = sum(hits_x) < 2 and sum(hits_y) < 2
        if (valid >> i) & 1 and fit:
            grant |= 1 << i
    return grant


def run():
    checked = 0
    for banks in itertools.product(range(3), repeat=8):
        a, b = banks[::2], banks[1::2]
        for valid in range(16):
            assert occupancy(valid, a, b) == threshold(valid, a, b), (valid, a, b)
            checked += 1
    assert checked == 104976
    rng = random.Random(0x2960CAFE)
    for _ in range(60000):
        a = [rng.randrange(16) for _ in range(4)]
        b = [rng.randrange(16) for _ in range(4)]
        valid = rng.randrange(16)
        assert occupancy(valid, a, b) == threshold(valid, a, b), (valid, a, b)
        checked += 1
    assert checked == 164976
    print(f"V296_INDEPENDENT_MATH_ORACLE_PASS cases={checked}")


if __name__ == "__main__":
    run()
