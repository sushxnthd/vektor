#!/usr/bin/env python3
"""Bank-aware equal-wall-time upper bound. Necessary capacity test, not GPU IPC."""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product

@dataclass(frozen=True)
class Case:
    wall_ps: int
    period_ps: int
    demand: tuple[int, ...]
    bank_ports: tuple[int, ...]
    return_ports: int

def bound(c):
    assert c.wall_ps >= 0 and c.period_ps > 0 and c.return_ports >= 0
    assert len(c.demand) == len(c.bank_ports) > 0
    assert all(v >= 0 for v in c.demand + c.bank_ports)
    cycles = c.wall_ps // c.period_ps
    return min(cycles*c.return_ports,
               sum(min(n, cycles*p) for n,p in zip(c.demand,c.bank_ports)))

def pooled(c):
    cycles = c.wall_ps // c.period_ps
    return min(sum(c.demand), cycles*c.return_ports,
               cycles*sum(c.bank_ports))

def test():
    count = 0
    for wall,period in product(range(7),range(1,5)):
      for demand in product(range(4),repeat=2):
       for ports in product(range(3),repeat=2):
        for ret in range(4):
         c = Case(wall,period,demand,ports,ret)
         cycles = wall//period
         feasible = [sum(v) for v in product(*(range(n+1) for n in demand))
                     if sum(v)<=cycles*ret and all(v[i]<=cycles*ports[i] for i in range(2))]
         assert bound(c)==max(feasible)
         assert bound(c)<=pooled(c)
         count += 1
    skew = Case(300000,3000,(160,0,0,0),(1,1,1,1),4)
    assert (bound(skew),pooled(skew)) == (100,160)
    fast = Case(300000,3000,(100,100),(1,1),2)
    slow = Case(300000,3750,(100,100),(1,1),2)
    assert Fraction(bound(fast),160)-1 == Fraction(1,4)
    assert Fraction(bound(slow),160)-1 == 0
    assert bound(Case(300000,3000,(200,0),(1,1),8)) == 100
    assert bound(Case(9,5,(10,),(2,),10)) == 2
    print(f"PASS {count} exhaustive cases; bank-skew and wall-time counterexamples")
    print("Necessary bound only; no RTL, STA, electrical closure or GPU IPC.")

if __name__ == "__main__":
    test()
