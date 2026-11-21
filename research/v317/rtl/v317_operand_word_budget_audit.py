#!/usr/bin/env python3
"""V317 retained-operand *word* accounting audit (abstract, not RTL).

A live request with one operand read holds one operand word; a fully read
request blocked on return holds TWO. Counting either as one request slot is
not equivalent to an equal-bit storage budget. No architecture speedup is
claimed. This checker is intentionally independent of the scheduling DP.
"""
from itertools import product

def occupancy(ready, done, n):
    partial = full = words = 0
    for i in range(n):
        if done & (1 << i):
            continue
        bits = (ready >> (2*i)) & 3
        partial += bits in (1, 2)
        full += bits == 3
        words += bits.bit_count()
    return partial, full, words

def audit():
    states = 0
    mismatches = 0
    for n in range(1, 6):
        for operands in product(range(4), repeat=n):
            ready = sum(v << (2*i) for i,v in enumerate(operands))
            for done in range(1 << n):
                p, f, words = occupancy(ready, done, n)
                assert words == p + 2*f
                assert words >= p + f
                assert words <= 2*(p+f)
                if f:
                    assert words > p+f
                    mismatches += 1
                states += 1
    # Two fully-read requests, one return grant: one pending request
    # requires two operand words, despite occupying one request slot.
    p, f, words = occupancy(0b1111, 0b0001, 2)
    assert (p, f, words) == (0, 1, 2)
    # An equal-bit comparator with only one operand-word of storage cannot
    # accept that pending request; a one-request-slot model can.
    assert p + f <= 1 and words > 1
    print("PASS states=%d full-state-accounting-mismatches=%d" % (states,mismatches))
    print("BOUND: retained_words = partial_requests + 2*fully_read_pending")
    print("LIMIT: request-slot count is not a matched storage-bit budget;")
    print("      no timing, physical area, power, or workload gain measured")

if __name__ == "__main__":
    audit()
