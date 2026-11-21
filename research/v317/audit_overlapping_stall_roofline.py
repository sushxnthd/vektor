#!/usr/bin/env python3
"""Falsify unsafe multiplicative throughput ceilings under overlapping stalls.

A proposed ceiling min(bank, issue, output, memory) * occupancy * (1-overhead)
is NOT universally an upper bound: occupancy and control-overhead fractions
can overlap, and an 'occupancy' fraction need not bound peak service rate.
This checker supplies constructive cycle traces and a safe alternative when
independent per-cycle service ceilings and measured eligible-cycle counts exist.
Synthetic proof/counterexample only; no RTL or GPU throughput evidence.
"""
from fractions import Fraction
from itertools import product

def evaluate(capacity, active, control_blocked, grants):
    n = len(active)
    assert n and len(control_blocked) == n and len(grants) == n
    assert isinstance(capacity, int) and capacity > 0
    assert all(isinstance(x, bool) for x in active + control_blocked)
    assert all(isinstance(g, int) and 0 <= g <= capacity for g in grants)
    assert all(g == 0 if (not a or b) else True
               for a, b, g in zip(active, control_blocked, grants))
    occupancy = Fraction(sum(active), n)
    overhead = Fraction(sum(control_blocked), n)
    naive = capacity * occupancy * (1 - overhead)
    eligible = sum(a and not b for a, b in zip(active, control_blocked))
    safe = Fraction(capacity * eligible, n)
    actual = Fraction(sum(grants), n)
    assert actual <= safe
    return dict(actual=actual, naive=naive, safe=safe,
                occupancy=occupancy, overhead=overhead)

def main():
    # Every blocked cycle is already inactive; multiplication double-counts
    # the same lost service and wrongly excludes a feasible workload.
    a = [True, True, False, False]
    b = [False, False, True, True]
    g = [1, 1, 0, 0]
    example = evaluate(1, a, b, g)
    assert example["actual"] == Fraction(1, 2)
    assert example["naive"] == Fraction(1, 4)
    assert example["safe"] == Fraction(1, 2)
    violations = 0
    checked = 0
    # Exhaustively enumerate four-cycle active/blocked masks, grant all
    # eligible cycles, and independently recompute eligible-cycle bound.
    for active_bits in product((False, True), repeat=4):
        for blocked_bits in product((False, True), repeat=4):
            grants = [int(a and not b) for a, b in zip(active_bits, blocked_bits)]
            result = evaluate(1, list(active_bits), list(blocked_bits), grants)
            checked += 1
            if result["actual"] > result["naive"]:
                violations += 1
            assert result["actual"] <= result["safe"]
    assert checked == 256 and violations > 0
    print("PASS: 256 synthetic traces; unsafe multiplicative ceiling violated on",
          violations, "traces")
    print("Counterexample: actual=1/2, naive ceiling=1/4, eligible-cycle ceiling=1/2")
    print("Inference: never kill hardware using independent occupancy*overhead"
          " multipliers without proving non-overlap/conditional semantics.")
    print("No RTL, synthesis, GPU measurement, or real-workload result.")

if __name__ == "__main__":
    main()
