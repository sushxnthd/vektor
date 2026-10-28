#!/usr/bin/env python3
"""Independent falsification checks; not RTL or physical validation."""
import json
from v298_holdout import evaluate


def single_credit_delay(background_latency, compute_delay):
    # Independently constructed two-event schedule: background refills at t=0;
    # dependent miss arrives at t=D. Guard holds the freed credit until D.
    dependent_arrival = compute_delay
    background_return = background_latency
    baseline_issue = max(dependent_arrival, background_return)
    guard_issue = dependent_arrival
    return baseline_issue - guard_issue


def main():
    for Lb in range(1, 65):
        for D in range(0, 65):
            assert single_credit_delay(Lb, D) == max(0, Lb - D)
    fresh = evaluate()
    assert fresh['results']['H1_predicted_win']['gate_pass']
    assert fresh['results']['H2_predicted_win']['gate_pass']
    for name in ('H3_predicted_no_win', 'H4_predicted_no_win',
                 'H5_short_chain', 'H6_oracle_advantage'):
        assert not fresh['results'][name]['gate_pass']
    # Negative control: replacing the guard with work-conserving behavior
    # must erase the H1 critical-latency improvement.
    h1 = fresh['results']['H1_predicted_win']['means']
    assert h1['work_conserving']['mean_burst_latency'] > 1.1 * h1['guard']['mean_burst_latency']
    assert h1['guard']['background_completed'] < h1['work_conserving']['background_completed']
    # The deadline-aware upper-bound controller exposes over-reservation on H6.
    h6 = fresh['results']['H6_oracle_advantage']['means']
    assert h6['deadline_aware']['background_completed'] > h6['guard']['background_completed']
    assert h6['deadline_aware']['mean_burst_latency'] < h6['guard']['mean_burst_latency']
    print(json.dumps({'isolated_credit_exhaustive_cases': 64 * 65,
                      'holdout_cases': len(fresh['results']),
                      'negative_control_detected': True,
                      'oracle_overreservation_counterexample': True,
                      'status': 'PASS'}))


if __name__ == '__main__':
    main()
