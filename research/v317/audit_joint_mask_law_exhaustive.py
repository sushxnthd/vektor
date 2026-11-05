#!/usr/bin/env python3
"""Independent exhaustive audit of correlated two-bank co-issue law.

Synthetic zero-queue mathematics only; not RTL, physical closure or GPU IPC.
Enumerates all 9-cell joint probability tables on a denominator-4 grid.
"""
from fractions import Fraction
from itertools import combinations

MASKS = (1, 2, 3)
PAIRS = tuple((x, y) for x in MASKS for y in MASKS)

def compositions(total, slots):
    # Stars and bars, deterministic exhaustive nonnegative compositions.
    for bars in combinations(range(total + slots - 1), slots - 1):
        positions = (-1,) + bars + (total + slots - 1,)
        yield tuple(positions[i + 1] - positions[i] - 1 for i in range(slots))

def check(counts, denominator):
    joint = {pair: Fraction(n, denominator) for pair, n in zip(PAIRS, counts)}
    actual = sum((p * (2 if (x & y) == 0 else 1)
                  for (x, y), p in joint.items()), Fraction())
    opposite = joint[(1, 2)] + joint[(2, 1)]
    assert actual == 1 + opposite
    # The independence correction must use both request marginals.
    left_atomic = sum(p for (x, y), p in joint.items() if x == 3)
    right_atomic = sum(p for (x, y), p in joint.items() if y == 3)
    left_one = sum(p for (x, y), p in joint.items() if x == 1)
    left_two = sum(p for (x, y), p in joint.items() if x == 2)
    right_one = sum(p for (x, y), p in joint.items() if y == 1)
    right_two = sum(p for (x, y), p in joint.items() if y == 2)
    independent_opposite = left_one * right_two + left_two * right_one
    correlation = opposite - independent_opposite
    assert actual == 1 + independent_opposite + correlation
    # General bound on co-issue using singleton marginals.
    assert opposite <= min(left_one, right_two) + min(left_two, right_one)
    assert opposite >= max(Fraction(), left_one + right_two - 1)
    assert opposite >= max(Fraction(), left_two + right_one - 1)
    assert 0 <= left_atomic <= 1 and 0 <= right_atomic <= 1
    return actual

def main():
    total = 0
    seen = set()
    for counts in compositions(4, len(PAIRS)):
        seen.add(check(counts, 4))
        total += 1
    assert total == 495, total
    assert Fraction(1) in seen and Fraction(2) in seen
    print(f"PASS: {total} exact joint tables, service range {min(seen)}..{max(seen)}")
    print("Evidence tier: synthetic exact arithmetic; no physical performance claim")

if __name__ == "__main__":
    main()
