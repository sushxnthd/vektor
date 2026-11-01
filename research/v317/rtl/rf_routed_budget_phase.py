"""Exact V317 budget-phase law using routed control-block inputs.

Other tile area, paths, bandwidth and offered work are hypothetical.
This is accounting, not measured GPU IPC or novel scheduling.
"""
from __future__ import annotations
import argparse
import json
import math
from dataclasses import asdict, dataclass
from fractions import Fraction

SOURCE_AREA = 1316
PAIR_AREA = 583
SOURCE_PERIOD_NS = 1.56
PAIR_PERIOD_NS = 0.58

@dataclass(frozen=True)
class Regime:
    name: str
    n_source: int
    other_area: int
    other_period_ns: float
    bandwidth: float = float("inf")
    offered: float = float("inf")
    work_per_tile_cycle: float = 1.0

def tile_count(budget: int, other_area: int, arbiter_area: int) -> int:
    if min(budget, other_area, arbiter_area) < 0 or other_area + arbiter_area <= 0:
        raise ValueError("invalid area")
    return budget // (other_area + arbiter_area)

def throughput(budget: int, c: Regime, pairwise: bool) -> float:
    a = PAIR_AREA if pairwise else SOURCE_AREA
    period = max(c.other_period_ns, PAIR_PERIOD_NS if pairwise else SOURCE_PERIOD_NS)
    return min(c.offered, c.bandwidth,
               tile_count(budget, c.other_area, a) * c.work_per_tile_cycle / period)

def extra_tile_fraction(c: Regime) -> Fraction:
    """Exact fraction of a source-tile budget interval allowing >=1 more tile."""
    if c.n_source < 1 or c.other_area < 0:
        raise ValueError("invalid source tile count or area")
    a = c.other_area + SOURCE_AREA
    if c.other_area + PAIR_AREA <= 0:
        raise ValueError("invalid pairwise tile area")
    numerator = (c.n_source + 1) * (SOURCE_AREA - PAIR_AREA)
    return Fraction(max(0, min(a, numerator)), a)

def exact_budget_phase_counts(c: Regime) -> dict:
    """Independent integer-budget enumeration, not a fit to the closed form."""
    a = c.other_area + SOURCE_AREA
    low = c.n_source * a
    extra = win = loss = max_extra = 0
    for budget in range(low, low + a):
        ns = tile_count(budget, c.other_area, SOURCE_AREA)
        np = tile_count(budget, c.other_area, PAIR_AREA)
        assert ns == c.n_source
        diff = np - ns
        extra += int(diff > 0)
        max_extra = max(max_extra, diff)
        s = throughput(budget, c, False)
        p = throughput(budget, c, True)
        win += int(p > s + 1e-12)
        loss += int(p < s - 1e-12)
    observed = Fraction(extra, a)
    return {
        "budgets": a, "extra_budget_count": extra, "win_budget_count": win,
        "loss_budget_count": loss, "max_extra_tiles": max_extra,
        "predicted_extra_fraction": str(extra_tile_fraction(c)),
        "observed_extra_fraction": str(observed),
        "predicted_exact_match": observed == extra_tile_fraction(c),
        "baseline_exact_budget_gain": throughput(low, c, True) / throughput(low, c, False),
    }

def frozen_regimes() -> list[Regime]:
    return [
        Regime("W1_area_phase", 24, 40000, 2.0),
        Regime("N1_bandwidth_kill", 24, 40000, 2.0, bandwidth=8.0),
        Regime("H1_transfer_17_100k", 17, 100000, 2.0),
        Regime("H2_transfer_32_80k", 32, 80000, 2.0),
        Regime("H3_transfer_48_200k", 48, 200000, 2.0),
        Regime("clock_critical_conditional", 24, 40000, 1.0),
    ]

def json_regime(c: Regime) -> dict:
    """Strict-JSON representation; infinity is a named unbounded assumption."""
    return {key: ("unbounded" if isinstance(value, float) and not math.isfinite(value) else value)
            for key, value in asdict(c).items()}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    output = {
        "evidence_tier": "routed control-block inputs + hypothetical tile accounting; no GPU IPC",
        "provenance": "RF_REGISTERED_OPENROAD_ROUTED_RESULT_20261101.md",
        "inputs": {"source_area_um2": SOURCE_AREA, "pairwise_area_um2": PAIR_AREA,
                   "source_period_ns": SOURCE_PERIOD_NS, "pairwise_period_ns": PAIR_PERIOD_NS},
        "regimes": [{"parameters": json_regime(c), "result": exact_budget_phase_counts(c)}
                    for c in frozen_regimes()],
    }
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
    else:
        for row in output["regimes"]:
            r = row["result"]
            print(f"{row['parameters']['name']:30s} extra={r['extra_budget_count']}/{r['budgets']} "
                  f"win={r['win_budget_count']} loss={r['loss_budget_count']} "
                  f"max_extra={r['max_extra_tiles']} exact={r['predicted_exact_match']} "
                  f"G_base={r['baseline_exact_budget_gain']:.6f}")

if __name__ == "__main__":
    main()
