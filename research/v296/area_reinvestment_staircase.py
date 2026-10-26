#!/usr/bin/env python3
"""Independent exact-rational equal-budget slice replication falsification.

Run: python3 research/v296/area_reinvestment_staircase.py --self-test
     python3 research/v296/area_reinvestment_staircase.py
Evidence: AREA_REINVESTMENT_STAIRCASE_PREREG_20261026.md.
This is a conditional *mapped-area* packing law, not routed GPU performance.
"""
import argparse
import json
from fractions import Fraction as F

A_PAIRWISE = F(9286592, 1000)  # um^2, hosted four-way mapped synthesis
A_SERIAL = F(9844926, 1000)
Q = F(957548877, 320000000)  # previously validated synthetic model
PERIOD_NS = F(7, 2)
BYTES_PER_WAVE = 4


def ceil_fraction(x):
    return -(-x.numerator // x.denominator)


def min_replication_budget(serial_copies, pairwise_area=A_PAIRWISE, serial_area=A_SERIAL):
    """Smallest serial-copy budget permitting one additional pairwise copy."""
    if serial_copies < 0 or pairwise_area <= 0 or serial_area <= 0:
        raise ValueError('invalid copy count or area')
    budget = serial_copies * serial_area
    return int(budget // pairwise_area)


def first_extra_threshold(pairwise_area=A_PAIRWISE, serial_area=A_SERIAL):
    """Exact closed-form threshold. None means no candidate packing advantage."""
    if pairwise_area <= 0 or serial_area <= 0:
        raise ValueError('areas must be positive')
    if pairwise_area >= serial_area:
        return None
    return ceil_fraction(pairwise_area / (serial_area - pairwise_area))


def reference_copy_count(budget, area):
    """Independent enumeration, without division or the threshold formula."""
    if budget < 0 or area <= 0:
        raise ValueError('invalid budget/area')
    copies = 0
    consumed = F(0)
    while consumed + area <= budget:
        consumed += area
        copies += 1
    return copies


def useful_waves_per_second(n, q=Q, period_ns=PERIOD_NS,
                            bandwidth_gbs=F(100), bytes_per_wave=BYTES_PER_WAVE,
                            overhead=F(0)):
    if n < 0 or q < 0 or period_ns <= 0 or bandwidth_gbs < 0 or bytes_per_wave <= 0 or overhead < 0:
        raise ValueError('invalid throughput parameter')
    offered = F(n) * q * F(10**9) / period_ns / (1 + overhead)
    bandwidth_cap = bandwidth_gbs * F(10**9) / bytes_per_wave
    return min(offered, bandwidth_cap)


def scenario(serial_copies, bandwidth_gbs, pairwise_area=A_PAIRWISE, serial_area=A_SERIAL,
             pairwise_period_ns=PERIOD_NS, serial_period_ns=PERIOD_NS,
             pairwise_overhead=F(0), serial_overhead=F(0)):
    candidate_copies = min_replication_budget(serial_copies, pairwise_area, serial_area)
    serial_rate = useful_waves_per_second(serial_copies, period_ns=serial_period_ns,
                                          bandwidth_gbs=bandwidth_gbs, overhead=serial_overhead)
    candidate_rate = useful_waves_per_second(candidate_copies, period_ns=pairwise_period_ns,
                                             bandwidth_gbs=bandwidth_gbs, overhead=pairwise_overhead)
    gain = candidate_rate / serial_rate - 1 if serial_rate else None
    return {'serial_copies': serial_copies, 'pairwise_copies': candidate_copies,
            'shared_bandwidth_GBps': str(bandwidth_gbs),
            'serial_waves_per_second': str(serial_rate),
            'pairwise_waves_per_second': str(candidate_rate),
            'gain_fraction': str(gain) if gain is not None else None,
            'gain_pct': float(gain * 100) if gain is not None else None}


def self_test():
    assert A_PAIRWISE == F(9286592, 1000)
    assert A_SERIAL == F(9844926, 1000)
    assert first_extra_threshold() == 17
    assert [min_replication_budget(n) for n in (1, 16, 17, 18)] == [1, 16, 18, 19]
    assert scenario(17, F(100))['gain_fraction'] == str(F(1, 17))
    assert scenario(1, F(100))['gain_fraction'] == '0'
    assert scenario(17, F(10))['gain_fraction'] == '0'
    assert first_extra_threshold(A_SERIAL, A_SERIAL) is None
    assert first_extra_threshold(A_SERIAL + 1, A_SERIAL) is None
    for n in range(1, 1001):
        budget = n * A_SERIAL
        assert min_replication_budget(n) == reference_copy_count(budget, A_PAIRWISE), n
        assert reference_copy_count(budget, A_SERIAL) == n, n
        assert (min_replication_budget(n) > n) == (n >= first_extra_threshold()), n
    for adverse in (F(0), F(2, 100), F(5, 100)):
        a = A_PAIRWISE * (1 + adverse)
        s = A_SERIAL * (1 - adverse)
        t = first_extra_threshold(a, s)
        if t is not None:
            assert reference_copy_count((t - 1) * s, a) <= t - 1
            assert reference_copy_count(t * s, a) >= t + 1
    for w in (F(0), F(1, 10), F(1), F(10), F(100), F(1000)):
        for n in (1, 2, 16):
            r = useful_waves_per_second(n, bandwidth_gbs=w)
            assert r == useful_waves_per_second(n, bandwidth_gbs=w)
            assert r <= w * F(10**9) / BYTES_PER_WAVE
    for args in ((-1, A_PAIRWISE, A_SERIAL), (1, 0, A_SERIAL), (1, A_PAIRWISE, 0)):
        try:
            min_replication_budget(*args)
            raise AssertionError('invalid input accepted')
        except ValueError:
            pass
    return 'PASS: 1000 independent enumerations, exact thresholds, three frozen regimes, adverse sensitivity, caps and invalid inputs'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    result = {'evidence_tier': 'exact_conditional_mapped_area_accounting_not_routed_GPU',
              'provenance': 'Actions 40244774412 / artifact 12618038449 / 2026-10-26',
              'pairwise_mapped_area_um2': str(A_PAIRWISE),
              'serial_mapped_area_um2': str(A_SERIAL),
              'area_saving_pct': float((1 - A_PAIRWISE / A_SERIAL) * 100),
              'first_extra_copy_threshold': first_extra_threshold(),
              'nominal_q_waves_per_cycle_per_slice': str(Q),
              'equal_clock_period_ns': str(PERIOD_NS),
              'frozen_scenarios': {
                  'single_slice_no_win': scenario(1, F(100)),
                  'sixteen_slices_no_win': scenario(16, F(100)),
                  'seventeen_slices_conditional_win': scenario(17, F(100)),
                  'seventeen_slices_bandwidth_no_win': scenario(17, F(10))},
              'adverse_area_sensitivity': {}}
    for pct in (0, 2, 5):
        adverse = F(pct, 100)
        a = A_PAIRWISE * (1 + adverse)
        s = A_SERIAL * (1 - adverse)
        result['adverse_area_sensitivity'][f'{pct}pct_candidate_up_serial_down'] = {
            'candidate_area_um2': str(a), 'serial_area_um2': str(s),
            'first_extra_copy_threshold': first_extra_threshold(a, s)}
    if args.self_test:
        result['self_test'] = self_test()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
