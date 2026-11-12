#!/usr/bin/env python3
"""Independent exhaustive multi-cycle reference for the V317 offline oracle.

This is synthetic scheduling verification, not GPU, RTL, or electrical evidence.
"""
from functools import lru_cache
from itertools import product, combinations

OPS = ((0,), (1,), (0, 1))

def independent(arrivals, ports=1, slots=2, output=2):
    @lru_cache(None)
    def search(t, pending):
        if t == len(arrivals):
            return 0
        live = pending + tuple((t, j, tuple(op)) for j, op in enumerate(arrivals[t]))
        best = 0
        for count in range(min(len(live), slots, output) + 1):
            for chosen in combinations(range(len(live)), count):
                if any(sum(live[i][2].count(b) for i in chosen) > ports for b in (0, 1)):
                    continue
                remainder = tuple(item for i, item in enumerate(live) if i not in chosen)
                best = max(best, count + search(t + 1, remainder))
        return best
    return search(0, ())

def run():
    from finite_horizon_offline_oracle import exact
    batches = [()] + [(x,) for x in OPS] + list(product(OPS, repeat=2))
    cases = 0
    for seq in product(batches, repeat=3):
        rows = [{"cycle": t, "requests": [
            {"id": f"{t}:{j}", "banks": list(op)} for j, op in enumerate(batch)
        ]} for t, batch in enumerate(seq)]
        for ports, slots, output in ((1, 1, 2), (1, 2, 1), (1, 2, 2), (2, 2, 2)):
            expected = independent(seq, ports, slots, output)
            observed = exact(rows, 2, ports, slots, output, max_live=6)
            assert observed == expected, (seq, ports, slots, output, expected, observed)
            cases += 1
    print(f"PASS: {cases} independent three-cycle oracle comparisons")

if __name__ == "__main__":
    run()
