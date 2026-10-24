#!/usr/bin/env python3
"""V296 pre-registered tile boundary model; analytical predictions, not GPU measurements."""
import argparse
import json
import math
from pathlib import Path


def predict(control_area_before_um2, control_area_after_um2, tile_area_before_um2,
            control_period_before_ns, control_period_after_ns, other_period_ns,
            ipc, bytes_per_instruction, bandwidth_bytes_per_ns):
    values = [control_area_before_um2, control_area_after_um2, tile_area_before_um2,
              control_period_before_ns, control_period_after_ns, other_period_ns,
              ipc, bytes_per_instruction, bandwidth_bytes_per_ns]
    if not all(math.isfinite(x) for x in values):
        raise ValueError('Nonfinite input')
    if not (0 < control_area_after_um2 <= control_area_before_um2 <= tile_area_before_um2):
        raise ValueError('Invalid areas or no controller saving')
    if not all(x > 0 for x in (control_period_before_ns, control_period_after_ns,
                                other_period_ns, ipc, bandwidth_bytes_per_ns)):
        raise ValueError('Periods, IPC and bandwidth must be positive')
    if bytes_per_instruction < 0:
        raise ValueError('Traffic must be nonnegative')
    if control_period_after_ns > control_period_before_ns:
        raise ValueError('This positive-law branch assumes controller timing does not worsen')
    t0 = max(control_period_before_ns, other_period_ns)
    t1 = max(control_period_after_ns, other_period_ns)
    traffic_limit = (bandwidth_bytes_per_ns / bytes_per_instruction
                     if bytes_per_instruction else float('inf'))
    rate0 = min(ipc / t0, traffic_limit)
    rate1 = min(ipc / t1, traffic_limit)
    area_delta = control_area_before_um2 - control_area_after_um2
    return {
        'tile_area_saving_fraction': area_delta / tile_area_before_um2,
        'controller_area_saving_fraction': area_delta / control_area_before_um2,
        'tile_period_before_ns': t0,
        'tile_period_after_ns': t1,
        'baseline_rate_instructions_per_ns': rate0,
        'candidate_rate_instructions_per_ns': rate1,
        'potential_frequency_or_bandwidth_speedup_fraction': rate1 / rate0 - 1,
        'same_clock_same_resources_issue_speedup_fraction': 0.0,
        'evidence_tier': 'ANALYTICAL_ONLY_UNVALIDATED',
    }


def self_test():
    common = dict(control_area_before_um2=100.0, control_area_after_um2=86.0,
                  tile_area_before_um2=10000.0, control_period_before_ns=3.5,
                  control_period_after_ns=3.0, ipc=1.0,
                  bytes_per_instruction=4.0, bandwidth_bytes_per_ns=2.0)
    win = predict(other_period_ns=2.8, **common)
    assert abs(win['tile_area_saving_fraction'] - .0014) < 1e-12
    assert abs(win['potential_frequency_or_bandwidth_speedup_fraction'] - (3.5/3.0-1)) < 1e-12
    no_critical = predict(other_period_ns=4.0, **common)
    assert no_critical['potential_frequency_or_bandwidth_speedup_fraction'] == 0
    no_bw = predict(other_period_ns=2.8, **(common | {'bandwidth_bytes_per_ns': 0.4}))
    assert no_bw['potential_frequency_or_bandwidth_speedup_fraction'] == 0
    for bad in (common | {'tile_area_before_um2': 10.0}, common | {'ipc': float('nan')},
                common | {'control_period_after_ns': 4.0}):
        try:
            predict(other_period_ns=2.8, **bad)
        except ValueError:
            continue
        raise AssertionError('Invalid model input accepted')
    print('V296_TILE_BOUNDARY_SELFTEST_PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--config', type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.config:
        print(json.dumps(predict(**json.loads(args.config.read_text())), indent=2))
    else:
        parser.error('Specify --self-test or --config')
