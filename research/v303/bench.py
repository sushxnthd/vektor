"""Frozen V303 policy sensitivity, using the existing V-Tile kernels.

Run: python -m research.v303.bench
"""
import json
from dataclasses import asdict
from sim.vektor.pipeline import (
    DependencyTileSimulator, TileConfig,
    dependency_fma_kernel, load_use_kernel, reuse_fma_kernel
)
from research.v303.coherence_oracle import run as independent_oracle


def run():
    workloads = {
        "H1_read_mostly_reuse": reuse_fma_kernel,
        "H2_dependent_overwrite": dependency_fma_kernel,
        "H3_load_use_negative": load_use_kernel,
    }
    rows = []
    for name, factory in workloads.items():
        for capacity in (0, 8, 64):
            result = {}
            for policy in ("invalidate", "ideal_update"):
                cfg = TileConfig(
                    operand_cache_entries=capacity,
                    operand_cache_write_policy=policy
                )
                stats = DependencyTileSimulator(cfg).run(factory())
                result[policy] = asdict(stats)
            invalid = result["invalidate"]
            ideal = result["ideal_update"]
            rows.append({
                "workload": name, "cache_entries": capacity,
                "invalidate": invalid, "ideal_update": ideal,
                "rf_read_increase": invalid["rf_reads"] - ideal["rf_reads"],
                "cycle_ratio_invalidate_over_ideal":
                    invalid["cycles"] / ideal["cycles"]
            })
    return {
        "experiment": "v303_operand_cache_write_coherence",
        "protocol": "research/v303/PROTOCOL.md",
        "claim_boundary": (
            "Synthetic V-Tile issue simulator; ideal_update is an unpriced "
            "coherent-write upper bound, not a physically implemented cache. "
            "No measured GPU speedup, area, power, or frequency."
        ),
        "independent_oracle": independent_oracle(),
        "rows": rows
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
