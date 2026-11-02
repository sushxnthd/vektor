#!/usr/bin/env python3
"""Independent V317 area-dominance arithmetic; NOT a raw OpenROAD parser.

The raw extracted-RC checker is audit_rf_proxy_compact_challenger.py.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, getcontext
import json
from pathlib import Path

getcontext().prec = 32
D = Decimal
THRESHOLD = D("0.02")
SOURCE_SHA = "96f4dae55effc33d3e8032cf1245b3384d18d5b2"


def number(value):
    try:
        result = D(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"Invalid measurement {value!r}") from exc
    if not result.is_finite():
        raise ValueError("Nonfinite measurement")
    return result


def calculate(payload):
    if payload["source_sha"] != SOURCE_SHA:
        raise ValueError("Physical source SHA mismatch")
    rows = payload["variants"]
    if set(rows) != {"source", "compact", "pairwise"}:
        raise ValueError("Expected three matched variants")
    if len({number(row["sequential_cells"]) for row in rows.values()}) != 1:
        raise ValueError("Sequential resources not matched")
    if any(number(row["macro_count"]) != 0 or row["route_exit"] != 0
           for row in rows.values()):
        raise ValueError("Unexpected macro or incomplete route")
    s, c, p = (number(rows[key]["area_um2"])
               for key in ("source", "compact", "pairwise"))
    if min(s, c, p) <= 0:
        raise ValueError("Nonpositive area")
    saving = D(1) - p / c
    both_legal = bool(rows["compact"]["legal"] and rows["pairwise"]["legal"])
    return {
        "source_sha": SOURCE_SHA,
        "area_um2": {"source": str(s), "compact": str(c), "pairwise": str(p)},
        "pairwise_raw_saving_pct": str(saving * 100),
        "compact_raw_saving_vs_source_pct": str((D(1) - c / s) * 100),
        "minimum_compact_area_for_2pct_win_um2": str(p / (D(1) - THRESHOLD)),
        "required_compact_area_increase_um2": str(p / (D(1) - THRESHOLD) - c),
        "maximum_pairwise_area_for_2pct_win_um2": str(c * (D(1) - THRESHOLD)),
        "required_pairwise_area_reduction_um2": str(p - c * (D(1) - THRESHOLD)),
        "compact_raw_area_dominates_pairwise": p >= c,
        "legal_material_win": both_legal and saving >= THRESHOLD,
        "electrical_legality": {"compact": bool(rows["compact"]["legal"]),
                               "pairwise": bool(rows["pairwise"]["legal"])},
        "conditional_discrete_packing_law":
            "P>=C implies floor(B/(P+H))<=floor(B/(C+H)) for all B,H>=0 "
            "with identical shared hardware, clock, service and occupancy",
        "positive_tile_capacity_gain_possible_under_equal_service_model": p < c,
        "gpu_ipc_measured": False,
    }


def self_test():
    payload = {"source_sha": SOURCE_SHA, "variants": {
        name: {"area_um2": area, "sequential_cells": 1213, "macro_count": 0,
               "route_exit": 0, "legal": False}
        for name, area in (("source", "21535.6"), ("compact", "21314.6"),
                           ("pairwise", "21324.7"))}}
    result = calculate(payload)
    assert result["compact_raw_area_dominates_pairwise"]
    assert not result["legal_material_win"]
    assert D(result["required_pairwise_area_reduction_um2"]) == D("436.392")
    assert D(result["required_compact_area_increase_um2"]) > 445
    for h in range(0, 51, 5):
        for budget in range(0, 150001, 97):
            assert (D(budget) // (D("21324.7") + D(h)) <=
                    D(budget) // (D("21314.6") + D(h)))
    payload["variants"]["pairwise"]["area_um2"] = "20800"
    assert not calculate(payload)["compact_raw_area_dominates_pairwise"]
    payload["variants"]["pairwise"]["legal"] = True
    payload["variants"]["compact"]["legal"] = True
    assert calculate(payload)["legal_material_win"]
    payload["variants"]["compact"]["sequential_cells"] = 1212
    try:
        calculate(payload)
    except ValueError:
        pass
    else:
        raise AssertionError("Unmatched resources should fail")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("audit_json", type=Path, nargs="?")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    self_test()
    if args.audit_json:
        result = calculate(json.loads(args.audit_json.read_text(encoding="utf-8")))
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
    else:
        print("PASS area-dominance arithmetic, budget enumeration, mutation controls")
