"""Finite-horizon FIFO greedy-versus-optimal scheduling falsification (synthetic).

Each source has a FIFO of (bank, release_cycle) requests; at most one request
per source per cycle. Compare a fixed-priority work-conserving scheduler to
the exact finite-horizon optimum at identical bank/output resources.
This does not establish RTL, electrical closure, or real GPU throughput.
"""
from functools import lru_cache
from itertools import product

def service(queues, horizon, outputs=2, ports=1, optimal=True):
    queues = tuple(tuple(q) for q in queues)
    @lru_cache(None)
    def solve(t, state):
        if t == horizon:
            return 0
        eligible = [(i, q[0][0]) for i, q in enumerate(state) if q and q[0][1] <= t]
        if not optimal:
            selected, banks = [], {}
            for i, bank in eligible:
                if len(selected) < outputs and banks.get(bank, 0) < ports:
                    selected.append(i)
                    banks[bank] = banks.get(bank, 0) + 1
            return len(selected) + solve(t + 1, tuple(q[1:] if i in selected else q for i, q in enumerate(state)))
        best = solve(t + 1, state)
        def choose(start, chosen, banks):
            nonlocal best
            if chosen:
                new = tuple(q[1:] if i in chosen else q for i, q in enumerate(state))
                best = max(best, len(chosen) + solve(t + 1, new))
            if len(chosen) == outputs:
                return
            for j in range(start, len(eligible)):
                i, bank = eligible[j]
                if banks.get(bank, 0) >= ports:
                    continue
                banks[bank] = banks.get(bank, 0) + 1
                choose(j + 1, chosen + (i,), banks)
                banks[bank] -= 1
        choose(0, (), {})
        return best
    return solve(0, queues)

def audit():
    count = strict = 0
    witness = None
    for config in product(product(range(2), range(2)), repeat=6):
        q = tuple(tuple(config[2*i:2*i+2]) for i in range(3))
        greedy = service(q, 3, optimal=False)
        optimum = service(q, 3, optimal=True)
        assert 0 <= greedy <= optimum <= 6
        count += 1
        if optimum > greedy:
            strict += 1
            if witness is None:
                witness = (q, greedy, optimum)
    assert (count, strict) == (4096, 1056)
    assert witness == (((((0, 0), (0, 0)), ((0, 0), (0, 0)), ((0, 0), (1, 0))), 3, 4))
    print({"cases": count, "greedy_strictly_worse": strict, "first_witness": witness})

if __name__ == "__main__":
    audit()
