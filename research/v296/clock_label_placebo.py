#!/usr/bin/env python3
"""Frozen architecture-label placebo for V296's shared synthetic scheduler.

The architecture is NOT an input to replay. Results are synthetic, not GPU evidence.
Protocol: research/v296/CLOCK_LABEL_PLACEBO_PREREG_20261025.md
"""
import argparse
import json
import math
import matched_walltime_workload as model

CASES = (
    ('clock_only_win', 296501, .95, .35, .90, 20., 64),
    ('bandwidth_no_win', 296502, .95, .35, .90, 1., 64),
    ('hotspot_stress', 296503, .95, .90, .98, 20., 64),
)


def evaluate():
    rows = {}
    for name, seed, probability, hotspot, persistence, bandwidth, bucket in CASES:
        events = model.events(seed, probability=probability,
                              hotspot=hotspot, persistence=persistence)
        t3 = model.replay(events, 3., bandwidth, bucket)
        t4 = model.replay(events, 4., bandwidth, bucket)
        assert t3['independent_oracle'] and t4['independent_oracle']
        assert t3['fifo_conservation'] and t4['fifo_conservation']
        assert t3['offered_per_ns'] == t4['offered_per_ns']
        q3, q4 = t3['issued_per_ns'], t4['issued_per_ns']
        if min(q3, q4) <= 0: raise AssertionError('Zero throughput')
        original = q3 / q4
        swapped = q4 / q3
        if not math.isclose(original*swapped, 1., abs_tol=1e-12):
            raise AssertionError('Clock-swap reciprocity failed')
        if name == 'clock_only_win' and not 1.01 <= original <= 1.50:
            raise AssertionError('Preregistered clock-only win prediction failed')
        if name == 'bandwidth_no_win' and not .999 <= original <= 1.001:
            raise AssertionError('Preregistered bandwidth no-win prediction failed')
        rows[name] = dict(seed=seed, bandwidth_gbs=bandwidth,
            hotspot=hotspot, persistence=persistence, bucket_bytes=bucket,
            serial_at_4ns=q4, v296_at_3ns=q3,
            original_label_ratio=original,
            swapped_label_ratio=swapped,
            matched_3ns_ratio=q3/q3,
            matched_4ns_ratio=q4/q4,
            architecture_specific_gain_identifiable=False,
            period_only_ratio=original,
            invariants_passed=True)
    return dict(protocol='CLOCK_LABEL_PLACEBO_PREREG_20261025.md',
        evidence='PROSPECTIVE_SYNTHETIC_NEGATIVE_CONTROL_NOT_GPU',
        model='SAME_ARBITER_REPLAY_FOR_BOTH_ARCHITECTURES',
        period_ns=[3.,4.], original_physical_gate='BOTH_INFEASIBLE',
        gpu_holdouts='SEALED', measured_gpu_speedup='NOT_ESTABLISHED', cases=rows)


def self_test():
    for row in evaluate()['cases'].values():
        assert row['matched_3ns_ratio'] == 1.
        assert row['matched_4ns_ratio'] == 1.
        assert abs(row['original_label_ratio']*row['swapped_label_ratio']-1.) < 1e-12
    print('V296_CLOCK_LABEL_PLACEBO_SELFTEST_PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--evaluate', action='store_true')
    args = parser.parse_args()
    if args.self_test: self_test()
    if args.evaluate: print(json.dumps(evaluate(), indent=2, sort_keys=True))
    if not args.self_test and not args.evaluate: parser.error('Choose --self-test or --evaluate')
