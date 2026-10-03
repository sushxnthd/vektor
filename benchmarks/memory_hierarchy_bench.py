from __future__ import annotations

import json
from dataclasses import asdict

from sim.vektor.memory import MemoryHierarchy, MemoryHierarchyConfig
from sim.vektor.pipeline import DependencyTileSimulator, addressed_load_use_kernel


def _run_case(name: str, mshrs: int, working_set_lines: int | None) -> dict:
    config = MemoryHierarchyConfig(mshrs=mshrs)
    memory = MemoryHierarchy(config)
    waves = addressed_load_use_kernel(
        wave_count=32,
        iterations=4,
        working_set_lines=working_set_lines,
        line_bytes=config.l1.line_bytes,
    )
    tile = DependencyTileSimulator().run(waves, memory=memory)
    return {
        "scenario": name,
        "mshrs": mshrs,
        "working_set_lines": working_set_lines,
        "memory_config": asdict(config),
        "tile_result": asdict(tile),
        "memory_stats": asdict(memory.stats),
    }


def run() -> dict:
    rows = []
    for mshrs in (8, 16, 32, 64, 128):
        rows.append(_run_case("cold_unique", mshrs, None))
        rows.append(_run_case("shared_working_set_8_lines", mshrs, 8))

    return {
        "benchmark": "memory_hierarchy_bench_v1",
        "claim_boundary": (
            "Synthetic timing-model evidence only. Cache geometry, latency, bandwidth, "
            "and MSHR values are architecture parameters, not measured silicon values. "
            "Results do not establish physical frequency, area, power, real-workload "
            "performance, or RTX 5090 equivalence."
        ),
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
