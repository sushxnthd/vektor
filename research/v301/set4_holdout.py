"""Prospectively frozen V301 four-way-set strong-control experiment.

The protocol was committed at 27c5e27 before any N1-N4 result was evaluated.
Run: python research/v301/set4_holdout.py
"""
import json
import statistics
from scoreboard import stream, run

CASES = {
    "N1_medium_skew_short_epoch": (.65, 64, .45, 37),
    "N2_uniform_high": (.82, 128, 0., 128),
    "N3_hot_short_epoch": (.80, 16, .80, 29),
    "N4_short_epoch_diagnostic": (.40, 64, .35, 11),
}
POLICIES = ("fifo", "ingress", "queue_merge", "set2", "set4", "banked")
SEEDS = range(201, 221)


def evaluate():
    results = {}
    for name, (offered, warps, hot, epoch_period) in CASES.items():
        by_policy = {p: [] for p in POLICIES}
        for seed in SEEDS:
            events = stream(seed, 5000, 4, offered, warps, hot,
                            epoch_period=epoch_period)
            for policy in POLICIES:
                result = run(events, policy, capacity=8, ingress=4,
                             return_digest=True)
                # An independent OR conservation checker exists in
                # independent_audit.py. Here cross-policy equality also
                # guards against implementation-specific drops.
                by_policy[policy].append(result)
            reference = by_policy["fifo"][-1]["digest"]
            assert all(by_policy[p][-1]["digest"] == reference for p in POLICIES)
        means = {p: {
            "event_rate": statistics.mean(x["event_rate"] for x in runs),
            "peak_pending": statistics.mean(x["peak_pending"] for x in runs),
            "writes": statistics.mean(x["writes"] for x in runs),
        } for p, runs in by_policy.items()}
        v = means["queue_merge"]["event_rate"]
        means["set4_over_v301"] = means["set4"]["event_rate"] / v
        means["banked_over_v301"] = means["banked"]["event_rate"] / v
        results[name] = means
    results["decision"] = {
        "n1_set4_ge_95pct_v301": results["N1_medium_skew_short_epoch"]["set4_over_v301"] >= .95,
        "n3_set4_ge_95pct_v301": results["N3_hot_short_epoch"]["set4_over_v301"] >= .95,
        "eight_way_cam_unjustified_by_new_synthetic_controls": (
            results["N1_medium_skew_short_epoch"]["set4_over_v301"] >= .95
            and results["N3_hot_short_epoch"]["set4_over_v301"] >= .95),
    }
    return results


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
