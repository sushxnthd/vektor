#!/usr/bin/env python3
"""V296 prospective fixed-total-warp area-packing and dependency test.

Preregistered in JOINT_OCCUPANCY_AREA_PACKING_PREREG_20261026.md at
commit c64723a5. Synthetic only; no physical clock/throughput claim.
"""
import argparse
from array import array
import json
import random
from pathlib import Path

SERIAL_AREA = 9844.926
PAIRWISE_AREA = 9286.592
SERIAL_SLICES = 17
PAIRWISE_SLICES = 18
ISSUE_SLOTS = 4
BANKS = 16
PORTS = 2
WARMUP = 500
MEASURE = 4000
SEEDS = (41719, 41743)
CELLS = (
    ("low_occupancy", 32, 0.0, None, 1.0),
    ("ideal_boundary_136", 136, 0.0, None, 1.0),
    ("boundary_140", 140, 0.0, None, 1.0),
    ("boundary_144", 144, 0.0, None, 1.0),
    ("high_occupancy", 180, 0.0, None, 1.0),
    ("shared_bandwidth_cap", 180, 0.0, 25.0, 1.0),
    ("candidate_period_plus_7pct", 180, 0.0, None, 1.07),
    ("hotspot_80pct", 180, 0.8, None, 1.0),
)

def bank_streams(seed, warps, hotspot, count=WARMUP+MEASURE+2):
    streams = []
    for warp in range(warps):
        rng = random.Random((seed << 21) ^ (warp * 0x9E3779B1))
        seq = array('B')
        for _ in range(count):
            a = 0 if rng.random() < hotspot else rng.randrange(BANKS)
            b = a if rng.random() < 0.2 else (
                0 if rng.random() < hotspot else rng.randrange(BANKS))
            seq.append((a << 4) | b)
        streams.append(seq)
    return streams

def simulate(streams, slices, latency, cycles=WARMUP+MEASURE, trace=False):
    if not (slices > 0 and latency > 0):
        raise ValueError('invalid physical resources')
    warps = len(streams)
    groups = [list(range(s, warps, slices)) for s in range(slices)]
    ready = [0] * warps
    position = [0] * warps
    measured = 0
    history = []
    for t in range(cycles):
        issued_this_cycle = []
        for group in groups:
            used = [0] * BANKS
            n = len(group)
            if not n:
                continue
            granted = 0
            for offset in range(n):
                if granted >= ISSUE_SLOTS:
                    break
                w = group[(t + offset) % n]
                if ready[w] > t:
                    continue
                if position[w] >= len(streams[w]):
                    raise ValueError('request stream exhausted')
                v = streams[w][position[w]]
                a, b = v >> 4, v & 15
                if a == b:
                    if used[a] + 2 > PORTS:
                        continue
                    used[a] += 2
                else:
                    if used[a] + 1 > PORTS or used[b] + 1 > PORTS:
                        continue
                    used[a] += 1
                    used[b] += 1
                assert max(used) <= PORTS
                assert ready[w] <= t
                ready[w] = t + latency
                position[w] += 1
                issued_this_cycle.append(w)
                granted += 1
        if t >= WARMUP:
            measured += len(issued_this_cycle)
        if trace:
            history.append(tuple(issued_this_cycle))
    return {'issued': measured, 'issued_per_cycle': measured / (cycles-WARMUP),
            'warp_distribution': [len(g) for g in groups],
            'history': history if trace else None}

def reference(streams, slices, latency, cycles):
    # Separate state machine: dict state, independent bank-needs accounting.
    groups = [[w for w in range(len(streams)) if w % slices == s]
              for s in range(slices)]
    busy_until = {w: 0 for w in range(len(streams))}
    cursor = {w: 0 for w in range(len(streams))}
    output = []
    for tick in range(cycles):
        this_tick = []
        for group in groups:
            ports = {bank: 0 for bank in range(BANKS)}
            granted = 0
            for offset in range(len(group)):
                if granted == ISSUE_SLOTS:
                    break
                w = group[(tick + offset) % len(group)]
                if busy_until[w] > tick:
                    continue
                pair = streams[w][cursor[w]]
                a, b = divmod(pair, BANKS)
                needs = {a: 2} if a == b else {a: 1, b: 1}
                if any(ports[k] + v > PORTS for k, v in needs.items()):
                    continue
                for k, v in needs.items():
                    ports[k] += v
                cursor[w] += 1
                busy_until[w] = tick + latency
                this_tick.append(w)
                granted += 1
        output.append(tuple(this_tick))
    return output

def self_test():
    budget = SERIAL_SLICES * SERIAL_AREA
    assert PAIRWISE_SLICES * PAIRWISE_AREA <= budget
    assert (PAIRWISE_SLICES+1) * PAIRWISE_AREA > budget
    assert SERIAL_SLICES * ISSUE_SLOTS == 68
    assert PAIRWISE_SLICES * ISSUE_SLOTS == 72
    for seed in (2, 7, 17):
        streams = bank_streams(seed, 11, 0.3, 80)
        for n in (1, 3, 7):
            for latency in (1, 2, 3):
                got = simulate(streams, n, latency, cycles=50, trace=True)['history']
                expected = reference(streams, n, latency, cycles=50)
                assert got == expected, (seed, n, latency)
    s = bank_streams(3, 1, 0.0, 30)
    for latency in (1, 2, 3):
        hist = simulate(s, 1, latency, cycles=21, trace=True)['history']
        assert [t for t, ids in enumerate(hist) if ids] == list(range(0, 21, latency))
    print('V296_JOINT_AREA_OCCUPANCY_INDEPENDENT_CHECK_PASS')

def evaluate(output):
    results = []
    for seed in SEEDS:
        for name, W, h, cap, period_ratio in CELLS:
            streams = bank_streams(seed, W, h)
            a = simulate(streams, SERIAL_SLICES, 1)
            b = simulate(streams, PAIRWISE_SLICES, 2)
            raw_a, raw_b = a['issued_per_cycle'], b['issued_per_cycle']
            useful_a = min(raw_a, cap) if cap is not None else raw_a
            useful_b = min(raw_b, cap) if cap is not None else raw_b
            gain = useful_b / useful_a / period_ratio - 1
            row = {'seed': seed, 'regime': name, 'total_warps': W,
                   'hotspot': h, 'shared_cap_waves_per_cycle': cap,
                   'candidate_period_ratio': period_ratio,
                   'serial_issued_per_cycle': round(raw_a, 6),
                   'candidate_issued_per_cycle': round(raw_b, 6),
                   'serial_useful_per_cycle': round(useful_a, 6),
                   'candidate_useful_per_cycle': round(useful_b, 6),
                   'physical_time_throughput_gain': round(gain, 8),
                   'serial_distribution': a['warp_distribution'],
                   'candidate_distribution': b['warp_distribution'],
                   'serial_ideal_upper': min(68, W),
                   'candidate_ideal_upper': min(72, W/2),
                   'serial_ideal_upper_with_cap': min(68, W, cap)
                        if cap is not None else min(68, W),
                   'candidate_ideal_upper_with_cap': min(72, W/2, cap)
                        if cap is not None else min(72, W/2)}
            assert raw_a <= row['serial_ideal_upper'] + 1e-8
            assert raw_b <= row['candidate_ideal_upper'] + 1e-8
            results.append(row)
            print(seed, name, 'serial',round(raw_a,3),'candidate',
                  round(raw_b,3),'gain',round(gain*100,4),'%')
    for seed in SEEDS:
        d = {x['regime']: x for x in results if x['seed']==seed}
        assert d['low_occupancy']['physical_time_throughput_gain'] < -0.2
        assert d['high_occupancy']['physical_time_throughput_gain'] > 0.02
        assert abs(d['shared_bandwidth_cap']['physical_time_throughput_gain']) < 1e-9
        assert d['candidate_period_plus_7pct']['physical_time_throughput_gain'] < 0
    payload = {'evidence_tier': 'PROSPECTIVE_SYNTHETIC_NOT_PHYSICAL',
               'prereg_commit': 'c64723a5c7adc98ebb95877ac1c0e1b2a2924b60',
               'mapped_area_um2': {'serial': SERIAL_AREA, 'candidate': PAIRWISE_AREA},
               'hypothetical_area_budget_um2': SERIAL_SLICES*SERIAL_AREA,
               'hypothetical_candidate_18_slice_area_um2':
                    PAIRWISE_SLICES*PAIRWISE_AREA,
               'ideal_threshold_total_warps': 136,
               'ideal_candidate_full_issue_total_warps': 144,
               'frozen_results': results}
    output = Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(payload,indent=2)+'\n')
    print('V296_JOINT_AREA_OCCUPANCY_PROSPECTIVE_PASS')

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--evaluate',action='store_true')
    p.add_argument('--output',default='research/v296/JOINT_OCCUPANCY_AREA_PACKING_RESULTS_20261026.json')
    args=p.parse_args()
    if args.self_test: self_test()
    if args.evaluate: evaluate(args.output)
    if not (args.self_test or args.evaluate):
        p.error('select --self-test or --evaluate')
