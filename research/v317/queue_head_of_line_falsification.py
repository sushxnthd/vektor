"""Exact synthetic falsification: queue order can loosen an optimistic service bound.

Two source FIFOs, fixed per-request release cycles, one issue/output slot
per cycle, and two single-port banks. No arrivals. The order-free comparator
has identical requests and resources but may skip a blocked FIFO head.
This is NOT a GPU measurement, RTL result, or electrical closure.
"""
from functools import lru_cache
from itertools import product

def optimal_completion(queues, horizon, preserve_order=True):
    queues = tuple(tuple(q) for q in queues)
    @lru_cache(None)
    def solve(t, remaining):
        if t == horizon:
            return 0
        best = solve(t + 1, remaining)
        for source, q in enumerate(remaining):
            candidates = (0,) if preserve_order else range(len(q))
            for index in candidates:
                if index >= len(q) or q[index][1] > t:
                    continue
                next_state = list(remaining)
                next_state[source] = q[:index] + q[index + 1:]
                best = max(best, 1 + solve(t + 1, tuple(next_state)))
        return best
    return solve(0, queues)

def audit():
    witness = (((0, 2), (1, 0)),)
    ordered = optimal_completion(witness, 2, True)
    relaxed = optimal_completion(witness, 2, False)
    assert (ordered, relaxed) == (0, 1)
    cases = loose = 0
    for releases in product(range(3), repeat=4):
        for banks in product(range(2), repeat=4):
            qs = (tuple(zip(banks[:2], releases[:2])),
                  tuple(zip(banks[2:], releases[2:])))
            actual = optimal_completion(qs, 3, True)
            upper = optimal_completion(qs, 3, False)
            assert actual <= upper
            cases += 1
            loose += actual < upper
    assert (cases, loose) == (1296, 432)
    return {"witness_ordered": ordered, "witness_relaxed": relaxed,
            "cases": cases, "strictly_loose": loose}

if __name__ == "__main__":
    print(audit())
