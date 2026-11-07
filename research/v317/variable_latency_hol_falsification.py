#!/usr/bin/env python3
"""Variable-latency credit retirement: exact deterministic falsification.

Synthetic queue model only; no GPU/RTL claims. Credits are occupied until
retirement. A request has an assigned service-ready timestamp. FIFO retirement
can head-of-line block shorter requests. Compare FIFO against ready-first
retirement with identical bank/output/credit resources.
"""
from collections import deque
from itertools import product

def fifo(latencies, credits, width, horizon):
    q = deque()
    retired = 0
    accepted = 0
    for t in range(horizon):
        for _ in range(width):
            if q and q[0] <= t:
                q.popleft()
                retired += 1
        if t < len(latencies) and len(q) < credits:
            q.append(t + latencies[t])
            accepted += 1
    return retired, accepted, len(q)

def ready_first(latencies, credits, width, horizon):
    q = []
    retired = 0
    accepted = 0
    for t in range(horizon):
        for _ in range(width):
            ready = [i for i, r in enumerate(q) if r <= t]
            if not ready:
                break
            q.pop(min(ready, key=lambda i: (q[i], i)))
            retired += 1
        if t < len(latencies) and len(q) < credits:
            q.append(t + latencies[t])
            accepted += 1
    return retired, accepted, len(q)

def test():
    count = 0
    wins = 0
    for n in range(7):
        for seq in product((1, 2, 4), repeat=n):
            for credits in range(1, 5):
                for width in (1, 2):
                    for horizon in range(n, n + 6):
                        a = fifo(seq, credits, width, horizon)
                        b = ready_first(seq, credits, width, horizon)
                        assert sum(a[1:]) >= a[0] # accepted >= retired
                        assert a[1] == a[0] + a[2]
                        assert b[1] == b[0] + b[2]
                        # ready-first can improve completions but credit reuse
                        # changes subsequent admissions; do not assert dominance.
                        wins += b[0] > a[0]
                        count += 1
    # Same mean latency but order-dependent completions.
    a = fifo((4, 1, 1, 1), 4, 2, 5)
    b = fifo((1, 1, 1, 4), 4, 2, 5)
    assert a[0] < b[0], (a, b)
    print("PASS", count, "conservation cases; ready-first higher completions in", wins)
    print("equal multiset/order sensitivity:", a, b)
    print("Mean latency and credit count alone cannot predict finite-window throughput.")
    print("No RTL, electrical, synthesis, or measured GPU performance claim.")

if __name__ == "__main__":
    test()
