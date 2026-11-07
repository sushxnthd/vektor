#!/usr/bin/env python3
"""Dimensional physical roofline audit; conditional only, NOT measured GPU throughput.

Corrects the prior model's invalid comparison of raw cycle counts with seconds.
The base clock is explicit, and candidate clock derives from a measured ratio.
Occupancy efficiency is an assumption, not a guaranteed inverse scaling law.
"""
from dataclasses import dataclass
from fractions import Fraction as F

FREQ_RATIO = F(9758, 10000)  # archived approximate ratio, not electrical signoff

@dataclass(frozen=True)
class Workload:
    name: str
    useful_ops: int
    baseline_cycles: int
    candidate_cycles: int
    bytes_per_op: int
    bandwidth_bytes_s: int
    baseline_frequency_hz: int
    baseline_efficiency: F = F(1)
    candidate_efficiency: F = F(1)

def evaluate(w: Workload):
    assert min(w.useful_ops, w.baseline_cycles, w.candidate_cycles,
               w.bytes_per_op, w.bandwidth_bytes_s, w.baseline_frequency_hz) > 0
    assert 0 < w.baseline_efficiency <= 1 and 0 < w.candidate_efficiency <= 1
    base_compute_s = F(w.baseline_cycles, w.baseline_frequency_hz) / w.baseline_efficiency
    cand_compute_s = F(w.candidate_cycles, w.baseline_frequency_hz) / (FREQ_RATIO * w.candidate_efficiency)
    mem_s = F(w.useful_ops * w.bytes_per_op, w.bandwidth_bytes_s)
    base_s, cand_s = max(base_compute_s, mem_s), max(cand_compute_s, mem_s)
    return {'name': w.name, 'throughput_ratio': base_s / cand_s,
            'baseline_seconds': base_s, 'candidate_seconds': cand_s,
            'memory_floor_seconds': mem_s, 'candidate_win': cand_s < base_s}

def test():
    def case(name, cycles, bandwidth, eff=F(1), freq=1000):
        return Workload(name, 1000, 1000, cycles, 4, bandwidth, freq, F(1), eff)
    no_win = case('frozen_no_win_equal_policy', 1000, 10000)
    win = case('conditional_compute_win_10pct_cycle_gain', 900, 10000)
    bandwidth = case('bandwidth_erases_cycle_gain', 900, 1000)
    occupancy = case('efficiency_erases_cycle_gain', 900, 10000, F(4,5))
    assert evaluate(no_win)['throughput_ratio'] == FREQ_RATIO
    assert evaluate(win)['throughput_ratio'] == F(9758, 9000)
    assert evaluate(bandwidth)['throughput_ratio'] == 1
    assert evaluate(occupancy)['throughput_ratio'] < 1
    slow = case('dimensional_slow_clock', 900, 10000, freq=100)
    fast = case('dimensional_fast_clock', 900, 10000, freq=10000)
    assert evaluate(slow)['throughput_ratio'] == F(9758,9000)
    assert evaluate(fast)['throughput_ratio'] == 1
    for cycles in range(1, 101):
        w = Workload('rescale', 1000, cycles, cycles, 4, 10000, 1000)
        scaled = Workload('rescale', 1000, cycles, cycles, 4, 100000, 10000)
        assert evaluate(w)['throughput_ratio'] == evaluate(scaled)['throughput_ratio']
        assert evaluate(w)['throughput_ratio'] <= 1
    return no_win, win, bandwidth, occupancy, slow, fast

if __name__ == '__main__':
    for w in test():
        r = evaluate(w)
        print(f"{w.name}: ratio={float(r['throughput_ratio']):.6f}, win={r['candidate_win']}")
    print('PASS: 6 controls and 100 dimensional-rescaling/equal-policy checks')
