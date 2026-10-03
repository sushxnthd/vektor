from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KernelWork:
    fp32_ops: int = 0
    fp4_matrix_ops: int = 0
    memory_bytes: int = 0

    def done(self) -> bool:
        return self.fp32_ops <= 0 and self.fp4_matrix_ops <= 0 and self.memory_bytes <= 0


@dataclass(frozen=True)
class TileResources:
    fp32_ops_per_cycle: int = 256  # 128 lanes x 1 FMA x 2 ops
    fp4_matrix_ops_per_cycle: int = 4096
    memory_bytes_per_cycle: int = 256  # provisional local-pipeline target; must be validated


@dataclass
class SimulationResult:
    cycles: int
    issued_fp32_ops: int
    issued_fp4_matrix_ops: int
    issued_memory_bytes: int
    fp32_utilization: float
    matrix_utilization: float
    memory_utilization: float


class TileSimulator:
    """Minimal deterministic resource simulator for one V-Tile.

    This is intentionally not yet a timing-accurate GPU simulator. It establishes
    explicit per-cycle resource accounting so later scheduler, dependency, cache,
    divergence, and latency models can be added without silently assuming peak use.
    """

    def __init__(self, resources: TileResources | None = None):
        self.r = resources or TileResources()

    def run(self, work: KernelWork) -> SimulationResult:
        remaining = KernelWork(work.fp32_ops, work.fp4_matrix_ops, work.memory_bytes)
        cycles = 0
        issued_fp32 = 0
        issued_matrix = 0
        issued_memory = 0

        while not remaining.done():
            cycles += 1

            fp32 = min(max(remaining.fp32_ops, 0), self.r.fp32_ops_per_cycle)
            matrix = min(max(remaining.fp4_matrix_ops, 0), self.r.fp4_matrix_ops_per_cycle)
            memory = min(max(remaining.memory_bytes, 0), self.r.memory_bytes_per_cycle)

            remaining.fp32_ops -= fp32
            remaining.fp4_matrix_ops -= matrix
            remaining.memory_bytes -= memory

            issued_fp32 += fp32
            issued_matrix += matrix
            issued_memory += memory

        if cycles == 0:
            return SimulationResult(0, 0, 0, 0, 0.0, 0.0, 0.0)

        return SimulationResult(
            cycles=cycles,
            issued_fp32_ops=issued_fp32,
            issued_fp4_matrix_ops=issued_matrix,
            issued_memory_bytes=issued_memory,
            fp32_utilization=issued_fp32 / (cycles * self.r.fp32_ops_per_cycle),
            matrix_utilization=issued_matrix / (cycles * self.r.fp4_matrix_ops_per_cycle),
            memory_utilization=issued_memory / (cycles * self.r.memory_bytes_per_cycle),
        )
