#!/usr/bin/env python3
"""Independent raw-artifact audit for frozen V317 legal-clock crossover.

Reads unmodified OpenROAD outputs, does not infer legality from make exit status,
and never promotes controller timing to GPU IPC. Run:
  python3 research/v317/rtl/audit_legal_clock_crossover.py ARTIFACT_DIRECTORY
"""
import argparse
import json
import math
import re
from pathlib import Path

SOURCE_SHA = "e9c2799b1c8eb331c6f89b5fd270f9f64ea44d24"
IMAGE = "sha256:9bd99a4657f491615a5a516a8de3352f8b82013a7d0788e0b244c233efd9f5b8"
PERIODS = ("2.050", "2.200")
VARIANTS = ("source", "pairwise")


def read(p):
    assert p.is_file(), f"Missing raw evidence: {p}"
    return p.read_text(encoding="utf-8", errors="replace")


def metric(report, key):
    k = "finish__" + key
    assert k in report and isinstance(report[k], (int, float)), f"Missing metric {k}"
    assert math.isfinite(report[k]), f"Nonfinite metric {k}"
    return report[k]


def inspect(root, period, variant):
    label = f"period{period}_{variant}"
    folder = root / label
    config = read(folder / "config.txt").splitlines()
    for expected in (f"period_ns={period}", f"variant={variant}", "seed=7",
                     "ABC_AREA=1", "GPL_TIMING_DRIVEN=1",
                     "PLACE_DENSITY_LB_ADDON=0.05"):
        assert expected in config, (label, expected)
    status = read(folder / "status.txt").strip()
    assert re.fullmatch(r"exit_code=\d+", status), (label, status)
    if status != "exit_code=0":
        return {"period_ns": float(period), "variant": variant,
                "route_status": status, "legal": False,
                "interpretation": "Route failed; preserved as negative evidence."}
    top = "vektor_v317_issue_integrated_top_" + variant
    logs = folder / "logs" / "nangate45" / top / "base"
    yosys = read(logs / "1_2_yosys.log")
    assert "Using ABC area script." in yosys and "abc_area.script" in yosys, label
    report = json.loads(read(logs / "6_report.json"))
    route = read(logs / "5_2_route.log")
    extract = read(logs / "6_report.log")
    assert "RCX-0045" in extract, (label, "No RC extraction")
    drc = re.findall(r"Number of violations\s*=\s*(\d+)", route)
    wire = re.findall(r"Total wire length\s*=\s*(\d+)\s*um", route)
    assert drc and wire, (label, "Missing final DRC/wire")
    assert "Found 0 net violations" in route and "Found 0 pin violations" in route
    assert metric(report, "design__instance__count__class:sequential_cell") == 356
    assert metric(report, "design__instance__count__macros") == 0
    out = {
        "period_ns": float(period), "variant": variant, "route_status": status,
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
    out["legal"] = (
        out["setup_slack_ps"] >= 0 and out["setup_violations"] == 0
        and out["hold_slack_ps"] >= 0 and out["hold_violations"] == 0
        and out["max_cap_violations"] == 0 and out["max_slew_violations"] == 0
        and out["max_fanout_violations"] == 0 and out["route_drc_violations"] == 0
    )
    return out


def audit(root):
    assert read(root / "source_sha.txt").strip() == SOURCE_SHA, "Source SHA mismatch"
    assert IMAGE in read(root / "pinned_image.txt")
    assert IMAGE in read(root / "container_digests.json")
    assert "PASS V317 integrated issue-control equivalence cycles=4096 accepted=13153" in read(
        root / "rtl_simulation.log")
    protocol = read(root / "frozen_protocol.md")
    assert "Frozen predictions and falsifiers" in protocol
    for period in PERIODS:
        sdc = read(root / f"period_{period}.sdc")
        assert re.search(r"create_clock\s+-name\s+core_clk\s+-period\s+" +
                         re.escape(period) + r"\s", sdc), "SDC target mismatch"
        assert "set_clock_uncertainty 0.100" in sdc
        assert "set_load 10.0" in sdc
    rows = [inspect(root, p, v) for p in PERIODS for v in VARIANTS]
    pairs = []
    for p in PERIODS:
        source, pair = [next(x for x in rows if x["period_ns"] == float(p)
                             and x["variant"] == v) for v in VARIANTS]
        result = {"period_ns": float(p), "source_legal": source["legal"],
                  "pairwise_legal": pair["legal"], "legal_comparison": source["legal"] and pair["legal"]}
        if result["legal_comparison"]:
            result["area_saving_pct"] = 100 * (1 - pair["area_um2"] / source["area_um2"])
            result["power_proxy_saving_pct"] = 100 * (1 - pair["power_proxy_mw"] / source["power_proxy_mw"])
            result["frozen_area_threshold_survives"] = result["area_saving_pct"] >= 7.0
        pairs.append(result)
    return {
        "provenance": {"source_sha": SOURCE_SHA, "pinned_image": IMAGE},
        "rows": rows, "matched_pairs": pairs,
        "source_2200_legal_prediction": next(x for x in pairs if x["period_ns"] == 2.2)["source_legal"],
        "source_2050_legal_prediction": next(x for x in pairs if x["period_ns"] == 2.05)["source_legal"],
        "same_clock_intrinsic_service_ratio": 1.0,
        "scope": "Nangate45 typical-corner 32-wave control only; no RF SRAM, tile IPC or RTX 5090 claim",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact_dir", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = audit(args.artifact_dir)
    serialized = json.dumps(result, sort_keys=True, indent=2)
    print(serialized)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
