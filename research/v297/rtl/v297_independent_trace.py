#!/usr/bin/env python3
"""Independent RTL trace oracle; no import from the JS simulators."""
import random
from collections import Counter
from pathlib import Path

def fits(pair_a, pair_b):
    return max(Counter(pair_a + pair_b).values()) <= 2

def greedy(valid, pairs, phase):
    chosen = []
    for step in range(3):
        i = (phase + step) % 3
        if not ((valid >> i) & 1) or len(chosen) == 2:
            continue
        if not chosen or fits(pairs[chosen[0]], pairs[i]):
            chosen.append(i)
    return sum(1 << i for i in chosen)

def make_trace(path):
    rng = random.Random(2971029)
    cool = False
    phase = 0
    cases = []
    # Complete 3-bank operand and validity enumeration (5832 patterns).
    for validity in range(8):
        for code in range(3**6):
            n, pairs = code, []
            for _ in range(3):
                a = n % 3; n //= 3
                b = n % 3; n //= 3
                pairs.append((a, b))
            cases.append((validity, pairs))
    # Random full 16-bank patterns, including same-bank double reads.
    for _ in range(12000):
        cases.append((rng.randrange(8), [(rng.randrange(16),rng.randrange(16))
                                         for _ in range(3)]))
    with Path(path).open('w') as f:
        for validity, pairs in cases:
            base = greedy(validity, pairs, 0)
            motif = base.bit_count() == 1 and validity & 0b110 == 0b110 and fits(pairs[1], pairs[2])
            rescued = bool(motif and not cool)
            candidate = 0b110 if rescued else base
            rotating = greedy(validity, pairs, phase)
            for grant in (candidate, rotating):
                assert (grant & ~validity) == 0
                assert grant.bit_count() <= 2
                selected = [pairs[i] for i in range(3) if (grant >> i) & 1]
                if len(selected) == 2:
                    assert fits(*selected)
            bank_a = sum(pair[0] << (4*i) for i,pair in enumerate(pairs))
            bank_b = sum(pair[1] << (4*i) for i,pair in enumerate(pairs))
            f.write(f"{validity:x} {bank_a:03x} {bank_b:03x} {candidate:x} {rotating:x}\n")
            cool = rescued
            phase = (phase + 1) % 3
    print(f"V297_RTL_ORACLE_GENERATED {len(cases)}")

if __name__ == "__main__":
    import sys
    make_trace(sys.argv[1] if len(sys.argv)>1 else "/tmp/v297_rtl_vectors.txt")
