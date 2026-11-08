#!/usr/bin/env python3
"""V317 synchronous-resource clock-domain falsification.

On-tile bank and return ports operate in cycles, not fixed transactions/ns.
A bank with B grants/cycle at clock T has B/T grants/ns. Treating this
as an invariant external per-ns limit across clock changes is unsound.
Necessary ceiling only: NOT measured RTL, STA, or GPU IPC.
"""
from dataclasses import dataclass
from itertools import product

@dataclass(frozen=True)
class Case:
    period_ns: float
    issue_per_cycle: float
    bank_grants_per_cycle: float
    returns_per_cycle: float
    operands_per_completion: float
    offered_per_ns: float
    external_per_ns: float

def ceiling(c):
    assert c.period_ns > 0 and c.operands_per_completion > 0
    assert min(c.issue_per_cycle, c.bank_grants_per_cycle,
               c.returns_per_cycle, c.offered_per_ns, c.external_per_ns) >= 0
    return min(c.issue_per_cycle / c.period_ns,
               c.bank_grants_per_cycle / (c.operands_per_completion*c.period_ns),
               c.returns_per_cycle / c.period_ns,
               c.offered_per_ns, c.external_per_ns)

def fixed_port_counterfactual(c, reference_period_ns):
    """INVALID for synchronous on-tile ports: hold port grants/ns fixed."""
    return min(c.issue_per_cycle / c.period_ns,
               c.bank_grants_per_cycle / (c.operands_per_completion*reference_period_ns),
               c.returns_per_cycle / reference_period_ns,
               c.offered_per_ns, c.external_per_ns)

def audit():
    base = Case(3, 1, 2, 2, 2, 10, 10)
    slower = Case(4, 2, 2, 2, 2, 10, 10)
    assert ceiling(base) == 1/3
    assert ceiling(slower) == 1/4
    assert fixed_port_counterfactual(slower, base.period_ns) == 1/3
    count = 0
    for t, issue, bank, ret, operands, offered, ext in product(
        (2.,3.,4.,5.), (0.,0.5,1.,2.,4.), (0.,1.,2.,4.),
        (0.,1.,2.,4.), (1.,2.), (0.25,1.,10.), (0.25,1.,10.)):
        c = Case(t,issue,bank,ret,operands,offered,ext)
        v = ceiling(c)
        assert 0 <= v <= issue/t + 1e-12
        assert v <= bank/(operands*t) + 1e-12
        assert v <= ret/t + 1e-12
        assert v <= offered + 1e-12 and v <= ext + 1e-12
        doubled = Case(2*t,2*issue,2*bank,2*ret,operands,offered,ext)
        assert abs(ceiling(doubled)-v) < 1e-12
        count += 1
    print(f"PASS {count} synchronous-resource configurations")
    print("FALSIFICATION: fixed per-ns port limits are invalid for on-tile synchronous ports")
    print("LIMIT: no matched RTL service, extracted timing, electrical closure or GPU IPC")

if __name__ == "__main__":
    audit()
