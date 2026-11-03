#!/usr/bin/env python3
"""Finite physical-time queue boundary: deterministic toy, not GPU IPC."""
from fractions import Fraction

def run(events, horizon, period, capacity):
    assert horizon > 0 and period > 0 and capacity > 0
    events = sorted((Fraction(t), int(n)) for t, n in events)
    assert all(t >= 0 and n >= 0 for t, n in events)
    backlog = done = idx = 0
    clock = period
    while clock <= horizon:
        while idx < len(events) and events[idx][0] <= clock:
            backlog += events[idx][1]
            idx += 1
        take = min(capacity, backlog)
        done += take
        backlog -= take
        clock += period
    arrived = sum(n for t, n in events if t <= horizon)
    return done, arrived - done

def boundary(arrival_rate, base_capacity, candidate_capacity, clock_penalty):
    r, b, c, d = map(Fraction, (arrival_rate, base_capacity, candidate_capacity, clock_penalty))
    assert r >= 0 and b > 0 and c > 0 and d >= 0
    base = min(r, b)
    cand = min(r, c / (1 + d))
    return None if base == 0 else cand / base

def test():
    assert boundary(1, 1, 2, Fraction(1, 100)) == 1
    assert boundary(3, 1, 2, Fraction(1, 100)) == Fraction(200, 101)
    assert boundary(Fraction(3, 2), 1, 2, Fraction(1, 100)) == Fraction(3, 2)
    assert boundary(3, 1, 1, Fraction(1, 100)) == Fraction(100, 101)
    events = [(0, 1000)]
    assert run(events, 100, 1, 1) == (100, 900)
    assert run(events, 100, Fraction(101, 100), 1) == (99, 901)
    assert run(events, 100, Fraction(101, 100), 2) == (198, 802)
    burst = [(0, 20)]
    assert run(burst, 100, 1, 1) == run(burst, 100, Fraction(101, 100), 2) == (20, 0)
    assert run([(Fraction(19999, 200), 1)], 100, Fraction(101, 100), 2) == (0, 1)
    print("PASS physical-time queue boundary, clock loss, demand ceiling, drain, edge timing")
    print("low:", boundary(1, 1, 2, Fraction(1, 100)))
    print("saturated:", boundary(3, 1, 2, Fraction(1, 100)))

if __name__ == "__main__":
    test()
