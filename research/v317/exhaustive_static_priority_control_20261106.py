#!/usr/bin/env python3
"""Exhaustive equal-port static-priority control for V317 (analytical, not RTL)."""
from collections import Counter
from itertools import permutations, product

N_REQ = 4
N_BANK = 3
READ_PORTS_PER_BANK = 2
ORDERS = tuple(permutations(range(N_REQ)))

def admit(requests, order):
    """Atomic two-read admission; one admitted request consumes two reads."""
    used = Counter()
    admitted = 0
    for i in order:
        a, b = requests[i]
        demand = Counter((a, b))
        if all(used[k] + v <= READ_PORTS_PER_BANK for k, v in demand.items()):
            used.update(demand)
            admitted += 1
    return admitted

def main():
    histogram = Counter()
    oracle_exceeds_rotation = 0
    for flat in product(range(N_BANK), repeat=2 * N_REQ):
        requests = tuple(zip(flat[::2], flat[1::2]))
        scores = [admit(requests, order) for order in ORDERS]
        oracle = max(scores)
        rotation_sum = sum(scores)
        histogram[(oracle, rotation_sum)] += 1
        oracle_exceeds_rotation += oracle * len(ORDERS) > rotation_sum
    assert sum(histogram.values()) == N_BANK ** (2 * N_REQ) == 6561
    assert oracle_exceeds_rotation == 3360
    assert histogram == {
        (1, 24): 51, (2, 36): 288, (2, 42): 912,
        (2, 48): 2946, (3, 62): 576, (3, 64): 1008,
        (3, 68): 576, (3, 72): 204,
    }
    print("Enumerated 6561 ordered four-request two-read workloads, three banks, two ports/bank.")
    print("Oracle exceeds mean of 24 static priority orders in 3360 / 6561 workloads.")
    print("Histogram (oracle admission, sum of 24 static admissions):", sorted(histogram.items()))
    print("NOT a physical speedup: oracle chooses order after seeing the workload.")
if __name__ == "__main__":
    main()
