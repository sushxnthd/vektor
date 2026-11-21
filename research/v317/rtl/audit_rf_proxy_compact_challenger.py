#!/usr/bin/env python3
"""Independent V317 three-way compact-greedy RF-proxy raw-artifact audit.

Source, pairwise and compact use exactly the same RF flop proxy, 3 ns SDC,
mapping, placement density and routed electrical constraints.  A successful
route exit or zero DRC is never accepted as electrical signoff.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path

from audit_rf_proxy_banked_tile import inspect, read

IMAGE = "sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8"
VARIANTS = ("source", "pairwise", "compact")
THRESHOLD = 2.0


def raw_saving(source: dict, candidate: dict) -> float | None:
    if "area_um2" not in source or "area_um2" not in candidate:
        return None
    a, b = float(source["area_um2"]), float(candidate["area_um2"])
    if not all(math.isfinite(x) and x > 0 for x in (a, b)):
        raise AssertionError("Invalid area observation")
    return 100.0 * (1.0 - b / a)


def decision(compact: dict, pairwise: dict) -> dict:
    saving = raw_saving(compact, pairwise)
    legal = bool(compact.get("legal") and pairwise.get("legal"))
    return {
        "raw_pairwise_saving_vs_compact_pct": saving,
        "raw_no_win_prediction": ("UNKNOWN" if saving is None else
                                  "PASS" if saving < THRESHOLD else "FALSIFIED"),
        "compact_pairwise_both_electrically_legal": legal,
        "legal_material_win": legal and saving is not None and saving >= THRESHOLD,
        "legal_material_gate": ("UNKNOWN_MISSING_AREA" if saving is None else
                                "FAIL_ELECTRICAL" if not legal else
                                "PASS" if saving >= THRESHOLD else "FAIL_AREA"),
        "pairwise_raw_area_dominated_by_compact":
            None if saving is None else saving <= 0.0,
        "pairwise_legality_dominated_by_compact":
            bool(compact.get("legal") and not pairwise.get("legal")),
    }


def self_test() -> None:
    a = {"area_um2": 100.0, "legal": True}
    assert decision(a, {"area_um2": 97.0, "legal": True})["legal_material_win"]
    assert decision(a, {"area_um2": 99.0, "legal": True})["raw_no_win_prediction"] == "PASS"
    assert decision(a, {"area_um2": 97.0, "legal": False})["legal_material_gate"] == "FAIL_ELECTRICAL"
    assert decision(a, {"area_um2": 101.0, "legal": True})["pairwise_raw_area_dominated_by_compact"]
    assert decision(a, {"legal": False})["raw_no_win_prediction"] == "UNKNOWN"
    assert not decision({"area_um2": 100.0, "legal": False},
                        {"area_um2": 97.0, "legal": True})["legal_material_win"]


def audit(root: Path, repo: Path) -> dict:
    self_test()
    source_sha = read(root / "source_sha.txt").strip()
    current_sha = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if source_sha != current_sha:
        raise AssertionError("Raw artifact source SHA does not match checkout")
    if IMAGE not in read(root / "pinned_image.txt") or IMAGE not in read(
        root / "container_digests.json"
    ):
        raise AssertionError("OpenROAD container digest mismatch")
    if read(root / "density_config.txt").strip() != "PLACE_DENSITY_LB_ADDON=0.35":
        raise AssertionError("Placement density mismatch")
    rtl = read(root / "rtl.log")
    m = re.search(r"PASS V317 compact challenger cycles=(\d+) accepted=(\d+) overflow=0", rtl)
    if not m or int(m.group(1)) != 4096 or int(m.group(2)) <= 0:
        raise AssertionError("Three-way RTL equivalence and RF port check absent")
    sdc = read(repo / "research/v317/rtl/rf_proxy_banked_tile.sdc")
    mk = read(repo / "research/v317/rtl/rf_proxy_compact_challenger.mk")
    frozen = read(repo / "research/v317/FROZEN_COMPACT_GREEDY_RF_PROXY_CHALLENGE_20261102.md")
    for needle in ("-period 3.000", "set_clock_uncertainty 0.100", "set_load 10.0"):
        if needle not in sdc:
            raise AssertionError(f"SDC drift: {needle}")
    for needle in ("ABC_AREA = 1", "PLATFORM = nangate45",
                   "compact_greedy_equal_policy.sv", "rf_proxy_compact_challenger.sv"):
        if needle not in mk:
            raise AssertionError(f"RTL or mapping drift: {needle}")
    if "less than 2.0%" not in frozen or "0.35" not in frozen:
        raise AssertionError("Missing frozen prediction")
    rows = {variant: inspect(root, variant) for variant in VARIANTS}
    completed = [x for x in rows.values() if x["route_exit"] == 0]
    if len(completed) == 3:
        seq = [x["sequential_cells"] for x in completed]
        if len(set(seq)) != 1:
            raise AssertionError(f"Non-matched sequential RF resources: {seq}")
    return {
        "source_sha": source_sha,
        "evidence_tier": "flop-mapped 16-bank 2R RF proxy, not SRAM/GPU tile",
        "variants": rows,
        "source_vs_pairwise_raw_saving_pct": raw_saving(rows["source"], rows["pairwise"]),
        "source_vs_compact_raw_saving_pct": raw_saving(rows["source"], rows["compact"]),
        "compact_baseline_decision": decision(rows["compact"], rows["pairwise"]),
        "frozen_materiality_pct": THRESHOLD,
        "same_clock_intrinsic_throughput_ratio": 1.0,
        "historical_v317_rf_proxy_gate": "FAIL_UNCHANGED",
        "gpu_ipc_established": False,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact_dir", type=Path)
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = audit(args.artifact_dir, args.repo)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
