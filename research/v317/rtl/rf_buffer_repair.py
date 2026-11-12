"""Matched output-buffer repair for V317 fixed-priority RF arbitration.

Preserves mapped core cells; adds four explicit Nangate45 output buffers to
both designs. No wire RC, placement, max-capacitance signoff or GPU IPC.
"""
import argparse
import json
import re
from pathlib import Path

from research.v317.rtl.audit_rf_sta import parse_electrical, parse_report

TOPS = {
    "source_fixed": "vektor_rf_bank_arbiter",
    "pairwise_fixed": "vektor_v317_rf_pairwise",
}
DRIVES = ("none", "x1", "x2", "x4", "x8", "x16")
LOADS = (10, 24, 30, 60, 100)


def wrapper(label, drive):
    if label not in TOPS or drive not in DRIVES or drive == "none":
        raise ValueError("unsupported matched buffer wrapper")
    top = f"v317_buf_{label}_{drive}"
    cell = f"BUF_{drive.upper()}"
    lines = [
        f"module {top}(",
        "  input wire [3:0] request_valid,",
        "  input wire [15:0] src0_bank_flat,",
        "  input wire [15:0] src1_bank_flat,",
        "  output wire [3:0] grant",
        ");",
        "  wire [3:0] raw_grant;",
        f"  {TOPS[label]} core (",
        "    .request_valid(request_valid),",
        "    .src0_bank_flat(src0_bank_flat),",
        "    .src1_bank_flat(src1_bank_flat),",
        "    .grant(raw_grant)",
        "  );",
    ]
    for i in range(4):
        lines.append(f"  {cell} output_buf_{i} (.A(raw_grant[{i}]), .Z(grant[{i}]));")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def make_wrappers(directory):
    directory.mkdir(parents=True, exist_ok=True)
    for label in TOPS:
        for drive in DRIVES:
            if drive != "none":
                (directory / f"{label}_{drive}.sv").write_text(wrapper(label, drive))


def liberty_areas(liberty):
    text = Path(liberty).read_text()
    starts = list(re.finditer(r'\bcell\s*\(\s*"?([A-Za-z][A-Za-z0-9_]*)"?\s*\)\s*\{', text))
    areas = {}
    for i, match in enumerate(starts):
        body = text[match.end():starts[i+1].start() if i+1 < len(starts) else len(text)]
        area = re.search(r'\barea\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*;', body)
        if area:
            areas[match.group(1)] = float(area.group(1))
    for drive in DRIVES[1:]:
        if f"BUF_{drive.upper()}" not in areas:
            raise AssertionError(f"missing BUF_{drive.upper()} Liberty area")
    return areas


def mapped_area(netlist, areas):
    text = Path(netlist).read_text()
    # All mapped Nangate45 cells have an _X<drive> suffix.
    instances = re.findall(
        r'(?m)^\s*([A-Za-z][A-Za-z0-9_]*_X\d+)\s+([\\]?[A-Za-z0-9_$]+)\s*\(',
        text,
    )
    if not instances:
        raise AssertionError(f"no mapped cell instances in {netlist}")
    unknown = sorted({cell for cell, _ in instances if cell not in areas})
    if unknown:
        raise AssertionError(f"unrecognized mapped cells: {unknown}")
    return sum(areas[cell] for cell, _ in instances), len(instances)


def audit(directory, liberty):
    directory = Path(directory)
    areas = liberty_areas(liberty)
    bases = {}
    for label in TOPS:
        base_area, count = mapped_area(directory / f"{label}.v", areas)
        bases[label] = {"area_um2": round(base_area, 6), "mapped_cells": count}
    results = {}
    for load in LOADS:
        results[str(load)] = {}
        for drive in DRIVES:
            results[str(load)][drive] = {}
            for label in TOPS:
                path = directory / f"{label}_{drive}_{load}.log"
                timing = parse_report(path)
                electrical = parse_electrical(path)
                buffer_area = 0.0 if drive == "none" else 4 * areas[f"BUF_{drive.upper()}"]
                results[str(load)][drive][label] = {
                    **timing,
                    **electrical,
                    "total_mapped_cell_area_um2": round(bases[label]["area_um2"] + buffer_area, 6),
                    "buffer_area_um2": round(buffer_area, 6),
                    "reported_max_transition_legal": not electrical["max_transition_violated"],
                }
    common = []
    for drive in DRIVES[1:]:
        pair = results["24"][drive]["pairwise_fixed"]
        source = results["24"][drive]["source_fixed"]
        if pair["reported_max_transition_legal"] and source["reported_max_transition_legal"]:
            common.append({
                "drive": drive,
                "pairwise_delay_ns": pair["arrival_ns"],
                "source_delay_ns": source["arrival_ns"],
                "pairwise_area_um2": pair["total_mapped_cell_area_um2"],
                "source_area_um2": source["total_mapped_cell_area_um2"],
                "pairwise_wins_delay_and_area": (
                    pair["arrival_ns"] < source["arrival_ns"]
                    and pair["total_mapped_cell_area_um2"] < source["total_mapped_cell_area_um2"]
                ),
            })
    win = any(row["pairwise_wins_delay_and_area"] for row in common)
    slow_x16 = (
        results["10"]["x16"]["pairwise_fixed"]["arrival_ns"]
        > results["10"]["none"]["pairwise_fixed"]["arrival_ns"]
    )
    return {
        "evidence_tier": "MATCHED_NANGATE45_BUFFERED_PRE_ROUTE_CELL_STA",
        "base_mapped_area": bases,
        "loads_ff": list(LOADS),
        "drive_choices": list(DRIVES),
        "results": results,
        "frozen_predictions": {
            "24ff_repaired_common_legal_pairwise_area_and_delay_win": win,
            "10ff_pairwise_x16_slower_than_unbuffered": slow_x16,
            "all_survive": win and slow_x16,
        },
        "first_common_legal_drive_24ff": common[0]["drive"] if common else None,
        "common_legal_choices_24ff": common,
        "max_capacitance_checked": False,
        "wire_rc_extracted": False,
        "placed_routed": False,
        "setup_closure_verified": False,
        "tile_critical_path_verified": False,
        "gpu_ipc_measured": False,
        "same_grants_intrinsic_service_gain": 1.0,
    }


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="action", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("directory", type=Path)
    score = sub.add_parser("audit")
    score.add_argument("directory", type=Path)
    score.add_argument("liberty", type=Path)
    args = p.parse_args()
    if args.action == "generate":
        make_wrappers(args.directory)
    else:
        result = audit(args.directory, args.liberty)
        print(json.dumps(result, indent=2, sort_keys=True))
        # A failed hypothesis is scientific evidence; CI preserves JSON and logs.
        if not result["frozen_predictions"]["all_survive"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
