from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryConfig:
    l1_sets: int = 64
    l1_ways: int = 4
    l1_line_bytes: int = 128
    l1_hit_latency: int = 20
    l2_sets: int = 256
    l2_ways: int = 8
    l2_line_bytes: int = 128
    l2_hit_latency: int = 120
    dram_latency: int = 420
    l1_mshrs: int = 16
    l2_mshrs: int = 64


@dataclass(frozen=True)
class AccessResult:
    level: str
    latency: int
    line: int


class _SetAssociative:
    def __init__(self, sets: int, ways: int, line_bytes: int):
        if sets <= 0 or ways <= 0 or line_bytes <= 0:
            raise ValueError("cache geometry must be positive")
        self.sets, self.ways, self.line_bytes = sets, ways, line_bytes
        self.data = [OrderedDict() for _ in range(sets)]

    def _key(self, address: int) -> tuple[int, int, int]:
        line = address // self.line_bytes
        return line % self.sets, line // self.sets, line

    def hit(self, address: int) -> bool:
        index, tag, _ = self._key(address)
        way = self.data[index]
        if tag not in way:
            return False
        way.move_to_end(tag)
        return True

    def fill(self, address: int) -> None:
        index, tag, _ = self._key(address)
        way = self.data[index]
        if tag in way:
            way.move_to_end(tag)
            return
        way[tag] = None
        if len(way) > self.ways:
            way.popitem(last=False)


class MemoryHierarchy:
    """Auditable inclusive L1/L2 latency model.

    This is a functional cache model, not a bandwidth/NoC/DRAM timing model.
    MSHR counts are exposed in MemoryConfig for the next integration step.
    """

    def __init__(self, config: MemoryConfig | None = None):
        self.config = config or MemoryConfig()
        c = self.config
        self.l1 = _SetAssociative(c.l1_sets, c.l1_ways, c.l1_line_bytes)
        self.l2 = _SetAssociative(c.l2_sets, c.l2_ways, c.l2_line_bytes)
        self.l1_hits = self.l2_hits = self.dram_accesses = 0

    def access(self, address: int) -> AccessResult:
        if address < 0:
            raise ValueError("address must be non-negative")
        c = self.config
        line = address // c.l1_line_bytes
        if self.l1.hit(address):
            self.l1_hits += 1
            return AccessResult("l1", c.l1_hit_latency, line)
        if self.l2.hit(address):
            self.l2_hits += 1
            self.l1.fill(address)
            return AccessResult("l2", c.l2_hit_latency, line)
        self.dram_accesses += 1
        self.l2.fill(address)
        self.l1.fill(address)
        return AccessResult("dram", c.dram_latency, line)
