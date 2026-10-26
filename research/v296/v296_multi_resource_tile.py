#!/usr/bin/env python3
"""Prospectively frozen V296 multi-resource replication boundary, with independent workload simulation.

Run: python3 research/v296/v296_multi_resource_tile.py --self-test
Evidence: MULTIRESOURCE_TILE_TRANSFER_PREREG_20261026.md
Neither this model nor the simulation is routed GPU throughput evidence.
"""
import argparse
import json
import random
from fractions import Fraction as F

A_C = F(9286592, 1000)  # measured mapped area, um^2
A_S = F(9844926, 1000)
Q_EXACT = F(957548877, 320000000)  # independent prior exact occupancy law
U = F(85, 100)
OVERHEAD = F(3, 100)
BASE_T = F(7, 2)
BYTES_PER_WAVE = F(4)
SLICES_S = 17
SLICES_C = (SLICES_S * A_S) // A_C
SEEDS = (41213, 49531)
CYCLES = 20000

SCENARIOS = {
    'conditional_win': {'candidate_period_ns': F(7, 2), 'bandwidth_GBps': F(100), 'read_ports_per_ns': F(100)},
    'bandwidth_no_win': {'candidate_period_ns': F(7, 2), 'bandwidth_GBps': F(10), 'read_ports_per_ns': F(100)},
    'port_no_win': {'candidate_period_ns': F(7, 2), 'bandwidth_GBps': F(100), 'read_ports_per_ns': F(4)},
    'clock_regression_loss': {'candidate_period_ns': F(3745, 1000), 'bandwidth_GBps': F(100), 'read_ports_per_ns': F(100)},
}

def offered_rate(n, period, q=Q_EXACT, occupancy=U, overhead=OVERHEAD):
    if n < 0 or period <= 0 or q < 0 or not (0 <= occupancy <= 1) or overhead < 0:
        raise ValueError('invalid offered-rate parameters')
    return F(n) * q * occupancy / ((1 + overhead) * period)

def useful_rate(n, period, bandwidth_gbps, reads_per_ns, q=Q_EXACT):
    if bandwidth_gbps < 0 or reads_per_ns < 0:
        raise ValueError('invalid shared budgets')
    return min(offered_rate(n, period, q), bandwidth_gbps / BYTES_PER_WAVE, reads_per_ns / 2)

def prediction(case):
    c = useful_rate(SLICES_C, case['candidate_period_ns'], case['bandwidth_GBps'], case['read_ports_per_ns'])
    s = useful_rate(SLICES_S, BASE_T, case['bandwidth_GBps'], case['read_ports_per_ns'])
    return c / s - 1

def admit_waves(waves, port_limit=2):
    """Independent concrete-bank first-fit admissions, no use of analytical q."""
    ports = [0] * 16
    admitted = 0
    for valid, a, b in waves:
        if not valid:
            continue
        if a == b:
            if ports[a] + 2 > port_limit:
                continue
            ports[a] += 2
        else:
            if ports[a] + 1 > port_limit or ports[b] + 1 > port_limit:
                continue
            ports[a] += 1
            ports[b] += 1
        admitted += 1
    assert max(ports) <= port_limit
    return admitted

def trace(seed, cycles=CYCLES):
    rng = random.Random(seed)
    paired = []
    total_admitted = 0
    total_active = 0
    active_prob = float(U / (1 + OVERHEAD))
    for _ in range(cycles):
        serial = 0
        candidate = 0
        for slice_id in range(SLICES_C):
            active = rng.random() < active_prob
            waves = []
            for _slot in range(4):
                valid = rng.random() < 0.8
                a = rng.randrange(16)
                b = a if rng.random() < 0.2 else rng.randrange(16)
                waves.append((valid, a, b))
            accepted = admit_waves(waves) if active else 0
            if active:
                total_active += 1
                total_admitted += accepted
            if slice_id < SLICES_S:
                serial += accepted
            candidate += accepted
        paired.append((serial, candidate))
    return paired, F(total_admitted, total_active)

def fluid_service(arrivals, period_ns, bandwidth_gbps, reads_per_ns):
    # Independent discrete-time fluid server with persistent queue and both global caps.
    capacity = float(min(bandwidth_gbps / BYTES_PER_WAVE, reads_per_ns / 2) * period_ns)
    backlog = 0.0
    served = 0.0
    steps = 0
    for arriving in arrivals:
        steps += 1
        backlog += arriving
        departure = min(backlog, capacity)
        backlog -= departure
        served += departure
    return served / (steps * float(period_ns))

def empirical(case, paired):
    s = fluid_service((x[0] for x in paired), BASE_T, case['bandwidth_GBps'], case['read_ports_per_ns'])
    c = fluid_service((x[1] for x in paired), case['candidate_period_ns'], case['bandwidth_GBps'], case['read_ports_per_ns'])
    return c / s - 1

def self_test():
    assert SLICES_C == 18
    assert admit_waves([(True, 0, 1), (True, 0, 2)]) == 2
    # Mutation: a one-port-per-bank implementation rejects a legitimate second wave.
    assert admit_waves([(True, 0, 1), (True, 0, 2)], port_limit=1) == 1
    assert admit_waves([(True, 0, 0), (True, 0, 1)]) == 1
    assert admit_waves([(True, 0, 0), (True, 0, 1)], port_limit=1) == 1
    assert prediction(SCENARIOS['conditional_win']) == F(1, 17)
    assert prediction(SCENARIOS['bandwidth_no_win']) == 0
    assert prediction(SCENARIOS['port_no_win']) == 0
    assert prediction(SCENARIOS['clock_regression_loss']) == F(18 * 100, 17 * 107) - 1
    for n in range(1, 101):
        assert useful_rate(n, BASE_T, F(0), F(100)) == 0
        assert useful_rate(n, BASE_T, F(100), F(0)) == 0
        assert useful_rate(n, BASE_T, F(10), F(4)) <= F(2)
    for bad in [(-1, BASE_T), (1, 0), (1, -BASE_T)]:
        try:
            offered_rate(*bad)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid offered rate accepted')
    return 'PASS: independent two-port mutation, four frozen boundary laws, 100 resource-cap tests'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    out = {'evidence_tier': 'synthetic_discrete_cycle_transfer_not_GPU_or_postroute',
           'mapped_area_provenance': 'hosted four-way Nangate45 synthesis, run 40244774412',
           'preregistration': 'research/v296/MULTIRESOURCE_TILE_TRANSFER_PREREG_20261026.md',
           'baseline_slices': SLICES_S, 'candidate_slices_conditional': int(SLICES_C),
           'exact_q': str(Q_EXACT), 'seeds': SEEDS, 'cycles_per_seed': CYCLES,
           'scenarios': {}, 'independent_empirical_validation': {}}
    if args.self_test:
        out['self_test'] = self_test()
    for name, case in SCENARIOS.items():
        out['scenarios'][name] = {'predicted_gain_fraction': str(prediction(case)),
                                  'predicted_gain_pct': float(prediction(case) * 100),
                                  'candidate_period_ns': str(case['candidate_period_ns']),
                                  'bandwidth_GBps': str(case['bandwidth_GBps']),
                                  'shared_reads_per_ns': str(case['read_ports_per_ns'])}
    for seed in SEEDS:
        paired, q_empirical = trace(seed)
        assert abs(float(q_empirical - Q_EXACT)) <= 0.03, ('q transfer failed', seed, q_empirical)
        out['independent_empirical_validation'][str(seed)] = {'q_per_active_slice_cycle': float(q_empirical), 'cases': {}}
        for name, case in SCENARIOS.items():
            observed = empirical(case, paired)
            predicted = float(prediction(case))
            error = abs(observed - predicted)
            assert error <= 0.02, ('gain transfer failed', seed, name, observed, predicted)
            out['independent_empirical_validation'][str(seed)]['cases'][name] = {
                'observed_gain_pct': observed * 100,
                'predicted_gain_pct': predicted * 100,
                'absolute_gain_error': error,
                'pass': True}
    out['verdict'] = 'SYNTHETIC_TRANSFER_PASS_NO_PHYSICAL_GPU_CLAIM'
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
