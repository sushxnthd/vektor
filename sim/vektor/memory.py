from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass


@dataclass(frozen=True)
class CacheConfig:
    size_bytes: int
    line_bytes: int
    associativity: int
    hit_latency: int
    accesses_per_cycle: int

    def __post_init__(self) -> None:
        if self.size_bytes <= 0 or self.line_bytes <= 0 or self.associativity <= 0:
            raise ValueError("cache geometry must be positive")
        lines = self.size_bytes // self.line_bytes
        if lines < self.associativity or lines % self.associativity:
            raise ValueError("cache lines must be divisible by associativity")


@dataclass(frozen=True)
class MemoryHierarchyConfig:
    l1: CacheConfig = CacheConfig(
        size_bytes=128 * 1024,
        line_bytes=128,
        associativity=4,
        hit_latency=4,
        accesses_per_cycle=4,
    )
    l2: CacheConfig = CacheConfig(
        size_bytes=8 * 1024 * 1024,
        line_bytes=128,
        associativity=16,
        hit_latency=40,
        accesses_per_cycle=4,
    )
    dram_latency: int = 300
    dram_requests_per_cycle: int = 2
    mshrs: int = 64


@dataclass(frozen=True)
class AccessResult:
    level: str
    completion_cycle: int
    merged: bool = False


@dataclass
class MemoryStats:
    l1_hits: int = 0
    l2_hits: int = 0
    dram_misses: int = 0
    merged_misses: int = 0
    mshr_stalls: int = 0
    l1_bandwidth_stalls: int = 0
    l2_bandwidth_stalls: int = 0
    dram_bandwidth_stalls: int = 0


class _SetAssociativeCache:
    def __init__(self, config: CacheConfig):
        self.config = config
        lines = config.size_bytes // config.line_bytes
        self.set_count = lines // config.associativity
        self._sets: list[OrderedDict[int, None]] = [
            OrderedDict() for _ in range(self.set_count)
        ]

    def _set_tag(self, address: int) -> tuple[int, int]:
        line = address // self.config.line_bytes
        return line % self.set_count, line // self.set_count

    def contains(self, address: int) -> bool:
        set_index, tag = self._set_tag(address)
        ways = self._sets[set_index]
        if tag not in ways:
            return False
        ways.move_to_end(tag)
        return True

    def insert(self, address: int) -> None:
        set_index, tag = self._set_tag(address)
        ways = self._sets[set_index]
        if tag in ways:
            ways.move_to_end(tag)
            return
        ways[tag] = None
        if len(ways) > self.config.associativity:
            ways.popitem(last=False)


class MemoryHierarchy:
    """Deterministic non-blocking L1 -> L2 -> DRAM timing model.

    A request may be rejected for the current cycle when a bandwidth limit or MSHR
    limit is reached. Accepted misses reserve one MSHR per cache line; accesses to
    an already outstanding line merge onto the existing completion. Fills become
    visible only when `advance()` reaches their completion cycle.

    Latencies and capacities are architecture parameters, not measurements of any
    commercial GPU or of future Vektor silicon.
    """

    def __init__(self, config: MemoryHierarchyConfig | None = None):
        self.config = config or MemoryHierarchyConfig()
        if self.config.l1.line_bytes != self.config.l2.line_bytes:
            raise ValueError("L1 and L2 line sizes must match in the current model")
        if self.config.dram_latency <= 0 or self.config.mshrs <= 0:
            raise ValueError("DRAM latency and MSHR count must be positive")

        self.l1 = _SetAssociativeCache(self.config.l1)
        self.l2 = _SetAssociativeCache(self.config.l2)
        self.stats = MemoryStats()

        # line -> (completion cycle, representative address, source level)
        self._pending: dict[int, tuple[int, int, str]] = {}
        # cycle -> [accepted L1 accesses, L2 accesses, DRAM transactions]
        self._usage: dict[int, list[int]] = {}

    @property
    def outstanding_misses(self) -> int:
        return len(self._pending)

    def _line(self, address: int) -> int:
        return address // self.config.l1.line_bytes

    def _cycle_usage(self, cycle: int) -> list[int]:
        return self._usage.setdefault(cycle, [0, 0, 0])

    def advance(self, cycle: int) -> None:
        completed = [
            line
            for line, (done, _address, _source) in self._pending.items()
            if done <= cycle
        ]
        for line in completed:
            _done, address, source = self._pending.pop(line)
            if source == "dram":
                self.l2.insert(address)
            self.l1.insert(address)

    def issue(self, cycle: int, address: int) -> AccessResult | None:
        if cycle < 0 or address < 0:
            raise ValueError("cycle and address must be non-negative")

        self.advance(cycle)
        usage = self._cycle_usage(cycle)

        if usage[0] >= self.config.l1.accesses_per_cycle:
            self.stats.l1_bandwidth_stalls += 1
            return None

        if self.l1.contains(address):
            usage[0] += 1
            self.stats.l1_hits += 1
            return AccessResult("l1", cycle + self.config.l1.hit_latency)

        line = self._line(address)
        if line in self._pending:
            usage[0] += 1
            self.stats.merged_misses += 1
            return AccessResult("merged", self._pending[line][0], merged=True)

        if len(self._pending) >= self.config.mshrs:
            self.stats.mshr_stalls += 1
            return None

        if usage[1] >= self.config.l2.accesses_per_cycle:
            self.stats.l2_bandwidth_stalls += 1
            return None

        if self.l2.contains(address):
            usage[0] += 1
            usage[1] += 1
            self.stats.l2_hits += 1
            completion = cycle + self.config.l2.hit_latency
            self._pending[line] = (completion, address, "l2")
            return AccessResult("l2", completion)

        if usage[2] >= self.config.dram_requests_per_cycle:
            self.stats.dram_bandwidth_stalls += 1
            return None

        usage[0] += 1
        usage[1] += 1
        usage[2] += 1
        self.stats.dram_misses += 1
        completion = cycle + self.config.dram_latency
        self._pending[line] = (completion, address, "dram")
        return AccessResult("dram", completion)
