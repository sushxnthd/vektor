#!/usr/bin/env python3
"""Independent V317 banked-RF-proxy physical audit; never treats a route exit as signoff.

Usage: python3 research/v317/rtl/audit_rf_proxy_banked_tile.py build/v317/rf_proxy
The artifact must be from the frozen 2026-11-02 source-pinned experiment.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

SOURCE_SHA = "fb76565c9319266bd3efa285b435130f06150bf2"
IMAGE = "sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8"
VARIANTS = ("source", "pairwise")


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"Missing evidence: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def metric(raw: dict, key: str) -> float:
    name = "finish__" + key
    value = raw.get(name)
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise AssertionError(f"Missing or nonfinite physical metric: {name}")
    return float(value)


def inspect(root: Path, variant: str) -> dict:
    folder = root / f"rf_proxy_{variant}"
    status = read(folder / "status.txt")
    code = re.search(r"exit_code=(\d+)", status)
    if not code:
        raise AssertionError(f"No route status for {variant}")
    out = {"variant": variant, "route_exit": int(code.group(1)), "legal": False}
    if out["route_exit"] != 0:
        out["failure_tail"] = read(folder / "make.log")[-1500:]
        return out
    top = f"vektor_v317_rf_proxy_top_{variant}"
    logs = folder / "logs" / "nangate45" / top / "base"
    report = json.loads(read(logs / "6_report.json"))
    route = read(logs / "5_2_route.log")
    extract = read(logs / "6_report.log")
    yosys = read(logs / "1_2_yosys.log")
    if "RCX-0045" not in extract:
        raise AssertionError(f"No extracted-RC evidence: {variant}")
    if "Using ABC area script." not in yosys:
        raise AssertionError(f"Unmatched ABC mapping: {variant}")
    drc = re.findall(r"Number of violations\s*=\s*(\d+)", route)
    wire = re.findall(r"Total wire length\s*=\s*(\d+)\s*um", route)
    if not drc or not wire:
        raise AssertionError(f"Missing detailed routing DRC or wire metrics: {variant}")
    if "Found 0 net violations" not in route or "Found 0 pin violations" not in route:
        raise AssertionError(f"Global route violations: {variant}")
    out.update({
        "area_um2": metric(report, "design__instance__area__stdcell"),
        "sequential_cells": metric(report, "design__instance__count__class:sequential_cell"),
        "macro_count": metric(report, "design__instance__count__macros"),
        "wire_um": int(wire[-1]),
        "fmax_mhz": metric(report, "timing__fmax") / 1e6,
        "setup_slack_ps": metric(report, "timing__setup__ws") * 1000,
        "setup_violations": metric(report, "timing__drv__setup_violation_count"),
        "hold_slack_ps": metric(report, "timing__hold__ws") * 1000,
        "hold_violations": metric(report, "timing__drv__hold_violation_count"),
        "max_cap_violations": metric(report, "timing__drv__max_cap"),
        "max_slew_violations": metric(report, "timing__drv__max_slew"),
        "max_fanout_violations": metric(report, "timing__drv__max_fanout"),
        "power_proxy_mw": metric(report, "power__total") * 1000,
        "route_drc_violations": int(drc[-1]),
    })
    if out["macro_count"] != 0 or out["sequential_cells"] < 512:
        raise AssertionError(f"RF proxy not retained as flop-mapped storage: {variant}")
    out["legal"] = (
        out["setup_slack_ps"] >= 0 and out["hold_slack_ps"] >= 0
        and all(out[k] == 0 for k in (
            "setup_violations", "hold_violations", "max_cap_violations",
            "max_slew_violations", "max_fanout_violations",
            "route_drc_violations"))
    )
    return out


def audit(root: Path, repo: Path) -> dict:
    if read(root / "source_sha.txt").strip() != SOURCE_SHA:
        raise AssertionError("Artifact does not match frozen commit")
    if IMAGE not in read(root / "pinned_image.txt"):
        raise AssertionError("Unpinned ORFS image")
    if IMAGE not in read(root / "container_digests.json"):
        raise AssertionError("Container digest mismatch")
    log = read(root / "rtl.log")
    passed = re.search(r"PASS V317 banked RF proxy cycles=(\d+) accepted=(\d+) overflow=0", log)
    if not passed or int(passed.group(1)) != 4096 or int(passed.group(2)) <= 0:
        raise AssertionError("Missing substantive RTL equivalence and port legality")
    sdc = read(repo / "research/v317/rtl/rf_proxy_banked_tile.sdc")
    mk = read(repo / "research/v317/rtl/rf_proxy_banked_tile.mk")
    protocol = read(repo / "research/v317/FROZEN_BANKED_RF_PROXY_TILE_GATE_20261102.md")
    for expected in ("-period 3.000", "set_clock_uncertainty 0.100", "set_load 10.0"):
        if expected not in sdc:
            raise AssertionError(f"Changed physical SDC: {expected}")
    for expected in ("ABC_AREA = 1", "PLATFORM = nangate45"):
        if expected not in mk:
            raise AssertionError(f"Changed matched synthesis: {expected}")
    if "at least 2.0%" not in protocol:
        raise AssertionError("Frozen area criterion missing")
    rows = [inspect(root, variant) for variant in VARIANTS]
    source, pair = rows
    both_legal = source["legal"] and pair["legal"]
    area_saving = 100 * (1 - pair["area_um2"] / source["area_um2"]) if both_legal else None
    return {
        "source_sha": SOURCE_SHA,
        "evidence_tier": "16-bank 2R flop RF proxy with registered sink; NOT SRAM macro/GPU tile",
        "rtl_equivalence_cycles": 4096,
        "rows": rows,
        "both_legal": both_legal,
        "frozen_area_saving_threshold_pct": 2.0,
        "area_saving_pct": area_saving,
        "area_win_survives": area_saving >= 2.0 if both_legal else None,
        "same_clock_intrinsic_throughput_ratio": 1.0,
        "gpu_ipc_established": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_dir", type=Path)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.artifact_dir, args.repo)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
