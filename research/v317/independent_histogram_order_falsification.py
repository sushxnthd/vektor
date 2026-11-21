"""Independent bounded-queue counterexample to bank-histogram-only throughput laws.

Requests are atomic sets of bank reads. Each cycle: append arrivals, select up
to two requests, one read port per bank, output capacity two; unselected requests
remain queued. Greedy selects earliest feasible requests. Exact per-cycle
packing maximizes completed requests, ties broken by earlier queue indices.
Synthetic service analysis, not GPU IPC or physical RTL evidence.
"""
from itertools import combinations, product

DEMANDS = ((0,), (1,), (0, 1))

def grant(queue, optimal=False):
    candidates = []
    for k in range(min(2, len(queue)) + 1):
        for indices in combinations(range(len(queue)), k):
            banks = [b for i in indices for b in queue[i]]
            if len(banks) == len(set(banks)):
                candidates.append(indices)
    if optimal:
        chosen = min(candidates, key=lambda x: (-len(x), x))
    else:
        chosen = []
        occupied = set()
        for i, req in enumerate(queue):
            if len(chosen) < 2 and not occupied.intersection(req):
                chosen.append(i)
                occupied.update(req)
    return tuple(queue[i] for i in range(len(queue)) if i not in chosen), len(chosen)

def simulate(trace, optimal=False):
    queue = ()
    served = 0
    for arrivals in trace:
        queue += arrivals
        queue, n = grant(queue, optimal)
        served += n
    return served, queue

def main():
    count = 0
    witness = None
    for n in range(1, 7):
        groups = {}
        for seq in product(DEMANDS, repeat=n):
            key = tuple(sorted(seq))
            g, _ = simulate((seq,))
            groups.setdefault(key, set()).add(g)
        for key, vals in groups.items():
            count += 1
            if len(vals) > 1 and witness is None:
                witness = (key, min(vals), max(vals))
    assert witness is not None
    a = ((0, 1), (0,), (1,))
    b = ((0,), (1,), (0, 1))
    assert sorted(a) == sorted(b)
    assert simulate((a,))[0] == 1
    assert simulate((b,))[0] == 2
    assert simulate((a,), optimal=True)[0] == 2
    assert simulate((b,), optimal=True)[0] == 2
    print(f'PASS: {count} bank-demand multiset classes enumerated; first varying class={witness}')
    print('FALSIFIED: bank-demand histogram alone determines greedy one-cycle service')
    print('LIMIT: synthetic one-cycle model; no physicality, GPU IPC, or online-horizon claim')

if __name__ == '__main__':
    main()
