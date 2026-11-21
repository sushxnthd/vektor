#!/usr/bin/env python3
"""Bank-skew conservation ceiling; optimistic bound, not measured GPU IPC.

Each request consumes one bank and one shared return port. Excludes multi-bank
requests, dependencies, and queue ordering. Clock period needs independent STA.
"""
from dataclasses import dataclass
from itertools import product

@dataclass(frozen=True)
class Regime:
    cycles: int
    demand: tuple[int, ...]
    bank_ports: tuple[int, ...]
    shared_ports: int

def ceiling(r):
    assert type(r.cycles) is type(r.shared_ports) is int
    assert r.cycles >= 0 and r.shared_ports >= 0
    assert len(r.demand) == len(r.bank_ports) > 0
    assert all(type(x) is int and x >= 0 for x in r.demand + r.bank_ports)
    return min(r.cycles * r.shared_ports,
               sum(min(d, r.cycles * p) for d, p in zip(r.demand, r.bank_ports)))

def pooled(r):
    return min(sum(r.demand), r.cycles * r.shared_ports,
               r.cycles * sum(r.bank_ports))

def test():
    # Frozen no-win: hot bank limits service despite three idle banks.
    hot = Regime(100, (160, 0, 0, 0), (1, 1, 1, 1), 4)
    assert ceiling(hot) == 100 and pooled(hot) == 160
    balanced = Regime(100, (100,)*4, (1,)*4, 4)
    assert ceiling(balanced) == 400
    slow = Regime(80, (100,)*4, (1,)*4, 4)
    assert ceiling(slow) == 320
    cases = 0
    for cycles in range(4):
      for demand in product(range(4), repeat=2):
       for ports in product(range(3), repeat=2):
        for shared in range(4):
         r = Regime(cycles, demand, ports, shared)
         oracle = max((a+b for a in range(demand[0]+1)
                       for b in range(demand[1]+1)
                       if a <= cycles*ports[0] and b <= cycles*ports[1]
                       and a+b <= cycles*shared), default=0)
         assert ceiling(r) == oracle
         assert ceiling(r) <= pooled(r)
         cases += 1
    print(f"PASS {cases} independent bank-allocation oracle cases")
    print("FALSIFICATION: pooled 160 versus bank-aware 100 completions")
    print("Analytical bound only; no RTL/STA/power/GPU IPC claim.")

if __name__ == "__main__":
    test()
