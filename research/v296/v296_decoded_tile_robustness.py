#!/usr/bin/env python3
"""V296 decoded tile area/timing robustness: conditional algebra, not routed GPU data.

Reads frozen pre-CTS evidence; no timing, power, bandwidth, or workload outcome
is inferred from an unrouted area proxy. Intended as a prospective decision map
for the already-running paired post-CTS experiment.
"""
import argparse
import json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 35
D = Decimal
BASE = Path(__file__).resolve().parent
PRECTS = BASE / 'BANK_DECODE_PAIRED_PRECTS_RESULT_20261026.json'


def read_anchor(path):
    data = json.loads(Path(path).read_text())
    if data.get('evidence_tier') != 'PAIRED_PRECTS_ESTIMATED_PARASITICS_NOT_ROUTED_SIGNOFF':
        raise ValueError('wrong evidence tier')
    if data.get('source_run_id') != 40337484954 or data.get('fifth_stage_serial_not_included') is not True:
        raise ValueError('missing frozen provenance or fifth-stage limitation')
    for v in ('candidate', 'serial'):
        if data[v].get('stage') != 'PRECTS_GLOBAL_ROUTE_ESTIMATED_PARASITICS_NOT_SIGNOFF':
            raise ValueError('not pre-CTS data')
    return data


def candidate_slices(serial_area, candidate_area, serial_slices, serial_extra, candidate_extra):
    """Area-only integer fit, not physically routable tile replication."""
    if not (serial_area > 0 and candidate_area > 0 and serial_slices > 0):
        raise ValueError('nonpositive area or baseline slices')
    if serial_extra < 0 or candidate_extra < 0:
        raise ValueError('negative overhead')
    budget = D(serial_slices) * serial_area * (1 + serial_extra)
    return int(budget // (candidate_area * (1 + candidate_extra)))


def overhead_limit(serial_area, candidate_area, serial_slices=17, target_slices=18, serial_extra=D(0)):
    """Exact maximal fractional candidate per-slice area overhead for a target fit."""
    return D(serial_slices) * serial_area * (1 + serial_extra) / (D(target_slices) * candidate_area) - 1


def setup_guard_status(setup_slack_ns, adverse_delta_ps, guard_ns=D('0.050')):
    """Algebraic adverse setup-slack perturbation, NOT an RC extraction model."""
    return setup_slack_ns - adverse_delta_ps / 1000 >= guard_ns


def ideal_capacity(slices, resident_warps, latency=2, issue_slots=4, read_ports_total=32):
    """Conservation ceiling per local cycle, not a measured issue rate."""
    return min(D(issue_slots * slices), D(resident_warps) / D(latency), D(read_ports_total * slices) / 2)


def conditional_gain(serial_rate, candidate_rate, period_ratio, shared_cap=None):
    """Same physical-time bandwidth cap; rates are per local clock before conversion."""
    if min(serial_rate, candidate_rate, period_ratio) <= 0:
        raise ValueError('invalid rates or period')
    sr = serial_rate
    cr = candidate_rate / period_ratio
    if shared_cap is not None:
        if shared_cap <= 0:
            raise ValueError('invalid shared cap')
        sr, cr = min(sr, shared_cap), min(cr, shared_cap)
    return cr / sr - 1


def self_test():
    sa, ca = D('17301.969634786474'), D('16089.542143049584')
    threshold = overhead_limit(sa, ca)
    assert D('0.0156') < threshold < D('0.0157')
    assert candidate_slices(sa, ca, 17, D(0), D(0)) == 18
    assert candidate_slices(sa, ca, 17, D(0), D('0.015')) == 18
    assert candidate_slices(sa, ca, 17, D(0), D('0.016')) == 17
    assert candidate_slices(sa, ca, 17, D(0), threshold - D('0.000000000001')) == 18
    assert candidate_slices(sa, ca, 17, D(0), threshold + D('0.000001')) == 17
    assert setup_guard_status(D('0.050206'), D('0.205'))
    assert setup_guard_status(D('0.050206'), D('0.206'))
    assert not setup_guard_status(D('0.050206'), D('0.207'))
    assert ideal_capacity(18, 32) == D(16)
    assert ideal_capacity(17, 32) == D(16)
    assert ideal_capacity(18, 180) == D(72)
    assert ideal_capacity(17, 180) == D(68)
    assert conditional_gain(D(68), D(72), D(1), D(25)) == 0
    assert conditional_gain(D(68), D(72), D(1), None) == D(72)/D(68)-1
    assert conditional_gain(D(68), D(68), D(1), None) == 0
    try:
        candidate_slices(sa, ca, 17, D(0), D('-0.01'))
    except ValueError:
        pass
    else:
        raise AssertionError('negative overhead was accepted')
    print('V296_DECODED_TILE_ROBUSTNESS_SELFTEST_PASS')


def evaluate(anchor, output):
    data = read_anchor(anchor)
    sa, ca = D(str(data['serial']['area_um2'])), D(str(data['candidate']['area_um2']))
    margin_ps = (D(str(data['candidate']['setup_slack_ns'])) - D('0.050')) * 1000
    serial_extras = [D(x) for x in ('0', '0.005', '0.01', '0.02')]
    candidate_extras = [D(x) for x in ('0', '0.005', '0.01', '0.015', '0.0156', '0.016', '0.02', '0.03')]
    sensitivity = []
    for se in serial_extras:
        for ce in candidate_extras:
            nc = candidate_slices(sa, ca, 17, se, ce)
            sensitivity.append({'serial_extra_fraction': str(se), 'candidate_extra_fraction': str(ce),
                                'candidate_slices_under_17_serial_budget': nc,
                                'ratio_of_ideal_high_occupancy_capacity_ceilings': str(D(nc)/17)})
    workloads = []
    for warps in (32, 180, 256):
        for candidate_extra in (D('0'), D('0.016')):
            nc = candidate_slices(sa, ca, 17, D(0), candidate_extra)
            qs, qp = ideal_capacity(17, warps), ideal_capacity(nc, warps)
            for period in (D('0.95'), D('1'), D('1.02')):
                for cap in (None, D(25)):
                    workloads.append({'warps': warps, 'candidate_extra_fraction': str(candidate_extra),
                                      'candidate_slices': nc, 'period_ratio_assumed': str(period),
                                      'shared_cap_assumed': None if cap is None else str(cap),
                                      'serial_ideal_ceiling_per_cycle': str(qs),
                                      'candidate_ideal_ceiling_per_cycle': str(qp),
                                      'ratio_of_ideal_capacity_ceilings_minus_one': str(conditional_gain(qs, qp, period, cap))})
    timing = [{'adverse_setup_delta_ps': str(d),
               'prects_guard_retained_algebraically': setup_guard_status(D(str(data['candidate']['setup_slack_ns'])), d)}
              for d in map(D, ('0', '0.1', '0.2', '0.205', '0.206', '0.207', '0.25', '1', '10', '50'))]
    result = {
        'tier': 'PROSPECTIVE_ALGEBRAIC_AREA_TIMING_SENSITIVITY_NOT_ROUTED_OR_GPU_PERFORMANCE',
        'source_pre_cts_run': data['source_run_id'],
        'source_serial_fifth_stage_missing': True,
        'candidate_prects_guard_margin_ps': str(margin_ps),
        'candidate_extra_area_threshold_for_18_slices_at_fixed_17_serial_budget_fraction': str(overhead_limit(sa, ca)),
        'area_sensitivity': sensitivity,
        'conditional_ideal_resource_ceiling_sweep': workloads,
        'setup_perturbation_sensitivity': timing,
        'physical_result_used': False,
        'claim': 'No physical clock, routed area, actual GPU throughput, power, or positive mechanism demonstrated.'
    }
    Path(output).write_text(json.dumps(result, indent=2) + '\n')
    print('V296_DECODED_TILE_ROBUSTNESS_EVALUATED', '18-slice overhead threshold', str(overhead_limit(sa, ca)),
          'preCTS setup margin ps', str(margin_ps))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--evaluate', action='store_true')
    p.add_argument('--anchor', type=Path, default=PRECTS)
    p.add_argument('--output', type=Path, default=BASE / 'DECODED_TILE_ROBUSTNESS_RESULTS_20261026.json')
    a = p.parse_args()
    if a.self_test: self_test()
    if a.evaluate: evaluate(a.anchor, a.output)
    if not (a.self_test or a.evaluate): p.error('select --self-test or --evaluate')
