#!/usr/bin/env python3
"""Finite-horizon falsification of mean-rate-only throughput prediction.

A rate-only law min(mean arrivals, service) cannot predict finite-window
completions without arrival timing and initial/final queue states.
No GPU hardware claim: this is a deterministic queue counterexample.
"""
from collections import deque

def simulate(arrivals, service=1, initial=0):
    assert service >= 1 and initial >= 0
    queue = deque([-1] * initial)
    completed = 0
    completion_times = []
    for t, count in enumerate(arrivals):
        assert count >= 0
        queue.extend([t] * count)
        for _ in range(min(service, len(queue))):
            completion_times.append((t, queue.popleft()))
            completed += 1
        assert completed + len(queue) == initial + sum(arrivals[:t+1])
    return completed, len(queue), completion_times

def main():
    horizon = 100
    # Identical mean arrival rate (one per cycle) and identical service capacity.
    early = [100] + [0] * 99
    uniform = [1] * 100
    late = [0] * 99 + [100]
    results = [simulate(x) for x in (early, uniform, late)]
    assert [r[0] for r in results] == [100, 100, 1]
    assert [r[1] for r in results] == [0, 0, 99]
    assert all(sum(x) == 100 for x in (early, uniform, late))
    # Candidate service doubling cannot rescue a burst that arrives on final edge.
    assert simulate(late, service=2)[0] == 2
    assert simulate(early, service=2)[0] == 100
    # One additional drain window makes all cases eventually complete.
    assert simulate(late + [0] * 99)[0] == 100
    print("PASS: same mean arrival=1 and service=1, completions early/uniform/late=100/100/1")
    print("PASS: late burst doubled service completes 2/100 within horizon")
    print("Interpretation: rate-only min-law is an asymptotic/steady-state ceiling,")
    print("not a finite-horizon prediction absent arrival timing and queue boundary states.")

if __name__ == "__main__":
    main()
