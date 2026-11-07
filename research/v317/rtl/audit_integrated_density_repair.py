#!/usr/bin/env python3
"""Independent audit of V317 density-repair source/pairwise physical runs.

Read immutable raw OpenROAD artifact from Actions run 41372770907. This
does not assume that a successful make command means timing closure.
Density sweep is POST-HOC TUNING, never an unseen prospective holdout.
"""
import argparse
import json
import math
import re
from pathlib import Path

RUN_ID = 41372770907
SOURCE_SHA = "f5247166cab17ae91074a17f55c6a32031dc9fbb"
IMAGE = "sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8"
ADDONS = ("0.05", "0.35")
VARIANTS = ("source", "pairwise")


def read(path):
    assert path.is_file(), "Missing original artifact: " + str(path)
    return path.read_text(encoding="utf-8", errors="replace")


def metric(report, name):
    key = "finish__" + name
    assert key in report, "Missing OpenROAD metric: " + key
    val = report[key]
    assert isinstance(val, (int, float)) and math.isfinite(val), key
    return val


def density_observations(folder, expected_addon):
    """Verify the intervention was applied in OpenROAD, not just named in config."""
    logs = list(folder.rglob("3_3_place_gp.log"))
    assert len(logs) == 1, "Missing/ambiguous global-placement log: " + str(folder)
    text = read(logs[0])
    pattern = r"Placement density is ([0-9.]+), computed from PLACE_DENSITY_LB_ADDON\s+([0-9.]+) and lower bound ([0-9.]+)"
    matches = re.findall(pattern, text)
    assert len(matches) == 1, "Missing actual target-density provenance: " + str(folder)
    density, applied_addon, lower_bound = map(float, matches[0])
    assert abs(applied_addon - float(expected_addon)) < 1e-8, "Intervention mismatch: " + str(folder)
    assert 0 < lower_bound < density < 1, "Invalid actual placement density: " + str(folder)
    assert re.search(r"global_placement -density\s+" + re.escape(matches[0][0]), text), "Global placer did not receive density"
    return {"actual_placement_density": density, "applied_addon": applied_addon, "lower_bound": lower_bound}

def inspect(root, addon, variant):
    label = "addon" + addon + "_" + variant
    folder = root / label
    top = "vektor_v317_issue_integrated_top_" + variant
    cfg = read(folder / "config.txt").splitlines()
    for expected in ("addon=" + addon, "variant=" + variant, "seed=7",
                     "ABC_AREA=1", "GPL_TIMING_DRIVEN=1"):
        assert expected in cfg, (label, expected)
    assert "exit_code=0" in read(folder / "status.txt"), label
    logs = folder / "logs" / "nangate45" / top / "base"
    yosys = read(logs / "1_2_yosys.log")
    assert "Using ABC area script." in yosys and "abc_area.script" in yosys, label
    report = json.loads(read(logs / "6_report.json"))
    route = read(logs / "5_2_route.log")
    extract = read(logs / "6_report.log")
    assert "RCX-0045" in extract, "Missing extracted-RC evidence: " + label
    drc = re.findall(r"Number of violations\s*=\s*(\d+)", route)
    wire = re.findall(r"Total wire length\s*=\s*(\d+)\s*um", route)
    assert drc and wire, "Missing final route DRC/wire: " + label
    assert "Found 0 net violations" in route and "Found 0 pin violations" in route, label
    assert metric(report, "design__instance__count__class:sequential_cell") == 356, label
    assert metric(report, "design__instance__count__macros") == 0, label
    out = {
        "addon": float(addon), "variant": variant, "seed": 7,
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
        "density_intervention": density_observations(folder, addon),
    }
    out["legal_at_2ns"] = (
        out["setup_slack_ps"] >= 0 and out["setup_violations"] == 0
        and out["hold_slack_ps"] >= 0 and out["hold_violations"] == 0
        and out["max_cap_violations"] == 0 and out["max_slew_violations"] == 0
        and out["max_fanout_violations"] == 0 and out["route_drc_violations"] == 0
    )
    return out


def audit(root):
    assert read(root / "source_sha.txt").strip() == SOURCE_SHA, "Unexpected source commit"
    assert IMAGE in read(root / "pinned_image.txt")
    assert IMAGE in read(root / "container_digests.json")
    assert "PASS V317 integrated issue-control equivalence cycles=4096 accepted=13153" in read(root / "rtl_simulation.log")
    rows = [inspect(root, a, v) for a in ADDONS for v in VARIANTS]
    for variant in VARIANTS:
        lo = next(r for r in rows if r["addon"] == 0.05 and r["variant"] == variant)
        hi = next(r for r in rows if r["addon"] == 0.35 and r["variant"] == variant)
        assert hi["density_intervention"]["actual_placement_density"] > lo["density_intervention"]["actual_placement_density"] + 0.08, "Density intervention did not materially change placement"
    paired = []
    for addon in ADDONS:
        source, pair = [next(r for r in rows if r["addon"] == float(addon) and r["variant"] == v)
                        for v in VARIANTS]
        paired.append({
            "addon": float(addon),
            "source_legal": source["legal_at_2ns"],
            "pairwise_legal": pair["legal_at_2ns"],
            "pairwise_area_saving_pct": 100 * (1 - pair["area_um2"] / source["area_um2"]),
            "pairwise_fmax_gain_pct": 100 * (pair["fmax_mhz"] / source["fmax_mhz"] - 1),
            "pairwise_power_proxy_saving_pct": 100 * (1 - pair["power_proxy_mw"] / source["power_proxy_mw"]),
        })
    legal = {v: [r for r in rows if r["variant"] == v and r["legal_at_2ns"]] for v in VARIANTS}
    return {
        "provenance": {"run": RUN_ID, "source_sha": SOURCE_SHA, "image": IMAGE},
        "rows": rows, "matched_pairs": paired,
        "legal_counts": {v: len(legal[v]) for v in VARIANTS},
        "best_legal_area": {v: min(legal[v], key=lambda x: x["area_um2"]) if legal[v] else None for v in VARIANTS},
        "best_legal_fmax": {v: max(legal[v], key=lambda x: x["fmax_mhz"]) if legal[v] else None for v in VARIANTS},
        "falsification": {
            "source_repaired_at_2ns": bool(legal["source"]),
            "pairwise_legal_at_both_densities": len(legal["pairwise"]) == 2,
            "pairwise_smaller_at_both_matched_densities": all(x["pairwise_area_saving_pct"] > 0 for x in paired),
            "intrinsic_same_clock_throughput_ratio": 1.0,
        },
        "interpretation": "Post-hoc density tuning, Nangate45 typical, no SRAM or GPU datapath. Density log lines retained for intervention audit. No tile IPC claim."
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact_dir", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = audit(args.artifact_dir)
    serialized = json.dumps(result, indent=2, sort_keys=True)
    print(serialized)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
