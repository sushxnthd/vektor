#!/usr/bin/env python3
"""Independent counterexample to interpreting capacity ratios as throughput bounds.

This is an analytic two-resource fluid model, not a GPU measurement. It leaves
the V317 frozen candidate and all prospective holdouts untouched.
"""
from fractions import Fraction as F

def delivered(issue_capacity, bandwidth_capacity):
    assert issue_capacity > 0 and bandwidth_capacity > 0
    return min(issue_capacity, bandwidth_capacity)

def test_capacity_ratio_not_throughput_ceiling():
    # Baseline is issue-limited. Candidate increases issue service by 20%;
    # both have identical physical memory bandwidth. A naive cap of 1.0
    # on the bandwidth-capacity ratio would falsely reject the 20% gain.
    baseline_issue, candidate_issue = F(1,2), F(3,5)
    baseline_bw = candidate_bw = F(1,1)
    base = delivered(baseline_issue, baseline_bw)
    cand = delivered(candidate_issue, candidate_bw)
    observed = cand / base
    naive_bw_ratio = candidate_bw / baseline_bw
    assert observed == F(6,5)
    assert naive_bw_ratio == 1
    assert observed > naive_bw_ratio
    # A valid throughput upper bound requires capacity normalized by
    # *baseline achieved throughput*, not baseline bandwidth capacity.
    valid_bw_ceiling = candidate_bw / base
    valid_issue_ceiling = candidate_issue / base
    assert observed == min(valid_bw_ceiling, valid_issue_ceiling)
    return observed, naive_bw_ratio, valid_bw_ceiling

def test_baseline_bandwidth_saturated():
    baseline_issue = candidate_issue = F(2,1)
    baseline_bw, candidate_bw = F(1,1), F(11,10)
    base = delivered(baseline_issue, baseline_bw)
    cand = delivered(candidate_issue, candidate_bw)
    assert cand/base == candidate_bw/baseline_bw == F(11,10)

if __name__ == "__main__":
    ratio, naive, valid = test_capacity_ratio_not_throughput_ceiling()
    test_baseline_bandwidth_saturated()
    print(f"PASS: capacity-ratio counterexample: achieved={ratio}, naive-bandwidth-cap={naive}, valid-absolute-cap={valid}")
    print("INTERPRETATION: min(service*clock*occupancy, bandwidth) is a conditional bound only when ratios are normalized consistently to baseline achieved throughput and resource bottlenecks are identified.")
    print("V317 policy remains rejected on measured development throughput; this test does not rehabilitate it.")
