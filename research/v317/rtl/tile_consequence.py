"""V317 conditional tile-consequence law. No routed GPU timing is implied.

All area and delay inputs are explicit. Source and pairwise arbiters issue
identical grants, so effective work/tile/cycle is shared by construction.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Case:
    name: str
    budget: float
    other_area: float
    source_area: float = 785.498
    pair_area: float = 260.414
    source_delay: float = 1.26
    pair_delay: float = 0.59
    other_delay: float = 1.50
    source_wire: float = 0.0
    pair_wire: float = 0.0
    offered: float = 100.0
    bandwidth: float = 100.0
    work_per_tile_cycle: float = 1.0


def evaluate(c: Case) -> dict:
    """Exact fluid throughput ceiling, not a physical measurement."""
    for field in ("budget", "other_area", "source_area", "pair_area", "source_delay",
                  "pair_delay", "other_delay", "offered", "bandwidth", "work_per_tile_cycle"):
        if not math.isfinite(getattr(c, field)) or getattr(c, field) <= 0:
            raise ValueError(f"{field} must be finite and positive")
    if min(c.source_wire, c.pair_wire) < 0 or not all(math.isfinite(x) for x in (c.source_wire, c.pair_wire)):
        raise ValueError("wire penalties must be finite and nonnegative")
    def one(area: float, delay: float, wire: float) -> dict:
        n = math.floor(c.budget / (c.other_area + area))
        period = max(c.other_delay, delay + wire)
        compute = n * c.work_per_tile_cycle / period
        return {"tiles": n, "period_ns": period, "compute_work_per_ns": compute,
                "throughput_work_per_ns": min(c.offered, c.bandwidth, compute)}
    source = one(c.source_area, c.source_delay, c.source_wire)
    pair = one(c.pair_area, c.pair_delay, c.pair_wire)
    gain = None if source["throughput_work_per_ns"] == 0 else pair["throughput_work_per_ns"] / source["throughput_work_per_ns"]
    return {"case": c.name, "source": source, "pairwise": pair, "gain": gain}


def frozen_cases() -> list[Case]:
    base = {"budget": 1_000_000.0, "other_area": 40_000.0}
    return [
        Case("no_win_noncritical", **base),
        Case("conditional_area_step", budget=1_010_000.0, other_area=40_000.0),
        Case("bandwidth_kill", budget=1_010_000.0, other_area=40_000.0, bandwidth=16.0),
        Case("conditional_clock_win", **base, other_delay=0.80),
        Case("differential_wire_kill", **base, other_delay=0.80, pair_wire=0.70),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    out = {"evidence_tier": "conditional analytic model, not placed/routed hardware",
           "frozen": [{"inputs": asdict(c), "result": evaluate(c)} for c in frozen_cases()]}
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        for row in out["frozen"]:
            r = row["result"]
            print(f"{r['case']:27s} N={r['source']['tiles']:2d}/{r['pairwise']['tiles']:2d} "
                  f"T={r['source']['period_ns']:.2f}/{r['pairwise']['period_ns']:.2f} ns "
                  f"G={r['gain']:.6f}x")


if __name__ == "__main__":
    main()
