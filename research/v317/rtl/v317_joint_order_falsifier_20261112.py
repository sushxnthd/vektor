"""Exact finite-workload falsification: marginals do not determine FIFO throughput.

Synthetic model only; not RTL, routing, or GPU measurements.
Two non-preemptive FIFO stages, compute followed by bank, infinite interstage buffer.
All values are rational. Candidate scales bank service by R, all stage times by c,
and may impose a minimum candidate issue spacing h (in pre-inflation cycles).
"""
from fractions import Fraction as F
from itertools import permutations, product

def makespan(compute, bank, issue=F(0)):
    assert len(compute) == len(bank) and len(compute) > 0
    assert all(x > 0 for x in compute + bank) and issue >= 0
    ready = F(0)
    bank_done = F(0)
    for i, (a, b) in enumerate(zip(compute, bank)):
        ready = max(ready, i * issue) + a
        bank_done = max(bank_done, ready) + b
    return bank_done

def independent_longest_path(compute, bank, issue=F(0)):
    # Longest path in a DAG: issue nodes -> compute nodes -> bank nodes.
    n = len(compute)
    starts = [i * issue for i in range(n)]
    comp = [F(0)] * n
    done = [F(0)] * n
    for i in range(n):
        comp[i] = max(starts[i], comp[i-1] if i else F(0)) + compute[i]
        done[i] = max(comp[i], done[i-1] if i else F(0)) + bank[i]
    return done[-1]

def speedup(a, b, r=F(2), c=F(1), h=F(0)):
    assert r > 0 and c > 0
    return makespan(a, b) / (c * makespan(a, tuple(x/r for x in b), h))

def distinct_orders(values):
    return sorted(set(permutations(values)))

def envelope(a_values, b_values, r, c, h):
    # Exhaust both within-stage ordering and cross-stage pairing.
    vals = [(speedup(a,b,r,c,h), a,b)
            for a in distinct_orders(a_values) for b in distinct_orders(b_values)]
    return min(vals), max(vals)

def main():
    checks = 0
    for n in (2,3,4):
        for a in product((F(1),F(2)), repeat=n):
            for b in product((F(1),F(3)), repeat=n):
                for h in (F(0),F(2)):
                    assert makespan(a,b,h) == independent_longest_path(a,b,h)
                    checks += 1
    a = (F(1),F(1),F(4),F(4))
    b = (F(1),F(1),F(4),F(4))
    lo, hi = envelope(a,b,F(2),F(101,100),F(0))
    assert lo[0] <= hi[0]
    assert lo[0] != hi[0], 'Expected an ordering-sensitive speedup interval'
    scores = [speedup(x,y,F(2),F(101,100))
              for x in distinct_orders(a) for y in distinct_orders(b)]
    assert lo[0] == min(scores) and hi[0] == max(scores)
    print('PASS independent recurrence comparisons:', checks)
    print('Fixed compute/bank marginals, distinct pairings:', len(scores))
    print('Min speedup:', lo[0], float(lo[0]), 'compute:', lo[1], 'bank:', lo[2])
    print('Max speedup:', hi[0], float(hi[0]), 'compute:', hi[1], 'bank:', hi[2])
    print('Scope: synthetic finite FIFO; physical validation NOT established')

if __name__ == '__main__':
    main()
