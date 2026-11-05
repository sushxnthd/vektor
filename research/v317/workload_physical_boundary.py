#!/usr/bin/env python3
"""V317 necessary-condition workload model; not measured GPU throughput."""
from dataclasses import dataclass
from fractions import Fraction as F

@dataclass(frozen=True)
class Workload:
    name: str
    useful_ops: int
    baseline_cycles: int
    candidate_cycles: int
    bytes_per_op: int
    bandwidth_bytes_s: int
    baseline_occupancy: F
    candidate_occupancy: F

# Archived approximate Fmax ratio: pairwise is 2.42% lower.
FREQ_RATIO = F(9758, 10000)

def evaluate(w: Workload):
    assert w.useful_ops > 0 and w.baseline_cycles > 0 and w.candidate_cycles > 0
    assert w.bytes_per_op > 0 and w.bandwidth_bytes_s > 0
    assert 0 < w.baseline_occupancy <= 1 and 0 < w.candidate_occupancy <= 1
    base_compute = F(w.baseline_cycles) / w.baseline_occupancy
    cand_compute = F(w.candidate_cycles) / (FREQ_RATIO * w.candidate_occupancy)
    mem = F(w.useful_ops * w.bytes_per_op, w.bandwidth_bytes_s)
    base_time, cand_time = max(base_compute, mem), max(cand_compute, mem)
    return {'name': w.name, 'throughput_ratio': base_time / cand_time,
            'baseline_time': base_time, 'candidate_time': cand_time,
            'memory_floor': mem, 'candidate_win': cand_time < base_time}

def test():
    no_win = Workload('frozen_no_win_equal_policy', 1000, 1000, 1000, 4, 10, F(1), F(1))
    assert evaluate(no_win)['throughput_ratio'] == FREQ_RATIO
    win = Workload('frozen_predicted_win_if_10pct_cycle_gain', 1000, 1000, 900, 4, 10, F(1), F(1))
    assert evaluate(win)['throughput_ratio'] == F(9758, 9000)
    bandwidth = Workload('bandwidth_erases_cycle_gain', 1000, 1000, 900, 4, 1, F(1), F(1))
    assert evaluate(bandwidth)['throughput_ratio'] == 1
    occupancy = Workload('occupancy_erases_cycle_gain', 1000, 1000, 900, 4, 10, F(1), F(4,5))
    assert not evaluate(occupancy)['candidate_win']
    for cycles in range(1, 101):
        w = Workload('equal_policy_check', 1000, cycles, cycles, 4, 1000000, F(1), F(1))
        assert evaluate(w)['throughput_ratio'] <= 1
    return no_win, win, bandwidth, occupancy

if __name__ == '__main__':
    for w in test():
        r = evaluate(w)
        print(f"{r['name']}: ratio={float(r['throughput_ratio']):.6f} win={r['candidate_win']}")
    print('PASS: four controls and 100 equal-policy checks')
