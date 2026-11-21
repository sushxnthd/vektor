"""V317 integrated routed-control area / occupancy and queue-semantics falsification.

Only the five 32-wave issue-control routed area/slack pairs are measured.
Other-tile area, occupancy, traffic, tile replication and workloads are synthetic.
No measured GPU IPC, SRAM, datapath, or multi-corner signoff is implied.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
from math import comb, floor
import json
import random

D = Decimal
A_OTHER = D('40000')

@dataclass(frozen=True)
class PhysicalRow:
    name: str
    source_area: Decimal
    pair_area: Decimal
    source_slack_ps: Decimal
    pair_slack_ps: Decimal

ROWS = (
    PhysicalRow('seed7', D('7426.72'), D('6595.20'), D('-3.063'), D('106.304')),
    PhysicalRow('seed19', D('7539.50'), D('6577.12'), D('-5.487'), D('70.861')),
    PhysicalRow('seed37', D('7367.67'), D('6586.69'), D('-3.561'), D('60.487')),
    PhysicalRow('density005_seed7', D('7539.24'), D('6609.04'), D('-1.483'), D('101.692')),
    PhysicalRow('density035_seed7', D('7407.83'), D('6577.91'), D('-6.600'), D('72.408')),
)

@dataclass(frozen=True)
class Regime:
    name: str
    budget: int
    source_occupancy: float
    pair_occupancy: float
    bandwidth: float = 100.0
    offered: float = 100.0
    other_period: float = 2.20

REGIMES = (
    Regime('W1_extra_tile', 1175000, .75, .75),
    Regime('N1_bandwidth_at_mean', 1175000, .75, .75, bandwidth=8),
    Regime('N2_occupancy_kill', 1175000, .75, .70),
    Regime('N3_no_extra_tile', 1150000, .75, .75),
    Regime('H1_near_boundary', 1175000, .80, .77),
)

def count_tiles(budget: int, issue_area: Decimal, other_area: Decimal = A_OTHER) -> int:
    if budget < 0 or issue_area < 0 or other_area <= 0:
        raise ValueError('invalid area or budget')
    return int(D(budget) // (other_area + issue_area))

def robust_25_vs_24_interval() -> tuple[int, int]:
    """Inclusive integer budgets where all five pairs fit 25 vs 24 tiles."""
    low = int((D(25) * (A_OTHER + max(x.pair_area for x in ROWS))).to_integral_value(rounding=ROUND_CEILING))
    first_source25 = D(25) * (A_OTHER + min(x.source_area for x in ROWS))
    high = int(first_source25.to_integral_value(rounding=ROUND_CEILING)) - 1
    assert all(count_tiles(low, x.pair_area) == 25 and count_tiles(high, x.source_area) == 24 for x in ROWS)
    return low, high

def period_ns(row: PhysicalRow, pairwise: bool, other_period: float = 2.20,
              repaired_source: bool = False) -> float:
    # Controller period estimate from setup slack at a 2-ns target.
    slack = row.pair_slack_ps if pairwise else row.source_slack_ps
    controller = 2.0 - float(slack) / 1000.0
    if repaired_source and not pairwise:
        controller = min(controller, 2.0)  # generous, UNMEASURED source repair
    return max(other_period, controller)

def fluid_rate(row: PhysicalRow, regime: Regime, pairwise: bool,
               repaired_source: bool = True) -> float:
    n = count_tiles(regime.budget, row.pair_area if pairwise else row.source_area)
    u = regime.pair_occupancy if pairwise else regime.source_occupancy
    return min(regime.offered, regime.bandwidth,
               n*u/period_ns(row, pairwise, regime.other_period, repaired_source))

def occupancy_boundary(row: PhysicalRow, regime: Regime) -> float:
    """Necessary/sufficient break-even occupancy ratio only when caps inactive."""
    ns = count_tiles(regime.budget, row.source_area)
    np = count_tiles(regime.budget, row.pair_area)
    return ns * period_ns(row, True, regime.other_period) / (
        np * period_ns(row, False, regime.other_period, True))

def expected_clipped_binomial(n: int, u: float, capacity: int) -> float:
    """E[min(Binomial(n,u),capacity)] with independent tile activity."""
    return sum(min(k, capacity)*comb(n,k)*(u**k)*((1-u)**(n-k))
               for k in range(n+1))

def instantaneous_rate(n: int, u: float, period: float, bandwidth: float) -> float:
    """Exact fractional-slot capacity average for UNQUEUED per-cycle work."""
    cap = bandwidth * period
    lo = floor(cap)
    frac = cap - lo
    return ((1-frac)*expected_clipped_binomial(n,u,lo)
            + frac*expected_clipped_binomial(n,u,lo+1))/period

def simulate(n: int, u: float, period: float, bandwidth: float, *,
             seed: int, cycles: int = 100000, backlog: bool = False) -> float:
    """Independent Bernoulli event executor, with dropped or queued opportunities."""
    rng = random.Random(seed)
    served = 0
    queue = 0
    credit = 0.0
    cap = bandwidth * period
    for _ in range(cycles):
        arrivals = sum(rng.random() < u for _ in range(n))
        credit += cap
        allowance = int(credit + 1e-9)
        credit -= allowance
        available = arrivals + (queue if backlog else 0)
        taken = min(available, allowance)
        served += taken
        if backlog:
            queue = available - taken
    return served/(cycles*period)

def evaluate(cycles: int = 100000) -> dict:
    low, high = robust_25_vs_24_interval()
    result = {'tier': 'integrated routed area inputs + hypothetical tile/traffic workload',
              'robust_25_vs_24_integer_budget': [low,high],
              'physical_rows': len(ROWS), 'regimes': []}
    for idx, c in enumerate(REGIMES):
        r = ROWS[0]  # representative; exact robust tile counts tested on all rows
        ns = count_tiles(c.budget, r.source_area)
        np = count_tiles(c.budget, r.pair_area)
        ts = period_ns(r,False,c.other_period,True)
        tp = period_ns(r,True,c.other_period)
        fs, fp = fluid_rate(r,c,False), fluid_rate(r,c,True)
        ss = simulate(ns,c.source_occupancy,ts,c.bandwidth,seed=107+idx,cycles=cycles)
        sp = simulate(np,c.pair_occupancy,tp,c.bandwidth,seed=107+idx,cycles=cycles)
        ds = instantaneous_rate(ns,c.source_occupancy,ts,c.bandwidth)
        dp = instantaneous_rate(np,c.pair_occupancy,tp,c.bandwidth)
        result['regimes'].append({
            'name': c.name, 'source_tiles': ns, 'pair_tiles': np,
            'occupancy_break_even_ratio': occupancy_boundary(r,c),
            'fluid_gain': fp/fs, 'instantaneous_exact_gain': dp/ds,
            'independent_stream_gain': sp/ss,
            'source_stream_rate': ss, 'pair_stream_rate': sp,
        })
    return result

if __name__ == '__main__':
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
