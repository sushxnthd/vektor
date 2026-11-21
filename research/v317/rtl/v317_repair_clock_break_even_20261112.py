"""Prospective matched-repair break-even screen; NOT routed signoff.

Historical compact/pairwise areas from 2026-11-02 three-way route are
ELECTRICALLY ILLEGAL. This model only identifies the minimum clock/service
improvement required after independently verified legal repairs.
"""
from fractions import Fraction as F
from itertools import product

COMPACT = F('21314.6')
PAIRWISE = F('21324.7')

def threshold(compact_repair_area, pairwise_repair_area, compact_period=F(3),
              pairwise_period=F(3), compact_work_cycles=1, pairwise_work_cycles=1):
    """Minimum candidate completed-work/service multiplier for throughput/area WIN.

    Service multiplier is baseline work cycles / candidate work cycles at
    equal clock; values above returned ratio are required for strict WIN.
    """
    ac = COMPACT + F(compact_repair_area)
    ap = PAIRWISE + F(pairwise_repair_area)
    assert ac > 0 and ap > 0
    return ap * F(pairwise_period) * F(pairwise_work_cycles) / (ac * F(compact_period) * F(compact_work_cycles))

def run():
    assert threshold(0, 0) == F('21324.7') / F('21314.6')
    assert threshold(0, 0) > 1
    assert threshold(0, 0, pairwise_period=F('2.9')) < 1
    assert threshold(0, 0, pairwise_period=F('3.1')) > 1
    assert threshold(0, 100) > threshold(0, 0)
    assert threshold(100, 0) < threshold(0, 0)
    for common in (0, 10, 100, 1000):
        assert threshold(common, common) > 1
    results = []
    for dc, dp, clock in product((0, 20, 100), (0, 20, 100), (F('2.9'), F(3), F('3.1'))):
        t = threshold(dc, dp, pairwise_period=clock)
        results.append((dc, dp, str(clock), str(t), float(t)))
    assert len(results) == 27
    pmax = F(3) * COMPACT / PAIRWISE
    assert pmax < 3
    print('historical raw pairwise/compact area ratio:', float(PAIRWISE / COMPACT))
    print('max candidate period (ns), equal work and no repair:', float(pmax))
    print('prospective scenarios:', len(results))
    print('WARNING: all inputs historical illegal routes or hypothetical repairs; no physical WIN')
    return results

if __name__ == '__main__':
    run()
