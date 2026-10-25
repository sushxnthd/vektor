#!/usr/bin/env python3
"""Independent, fail-closed V296 integrated RF-slice physical audit.

Reuses the frozen post-CTS SPEF/DEF/clock-tree audit but deliberately DOES NOT
reuse its 7400 um2 controller area ceiling for this larger integrated slice.
"""
import argparse
import json
import math
from pathlib import Path

import audit_cts45_setup250 as original
from tile_slice_flow import OUT, NEW_FLOOR, sha

VARIANTS = ("pairwise", "serial_onehot")
TILE_AREA_CEILING = 30000.0
SETUP_GUARD_NS = 0.050
MIN_AREA_FRACTION = 0.01
MIN_SETUP_LEAD_NS = 0.050
FLOORPLAN_MARKER = "V296_TILE_SLICE_FLOORPLAN die260_core240"


def validate_manifest(root):
    m = json.loads((root / "tile_manifest.json").read_text())
    if m.get("same_tcl_for_both") is not True or m.get("die_um") != 260 or m.get("core_um") != 240:
        raise ValueError("Wrong integrated floorplan or contestant provenance")
    for name, expected in m["generated_sha256"].items():
        if sha((root / name).read_text()) != expected:
            raise ValueError("Modified physical Tcl: " + name)
    if (root / "cap_margin_repair_tile.tcl").read_text().count(NEW_FLOOR) != 1:
        raise ValueError("Invalid floorplan transformation")


def check_log(log):
    lines = log.splitlines()
    if lines.count(FLOORPLAN_MARKER) != 1:
        raise ValueError("Missing or duplicate integrated floorplan marker")
    if any(s.startswith("V296_TILE_SLICE_FLOORPLAN ") and s != FLOORPLAN_MARKER for s in lines):
        raise ValueError("Ambiguous integrated floorplan")
    if "V296_CTS45_DONE" not in lines:
        raise ValueError("Physical implementation incomplete")


def case(root, variant):
    if variant not in VARIANTS:
        raise ValueError("Unknown contestant")
    validate_manifest(root)
    check_log((root / f"{variant}.high.log").read_text(errors="replace"))
    row = original.case(root, variant)
    if not row.get("complete"):
        raise ValueError("Incomplete physical CTS/DEF/SPEF evidence")
    f = row["final"]
    row["controller_7400_um2_limit_not_applied"] = True
    row["integrated_area_limit_um2"] = TILE_AREA_CEILING
    row["feasible"] = (f["area_um2"] <= TILE_AREA_CEILING
                       and f["setup_ns"] >= SETUP_GUARD_NS
                       and f["hold_ns"] >= 0
                       and f["slew"] == 0 and f["cap"] == 0)
    return row


def decision(rows):
    p, c = (rows.get(v, {}) for v in VARIANTS)
    if not p.get("complete") or not c.get("complete"):
        return "INCOMPLETE_NO_TILE_PHYSICAL_CLAIM", None
    pf, cf = p["final"], c["final"]
    values = (pf["area_um2"], cf["area_um2"], pf["setup_ns"], cf["setup_ns"])
    if not all(math.isfinite(x) for x in values) or min(values[:2]) <= 0:
        return "INCOMPLETE_NO_TILE_PHYSICAL_CLAIM", None
    area_fraction = (cf["area_um2"] - pf["area_um2"]) / cf["area_um2"]
    slack_lead = pf["setup_ns"] - cf["setup_ns"]
    comparison = {
        "candidate_integrated_area_saving_fraction": area_fraction,
        "candidate_integrated_extracted_setup_lead_ns": slack_lead,
        "candidate_feasible": bool(p["feasible"]),
        "control_feasible": bool(c["feasible"]),
        "same_rf_banks_ports_and_execution": True,
        "strict_equal_consumed_area": False,
        "same_clock_admission_gain": 0.0,
        "tile_fmax_measured": False,
        "gpu_throughput_measured": False,
    }
    if not p["feasible"]:
        verdict = "CANDIDATE_TILE_SLICE_PHYSICAL_GATE_FAIL"
    elif not c["feasible"]:
        verdict = "CONTROL_TILE_SLICE_INFEASIBLE_NO_PARETO_CLAIM"
    elif area_fraction + 1e-12 < MIN_AREA_FRACTION or slack_lead + 1e-12 < MIN_SETUP_LEAD_NS:
        verdict = "TILE_SLICE_PARETO_HYPOTHESIS_FALSIFIED"
    else:
        verdict = "TILE_SLICE_FEASIBLE_PARETO_SUPPORTED_NOT_GPU"
    return verdict, comparison


def aggregate(root):
    rows = {}
    for variant in VARIANTS:
        try:
            rows[variant] = case(root, variant)
        except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
            rows[variant] = {"variant": variant, "complete": False, "error": str(exc)}
    verdict, comparison = decision(rows)
    result = {
        "decision": verdict, "rows": rows, "comparison": comparison,
        "preregistered_area_limit_um2": TILE_AREA_CEILING,
        "preregistered_min_area_saving_fraction": MIN_AREA_FRACTION,
        "preregistered_min_setup_lead_ns": MIN_SETUP_LEAD_NS,
        "strict_equal_consumed_area": False,
        "full_gpu_tile": False, "measured_power": False,
        "gpu_speedup": "NOT_ESTABLISHED", "holdouts": "SEALED",
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "aggregate.tile_slice.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if verdict != "TILE_SLICE_FEASIBLE_PARETO_SUPPORTED_NOT_GPU":
        raise SystemExit(3)


def self_test():
    def row(area, setup, feasible=True):
        return {"complete": True, "feasible": feasible,
                "final": {"area_um2": area, "setup_ns": setup}}
    assert decision({"pairwise": row(15000,.25), "serial_onehot": row(16000,.1)})[0] == "TILE_SLICE_FEASIBLE_PARETO_SUPPORTED_NOT_GPU"
    assert decision({"pairwise": row(15000,.25), "serial_onehot": row(16000,.1,False)})[0] == "CONTROL_TILE_SLICE_INFEASIBLE_NO_PARETO_CLAIM"
    assert decision({"pairwise": row(15000,.25,False), "serial_onehot": row(16000,.1)})[0] == "CANDIDATE_TILE_SLICE_PHYSICAL_GATE_FAIL"
    assert decision({"pairwise": row(15900,.25), "serial_onehot": row(16000,.1)})[0] == "TILE_SLICE_PARETO_HYPOTHESIS_FALSIFIED"
    assert decision({"pairwise": row(15000,.11), "serial_onehot": row(16000,.1)})[0] == "TILE_SLICE_PARETO_HYPOTHESIS_FALSIFIED"
    assert decision({"pairwise": row(float("nan"),.25), "serial_onehot": row(16000,.1)})[0] == "INCOMPLETE_NO_TILE_PHYSICAL_CLAIM"
    assert decision({"pairwise": row(15000,.25)})[0] == "INCOMPLETE_NO_TILE_PHYSICAL_CLAIM"
    try:
        check_log(FLOORPLAN_MARKER + "\n" + FLOORPLAN_MARKER + "\nV296_CTS45_DONE\n")
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate marker accepted")
    print("V296_TILE_SLICE_INDEPENDENT_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--single", nargs=2, metavar=("ROOT","VARIANT"))
    p.add_argument("--aggregate", type=Path)
    a = p.parse_args()
    if a.self_test:
        self_test()
    elif a.single:
        root, variant = Path(a.single[0]), a.single[1]
        try:
            row = case(root, variant)
        except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
            row = {"variant": variant, "complete": False, "error": str(exc)}
        (root / f"{variant}.tile.audit.json").write_text(json.dumps(row, indent=2) + "\n")
        print(json.dumps(row, indent=2))
        if not row.get("complete"):
            raise SystemExit(3)
    elif a.aggregate:
        aggregate(a.aggregate)
    else:
        p.error("Specify --self-test, --single ROOT VARIANT or --aggregate ROOT")
