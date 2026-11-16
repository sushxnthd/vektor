#!/usr/bin/env python3
"""Independent bounded-lookahead benefit/overhead boundary, NOT routed GPU evidence.

A deliberately small deterministic FIFO queue model. Two banks, one request
per bank per cycle, max two requests/cycle, 4-entry lookahead. The comparator
is adjacent-only pairing. Both drain the identical finite input stream.
The lookahead policy always serves the head and then the earliest compatible
request among the next three. It is NOT a matched-area implementation.
"""
from fractions import Fraction
from itertools import product

def drain(stream, depth):
    queue = list(stream)
    cycles = 0
    while queue:
        first = queue.pop(0)
        for index, bank in enumerate(queue[:depth-1]):
            if bank != first:
                queue.pop(index)
                break
        cycles += 1
    return cycles

def required_overhead_headroom(stream):
    adjacent = drain(stream, 2)
    lookahead = drain(stream, 4)
    # With equal completed work, candidate wins throughput/area iff
    # (T_candidate/T_base)*(A_candidate/A_base) < adjacent/lookahead.
    return Fraction(adjacent, lookahead)

def audit():
    assert required_overhead_headroom([0,0,1,1]*32) == Fraction(65,64)
    assert required_overhead_headroom([0,1]*64) == 1
    assert required_overhead_headroom([0]*128) == 1
    # A hypothetical 1% area and 1% clock penalty already destroys
    # the clustered workload's modest scheduling advantage.
    assert Fraction(101,100)**2 > Fraction(65,64)
    counts = {}
    for n in range(2, 11):
        wins = ties = losses = 0
        for stream in product((0,1), repeat=n):
            a = drain(stream, 2)
            b = drain(stream, 4)
            wins += b < a
            ties += b == a
            losses += b > a
            assert required_overhead_headroom(stream) == Fraction(a,b)
        assert wins + ties + losses == 2**n
        assert losses == 0  # model-specific monotonicity, not a hardware theorem
        counts[n] = wins
    assert counts[10] == 484
    print("PASS: independent finite-stream scheduler audit")
    print("length-10 improved streams:", counts[10], "/ 1024")
    print("clustered 0011 threshold:", required_overhead_headroom([0,0,1,1]*32))
    print("1% area * 1% clock penalty: NO WIN")
    print("LIMIT: no RTL, occupancy, wires, port arbitration, or physical timing.")

if __name__ == "__main__":
    audit()
