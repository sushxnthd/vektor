from __future__ import annotations

import json
from dataclasses import asdict

from sim.vektor.divergence import (
    alternating_trace,
    coherent_trace,
    evaluate_compaction,
    evaluate_ipdom,
    minority_trace,
    random_trace,
)


def run() -> dict:
    scenarios = {
        "coherent": coherent_trace(),
        "balanced_16_16": alternating_trace(),
        "minority_31_1": minority_trace(),
        "random_4_path_seed7": random_trace(seed=7),
        "short_balanced": alternating_trace(path_instructions=1),
    }

    rows = []
    for name, trace in scenarios.items():
        baseline = evaluate_ipdom(trace)
        for window in (2, 4, 8, 16, 32):
            for overhead in (0, 2, 4, 8, 16):
                naive = evaluate_compaction(
                    trace,
                    window_warps=window,
                    overhead_issue_slots_per_window=overhead,
                    oracle_gate=False,
                )
                oracle = evaluate_compaction(
                    trace,
                    window_warps=window,
                    overhead_issue_slots_per_window=overhead,
                    oracle_gate=True,
                )
                rows.append(
                    {
                        "scenario": name,
                        "window_warps": window,
                        "overhead_issue_slots_per_window": overhead,
                        "baseline": asdict(baseline),
                        "naive_compaction": asdict(naive),
                        "oracle_gated_compaction": asdict(oracle),
                        "naive_speedup_proxy": (
                            baseline.effective_issue_slots / naive.effective_issue_slots
                        ),
                        "oracle_speedup_proxy": (
                            baseline.effective_issue_slots / oracle.effective_issue_slots
                        ),
                    }
                )

    return {
        "benchmark": "divergence_compaction_bound_v1",
        "prior_art_boundary": (
            "Dynamic warp formation, thread-block compaction, adequacy prediction, and "
            "shader execution reordering are established prior art. This benchmark treats "
            "cross-warp compaction as a baseline mechanism, not a Vektor novelty claim."
        ),
        "claim_boundary": (
            "Synthetic issue-slot accounting over reorder-safe branch regions only. "
            "The oracle gate is an unattainable upper bound that knows whether compaction "
            "will pay off. Results do not include register migration energy, cache/locality "
            "disruption, memory timing, synchronization semantics, physical timing, or RTL."
        ),
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
