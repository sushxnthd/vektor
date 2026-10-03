import pytest

from sim.vektor.divergence import (
    DivergenceTrace,
    alternating_trace,
    coherent_trace,
    evaluate_compaction,
    evaluate_ipdom,
    minority_trace,
    random_trace,
)


def test_coherent_trace_has_full_ipdom_lane_utilization():
    baseline = evaluate_ipdom(coherent_trace())
    assert baseline.lane_utilization == 1.0
    assert baseline.effective_issue_slots == 32 * 16


def test_naive_compaction_loses_on_coherent_trace_when_overhead_is_charged():
    trace = coherent_trace()
    baseline = evaluate_ipdom(trace)
    compacted = evaluate_compaction(
        trace,
        window_warps=8,
        overhead_issue_slots_per_window=4,
    )
    gated = evaluate_compaction(
        trace,
        window_warps=8,
        overhead_issue_slots_per_window=4,
        oracle_gate=True,
    )
    assert compacted.effective_issue_slots > baseline.effective_issue_slots
    assert gated.effective_issue_slots == baseline.effective_issue_slots
    assert gated.bypassed_windows == 4


def test_balanced_divergence_can_nearly_double_effective_slot_efficiency():
    trace = alternating_trace()
    baseline = evaluate_ipdom(trace)
    compacted = evaluate_compaction(
        trace,
        window_warps=8,
        overhead_issue_slots_per_window=4,
    )
    assert baseline.lane_utilization == 0.5
    assert compacted.data_issue_slots == 512
    assert compacted.overhead_issue_slots == 16
    assert compacted.effective_issue_slots == 528
    assert baseline.effective_issue_slots / compacted.effective_issue_slots > 1.9


def test_minority_path_compaction_is_incomplete_but_useful():
    trace = minority_trace()
    baseline = evaluate_ipdom(trace)
    compacted = evaluate_compaction(
        trace,
        window_warps=8,
        overhead_issue_slots_per_window=4,
    )
    assert baseline.effective_issue_slots == 1024
    assert compacted.data_issue_slots == 576
    assert compacted.effective_issue_slots == 592
    assert compacted.lane_utilization < 1.0
    assert baseline.effective_issue_slots / compacted.effective_issue_slots > 1.7


def test_oracle_gate_never_exceeds_ipdom_issue_slot_cost():
    for trace in (
        coherent_trace(),
        alternating_trace(),
        minority_trace(),
        random_trace(seed=7),
    ):
        baseline = evaluate_ipdom(trace)
        for window in (2, 4, 8, 16, 32):
            for overhead in (0, 2, 4, 8, 16):
                gated = evaluate_compaction(
                    trace,
                    window_warps=window,
                    overhead_issue_slots_per_window=overhead,
                    oracle_gate=True,
                )
                assert gated.effective_issue_slots <= baseline.effective_issue_slots


def test_trace_validation_rejects_non_wave32_warp():
    with pytest.raises(ValueError):
        DivergenceTrace(warps=((0, 1),), path_instructions=(1, 1))
