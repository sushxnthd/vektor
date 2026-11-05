#!/usr/bin/env python3
"""V309 source-conditional sector-service pressure sensitivity; not a GPU simulator.

The archive's original tracer producer is not authenticated. Sector counts are
per-warp 32-byte sets, not cache misses, DRAM transactions, stalls or cycles.
This is a falsification gate for proposed sector-reducing mechanisms, not a
new mechanism or an RTX 5090 performance estimate.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import json

ROWS = 3937565
SECTOR_LO = 1586194
SECTOR_HI = 1595385
SECTOR_BYTES = 32


def fstr(x: Fraction) -> str:
    return f'{x.numerator}/{x.denominator}'


def ceiling(instructions: int, sectors: int, bandwidth: Fraction,
            issue: Fraction, reduction: Fraction = Fraction(0),
            issue_penalty: Fraction = Fraction(0)) -> Fraction:
    """Conditional sector-service throughput ceiling in instructions/cycle.

    Every sector is assumed to consume exactly 32 service bytes at the modeled
    bottleneck. Does not model cache reuse, bursts, memory-level parallelism,
    occupancy, routing, latency, control, or inter-workload phase structure.
    """
    if instructions <= 0 or sectors <= 0 or bandwidth <= 0 or issue <= 0:
        raise ValueError('positive instructions, sectors, bandwidth and issue required')
    if not 0 <= reduction < 1 or issue_penalty < 0:
        raise ValueError('invalid reduction or penalty')
    issue_after = issue / (1 + issue_penalty)
    sector_after = Fraction(sectors) * (1 - reduction)
    return min(issue_after, bandwidth * instructions / (SECTOR_BYTES * sector_after))


def evaluate(instructions: int, sectors: int, bandwidth: Fraction,
             issue: Fraction, reduction: Fraction, penalty: Fraction) -> dict:
    baseline = ceiling(instructions, sectors, bandwidth, issue)
    changed = ceiling(instructions, sectors, bandwidth, issue, reduction, penalty)
    return {'baseline_ipc': fstr(baseline), 'candidate_ipc': fstr(changed),
            'gain': fstr(changed / baseline - 1),
            'break_even_sector_bytes_per_instruction': fstr(Fraction(SECTOR_BYTES * sectors, instructions)),
            'status': 'WIN' if changed > baseline else 'NO_WIN'}


def selftest() -> dict:
    # Independent explicit service-time oracle, without invoking ceiling().
    def oracle(i, s, b, p, r, h):
        issue_time = Fraction(i) * (1 + h) / p
        memory_time = Fraction(32 * s) * (1 - r) / b
        return Fraction(i) / max(issue_time, memory_time)
    n = 0
    for i in (1, 7, 23):
        for s in (1, 3, 41):
            for b in (Fraction(1), Fraction(8), Fraction(32)):
                for p in (Fraction(1, 2), Fraction(1), Fraction(4)):
                    for r in (Fraction(0), Fraction(1, 4), Fraction(3, 4)):
                        for h in (Fraction(0), Fraction(1, 20), Fraction(1, 2)):
                            assert ceiling(i, s, b, p, r, h) == oracle(i, s, b, p, r, h)
                            n += 1
    # If sector count cannot change, overhead can never help.
    for b in (Fraction(1), Fraction(8), Fraction(32), Fraction(128)):
        for s in (SECTOR_LO, SECTOR_HI):
            assert ceiling(ROWS, s, b, Fraction(1), Fraction(0), Fraction(1, 20)) <= ceiling(ROWS, s, b, Fraction(1))
    # Higher sector pressure cannot improve a memory-service ceiling.
    for b in (Fraction(1), Fraction(8), Fraction(32)):
        assert ceiling(ROWS, SECTOR_HI, b, Fraction(1)) <= ceiling(ROWS, SECTOR_LO, b, Fraction(1))
    for bad in (Fraction(-1, 4), Fraction(1)):
        try: ceiling(ROWS, SECTOR_LO, Fraction(8), Fraction(1), bad)
        except ValueError: pass
        else: raise AssertionError('invalid reduction accepted')
    return {'status': 'PASS', 'independent_time_oracle_cases': n,
            'no_free_fixed_address_coalescer_gain': True,
            'sector_interval_monotonicity': True}


def report() -> dict:
    cases = {}
    for name, bandwidth, issue, reduction, penalty in (
        ('frozen_predicted_win_synthetic', Fraction(8), Fraction(1), Fraction(1, 4), Fraction(1, 20)),
        ('frozen_predicted_no_win_synthetic', Fraction(32), Fraction(1), Fraction(1, 4), Fraction(1, 20)),
        ('equal_resource_ideal_fixed_address_coalescer', Fraction(8), Fraction(1), Fraction(0), Fraction(0)),
        ('fixed_address_coalescer_with_control_cost', Fraction(8), Fraction(1), Fraction(0), Fraction(1, 20)),
    ):
        cases[name] = {'assumed_service_bytes_per_cycle': fstr(bandwidth),
                       'assumed_issue_instructions_per_cycle': fstr(issue),
                       'hypothetical_sector_reduction': fstr(reduction),
                       'hypothetical_issue_penalty': fstr(penalty),
                       'sector_low': evaluate(ROWS, SECTOR_LO, bandwidth, issue, reduction, penalty),
                       'sector_high': evaluate(ROWS, SECTOR_HI, bandwidth, issue, reduction, penalty)}
    return {'status': 'PASS', 'evidence_tier': 'conditional_trace_sector_service_roofline_NOT_measured_GPU',
            'archive_producer_verified': False, 'rows': ROWS,
            'source_conditional_sector_interval': [SECTOR_LO, SECTOR_HI],
            'source_conditional_bytes_per_instruction': [fstr(Fraction(32 * SECTOR_LO, ROWS)), fstr(Fraction(32 * SECTOR_HI, ROWS))],
            'cases': cases, 'selftest': selftest(),
            'limitations': ['Sector-set counts are not DRAM bytes or measured stalls',
                            'No cache, MLP, latency, occupancy, control-path, or clock model',
                            'All 11 Rodinia workloads previously explored; no unseen evaluation',
                            'Hypothetical 25% sector reduction has no RTL implementation',
                            'Equal-resource ideal fixed-address coalescer cannot reduce sector count',
                            'No GPU mechanism promoted']}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--selftest', action='store_true')
    a = p.parse_args()
    print(json.dumps(selftest() if a.selftest else report(), indent=2, sort_keys=True))
