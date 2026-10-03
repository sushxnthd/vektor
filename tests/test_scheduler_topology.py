from sim.vektor.scheduler_topology import (
    balanced_trace,
    clustered_trace,
    evaluate_fixed_four_by_eight,
    evaluate_global_four_wide,
    evaluate_limited_steal,
    lopsided_memory_trace,
    rotating_cluster_trace,
)


def test_balanced_readiness_has_no_partition_penalty():
    trace = balanced_trace()
    fixed = evaluate_fixed_four_by_eight(trace)
    steal = evaluate_limited_steal(trace)
    global_ = evaluate_global_four_wide(trace)
    assert fixed.issue_utilization == 1.0
    assert steal.issue_utilization == 1.0
    assert global_.issue_utilization == 1.0


def test_clustered_readiness_is_partially_recovered_by_one_backup_per_partition():
    trace = clustered_trace()
    fixed = evaluate_fixed_four_by_eight(trace)
    steal = evaluate_limited_steal(trace)
    global_ = evaluate_global_four_wide(trace)
    assert fixed.issue_utilization == 0.25
    assert steal.issue_utilization == 0.5
    assert global_.issue_utilization == 1.0


def test_rotating_cluster_is_fully_recovered_by_limited_steal():
    trace = rotating_cluster_trace()
    fixed = evaluate_fixed_four_by_eight(trace)
    steal = evaluate_limited_steal(trace)
    global_ = evaluate_global_four_wide(trace)
    assert fixed.issue_utilization == 0.5
    assert steal.issue_utilization == 1.0
    assert global_.issue_utilization == 1.0


def test_lopsided_memory_proxy_recovers_part_of_partition_loss():
    trace = lopsided_memory_trace()
    fixed = evaluate_fixed_four_by_eight(trace)
    steal = evaluate_limited_steal(trace)
    global_ = evaluate_global_four_wide(trace)
    assert abs(fixed.issue_utilization - 0.46875) < 1e-12
    assert abs(steal.issue_utilization - 0.6875) < 1e-12
    assert global_.issue_utilization == 1.0
