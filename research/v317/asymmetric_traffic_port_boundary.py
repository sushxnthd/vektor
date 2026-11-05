#!/usr/bin/env python3
"""Prospective physical throughput boundary with asymmetric traffic and port pressure.

Conditional analytical model, not RTL, synthesis, or GPU performance evidence.
A paired candidate can change bytes/op and sustainable bandwidth; assuming a
common memory floor can therefore falsely predict a win. All times in seconds.
"""
from dataclasses import dataclass
from fractions import Fraction as Q

@dataclass(frozen=True)
class Regime:
    name: str
    cycles_base: int
    cycles_candidate: int
    frequency_base: int
    frequency_candidate: int
    useful_ops: int
    bytes_base: int
    bytes_candidate: int
    bandwidth_base: int
    bandwidth_candidate: int
    occupancy_base: Q = Q(1)
    occupancy_candidate: Q = Q(1)
    control_cycles_candidate: int = 0

def measure(r):
    v = (r.cycles_base, r.cycles_candidate, r.frequency_base,
         r.frequency_candidate, r.useful_ops, r.bytes_base,
         r.bytes_candidate, r.bandwidth_base, r.bandwidth_candidate)
    if any(x <= 0 for x in v) or r.control_cycles_candidate < 0:
        raise ValueError("nonpositive physical inputs")
    if not (0 < r.occupancy_base <= 1 and 0 < r.occupancy_candidate <= 1):
        raise ValueError("occupancy outside (0,1]")
    cb = Q(r.cycles_base, r.frequency_base) / r.occupancy_base
    cc = Q(r.cycles_candidate + r.control_cycles_candidate,
           r.frequency_candidate) / r.occupancy_candidate
    mb = Q(r.useful_ops * r.bytes_base, r.bandwidth_base)
    mc = Q(r.useful_ops * r.bytes_candidate, r.bandwidth_candidate)
    tb, tc = max(cb, mb), max(cc, mc)
    return {"ratio": tb / tc, "base_seconds": tb, "candidate_seconds": tc,
            "base_compute": cb, "candidate_compute": cc,
            "base_memory": mb, "candidate_memory": mc}

def regime(name, cycles=900, bytes_candidate=4, bandwidth=10000,
           occupancy=Q(1), overhead=0, candidate_bandwidth=None):
    return Regime(name, 1000, cycles, 1000, 975, 1000, 4,
                  bytes_candidate, bandwidth,
                  bandwidth if candidate_bandwidth is None else candidate_bandwidth,
                  Q(1), occupancy, overhead)

def test():
    # Frozen qualitative regimes: prospective before any measured workload.
    win = regime("predicted_win_compute_bound")
    no_win = regime("predicted_no_win_bandwidth_bound", bandwidth=1000)
    traffic = regime("traffic_increase_erases_win", bytes_candidate=5,
                     bandwidth=4000)
    port = regime("port_pressure_erases_win", candidate_bandwidth=3000,
                  bandwidth=4000)
    control = regime("control_overhead_erases_win", overhead=130)
    occupancy = regime("occupancy_erases_win", occupancy=Q(4,5))
    assert measure(win)["ratio"] == Q(975,900) > 1
    assert measure(no_win)["ratio"] == 1
    assert measure(traffic)["ratio"] == Q(4,5)
    assert measure(port)["ratio"] == Q(3,4)
    assert measure(control)["ratio"] < 1
    assert measure(occupancy)["ratio"] < 1
    # Monotonicity under candidate-only traffic, pressure, control and occupancy.
    for n in range(1,101):
        a = regime("sweep", bytes_candidate=4+n, bandwidth=5000)
        b = regime("sweep", bytes_candidate=5+n, bandwidth=5000)
        assert measure(b)["ratio"] <= measure(a)["ratio"]
        a = regime("sweep", overhead=n)
        b = regime("sweep", overhead=n+1)
        assert measure(b)["ratio"] <= measure(a)["ratio"]
        a = regime("sweep", candidate_bandwidth=1000+n)
        b = regime("sweep", candidate_bandwidth=1001+n)
        assert measure(b)["ratio"] >= measure(a)["ratio"]
    return [win, no_win, traffic, port, control, occupancy]

if __name__ == "__main__":
    for r in test():
        print(f"{r.name}: {float(measure(r)['ratio']):.6f}x")
    print("PASS: six frozen illustrative regimes, 300 monotonic controls")
