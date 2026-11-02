#!/usr/bin/env python3
"""Independent extracted-RC audit of V317 matched RF-proxy placement-density repair.

Reads original route logs, never infers signoff from route process exit or DRC alone.
The frozen earlier 0.05 RF-proxy gate remains FAIL regardless of these outcomes.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path

from audit_rf_proxy_banked_tile import inspect, read

DENSITIES = (("density_015", 0.15), ("density_035", 0.35))
THRESHOLD_PCT = 2.0
IMAGE = "sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8"


def audit(root: Path, repo: Path) -> dict:
    source_sha = read(root / "source_sha.txt").strip()
    expected_sha = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if source_sha != expected_sha:
        raise AssertionError("Source provenance differs from audited checkout")
    if IMAGE not in read(root / "pinned_image.txt"):
        raise AssertionError("Unpinned OpenROAD image")
    if IMAGE not in read(root / "container_digests.json"):
        raise AssertionError("Pinned image digest not confirmed")
    rtl = read(root / "rtl.log")
    match = re.search(
        r"PASS V317 banked RF proxy cycles=(\d+) accepted=(\d+) overflow=0", rtl
    )
    if not match or int(match.group(1)) != 4096 or int(match.group(2)) <= 0:
        raise AssertionError("RTL equivalence or bank-port test missing")
    sdc = read(repo / "research/v317/rtl/rf_proxy_banked_tile.sdc")
    mk = read(repo / "research/v317/rtl/rf_proxy_banked_tile.mk")
    frozen = read(repo / "research/v317/FROZEN_RF_PROXY_DENSITY_ELECTRICAL_REPAIR_20261102.md")
    for x in ("-period 3.000", "set_clock_uncertainty 0.100", "set_load 10.0"):
        if x not in sdc:
            raise AssertionError(f"SDC constraint changed: {x}")
    for x in ("ABC_AREA = 1", "PLATFORM = nangate45"):
        if x not in mk:
            raise AssertionError(f"Mapping changed: {x}")
    if "below 2.0%" not in frozen or "0.15 and 0.35" not in frozen:
        raise AssertionError("Prospective protocol missing")

    rows = []
    for label, density in DENSITIES:
        setting = read(root / label / "density_config.txt").strip()
        if setting != f"PLACE_DENSITY_LB_ADDON={density:.2f}":
            raise AssertionError(f"Density provenance missing: {label}")
        source = inspect(root / label, "source")
        pairwise = inspect(root / label, "pairwise")
        area = None
        if "area_um2" in source and "area_um2" in pairwise:
            if source["area_um2"] <= 0 or pairwise["area_um2"] <= 0:
                raise AssertionError("Invalid area")
            area = 100.0 * (1.0 - pairwise["area_um2"] / source["area_um2"])
            if not math.isfinite(area):
                raise AssertionError("Nonfinite area ratio")
        legal = bool(source["legal"] and pairwise["legal"])
        rows.append({
            "placement_density_addon": density,
            "source": source,
            "pairwise": pairwise,
            "both_legal": legal,
            "raw_area_saving_pct": area,
            "legal_material_win": legal and area is not None and area >= THRESHOLD_PCT,
            "legal_no_material_win": legal and area is not None and area < THRESHOLD_PCT,
            "electrical_gate": "PASS" if legal else "FAIL",
            "area_gate": ("INDETERMINATE_ELECTRICAL"
                          if not legal else
                          "PASS" if area >= THRESHOLD_PCT else "FAIL"),
        })
    return {
        "source_sha": source_sha,
        "evidence_tier": "flop RF proxy, NOT SRAM macro/GPU tile",
        "previous_frozen_005_gate": "FAIL_UNCHANGED",
        "frozen_material_threshold_pct": THRESHOLD_PCT,
        "same_clock_intrinsic_throughput_ratio": 1.0,
        "rows": rows,
        "any_legal_material_win": any(x["legal_material_win"] for x in rows),
        "all_legal_no_material_win": all(x["legal_no_material_win"] for x in rows),
        "gpu_ipc_established": False,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("artifact_dir", type=Path)
    p.add_argument("--repo", type=Path, default=Path("."))
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = audit(args.artifact_dir, args.repo)
    rendered = json.dumps(result, sort_keys=True, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
