#!/usr/bin/env python3
"""Fail-closed arithmetic/feasibility check of run 40156470550 aggregate.
Does not replace raw-log or independent OpenROAD audits.
"""
import argparse
import json
import math

EXPECTED = {
    'pairwise': (17857.644252217142, -1.047895, -0.036622, 0, 3),
    'serial_onehot': (18953.830505097358, -1.859922, -0.019796, 0, 3),
}
FIELDS = ('area_um2', 'setup_ns', 'hold_ns', 'slew', 'cap')


def check(a):
    if (a.get('decision') != 'CANDIDATE_TILE_SLICE_PHYSICAL_GATE_FAIL'
            or a.get('gpu_speedup') != 'NOT_ESTABLISHED'
            or a.get('holdouts') != 'SEALED'
            or a.get('strict_equal_consumed_area') is not False
            or a.get('preregistered_area_limit_um2') != 30000.0
            or a.get('preregistered_min_area_saving_fraction') != .01
            or a.get('preregistered_min_setup_lead_ns') != .05):
        raise ValueError('Original frozen protocol or verdict changed')
    rows = a.get('rows', {})
    if set(rows) != set(EXPECTED):
        raise ValueError('Missing or extra contestant')
    for name, reference in EXPECTED.items():
        r = rows[name]
        if r.get('complete') is not True or r.get('feasible') is not False:
            raise ValueError('Incomplete or incorrectly marked contestant')
        if r.get('evidence_tier') != 'post-CTS propagated-clock detailed-route OpenRCX; not signoff':
            raise ValueError('Wrong evidence tier')
        vals = [r['final'][k] for k in FIELDS]
        if any(type(v) not in (float, int) or not math.isfinite(v)
               or abs(v - ref) > 1e-6 for v, ref in zip(vals, reference)):
            raise ValueError('Original physical measurements altered')
        area, setup, hold, slew, cap = vals
        if area <= 30000 and setup >= .05 and hold >= 0 and slew == cap == 0:
            raise ValueError('Infeasibility classification inconsistent')
    p, c = EXPECTED['pairwise'], EXPECTED['serial_onehot']
    saving = (c[0] - p[0]) / c[0]
    lead = p[1] - c[1]
    comp = a['comparison']
    if (abs(comp['candidate_integrated_area_saving_fraction'] - saving) > 1e-10
            or abs(comp['candidate_integrated_extracted_setup_lead_ns'] - lead) > 1e-10
            or comp['candidate_feasible'] is not False
            or comp['control_feasible'] is not False
            or comp['same_clock_admission_gain'] != 0.0
            or comp['gpu_throughput_measured'] is not False):
        raise ValueError('Invalid comparison or unsupported throughput claim')
    return {'verdict': 'BOTH_PHYSICALLY_INFEASIBLE_NO_PARETO_CLAIM',
            'area_saving_fraction': saving, 'setup_slack_lead_ns': lead,
            'candidate_setup_shortfall_ns': .05 - p[1],
            'control_setup_shortfall_ns': .05 - c[1],
            'same_clock_admission_gain': 0.0, 'gpu_speedup': 'NOT_ESTABLISHED'}


def self_test():
    from copy import deepcopy
    rows = {k: {'complete': True, 'feasible': False,
                'evidence_tier': 'post-CTS propagated-clock detailed-route OpenRCX; not signoff',
                'final': dict(zip(FIELDS, v))} for k, v in EXPECTED.items()}
    p, c = EXPECTED['pairwise'], EXPECTED['serial_onehot']
    a = {'decision': 'CANDIDATE_TILE_SLICE_PHYSICAL_GATE_FAIL',
         'gpu_speedup': 'NOT_ESTABLISHED', 'holdouts': 'SEALED',
         'strict_equal_consumed_area': False,
         'preregistered_area_limit_um2': 30000.0,
         'preregistered_min_area_saving_fraction': .01,
         'preregistered_min_setup_lead_ns': .05, 'rows': rows,
         'comparison': {'candidate_integrated_area_saving_fraction': (c[0]-p[0])/c[0],
                        'candidate_integrated_extracted_setup_lead_ns': p[1]-c[1],
                        'candidate_feasible': False, 'control_feasible': False,
                        'same_clock_admission_gain': 0.0,
                        'gpu_throughput_measured': False}}
    assert check(a)['verdict'].startswith('BOTH_PHYSICALLY')
    for mutate in (lambda d: d['rows']['serial_onehot']['final'].update(cap=0),
                   lambda d: d['rows']['pairwise'].update(feasible=True),
                   lambda d: d.update(holdouts='OPEN'),
                   lambda d: d['comparison'].update(candidate_integrated_extracted_setup_lead_ns=2),
                   lambda d: d['rows']['pairwise']['final'].update(setup_ns=float('nan'))):
        d = deepcopy(a)
        mutate(d)
        try:
            check(d)
        except (ValueError, KeyError, TypeError):
            continue
        raise AssertionError('Tampered evidence accepted')
    print('V296_PAIRED_ORIGINAL_AUDIT_SELFTEST_PASS')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--aggregate')
    args = ap.parse_args()
    if args.self_test:
        self_test()
    if args.aggregate:
        with open(args.aggregate) as f:
            print(json.dumps(check(json.load(f)), indent=2))
    if not args.self_test and not args.aggregate:
        ap.error('Pass --self-test or --aggregate')
