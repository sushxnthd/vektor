#!/usr/bin/env python3
"""Optimistic, non-physical V296 area-replication/clock/bandwidth ceiling.

This is an algebraic sensitivity bound on an *infeasible* post-route experiment,
NOT measured GPU speedup, not an implementation or a claim of physical closure.
"""
import argparse
import json
from fractions import Fraction as F

AREA_PAIR = F('17857.644252')
AREA_SERIAL = F('18953.830505')
SETUP_PAIR_NS = F('-1.047895')
SETUP_SERIAL_NS = F('-1.859922')
HOLD_PAIR_NS = F('-0.036622')
HOLD_SERIAL_NS = F('-0.019796')
ORIGINAL_CAP_VIOLATIONS = (3, 3)
AREA_SAVING = 1 - AREA_PAIR / AREA_SERIAL


def bound(slice_fraction, freq_ratio, bandwidth_headroom):
    f, r, h = map(F, (slice_fraction, freq_ratio, bandwidth_headroom))
    if not (0 <= f <= 1 and r > 0 and h >= 1):
        raise ValueError('Requires 0<=f<=1, freq_ratio>0, bandwidth_headroom>=1')
    area_multiplier = 1 / (1 - f * AREA_SAVING)
    upper = min(area_multiplier * r, h)
    return {
        'baseline_tile_slice_fraction': float(f),
        'candidate_clock_over_serial': float(r),
        'bandwidth_headroom_over_baseline_demand': float(h),
        'ideal_area_replication_multiplier': float(area_multiplier),
        'clock_break_even_ratio_without_bandwidth_limit': float(1 / area_multiplier),
        'optimistic_throughput_ratio_upper_bound': float(upper),
        'optimistic_gain_upper_bound_percent': float(100 * (upper - 1)),
        'positive_gain_possible_under_bound': upper > 1,
        'physically_feasible': False,
        'gpu_speedup_measured': False,
    }


def integer_replication(slice_fraction, baseline_tiles):
    f = F(slice_fraction)
    n = int(baseline_tiles)
    if not (0 < f <= 1 and n > 0):
        raise ValueError('Require positive fraction and baseline tile count')
    baseline_tile_area = AREA_SERIAL / f
    candidate_tile_area = baseline_tile_area - (AREA_SERIAL - AREA_PAIR)
    budget = n * baseline_tile_area
    new_count = budget // candidate_tile_area
    ideal = baseline_tile_area / candidate_tile_area
    assert F(new_count, n) <= ideal
    return {'slice_fraction': float(f), 'baseline_tile_count': n,
            'maximum_whole_candidate_tiles_under_fixed_area': int(new_count),
            'integer_area_only_throughput_ratio': float(F(new_count, n)),
            'continuous_area_only_ratio': float(ideal)}


def self_test():
    assert AREA_PAIR < AREA_SERIAL
    assert SETUP_PAIR_NS < 0 and SETUP_SERIAL_NS < 0
    assert HOLD_PAIR_NS < 0 and HOLD_SERIAL_NS < 0
    assert ORIGINAL_CAP_VIOLATIONS == (3, 3)
    assert bound('0', '1', '2')['optimistic_throughput_ratio_upper_bound'] == 1.0
    assert bound('.5', '1', '1')['optimistic_throughput_ratio_upper_bound'] == 1.0
    assert bound('1', '1', '2')['ideal_area_replication_multiplier'] == float(AREA_SERIAL / AREA_PAIR)
    assert not bound('.5', '.97', '2')['positive_gain_possible_under_bound']
    assert bound('.5', '1', '1.1')['positive_gain_possible_under_bound']
    for f in ('.05', '.1', '.25', '.5', '.75', '1'):
        for n in (1, 16, 64, 1024):
            integer_replication(f, n)
    for args in (('-1', '1', '2'), ('1.01', '1', '2'), ('.5', '0', '2'), ('.5', '1', '.9')):
        try: bound(*args)
        except ValueError: pass
        else: raise AssertionError('Accepted invalid input')
    print('V296_OPTIMISTIC_TILE_BOUND_SELFTEST_PASS')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test: self_test()
    rows = [bound(f, r, h) for f, r, h in [
        ('.1', '1', '1.1'), ('.25', '1', '1.1'), ('.5', '1', '1.1'),
        ('.5', '1', '1'), ('.5', '1', '1.01'), ('.5', '.97', '1.1'),
        ('1', '1', '1.1')]]
    print(json.dumps({'evidence_tier': 'counterfactual_analytic_upper_bound',
        'original_physical_gate': 'BOTH_INFEASIBLE',
        'original_area_pair_um2': float(AREA_PAIR),
        'original_area_serial_um2': float(AREA_SERIAL),
        'slice_area_saving_percent': float(100 * AREA_SAVING),
        'formula': 'R_throughput <= min(clock_ratio/(1-f_slice*area_saving), bandwidth_headroom)',
        'assumptions': ['same useful work and traffic per admitted request',
                        'area-replicable tile', 'no additional overhead or lost occupancy',
                        'equal admission throughput per clock', 'physical closure hypothetical'],
        'scenarios': rows,
        'integer_replication_f_half': [integer_replication('.5', n) for n in (16, 64, 1024)]}, indent=2))


if __name__ == '__main__':
    main()
