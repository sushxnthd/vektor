from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SchedulerTopologyResult:
    cycles: int
    ready_wave_slots: int
    issued_wave_slots: int
    issue_capacity: int
    issue_utilization: float
    ready_service_ratio: float


def _validate_trace(trace: list[int]) -> None:
    if not trace:
        raise ValueError("readiness trace must not be empty")
    if any(mask < 0 or mask >= (1 << 32) for mask in trace):
        raise ValueError("readiness masks must fit 32 waves")


def _result(trace: list[int], issued: int, ready: int) -> SchedulerTopologyResult:
    capacity = 4 * len(trace)
    return SchedulerTopologyResult(
        cycles=len(trace),
        ready_wave_slots=ready,
        issued_wave_slots=issued,
        issue_capacity=capacity,
        issue_utilization=issued / capacity,
        ready_service_ratio=issued / ready if ready else 1.0,
    )


def evaluate_global_four_wide(trace: list[int]) -> SchedulerTopologyResult:
    """Idealized four-wide global scheduler upper bound."""
    _validate_trace(trace)
    issued = 0
    ready = 0
    for mask in trace:
        count = mask.bit_count()
        ready += count
        issued += min(4, count)
    return _result(trace, issued, ready)


def evaluate_fixed_four_by_eight(trace: list[int]) -> SchedulerTopologyResult:
    """Four independent 8-wave partitions, one issue per partition/cycle."""
    _validate_trace(trace)
    issued = 0
    ready = 0
    for mask in trace:
        ready += mask.bit_count()
        for partition in range(4):
            if ((mask >> (partition * 8)) & 0xFF):
                issued += 1
    return _result(trace, issued, ready)


def evaluate_limited_steal(trace: list[int]) -> SchedulerTopologyResult:
    """Four 8-wave partitions plus at most one backup issue per donor partition.

    Each non-empty partition supplies one primary issue. If issue slots remain,
    a partition with at least two ready waves may supply one additional backup.
    This models the low-state RTL alternative between rigid partitioning and a
    full 32-wave four-wide arbiter.
    """
    _validate_trace(trace)
    issued = 0
    ready = 0
    for mask in trace:
        counts = [((mask >> (partition * 8)) & 0xFF).bit_count() for partition in range(4)]
        ready += sum(counts)
        primary = sum(count > 0 for count in counts)
        backups = sum(count > 1 for count in counts)
        issued += min(4, primary + backups)
    return _result(trace, issued, ready)


def balanced_trace(cycles: int = 256) -> list[int]:
    """At least one ready wave in every 8-wave partition every cycle."""
    return [
        (1 << ((cycle + 0) % 8))
        | (1 << (8 + (cycle + 1) % 8))
        | (1 << (16 + (cycle + 2) % 8))
        | (1 << (24 + (cycle + 3) % 8))
        for cycle in range(cycles)
    ]


def clustered_trace(cycles: int = 256) -> list[int]:
    """Four ready waves exist, but all are concentrated in one partition."""
    trace = []
    for cycle in range(cycles):
        partition = cycle % 4
        base = partition * 8
        trace.append(sum(1 << (base + lane) for lane in range(4)))
    return trace


def rotating_cluster_trace(cycles: int = 256) -> list[int]:
    """Eight ready waves/cycle concentrated across two neighboring partitions."""
    trace = []
    for cycle in range(cycles):
        first = cycle % 4
        second = (first + 1) % 4
        mask = 0
        for partition in (first, second):
            base = partition * 8
            for lane in range(4):
                mask |= 1 << (base + lane)
        trace.append(mask)
    return trace


def lopsided_memory_trace(cycles: int = 256) -> list[int]:
    """Deterministic proxy for correlated stalls leaving readiness lopsided."""
    trace = []
    for cycle in range(cycles):
        mask = 0
        for lane in range(6):
            mask |= 1 << lane
        if cycle % 2 == 0:
            mask |= 1 << (8 + (cycle // 2) % 8)
        if cycle % 4 == 0:
            mask |= 1 << (16 + (cycle // 4) % 8)
        if cycle % 8 == 0:
            mask |= 1 << (24 + (cycle // 8) % 8)
        trace.append(mask)
    return trace
