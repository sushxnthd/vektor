"""Exact bounded-wait audit for a four-entry bank queue; mathematical control only.

Every request has two bank reads; each bank has two read ports. A scheduler
must serve the oldest entry on every nonempty cycle and maximizes simultaneous
service among feasible subsets, with lexicographic ties. FIFO survivors retain
order and new arrivals append. This is not a synthesized implementation.
"""
from itertools import combinations, product
from collections import Counter
from fractions import Fraction


def feasible(queue, selected):
    usage = Counter(b for i in selected for b in queue[i][1])
    return all(v <= 2 for v in usage.values())


def select(queue, protected):
    n = len(queue)
    choices = (ids for k in range(n + 1) for ids in combinations(range(n), k))
    choices = (ids for ids in choices if feasible(queue, ids) and
               (not protected or not queue or 0 in ids))
    return min(choices, key=lambda ids: (-len(ids), ids))


def exact(banks):
    counts = [0, 0]
    strict_advantage = 0
    for flat in product(range(banks), repeat=8):
        queue = tuple((i, (flat[2*i], flat[2*i+1])) for i in range(4))
        p = select(queue, True)
        u = select(queue, False)
        assert p and 0 in p and feasible(queue, p)
        assert len(u) >= len(p)
        counts[0] += len(p)
        counts[1] += len(u)
        strict_advantage += len(u) > len(p)
    return counts, strict_advantage


def adversarial(banks, steps=1000):
    for seed in range(17):
        next_id = 0
        queue = []
        ages = {}
        for t in range(steps):
            while len(queue) < 4:
                pair = ((next_id * 7 + seed + t) % banks,
                        (next_id * 11 + 3 * seed + t) % banks)
                queue.append((next_id, pair))
                ages[next_id] = t
                next_id += 1
            selected = select(queue, True)
            assert 0 in selected
            for i in selected:
                ident = queue[i][0]
                assert t - ages.pop(ident) <= 3
            queue = [v for i, v in enumerate(queue) if i not in selected]


def test():
    for b in (2, 3):
        counts, advantage = exact(b)
        print('banks', b, 'protected', counts[0], 'unrestricted', counts[1],
              'oracle/protected', str(Fraction(counts[1], counts[0])),
              'strict_gap_cases', advantage)
        adversarial(b)
    print('PASS exact feasibility and 17 x 1000-cycle bounded-wait traces per bank count')


if __name__ == '__main__':
    test()
