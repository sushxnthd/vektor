#!/usr/bin/env python3
"""Identical-demand deterministic RF-port service falsifier; NOT GPU IPC."""
from dataclasses import dataclass
from fractions import Fraction

PORTS = 2
COMPACT = Fraction("21314.6")
PAIRWISE = Fraction("21324.7")

@dataclass(frozen=True)
class Warp:
    demand: tuple[int, int]
    mask: int
    compatible: bool = True

def legal(a, b):
    return (a.compatible and b.compatible and (a.mask & b.mask) == 0
            and all(x + y <= PORTS for x, y in zip(a.demand, b.demand)))

def run(trace, dual):
    i = clocks = pairs = 0
    while i < len(trace):
        assert all(0 <= x <= PORTS for x in trace[i].demand)
        take = 2 if dual and i + 1 < len(trace) and legal(trace[i], trace[i+1]) else 1
        pairs += (take == 2)
        i += take
        clocks += 1
    return clocks, pairs, i

def tpa(trace, pair_period=Fraction(1), compact_period=Fraction(1), shared_area=Fraction(0)):
    assert pair_period > 0 and compact_period > 0 and shared_area >= 0
    c, _, n = run(trace, False)
    p, pairs, m = run(trace, True)
    assert n == m == len(trace)
    ratio = Fraction(c, p) * compact_period / pair_period * (COMPACT + shared_area) / (PAIRWISE + shared_area)
    return ratio, c, p, pairs

def audit():
    # Frozen synthetic predicted-win/no-win controls; no tuning to observed outcomes.
    win = [Warp((2, 0), 0x0f), Warp((0, 2), 0xf0)] * 100
    same_bank = [Warp((2, 0), 0x0f), Warp((2, 0), 0xf0)] * 100
    overlap = [Warp((2, 0), 0x0f), Warp((0, 2), 0x0f)] * 100
    incompatible = [Warp((2, 0), 0x0f, False), Warp((0, 2), 0xf0)] * 100
    for name, trace, expect_win in (
        ("separate-bank", win, True), ("same-bank", same_bank, False),
        ("overlap", overlap, False), ("incompatible", incompatible, False)):
        ratio, c, p, fused = tpa(trace)
        assert (ratio > 1) == expect_win
        assert c == 200 and p == (100 if expect_win else 200)
        print(name, "cycles", c, p, "pairs", fused, "optimistic_TPA", float(ratio))
    assert tpa(win, pair_period=Fraction(2))[0] < 1
    for shared in (0, 10000, 100000):
        assert tpa(same_bank, shared_area=Fraction(shared))[0] < 1
    print("PASS analytical conservation controls; NOT routed timing, power, or GPU IPC")

if __name__ == "__main__":
    audit()
