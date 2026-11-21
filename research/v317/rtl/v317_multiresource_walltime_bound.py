#!/usr/bin/env python3
"""Necessary multi-resource, equal-wall-time throughput bound (not measured GPU IPC).

Every completed request consumes at least units_per_completion[i] service units
of resource i. Clock periods must be independently validated by physical STA.
This bound assumes fixed resource counts and no inter-request resource sharing.
"""
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class Regime:
    wall_ps: int
    period_ps: int
    offered: int
    capacity_per_cycle: tuple[int, ...]
    units_per_completion: tuple[int, ...]

def bound(r: Regime) -> int:
    assert type(r.wall_ps) is type(r.period_ps) is type(r.offered) is int
    assert r.wall_ps > 0 and r.period_ps > 0 and r.offered >= 0
    assert len(r.capacity_per_cycle) == len(r.units_per_completion) > 0
    assert all(type(x) is int and x >= 0 for x in r.capacity_per_cycle)
    assert all(type(x) is int and x > 0 for x in r.units_per_completion)
    cycles = r.wall_ps // r.period_ps
    return min([r.offered] + [cycles*c//a for c,a in
        zip(r.capacity_per_cycle, r.units_per_completion)])

def gain_ceiling(baseline_completed: int, candidate: Regime):
    assert type(baseline_completed) is int and baseline_completed > 0
    return Fraction(bound(candidate), baseline_completed) - 1

def test():
    # Frozen no-win regime: baseline saturates common return port.
    no_win = Regime(300_000, 3000, 100, (4, 1), (1, 1))
    assert bound(no_win) == 100 and gain_ceiling(100, no_win) == 0
    assert bound(Regime(300_000, 3000, 200, (8, 1), (1, 1))) == 100
    # Frozen predicted headroom (not a predicted actual win): 80% baseline.
    assert gain_ceiling(80, no_win) == Fraction(1, 4)
    # 25% slower clock eliminates that nominal headroom at equal wall time.
    slower = Regime(300_000, 3750, 100, (4, 1), (1, 1))
    assert bound(slower) == 80 and gain_ceiling(80, slower) == 0
    # Faster clock is only admissible with independent timing closure.
    assert bound(Regime(300_000, 2500, 200, (4, 1), (1, 1))) == 120
    cases = 0
    for wall in range(1, 9):
      for period in range(1, 5):
       for offered in range(9):
        for c1 in range(4):
         for c2 in range(4):
          for a1 in range(1, 4):
           for a2 in range(1, 4):
            r = Regime(wall, period, offered, (c1, c2), (a1, a2))
            cycles = wall // period
            feasible = [n for n in range(offered+1)
                        if n*a1 <= cycles*c1 and n*a2 <= cycles*c2]
            assert bound(r) == max(feasible)
            cases += 1
    print(f'PASS {cases} exhaustive integer-capacity cases')
    print('NO-WIN: saturated return port; HEADROOM: <=25% at 80% utilization')
    print('TIMING: 3.0ns to 3.75ns removes the 25% theoretical headroom')
    print('Necessary bound only; no RTL, STA, power or GPU IPC validation.')

if __name__ == '__main__':
    test()
