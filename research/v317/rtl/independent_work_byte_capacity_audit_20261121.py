#!/usr/bin/env python3
"""V317 independent work/byte capacity-bound audit (development only).

Exact rational tests; does not import the scheduler or open reserved holdouts.
Capacity comparisons require a fixed completed-work unit, matched workload,
and a defensible lower bound on bytes per completed work for the candidate.
"""
from fractions import Fraction as Q

def traffic_limited_speedup(baseline_work_rate, candidate_bytes_per_second,
                            minimum_candidate_bytes_per_work):
    """Upper bound T_c/T_b if every completed work consumes >= b bytes."""
    assert all(v > 0 for v in (baseline_work_rate, candidate_bytes_per_second,
                               minimum_candidate_bytes_per_work))
    return candidate_bytes_per_second / (minimum_candidate_bytes_per_work *
                                          baseline_work_rate)

def joint_capacity_bound(baseline_work_rate, candidate_issue_work_rate,
                         candidate_bytes_per_second, minimum_bytes_per_work):
    assert candidate_issue_work_rate > 0
    return min(candidate_issue_work_rate / baseline_work_rate,
               traffic_limited_speedup(baseline_work_rate,
                                       candidate_bytes_per_second,
                                       minimum_bytes_per_work))

def main():
    # Matched units: work/s, bytes/s, bytes/work.
    assert traffic_limited_speedup(Q(50), Q(1000), Q(10)) == 2
    assert joint_capacity_bound(Q(50), Q(75), Q(1000), Q(10)) == Q(3, 2)
    # Same nominal bandwidth but lower bytes/work can permit higher throughput.
    assert traffic_limited_speedup(Q(50), Q(1000), Q(8)) == Q(5, 2)
    # More bytes/work can eliminate a hypothetical issue-rate advantage.
    assert joint_capacity_bound(Q(50), Q(100), Q(1000), Q(25)) == Q(4, 5)
    # A conservative LOWER bound on bytes/work is necessary for a sound
    # throughput UPPER bound; an average or upper bound is insufficient.
    assert traffic_limited_speedup(Q(50), Q(1000), Q(5)) > traffic_limited_speedup(
        Q(50), Q(1000), Q(10))
    # Zero traffic lower bound gives no finite bandwidth-derived ceiling.
    try:
        traffic_limited_speedup(Q(50), Q(1000), Q(0))
    except AssertionError:
        pass
    else:
        raise AssertionError("Missing positive traffic floor must be rejected")
    print("PASS: exact-rational dimensional traffic ceiling; no measured PPA claim")

if __name__ == "__main__":
    main()
