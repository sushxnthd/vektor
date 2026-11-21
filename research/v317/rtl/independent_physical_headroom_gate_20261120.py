#!/usr/bin/env python3
"""V317 development-only utilization-aware physical capacity sanity checks.

Independent of scheduler simulator. No prospective holdout access.
This replaces the INVALID universal bandwidth-ratio ceiling. The earlier
product of service, clock and occupancy is only conditional on a specified
resource model, not a general throughput theorem.
"""
from fractions import Fraction as F

MATERIALITY = F(102, 100)
DEVELOPMENT_RATIOS = (
    F("1.000009115360"), F("0.999919909597"),
    F("0.999751245871"), F("1.000058828344"),
)

def capacity_ceiling(baseline_throughput, candidate_issue_capacity,
                     candidate_bandwidth_capacity):
    """Necessary upper bound when all inputs are in SAME work/time units.

    Traffic bandwidth must first be converted using a justified work/byte
    bound; it cannot be compared directly to issue throughput.
    """
    assert min(baseline_throughput, candidate_issue_capacity,
               candidate_bandwidth_capacity) > 0
    return min(candidate_issue_capacity, candidate_bandwidth_capacity) / baseline_throughput

def normalized_ceiling(issue_capacity_ratio, bandwidth_capacity_ratio,
                       baseline_issue_utilization, baseline_bw_utilization):
    """Capacity-only necessary bound relative to measured baseline throughput.

    U_i=T_b/C_i,b; U_b=T_b/C_b,b. For comparable work definitions,
    candidate upper bound is min(r_i/U_i, r_b/U_b).
    """
    assert all(x > 0 for x in (issue_capacity_ratio, bandwidth_capacity_ratio,
                               baseline_issue_utilization, baseline_bw_utilization))
    assert baseline_issue_utilization <= 1 and baseline_bw_utilization <= 1
    return min(issue_capacity_ratio / baseline_issue_utilization,
               bandwidth_capacity_ratio / baseline_bw_utilization)

def main():
    # Counterexample: equal bandwidth capacities do NOT imply <=1x speedup.
    assert capacity_ceiling(F(50), F(120), F(100)) == 2
    assert normalized_ceiling(F(1), F(1), F(1,2), F(1,2)) == 2
    # Saturated bandwidth baseline gives an actual 1x bandwidth ceiling.
    assert normalized_ceiling(F(2), F(1), F(1), F(1)) == 1
    # Unsaturated baseline can improve even if candidate capacity falls.
    assert normalized_ceiling(F(1), F(9,10), F(1,2), F(1,2)) == F(9,5)
    # Strict prospective threshold can be ruled out ONLY if justified
    # candidate capacities and baseline utilizations yield a ceiling <1.02.
    assert normalized_ceiling(F(1), F(1), F(1), F(1)) < MATERIALITY
    assert normalized_ceiling(F(11,10), F(11,10), F(1), F(1)) >= MATERIALITY
    # Observed dev seed ratios are descriptive, NOT physical capacity ceilings.
    assert max(DEVELOPMENT_RATIOS) < MATERIALITY
    print("PASS: utilization-aware necessary capacity bounds; "
          "V317 development no-go descriptive only; holdouts untouched")

if __name__ == "__main__":
    main()
