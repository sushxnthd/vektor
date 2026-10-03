from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .memory import MemoryHierarchy


@dataclass(frozen=True)
class Instruction:
    """One in-order Wave32 instruction for the provisional V-Tile model."""

    op: str
    src: tuple[int, ...] = ()
    dst: Optional[int] = None
    latency: int = 1
    active_lanes: int = 32
    matrix_ops: int = 0
    memory_bytes: int = 0
    address: Optional[int] = None


@dataclass
class Wave:
    instructions: list[Instruction]
    wave_id: int
    pc: int = 0
    ready_at: dict[int, int] = field(default_factory=dict)

    @property
    def done(self) -> bool:
        return self.pc >= len(self.instructions)


@dataclass(frozen=True)
class TileConfig:
    schedulers: int = 4
    fp32_issue_per_cycle: int = 4
    matrix_issue_per_cycle: int = 2
    memory_issue_per_cycle: int = 2
    rf_banks: int = 16
    rf_read_ports_per_bank: int = 2
    operand_cache_entries: int = 64
    memory_latency: int = 120
    max_outstanding_loads: int = 64


@dataclass(frozen=True)
class SimulationResult:
    cycles: int
    instructions: int
    fp32_ops: int
    matrix_ops: int
    memory_bytes: int
    dependency_stalls: int
    resource_stalls: int
    bank_stalls: int
    idle_cycles: int
    rf_reads: int
    operand_cache_hits: int
    operand_cache_misses: int
    issue_utilization: float


class _OperandCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._lru: OrderedDict[tuple[int, int], None] = OrderedDict()

    def contains(self, key: tuple[int, int]) -> bool:
        return key in self._lru

    def touch(self, key: tuple[int, int]) -> None:
        if self.capacity <= 0:
            return
        if key in self._lru:
            self._lru.move_to_end(key)
            return
        self._lru[key] = None
        if len(self._lru) > self.capacity:
            self._lru.popitem(last=False)


class DependencyTileSimulator:
    """Deterministic issue/dependency model for one V-Tile.

    The model contains four shared issue slots, separate FP32/matrix/memory issue
    limits, in-order waves, register dependencies, banked RF reads and an operand
    cache. Loads can either use the legacy fixed-latency path or, when an address
    and `MemoryHierarchy` are supplied, take latency/backpressure from the explicit
    L1 -> L2 -> DRAM model. It is not a physical-timing, NoC, or power model.
    """

    def __init__(self, config: TileConfig | None = None):
        self.config = config or TileConfig()

    def run(
        self,
        waves: list[Wave],
        max_cycles: int = 10_000_000,
        memory: MemoryHierarchy | None = None,
    ) -> SimulationResult:
        waves = [
            Wave(list(w.instructions), w.wave_id, w.pc, dict(w.ready_at))
            for w in waves
        ]
        if not waves:
            return SimulationResult(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0)

        c = self.config
        cache = _OperandCache(c.operand_cache_entries)
        round_robin = 0
        cycle = 0
        outstanding_loads: list[int] = []

        instructions = 0
        fp32_ops = 0
        matrix_ops = 0
        memory_bytes = 0
        dependency_stalls = 0
        resource_stalls = 0
        bank_stalls = 0
        idle_cycles = 0
        rf_reads = 0
        operand_cache_hits = 0
        operand_cache_misses = 0

        while any(not wave.done for wave in waves):
            if cycle >= max_cycles:
                raise RuntimeError("simulation exceeded max_cycles")

            cycle += 1
            if memory is not None:
                memory.advance(cycle)
            outstanding_loads = [done for done in outstanding_loads if done > cycle]

            issued = 0
            fp32_used = 0
            matrix_used = 0
            memory_used = 0
            bank_reads: dict[int, int] = {}
            next_round_robin = round_robin

            for offset in range(len(waves)):
                if issued >= c.schedulers:
                    break

                index = (round_robin + offset) % len(waves)
                wave = waves[index]
                if wave.done:
                    continue

                ins = wave.instructions[wave.pc]

                if any(wave.ready_at.get(reg, 0) > cycle for reg in ins.src):
                    dependency_stalls += 1
                    continue

                if ins.op == "fp32" and fp32_used >= c.fp32_issue_per_cycle:
                    resource_stalls += 1
                    continue
                if ins.op == "matrix" and matrix_used >= c.matrix_issue_per_cycle:
                    resource_stalls += 1
                    continue
                if ins.op in ("load", "store") and memory_used >= c.memory_issue_per_cycle:
                    resource_stalls += 1
                    continue
                if ins.op not in ("fp32", "matrix", "load", "store"):
                    raise ValueError(f"unsupported op: {ins.op}")

                uses_hierarchy = (
                    ins.op == "load" and memory is not None and ins.address is not None
                )
                if (
                    ins.op == "load"
                    and not uses_hierarchy
                    and len(outstanding_loads) >= c.max_outstanding_loads
                ):
                    resource_stalls += 1
                    continue

                required_bank_reads: dict[int, int] = {}
                for reg in ins.src:
                    key = (wave.wave_id, reg)
                    if cache.contains(key):
                        continue
                    bank = reg % c.rf_banks
                    required_bank_reads[bank] = required_bank_reads.get(bank, 0) + 1

                if any(
                    bank_reads.get(bank, 0) + count > c.rf_read_ports_per_bank
                    for bank, count in required_bank_reads.items()
                ):
                    bank_stalls += 1
                    continue

                hierarchy_result = None
                if uses_hierarchy:
                    hierarchy_result = memory.issue(cycle, ins.address)
                    if hierarchy_result is None:
                        resource_stalls += 1
                        continue

                for reg in ins.src:
                    key = (wave.wave_id, reg)
                    if cache.contains(key):
                        operand_cache_hits += 1
                    else:
                        operand_cache_misses += 1
                        rf_reads += 1
                        bank = reg % c.rf_banks
                        bank_reads[bank] = bank_reads.get(bank, 0) + 1
                    cache.touch(key)

                issued += 1
                instructions += 1
                next_round_robin = (index + 1) % len(waves)

                if ins.op == "fp32":
                    fp32_used += 1
                    fp32_ops += ins.active_lanes * 2
                elif ins.op == "matrix":
                    matrix_used += 1
                    matrix_ops += ins.matrix_ops or 2048
                else:
                    memory_used += 1
                    memory_bytes += ins.memory_bytes

                if ins.dst is not None:
                    if hierarchy_result is not None:
                        wave.ready_at[ins.dst] = hierarchy_result.completion_cycle
                    else:
                        latency = c.memory_latency if ins.op == "load" else ins.latency
                        wave.ready_at[ins.dst] = cycle + latency

                if ins.op == "load" and not uses_hierarchy:
                    outstanding_loads.append(cycle + c.memory_latency)

                wave.pc += 1

            round_robin = next_round_robin
            if issued == 0:
                idle_cycles += 1

        issue_utilization = instructions / (cycle * c.schedulers)
        return SimulationResult(
            cycles=cycle,
            instructions=instructions,
            fp32_ops=fp32_ops,
            matrix_ops=matrix_ops,
            memory_bytes=memory_bytes,
            dependency_stalls=dependency_stalls,
            resource_stalls=resource_stalls,
            bank_stalls=bank_stalls,
            idle_cycles=idle_cycles,
            rf_reads=rf_reads,
            operand_cache_hits=operand_cache_hits,
            operand_cache_misses=operand_cache_misses,
            issue_utilization=issue_utilization,
        )


def reuse_fma_kernel(wave_count: int = 32, instructions: int = 64) -> list[Wave]:
    """High operand-reuse FP32 kernel used to stress RF banking/cache effects."""

    return [
        Wave(
            [
                Instruction("fp32", (0, 1), dst=2 + (i % 30), latency=4)
                for i in range(instructions)
            ],
            wave_id,
        )
        for wave_id in range(wave_count)
    ]


def dependency_fma_kernel(wave_count: int = 32, instructions: int = 64) -> list[Wave]:
    """FP32 dependency chains across enough waves to expose latency hiding."""

    waves: list[Wave] = []
    for wave_id in range(wave_count):
        reg = 2
        sequence: list[Instruction] = []
        for _ in range(instructions):
            dst = 3 if reg == 2 else 2
            sequence.append(Instruction("fp32", (reg, 1), dst=dst, latency=4))
            reg = dst
        waves.append(Wave(sequence, wave_id))
    return waves


def load_use_kernel(wave_count: int = 32, iterations: int = 8) -> list[Wave]:
    """Repeated dependent load/use pairs for the legacy fixed-latency path."""

    waves: list[Wave] = []
    for wave_id in range(wave_count):
        sequence: list[Instruction] = []
        for i in range(iterations):
            loaded = 2 + (i % 8)
            sequence.append(Instruction("load", dst=loaded, memory_bytes=128))
            sequence.append(
                Instruction("fp32", (loaded, 1), dst=10 + (i % 8), latency=4)
            )
        waves.append(Wave(sequence, wave_id))
    return waves


def addressed_load_use_kernel(
    wave_count: int = 32,
    iterations: int = 8,
    working_set_lines: int | None = None,
    line_bytes: int = 128,
) -> list[Wave]:
    """Dependent load/use pairs with deterministic cache-line addresses.

    `working_set_lines=None` gives every load a unique line. A smaller positive
    working set intentionally creates inter-wave reuse/coalescing.
    """

    if working_set_lines is not None and working_set_lines <= 0:
        raise ValueError("working_set_lines must be positive when supplied")

    waves: list[Wave] = []
    for wave_id in range(wave_count):
        sequence: list[Instruction] = []
        for i in range(iterations):
            loaded = 2 + (i % 8)
            linear_line = wave_id * iterations + i
            line = (
                linear_line
                if working_set_lines is None
                else linear_line % working_set_lines
            )
            sequence.append(
                Instruction(
                    "load",
                    dst=loaded,
                    memory_bytes=line_bytes,
                    address=line * line_bytes,
                )
            )
            sequence.append(
                Instruction("fp32", (loaded, 1), dst=10 + (i % 8), latency=4)
            )
        waves.append(Wave(sequence, wave_id))
    return waves
