from __future__ import annotations

import json
from dataclasses import asdict

from sim.vektor.scheduler_topology import (
    balanced_trace,
    clustered_trace,
    evaluate_fixed_four_by_eight,
    evaluate_global_four_wide,
    evaluate_limited_steal,
    lopsided_memory_trace,
    rotating_cluster_trace,
)


def run() -> dict:
    traces = {
        "balanced": balanced_trace(),
        "clustered": clustered_trace(),
        "rotating_cluster": rotating_cluster_trace(),
        "lopsided_memory_proxy": lopsided_memory_trace(),
    }
    rows = []
    for name, trace in traces.items():
        fixed = evaluate_fixed_four_by_eight(trace)
        steal = evaluate_limited_steal(trace)
        global_ = evaluate_global_four_wide(trace)
        rows.append(
            {
                "trace": name,
                "fixed_4x8": asdict(fixed),
                "limited_steal": asdict(steal),
                "global_4wide_upper_bound": asdict(global_),
                "steal_vs_fixed_utilization_x": (
                    steal.issue_utilization / fixed.issue_utilization
                    if fixed.issue_utilization
                    else None
                ),
                "global_vs_fixed_utilization_x": (
                    global_.issue_utilization / fixed.issue_utilization
                    if fixed.issue_utilization
                    else None
                ),
            }
        )
    return {
        "benchmark": "scheduler_topology_v2",
        "claim_boundary": (
            "Synthetic readiness-trace evidence only. The global scheduler is an "
            "issue-utilization upper bound; limited stealing is an implementable RTL "
            "candidate whose logic cost is measured separately by generic synthesis. "
            "No application speedup, frequency, power, area, or RTX 5090 equivalence is established."
        ),
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
