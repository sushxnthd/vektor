#!/usr/bin/env python3
"""Prospective finite-horizon lookahead sensitivity audit (synthetic only).

Tests whether a hindsight-optimal scheduler is a credible online comparator.
The oracle sees future arrivals; online greedy cannot. A nonzero gap must
NEVER be attributed to an implementable V317 scheduler.
"""
from itertools import product
from finite_horizon_offline_oracle import exact

OPS = ((0,), (1,), (0, 1))
BATCHES = ((),) + tuple((op,) for op in OPS) + tuple(product(OPS, repeat=2))

def rows_for(sequence):
    return [{"cycle": t, "requests": [
        {"id": f"{t}:{j}", "banks": list(op)} for j, op in enumerate(batch)
    ]} for t, batch in enumerate(sequence)]

def online_greedy(sequence, ports, slots, output):
    pending = []
    completed = 0
    for batch in sequence:
        pending.extend(batch)
        used = [0, 0]
        selected = []
        for i, req in enumerate(pending):
            if len(selected) >= min(slots, output):
                break
            if all(used[b] + req.count(b) <= ports for b in (0, 1)):
                selected.append(i)
                for b in (0, 1):
                    used[b] += req.count(b)
        chosen = set(selected)
        pending = [req for i, req in enumerate(pending) if i not in chosen]
        completed += len(chosen)
    return completed

def run():
    cases = 0
    gaps = 0
    max_gap = 0
    witnesses = []
    for seq in product(BATCHES, repeat=3):
        rows = rows_for(seq)
        for ports, slots, output in ((1, 1, 2), (1, 2, 1), (1, 2, 2), (2, 2, 2)):
            upper = exact(rows, 2, ports, slots, output, max_live=6)
            online = online_greedy(seq, ports, slots, output)
            assert online <= upper, (seq, ports, slots, output, online, upper)
            gap = upper - online
            if gap:
                gaps += 1
                if len(witnesses) < 5:
                    witnesses.append((seq, (ports, slots, output), online, upper))
            max_gap = max(max_gap, gap)
            cases += 1
    print(f"cases={cases} hindsight_gaps={gaps} max_gap={max_gap}")
    for witness in witnesses:
        print("witness:", witness)
    assert cases == 8788

if __name__ == "__main__":
    run()
