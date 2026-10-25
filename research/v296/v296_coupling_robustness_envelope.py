#!/usr/bin/env python3
"""V296 SPEF-derived external-capacitance robustness envelope.

Measured-input, algebraic sensitivity only. Not measured switching activity,
not extracted energy, not physical timing closure or a GPU speedup.
"""
import argparse
import json
import math

# Original SHA-locked post-route SPEF accounting, pF (rounded to 6 decimals).
# See ORIGINAL_SPEF_COUPLING_ACTIVITY_RESULT_20261025.md, run 40173311725.
PAIR = dict(ground=21.788331, coupling=14.878993)
SERIAL = dict(ground=24.937753, coupling=17.074129)


def coefficient(row, rho):
    if not math.isfinite(rho) or not -1 <= rho <= 1:
        raise ValueError('Correlation must be finite in [-1,1]')
    return row['ground'] + 2 * row['coupling'] * (1 - rho)


def worst_ratio(activity_ratio, correlation_disadvantage):
    """Worst possible candidate/control proxy under rho_p>=rho_s-delta.

    The extremum is rho_s=+1, rho_p=1-delta for this measured pair.
    The derivative sign is checked independently in self_test().
    """
    if (not math.isfinite(activity_ratio) or activity_ratio <= 0 or
        not math.isfinite(correlation_disadvantage) or
        not 0 <= correlation_disadvantage <= 2):
        raise ValueError('Invalid activity ratio or correlation bound')
    return activity_ratio * (PAIR['ground'] + 2 * PAIR['coupling'] * correlation_disadvantage) / SERIAL['ground']


def delta_break_even(activity_ratio):
    if not math.isfinite(activity_ratio) or activity_ratio <= 0:
        raise ValueError('Invalid activity ratio')
    return (SERIAL['ground'] / activity_ratio - PAIR['ground']) / (2 * PAIR['coupling'])


def brute_worst(activity_ratio, delta, points=4001):
    if points < 2:
        raise ValueError('At least two points required')
    best = (-1., None, None)
    for i in range(points):
        rho_s = -1 + 2 * i / (points - 1)
        rho_p = max(-1., rho_s - delta)
        ratio = activity_ratio * coefficient(PAIR, rho_p) / coefficient(SERIAL, rho_s)
        if ratio > best[0]:
            best = (ratio, rho_s, rho_p)
    return best


def evaluate():
    rows = []
    for a in (1., 1.05, 1.10, 1.145):
        d = delta_break_even(a)
        row = {'activity_ratio_upper_bound': a, 'delta_break_even': d,
               'guaranteed_positive_at_equal_correlation': d > 0,
               'tested_delta': max(0., min(2., d - .01)),
               'tested_worse_delta': max(0., min(2., d + .01))}
        for key, delta in (('inside', row['tested_delta']), ('outside', row['tested_worse_delta'])):
            formula = worst_ratio(a, delta)
            brute, rs, rp = brute_worst(a, delta)
            if abs(formula - brute) > 1e-11:
                raise AssertionError('Independent correlation sweep contradicts boundary')
            row[key] = {'delta': delta, 'worst_ratio': formula,
                        'grid_worst_ratio': brute, 'grid_worst_rho_serial': rs,
                        'grid_worst_rho_pairwise': rp,
                        'candidate_better_in_every_allowed_corner': formula < 1}
        rows.append(row)
    return {'evidence_tier': 'MEASURED_SPEF_INPUTS_ALGEBRAIC_ACTIVITY_CORRELATION_SENSITIVITY',
            'source_run': 40173311725, 'physical_gate': 'BOTH_INFEASIBLE',
            'pairwise_pf': PAIR, 'serial_onehot_pf': SERIAL,
            'law': 'alpha_ratio*(Cg_pair+2*Cc_pair*delta)/Cg_serial < 1',
            'scope': 'all rho_serial in [-1,1] with rho_pair >= rho_serial-delta; alpha_pair/alpha_serial <= alpha_ratio',
            'equal_correlation_robust_activity_ceiling': SERIAL['ground']/PAIR['ground'],
            'rows': rows, 'measured_power': False, 'gpu_speedup': 'NOT_ESTABLISHED',
            'holdouts': 'SEALED'}


def self_test():
    # On the unsaturated segment, the ratio derivative wrt rho_serial is
    # proportional to Cc_serial*Cg_pair-Cc_pair*Cg_serial + 2*Cc_serial*Cc_pair*delta.
    deriv0 = SERIAL['coupling'] * PAIR['ground'] - PAIR['coupling'] * SERIAL['ground']
    assert deriv0 > 0, 'Endpoint proof invalid for this physical pair'
    assert abs(delta_break_even(1.) - .10583451447285452) < 1e-12
    assert abs(delta_break_even(1.05) - .06592885527874615) < 1e-12
    assert abs(delta_break_even(1.10) - .029650983284102095) < 1e-12
    assert worst_ratio(1., 0.10) < 1 < worst_ratio(1., 0.11)
    assert worst_ratio(1.1, .02) < 1 < worst_ratio(1.1, .04)
    for a in (0.5, 1, 1.05, 1.1, 1.2):
        for delta in (0, .02, .1, .5, 1., 1.7, 2.):
            brute, rs, rp = brute_worst(a, delta, points=1001)
            assert abs(brute - worst_ratio(a, delta)) < 1e-11
            assert rs == 1. and abs(rp-(1-delta)) < 1e-12
    for bad_a, bad_d in ((0, 0), (float('nan'), 0), (1, -0.01), (1, 2.01), (1, float('inf'))):
        try: worst_ratio(bad_a, bad_d)
        except ValueError: pass
        else: raise AssertionError('Invalid input accepted')
    print('V296_COUPLING_ROBUSTNESS_SELFTEST_PASS')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test: self_test()
    else: print(json.dumps(evaluate(), indent=2))
