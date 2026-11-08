#!/usr/bin/env python3
"""V317 prospective clock/throughput rejection gate for same-cycle bypass.

Analytical NECESSARY conditions only, not synthesis, STA or measured throughput.
All delays are explicit assumptions. The comparator has the same bank and
return capacities; service rate is supplied from matched-resource traces.
"""
from dataclasses import dataclass
from itertools import product

@dataclass(frozen=True)
class Case:
    base_period_ns: float
    bypass_period_ns: float
    base_completed_per_cycle: float
    bypass_completed_per_cycle: float
    offered_per_ns: float
    bank_limit_per_ns: float
    return_limit_per_ns: float


def bound(c: Case):
    assert min(c.base_period_ns, c.bypass_period_ns) > 0
    assert min(c.base_completed_per_cycle, c.bypass_completed_per_cycle) >= 0
    assert min(c.offered_per_ns, c.bank_limit_per_ns, c.return_limit_per_ns) >= 0
    common = min(c.offered_per_ns, c.bank_limit_per_ns, c.return_limit_per_ns)
    base = min(common, c.base_completed_per_cycle / c.base_period_ns)
    candidate = min(common, c.bypass_completed_per_cycle / c.bypass_period_ns)
    return base, candidate


def clock_threshold(base_period_ns, base_service, candidate_service):
    """Strict candidate improvement requires candidate period below threshold
    if common resources do not already cap baseline. Not sufficient for a win.
    """
    assert base_period_ns > 0 and base_service > 0 and candidate_service >= 0
    return base_period_ns * candidate_service / base_service


def audit():
    # Freeze illustrative regimes before enumerating. These are not workloads.
    win = Case(3, 3.2, 1, 1.25, 10, 10, 10)
    no_win = Case(3, 3.75, 1, 1.25, 10, 10, 10)
    saturated = Case(3, 3, 1, 2, 0.25, 10, 10)
    assert bound(win)[1] > bound(win)[0]
    assert bound(no_win)[1] == bound(no_win)[0]
    assert bound(saturated)[1] == bound(saturated)[0]
    checks = 0
    for bp, cp, bs, cs, demand, bank, port in product(
        (2., 3., 4.), (2., 3., 4., 5.), (0.5, 1., 2.),
        (0.5, 1., 2.), (0.2, 0.5, 2.), (0.2, 0.5, 2.), (0.2, 0.5, 2.)
    ):
        c = Case(bp, cp, bs, cs, demand, bank, port)
        b, v = bound(c)
        cap = min(demand, bank, port)
        assert 0 <= b <= cap and 0 <= v <= cap
        if cp >= clock_threshold(bp, bs, cs):
            assert v <= b + 1e-12
        if cap <= min(bs/bp, cs/cp):
            assert abs(v-b) < 1e-12
        checks += 1
    print(f'PASS {checks} boundary cases')
    for name, case in [('predicted-win illustrative', win),
                       ('predicted-no-win illustrative', no_win),
                       ('shared-resource saturation', saturated)]:
        b, v = bound(case)
        print(f'{name}: baseline={b:.6f}/ns candidate={v:.6f}/ns ratio={v/b if b else float("nan"):.6f}')
    print('NOT EVIDENCE: service rates and periods are assumed, not extracted from RTL/STA.')

if __name__ == '__main__':
    audit()
