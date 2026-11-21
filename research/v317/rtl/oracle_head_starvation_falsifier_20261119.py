"""Exact two-bank head-starvation counterexample for the zero-cost four-slot oracle.
No hardware or GPU speedup is claimed. Run: python research/v317/rtl/oracle_head_starvation_falsifier_20261119.py
"""
from itertools import product, combinations

def select(queue, oracle):
    best = ()
    if oracle:
        for n in range(len(queue)+1):
            for ids in combinations(range(len(queue)), n):
                use = [0, 0]
                for i in ids:
                    for b in queue[i]: use[b] += 1
                if max(use) <= 2 and len(ids) > len(best): best = ids
        return best
    use = [0, 0]
    selected = []
    for i, pair in enumerate(queue):
        nxt = use.copy()
        for b in pair: nxt[b] += 1
        if max(nxt) <= 2:
            selected.append(i)
            use = nxt
    return tuple(selected)

def main():
    more = bypass = 0
    example = None
    for flat in product(range(2), repeat=8):
        queue = tuple(tuple(flat[i:i+2]) for i in range(0, 8, 2))
        greedy, oracle = select(queue, False), select(queue, True)
        assert len(oracle) >= len(greedy)
        for ids in (greedy, oracle):
            assert all(sum(queue[i].count(b) for i in ids) <= 2 for b in range(2))
        more += len(oracle) > len(greedy)
        if oracle and 0 not in oracle:
            bypass += 1
            if example is None: example = (queue, greedy, oracle)
    assert (more, bypass) == (52, 52)
    assert example == (((0,0),(0,0),(0,1),(0,1)),(0,),(2,3))
    # Construct a perpetual two-arrivals/two-grants schedule.
    # Queue remains [old (0,0), (0,0), (0,1), (0,1)] forever.
    queue = [(0,0),(0,0),(0,1),(0,1)]
    for _ in range(1000):
        ids = select(queue, True)
        assert ids == (2,3) and 0 not in ids
        for i in reversed(ids): queue.pop(i)
        queue.extend([(0,1),(0,1)])
        assert len(queue) == 4
    print("PASS: 256 exhaustive assignments; 52 oracle-gain/head-bypass cases")
    print("PASS: oldest request starves for 1000 cycles under repeated legal arrivals")
    print("WITNESS:", example)

if __name__ == "__main__": main()
