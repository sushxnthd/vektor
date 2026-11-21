#!/usr/bin/env python3
"""V317 strong-baseline materiality boundary, before three-way physical outcomes.

Uses immutable historical RF-proxy extracted-RC observations; NOT new routing.
The compact baseline is an independent equal-policy implementation.  A
2% pairwise saving relative to it is impossible unless its area exceeds
pairwise area / 0.98.  No electrical legality is inferred.
"""
from __future__ import annotations

import json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 30
TARGET = Decimal("0.02")


def row_boundary(row: dict) -> dict:
    s = Decimal(str(row["source"]["area_um2"]))
    p = Decimal(str(row["pairwise"]["area_um2"]))
    if not (s > 0 and p > 0):
        raise ValueError("Areas must be positive")
    minimum_compact = p / (Decimal(1) - TARGET)
    maximum_compact_improvement = Decimal(1) - minimum_compact / s
    regimes = {}
    for label, compact_vs_source in (
        ("compact_one_pct_smaller", Decimal("0.99")),
        ("compact_equal_to_source", Decimal("1.00")),
        ("compact_one_pct_larger", Decimal("1.01")),
        ("compact_two_pct_larger", Decimal("1.02")),
    ):
        c = s * compact_vs_source
        gain = Decimal(1) - p / c
        regimes[label] = {
            "raw_pairwise_saving_pct": float(100 * gain),
            "passes_raw_2pct": gain >= TARGET,
        }
    return {
        "density": row["density"],
        "historical_source_um2": float(s),
        "historical_pairwise_um2": float(p),
        "compact_area_required_for_2pct_um2": float(minimum_compact),
        "compact_required_excess_over_source_um2": float(minimum_compact - s),
        "max_compact_improvement_vs_source_pct": float(
            100 * maximum_compact_improvement
        ),
        "regimes": regimes,
    }


def self_test() -> None:
    x = {"density": 0, "source": {"area_um2": 100},
         "pairwise": {"area_um2": 98}}
    r = row_boundary(x)
    assert abs(r["compact_area_required_for_2pct_um2"] - 100) < 1e-12
    assert abs(r["max_compact_improvement_vs_source_pct"]) < 1e-12
    y = {"density": 0, "source": {"area_um2": 100},
         "pairwise": {"area_um2": 99}}
    q = row_boundary(y)
    assert q["compact_required_excess_over_source_um2"] > 0
    assert not q["regimes"]["compact_equal_to_source"]["passes_raw_2pct"]
    assert q["regimes"]["compact_two_pct_larger"]["passes_raw_2pct"]


def main() -> None:
    self_test()
    path = Path(__file__).resolve().parents[1] / (
        "RF_PROXY_DENSITY_OBSERVATIONS_20261102.json"
    )
    observations = json.loads(path.read_text(encoding="utf-8"))
    assert observations["threshold_pct"] == 2
    rows = [row_boundary(x) for x in observations["rows"]]
    assert len(rows) == 3
    assert all(x["compact_required_excess_over_source_um2"] > 0
               for x in rows)
    assert all(not x["regimes"]["compact_one_pct_larger"]["passes_raw_2pct"]
               for x in rows)
    assert all(x["regimes"]["compact_two_pct_larger"]["passes_raw_2pct"]
               for x in rows)
    print(json.dumps({
        "evidence_tier": "conditional historical-area algebra; no new route",
        "frozen_threshold_pct": 2,
        "prospective_compact_route": "PENDING",
        "historical_rf_proxy_electrical_gate": "FAIL_UNCHANGED",
        "rows": rows,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
