from __future__ import annotations

import math
import random
from dataclasses import dataclass


WAVE_SIZE = 32


@dataclass(frozen=True)
class DivergenceTrace:
    """One reorder-safe divergent region across a set of original Wave32 warps.

    Each lane is assigned a path id. `path_instructions[p]` is the number of
    dynamic instructions executed by a lane taking path p before reconvergence.
    The model intentionally excludes barriers, cross-lane communication and other
    regions where arbitrary regrouping would be semantically unsafe.
    """

    warps: tuple[tuple[int, ...], ...]
    path_instructions: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.warps:
            raise ValueError("trace must contain at least one warp")
        if not self.path_instructions or any(length <= 0 for length in self.path_instructions):
            raise ValueError("path instruction counts must be positive")
        for warp in self.warps:
            if len(warp) != WAVE_SIZE:
                raise ValueError("every warp must contain exactly 32 lanes")
            if any(path < 0 or path >= len(self.path_instructions) for path in warp):
                raise ValueError("lane path id is outside path_instructions")


@dataclass(frozen=True)
class ScheduleResult:
    data_issue_slots: int
    overhead_issue_slots: int
    effective_issue_slots: int
    useful_lane_instructions: int
    lane_utilization: float
    effective_slot_efficiency: float
    compacted_windows: int
    bypassed_windows: int


def _useful_lane_instructions(trace: DivergenceTrace) -> int:
    total = 0
    for warp in trace.warps:
        for path in warp:
            total += trace.path_instructions[path]
    return total


def _ipdom_slots_for_warps(
    warps: tuple[tuple[int, ...], ...], path_instructions: tuple[int, ...]
) -> int:
    slots = 0
    for warp in warps:
        present = set(warp)
        slots += sum(path_instructions[path] for path in present)
    return slots


def evaluate_ipdom(trace: DivergenceTrace) -> ScheduleResult:
    """Immediate-postdominator style masked execution baseline.

    Every non-empty path in an original warp executes separately. This is a
    control-flow accounting model, not a cycle-accurate implementation of a
    specific commercial GPU.
    """

    slots = _ipdom_slots_for_warps(trace.warps, trace.path_instructions)
    useful = _useful_lane_instructions(trace)
    lane_utilization = useful / (slots * WAVE_SIZE)
    return ScheduleResult(
        data_issue_slots=slots,
        overhead_issue_slots=0,
        effective_issue_slots=slots,
        useful_lane_instructions=useful,
        lane_utilization=lane_utilization,
        effective_slot_efficiency=lane_utilization,
        compacted_windows=0,
        bypassed_windows=0,
    )


def evaluate_compaction(
    trace: DivergenceTrace,
    *,
    window_warps: int,
    overhead_issue_slots_per_window: int = 0,
    oracle_gate: bool = False,
) -> ScheduleResult:
    """Bounded cross-warp compaction model.

    Threads taking the same path may be regrouped only within a fixed-size window
    of original warps. `overhead_issue_slots_per_window` charges a synthetic cost
    for synchronization, mask collection, register remapping and scheduling.

    With `oracle_gate=True`, a window compacts only when compacted data slots plus
    overhead are strictly cheaper than the IPDOM baseline. This is an *upper
    bound*, not an implementable predictor and not a novelty claim. Prior work
    including DWF, TBC and CAPRI already studies dynamic compaction and adequacy.
    """

    if window_warps <= 0:
        raise ValueError("window_warps must be positive")
    if overhead_issue_slots_per_window < 0:
        raise ValueError("overhead must be non-negative")

    total_data_slots = 0
    total_overhead = 0
    compacted_windows = 0
    bypassed_windows = 0

    for start in range(0, len(trace.warps), window_warps):
        window = trace.warps[start : start + window_warps]
        baseline_slots = _ipdom_slots_for_warps(window, trace.path_instructions)

        lanes_per_path = [0 for _ in trace.path_instructions]
        for warp in window:
            for path in warp:
                lanes_per_path[path] += 1

        compacted_data_slots = 0
        for path, lane_count in enumerate(lanes_per_path):
            if lane_count:
                formed_waves = math.ceil(lane_count / WAVE_SIZE)
                compacted_data_slots += formed_waves * trace.path_instructions[path]

        compacted_effective = compacted_data_slots + overhead_issue_slots_per_window
        if oracle_gate and compacted_effective >= baseline_slots:
            total_data_slots += baseline_slots
            bypassed_windows += 1
        else:
            total_data_slots += compacted_data_slots
            total_overhead += overhead_issue_slots_per_window
            compacted_windows += 1

    effective = total_data_slots + total_overhead
    useful = _useful_lane_instructions(trace)
    lane_utilization = useful / (total_data_slots * WAVE_SIZE)
    effective_efficiency = useful / (effective * WAVE_SIZE)
    return ScheduleResult(
        data_issue_slots=total_data_slots,
        overhead_issue_slots=total_overhead,
        effective_issue_slots=effective,
        useful_lane_instructions=useful,
        lane_utilization=lane_utilization,
        effective_slot_efficiency=effective_efficiency,
        compacted_windows=compacted_windows,
        bypassed_windows=bypassed_windows,
    )


def coherent_trace(warp_count: int = 32, path_instructions: int = 16) -> DivergenceTrace:
    return DivergenceTrace(
        warps=tuple(tuple(0 for _ in range(WAVE_SIZE)) for _ in range(warp_count)),
        path_instructions=(path_instructions, path_instructions),
    )


def alternating_trace(warp_count: int = 32, path_instructions: int = 16) -> DivergenceTrace:
    return DivergenceTrace(
        warps=tuple(
            tuple(lane % 2 for lane in range(WAVE_SIZE)) for _ in range(warp_count)
        ),
        path_instructions=(path_instructions, path_instructions),
    )


def minority_trace(warp_count: int = 32, path_instructions: int = 16) -> DivergenceTrace:
    return DivergenceTrace(
        warps=tuple(
            tuple(0 if lane < WAVE_SIZE - 1 else 1 for lane in range(WAVE_SIZE))
            for _ in range(warp_count)
        ),
        path_instructions=(path_instructions, path_instructions),
    )


def random_trace(
    warp_count: int = 32,
    path_count: int = 4,
    path_instructions: int = 8,
    seed: int = 1,
) -> DivergenceTrace:
    if path_count <= 0:
        raise ValueError("path_count must be positive")
    rng = random.Random(seed)
    return DivergenceTrace(
        warps=tuple(
            tuple(rng.randrange(path_count) for _ in range(WAVE_SIZE))
            for _ in range(warp_count)
        ),
        path_instructions=tuple(path_instructions for _ in range(path_count)),
    )
