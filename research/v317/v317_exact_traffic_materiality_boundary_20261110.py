#!/usr/bin/env python3
"""Exact bandwidth-limited traffic boundary against compact; analytical, NOT physical evidence.

The area inputs are historical matched RF-proxy values, NOT from the later
electrically illegal 300x300 timing experiment. Neither route is signed off.
"""
from fractions import Fraction as F

def required_traffic_ratio(area_compact, area_pairwise, materiality=F(102,100)):
    """Maximum candidate/base bytes per useful op for material throughput/area win.

    Applies ONLY if both variants are bandwidth saturated, share physical byte/s,
    and neither has an issue/occupancy ceiling below its bandwidth-limited rate.
    """
    assert area_compact > 0 and area_pairwise > 0 and materiality >= 1
    return area_compact / (materiality * area_pairwise)

def audit():
    c, p = F('21314.6'), F('21324.7')
    threshold = required_traffic_ratio(c, p)
    print('observed_area_pairwise_over_compact', float(p/c))
    print('maximum_pairwise_bytes_per_op_ratio_for_2pct_gain', float(threshold))
    print('minimum_traffic_reduction_percent', float(100*(1-threshold)))
    for traffic in [F(1), F('0.99'), F('0.98'), F('0.97'), F('0.95')]:
        ratio = c/(p*traffic)
        print('candidate_traffic_ratio', float(traffic),
              'bw_limited_perf_per_area_ratio', float(ratio),
              'material', ratio >= F(102,100))
    assert c/p < 1
    assert c/(p*F('0.98')) < F(102,100)
    assert c/(p*F('0.97')) > F(102,100)
    assert required_traffic_ratio(F(100),F(100)) == F(50,51)
    print('PASS exact rational assertions')

if __name__ == '__main__':
    audit()
