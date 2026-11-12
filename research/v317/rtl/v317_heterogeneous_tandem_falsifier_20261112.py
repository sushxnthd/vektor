#!/usr/bin/env python3
"""Exact counterexample: stage means do not determine finite-N tandem throughput.

Two single-server FIFO stages, compute then bank, with per-request service times.
No physical GPU performance claim. Independent exhaustive enumeration verifies
the event recurrence and finds equal-marginal workloads with unequal makespans.
"""
from fractions import Fraction as F
from itertools import permutations, product

def makespan(compute, bank):
    assert len(compute) == len(bank) and len(compute) > 0
    ca = cb = F(0)
    for a, b in zip(compute, bank):
        assert a > 0 and b > 0
        ca += a
        cb = max(ca, cb) + b
    return cb

def independent_dag(compute, bank):
    n = len(compute)
    # Longest path in the two-row precedence DAG, computed by explicit path splits.
    return max(sum(compute[:k+1]) + sum(bank[k:]) for k in range(n))

def homogeneous_proxy(compute, bank):
    n = len(compute)
    a = sum(compute) / n
    b = sum(bank) / n
    return a+b+(n-1)*max(a,b)

def main():
    for n in (2,3,4):
        for aa in product((F(1),F(2)), repeat=n):
            for bb in product((F(1),F(3)), repeat=n):
                assert makespan(aa,bb) == independent_dag(aa,bb)
    a = (F(1),F(1),F(1),F(1))
    b1 = (F(1),F(1),F(4),F(4))
    b2 = (F(4),F(4),F(1),F(1))
    assert sorted(b1) == sorted(b2)
    assert homogeneous_proxy(a,b1) == homogeneous_proxy(a,b2)
    assert makespan(a,b1) != makespan(a,b2)
    print("PASS exhaustive recurrence vs independent DAG path calculation")
    print("same per-stage marginals; different finite-N makespan:",
          makespan(a,b1), makespan(a,b2))
    print("homogeneous mean-based proxy (both):",homogeneous_proxy(a,b1))
    print("Scope: deterministic two-stage FIFO; no RTL, routing, or GPU IPC")
if __name__ == "__main__":
    main()
