#!/usr/bin/env python3
"""Necessary (not sufficient) throughput/area bound from routed area and bank service.

Uses measured Nov 2 routed areas, which are ELECTRICALLY ILLEGAL. The
bound cannot be used to claim a viable implementation. No cycle data invented.
"""
from fractions import Fraction as F

COMPACT = F('21314.6')
PAIRWISE = F('21324.7')

def necessary_cycle_ratio(candidate_area=PAIRWISE, baseline_area=COMPACT,
                          candidate_period=F(1), baseline_period=F(1)):
    """Minimum C_base/C_candidate for candidate throughput per area to win."""
    return candidate_area * candidate_period / (baseline_area * baseline_period)

def bank_bound(total_requests, bank_histogram, read_ports_per_bank=2):
    """Lower bound on cycles for unit-service bank requests; not an IPC model."""
    assert sum(bank_histogram) == total_requests
    assert total_requests >= 0 and read_ports_per_bank > 0
    return max((n + read_ports_per_bank - 1)//read_ports_per_bank for n in bank_histogram) if bank_histogram else 0

def max_candidate_cycles(base_cycles, candidate_area=PAIRWISE,
                         baseline_area=COMPACT, candidate_period=F(1), baseline_period=F(1)):
    """Strict win requires candidate cycles BELOW this rational threshold."""
    return F(base_cycles) * baseline_area * baseline_period / (candidate_area * candidate_period)

def self_test():
    assert PAIRWISE > COMPACT
    assert necessary_cycle_ratio() == F('21324.7') / F('21314.6')
    assert bank_bound(512,[512,0]) == 256
    assert bank_bound(512,[256,256]) == 128
    assert bank_bound(512,[0,512]) == 256
    assert max_candidate_cycles(512) < 512
    assert necessary_cycle_ratio(candidate_period=F(101,100)) > necessary_cycle_ratio()
    assert F(257,256) < necessary_cycle_ratio(candidate_period=F(101,100))
    for base_cycles in range(1,101):
        for cand_cycles in range(1,101):
            lhs = F(base_cycles,cand_cycles) > necessary_cycle_ratio()
            rhs = F(base_cycles)*COMPACT > F(cand_cycles)*PAIRWISE
            assert lhs == rhs
    print('PASS 10,000 exact area-clock/cycle cross-product checks')
    print('Observed area ratio:', float(PAIRWISE/COMPACT))
    print('Minimum cycle reduction at equal clock:', float(1-COMPACT/PAIRWISE))
    print('Minimum cycle reduction at 1% slower clock:', float(1-COMPACT/(PAIRWISE*F(101,100))))
    print('Status: necessary analytical bound only; both physical routes electrically illegal')

if __name__ == '__main__':
    self_test()
