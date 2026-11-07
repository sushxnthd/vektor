#!/usr/bin/env python3
"""Independent six-route OpenROAD audit for the V317 frozen placement-seed challenge.

Input is the immutable artifact from GitHub Actions run 41364018384.
Read-only, no use of claims from prior summary files. Exit nonzero on provenance,
missing raw reports, or internal metric inconsistencies. Timing failures are data.
"""
import argparse
import json
import math
from pathlib import Path
import re

SOURCE_SHA = "0cd47389b11535917e2b89193d7520fe222501ba"
IMAGE_DIGEST = "sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8"
SEEDS = (7, 19, 37)
VARIANTS = ("source", "pairwise")


def read(root, path):
    f = root / path
    if not f.is_file():
        raise AssertionError("Missing raw artifact: " + str(f))
    return f.read_text(encoding="utf-8", errors="replace")


def metric(report, key):
    name = "finish__" + key
    if name not in report:
        raise AssertionError("Missing OpenROAD metric " + name)
    v = report[name]
    if not isinstance(v, (int, float)) or not math.isfinite(v):
        raise AssertionError("Nonfinite OpenROAD metric " + name)
    return v


def inspect(root, seed, variant):
    top = "vektor_v317_issue_integrated_top_" + variant
    sub = "seed%d_%s" % (seed, variant)
    cfg = read(root, sub + "/config.txt")
    for expected in ("seed=%d" % seed, "variant=" + variant, "GPL_RANDOM_SEED=%d" % seed,
                     "ABC_AREA=1", "GPL_TIMING_DRIVEN=1"):
        assert expected in cfg.splitlines(), (sub, expected)
    status = read(root, sub + "/status.txt")
    assert "exit_code=0" in status, (sub, status)
    logroot = sub + "/logs/nangate45/" + top + "/base/"
    yosys = read(root, logroot + "1_2_yosys.log")
    assert "Using ABC area script." in yosys and "abc_area.script" in yosys
    report = json.loads(read(root, logroot + "6_report.json"))
    route = read(root, logroot + "5_2_route.log")
    extraction = read(root, logroot + "6_report.log")
    assert "RCX-0045" in extraction, "No extracted RC evidence: " + sub
    drc = re.findall(r"Number of violations\s*=\s*(\d+)", route)
    assert drc, "Missing final route DRC: " + sub
    wire = re.findall(r"Total wire length\s*=\s*(\d+)\s*um", route)
    assert wire, "Missing routed wire length: " + sub
    assert "Found 0 net violations" in route and "Found 0 pin violations" in route
    assert metric(report, "design__instance__count__class:sequential_cell") == 356
    assert metric(report, "design__instance__count__macros") == 0
    out = {
        "seed": seed,
        "variant": variant,
        "area_um2": metric(report, "design__instance__area__stdcell"),
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
    }
    out["legal_at_2ns"] = (
        out["setup_slack_ps"] >= 0 and out["setup_violations"] == 0
        and out["hold_slack_ps"] >= 0 and out["hold_violations"] == 0
        and out["max_cap_violations"] == 0 and out["max_slew_violations"] == 0
        and out["max_fanout_violations"] == 0 and out["route_drc_violations"] == 0
    )
    return out


def audit(root):
    assert read(root, "source_sha.txt").strip() == SOURCE_SHA
    assert IMAGE_DIGEST in read(root, "pinned_image.txt")
    assert IMAGE_DIGEST in read(root, "container_digests.json")
    assert "PASS V317 integrated issue-control equivalence cycles=4096 accepted=13153" in read(root, "rtl_simulation.log")
    rows = [inspect(root, s, v) for s in SEEDS for v in VARIANTS]
    paired = []
    for seed in SEEDS:
        a, b = [next(r for r in rows if r["seed"] == seed and r["variant"] == v)
                for v in VARIANTS]
        paired.append({
            "seed": seed,
            "pairwise_area_saving_pct": 100 * (1 - b["area_um2"] / a["area_um2"]),
            "pairwise_fmax_delta_pct": 100 * (b["fmax_mhz"] / a["fmax_mhz"] - 1),
            "pairwise_power_proxy_saving_pct": 100 * (1 - b["power_proxy_mw"] / a["power_proxy_mw"]),
            "source_legal": a["legal_at_2ns"],
            "pairwise_legal": b["legal_at_2ns"],
        })
    legal_source = [r for r in rows if r["variant"] == "source" and r["legal_at_2ns"]]
    legal_pairwise = [r for r in rows if r["variant"] == "pairwise" and r["legal_at_2ns"]]
    best = lambda xs, k: min(xs, key=lambda r: r[k]) if xs else None
    result = {
        "provenance": {"run": 41364018384, "source_sha": SOURCE_SHA,
                       "image_digest": IMAGE_DIGEST, "seed_set": list(SEEDS)},
        "rows": rows,
        "paired": paired,
        "frozen_predictions": {
            "P1_at_least_two_pairwise_legal": len(legal_pairwise) >= 2,
            "P2_pairwise_smaller_area_each_seed": all(p["pairwise_area_saving_pct"] > 0 for p in paired),
            "P3_any_source_legal_adversarial_possibility": bool(legal_source),
            "P4_intrinsic_same_clock_service_ratio": 1.0,
        },
        "legal_counts": {"source": len(legal_source), "pairwise": len(legal_pairwise)},
        "best_legal_area": {"source": best(legal_source, "area_um2"),
                            "pairwise": best(legal_pairwise, "area_um2")},
        "best_legal_power": {"source": best(legal_source, "power_proxy_mw"),
                             "pairwise": best(legal_pairwise, "power_proxy_mw")},
        "best_legal_fmax": {"source": max(legal_source, key=lambda r:r["fmax_mhz"]) if legal_source else None,
                            "pairwise": max(legal_pairwise, key=lambda r:r["fmax_mhz"]) if legal_pairwise else None},
        "limits": "Nangate45 typical, 2ns, 10fF, no SRAM, no GPU datapath, no workload-calibrated power",
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.artifact_dir)
    output = json.dumps(result, indent=2, sort_keys=True)
    print(output)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
