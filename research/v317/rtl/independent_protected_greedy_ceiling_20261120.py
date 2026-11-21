"""Independent exhaustive oldest-protected vs scan-greedy service audit.

Reproduction: python3 research/v317/rtl/independent_protected_greedy_ceiling_20261120.py
Four requests, two operand reads/request, two ports/bank, ordered bank pairs.
No external dependencies. No RTL, timing, power or workload throughput claim.

Independent local execution 2026-11-20:
banks assignments greedy protected delta_histogram protected/greedy
2 256 442 442 {0:256} 1.000000000
3 6561 14391 14667 {0:6285,1:276} 1.019178653
4 65536 171076 173572 {0:63040,1:2496} 1.014590007

Falsification: under uniformly enumerated ordered bank assignments, even
a zero-cost oldest-protected maximum-cardinality oracle cannot achieve the
frozen 1.02x materiality threshold for bank counts 2, 3, or 4.
This is not a universal no-win proof for nonuniform workloads or larger banks.
Unlike earlier protected-vs-unrestricted comparisons, this directly compares
the protected oracle to the actual scan-greedy reference.
"""
from itertools import product, combinations
from collections import Counter
from fractions import Fraction

def feasible(q, ids, banks, ports=2):
    used = [0] * banks
    for i in ids:
        for bank in q[i]:
            used[bank] += 1
            if used[bank] > ports:
                return False
    return True

def greedy(q, banks):
    selected = []
    for i in range(len(q)):
        if feasible(q, selected + [i], banks):
            selected.append(i)
    return tuple(selected)

def protected(q, banks):
    options = (ids for k in range(1, len(q) + 1)
               for ids in combinations(range(len(q)), k)
               if 0 in ids and feasible(q, ids, banks))
    return min(options, key=lambda ids: (-len(ids), ids))

def run():
    expected = {2: (256, 442, 442, 0),
                3: (6561, 14391, 14667, 276),
                4: (65536, 171076, 173572, 2496)}
    for banks in (2, 3, 4):
        count = greedy_total = protected_total = 0
        histogram = Counter()
        for flat in product(range(banks), repeat=8):
            q = tuple((flat[2*i], flat[2*i+1]) for i in range(4))
            g, p = greedy(q, banks), protected(q, banks)
            assert feasible(q, g, banks) and feasible(q, p, banks)
            assert p and 0 in p and len(p) >= len(g)
            histogram[len(p)-len(g)] += 1
            greedy_total += len(g)
            protected_total += len(p)
            count += 1
        assert (count, greedy_total, protected_total, histogram[1]) == expected[banks]
        assert Fraction(protected_total, greedy_total) < Fraction(102, 100)
        print(banks, count, greedy_total, protected_total,
              dict(sorted(histogram.items())),
              str(Fraction(protected_total, greedy_total)))
    print("PASS: exhaustive independent protected-vs-greedy ceiling audit")

if __name__ == "__main__":
    run()
