from __future__ import annotations

import json
from dataclasses import asdict

from sim.vektor.pipeline import (
    DependencyTileSimulator,
    TileConfig,
    dependency_fma_kernel,
    load_use_kernel,
    reuse_fma_kernel,
)


def run() -> dict:
    scenarios = {
        "reuse_fma": reuse_fma_kernel,
        "dependency_fma": dependency_fma_kernel,
        "load_use": load_use_kernel,
    }
    cache_entries = [0, 8, 16, 32, 64, 128]
    rows = []

    for name, kernel in scenarios.items():
        for entries in cache_entries:
            config = TileConfig(operand_cache_entries=entries)
            result = DependencyTileSimulator(config).run(kernel())
            row = {
                "scenario": name,
                "operand_cache_entries": entries,
                "config": asdict(config),
                "result": asdict(result),
            }
            rows.append(row)

    return {
        "benchmark": "vtile_issue_bench_v1",
        "claim_boundary": (
            "Synthetic simulator evidence only. Results do not establish physical "
            "frequency, area, power, real-workload performance, or RTX 5090 equivalence."
        ),
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
