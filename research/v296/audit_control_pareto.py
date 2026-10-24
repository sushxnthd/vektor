#!/usr/bin/env python3
"""Fail-closed four-way high-RC control-advantaged physical Pareto audit.

Never upgrades the previously failed six-case extracted gate. The fifth
repair is deliberately granted to controls, not to V296.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import sys

from audit_detailed_route import extract_metric

VARIANTS = ("original", "serial_onehot", "parallel_onehot", "pairwise")
AREA_CEILING_UM2 = 7400.0
REQUIRED = (
    "V296_CLOCK_PERIOD_NS 3.5",
    "V296_CAP_MARGIN_PERCENT 20",
    "V296_PLACE_DENSITY 0.65",
    "V296_THIRD_PHYSICAL_DONE",
    "V296_PARETO_FOURTH_DONE",
    "V296_PARETO_DETAIL_BEGIN",
    "V296_PARETO_IS_ROUTED 1",
    "V296_PARETO_RC_MULTIPLIER 2.0",
    "V296_PARETO_HOLD_BEGIN",
    "V296_PARETO_HOLD_END",
    "V296_PARETO_DONE",
)


def parse_log(log, variant):
    lines = set(log.splitlines())
    expected_extra = 0 if variant == "pairwise" else 1
    for marker in REQUIRED + (
        f"V296_PARETO_VARIANT {variant}",
        f"V296_PARETO_EXTRA_REPAIR {expected_extra}",
    ):
        if marker not in lines:
            raise ValueError(f"{variant}: missing exact marker {marker}")
    if expected_extra and "V296_PARETO_CONTROL_FIFTH_DONE" not in lines:
        raise ValueError(f"{variant}: control fifth repair missing")
    if not expected_extra and "V296_PARETO_CONTROL_FIFTH_DONE" in lines:
        raise ValueError("Candidate received prohibited fifth repair")
    drc = re.search(r"(?m)^V296_PARETO_DRC_COUNT (\d+)\r?$", log)
    hold = re.search(
        r"(?ms)^V296_PARETO_HOLD_BEGIN\r?\n(.*?)^V296_PARETO_HOLD_END\r?$",
        log,
    )
    if not drc or not hold:
        raise ValueError(f"{variant}: missing DRC or extracted hold block")
    match = re.search(
        r"(?mi)^worst slack(?:\s+min)?\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*$",
        hold.group(1),
    )
    if not match:
        raise ValueError(f"{variant}: missing finite extracted hold slack")
    row = extract_metric(log, "pareto_extracted")
    row["hold_ns"] = float(match.group(1))
    row["drc"] = int(drc.group(1))
    row["extra_control_repair"] = bool(expected_extra)
    if not math.isfinite(row["hold_ns"]):
        raise ValueError(f"{variant}: nonfinite hold slack")
    return row


def feasible(row):
    return (
        row["area_um2"] <= AREA_CEILING_UM2
        and row["slew"] == row["cap"] == row["drc"] == 0
        and row["setup_ns"] >= 0
        and row["hold_ns"] >= 0
    )


def evaluate(rows):
    cand = rows["pairwise"]
    controls = {k: v for k, v in rows.items() if k != "pairwise"}
    best_area = min(v["area_um2"] for v in controls.values())
    best_setup = max(v["setup_ns"] for v in controls.values())
    saving = 100.0 * (best_area - cand["area_um2"]) / best_area
    lead = cand["setup_ns"] - best_setup
    candidate_feasible = feasible(cand)
    controls_feasible = [k for k, v in controls.items() if feasible(v)]
    matched = [k for k in controls_feasible if controls[k]["area_um2"] <= cand["area_um2"]]
    prereg_advantage = saving >= 10.0 and lead >= 0.20
    if not candidate_feasible:
        decision = "V296_CANDIDATE_PHYSICAL_FAIL"
    elif not prereg_advantage:
        decision = "V296_AREA_OR_TIMING_BOUNDARY_FALSIFIED"
    elif not controls_feasible:
        decision = "NO_FEASIBLE_CONTROL"
    elif not matched:
        decision = "COMMON_CEILING_PARETO_PASS_NOT_AREA_MATCHED"
    else:
        # If area matched, >=10% candidate area saving cannot also hold.
        raise AssertionError("Inconsistent area-matching arithmetic")
    return {
        "decision": decision,
        "candidate_feasible": candidate_feasible,
        "all_case_data_complete": True,
        "common_area_ceiling_um2": AREA_CEILING_UM2,
        "candidate_area_saving_pct_vs_smallest_control": saving,
        "candidate_setup_lead_ns_vs_fastest_control": lead,
        "preregistered_margin_supported": prereg_advantage,
        "feasible_controls": controls_feasible,
        "feasible_area_matched_controls": matched,
        "rows": rows,
        "frozen_six_case_gate": "DETAILED_PHYSICAL_GATE_FAIL",
        "holdouts": "SEALED",
        "limitations": (
            "Ideal-clock pre-CTS high-RC extracted controller-only evidence; "
            "common area ceiling is not identical consumed area. "
            "No equal-area timing Pareto, CTS, signoff, power, "
            "tile-level or same-clock throughput gain."
        ),
    }


def audit(root):
    rows, hashes = {}, {}
    for variant in VARIANTS:
        stem = variant + ".high"
        log = (root / (stem + ".log")).read_text()
        rows[variant] = parse_log(log, variant)
        for suffix in (".pareto.def", ".pareto.spef", ".pareto.drc.rpt", ".fourth.guide"):
            file = root / (stem + suffix)
            if not file.is_file() or (suffix != ".pareto.drc.rpt" and file.stat().st_size == 0):
                raise ValueError(f"{stem}: missing or empty {suffix}")
        if variant != "pairwise":
            fifth = root / (stem + ".fifth.guide")
            if not fifth.is_file() or fifth.stat().st_size == 0:
                raise ValueError(f"{stem}: missing control-only fifth route")
        spef = (root / (stem + ".pareto.spef")).read_text()
        if "*D_NET" not in spef or "*SPEF" not in spef:
            raise ValueError(f"{stem}: malformed extracted SPEF")
        netlist = root / (variant + ".v")
        if not netlist.is_file() or netlist.stat().st_size == 0:
            raise ValueError(f"{stem}: missing mapped netlist")
        hashes[variant] = hashlib.sha256(netlist.read_bytes()).hexdigest()
    if len(set(hashes.values())) != len(VARIANTS):
        raise ValueError("Distinct architectural contestants have identical mapped netlists")
    result = evaluate(rows)
    result["mapped_netlist_sha256"] = hashes
    return result


def self_test():
    variant = "serial_onehot"
    markers = [m for m in REQUIRED if m not in ("V296_PARETO_HOLD_BEGIN", "V296_PARETO_HOLD_END")] + [
        "V296_PARETO_VARIANT serial_onehot",
        "V296_PARETO_EXTRA_REPAIR 1",
        "V296_PARETO_CONTROL_FIFTH_DONE",
        "V296_PARETO_DRC_COUNT 0",
    ]
    sample = "\n".join(markers) + (
        "\nV296_STAGE_BEGIN pareto_extracted\n"
        "V296_METRIC stage=pareto_extracted area_um2=6900 slew=0 cap=0\n"
        "worst slack max 0.12\nV296_STAGE_END pareto_extracted\n"
        "V296_PARETO_HOLD_BEGIN\nworst slack min 0.24\n"
        "V296_PARETO_HOLD_END\n"
    )
    row = parse_log(sample, variant)
    assert row["setup_ns"] == 0.12 and row["hold_ns"] == 0.24
    for bad in (
        sample.replace("V296_PARETO_EXTRA_REPAIR 1", "V296_PARETO_EXTRA_REPAIR 0"),
        sample.replace("V296_PARETO_CONTROL_FIFTH_DONE", "V296_PARETO_CONTROL_FIFTH_SKIP"),
        sample.replace("V296_PARETO_DRC_COUNT 0", "V296_PARETO_DRC_COUNT bad"),
        sample.replace("worst slack min 0.24", "worst slack min nan"),
        sample.replace("V296_PARETO_DONE", "V296_PARETO_ABORT"),
    ):
        try:
            parse_log(bad, variant)
        except ValueError:
            continue
        raise AssertionError("Accepted malformed physical evidence")
    base = {
        "area_um2": 6000.0, "setup_ns": 0.4, "hold_ns": 0.2,
        "slew": 0, "cap": 0, "drc": 0,
    }
    rows = {
        "pairwise": dict(base),
        "original": dict(base, area_um2=7200, setup_ns=0.0),
        "serial_onehot": dict(base, area_um2=7000, setup_ns=0.1),
        "parallel_onehot": dict(base, area_um2=7100, setup_ns=0.15),
    }
    assert evaluate(rows)["decision"] == "COMMON_CEILING_PARETO_PASS_NOT_AREA_MATCHED"
    rows["original"]["setup_ns"] = -0.01
    rows["serial_onehot"]["slew"] = 2
    rows["parallel_onehot"]["cap"] = 1
    assert evaluate(rows)["decision"] == "NO_FEASIBLE_CONTROL"
    rows["pairwise"]["slew"] = 1
    assert evaluate(rows)["decision"] == "V296_CANDIDATE_PHYSICAL_FAIL"
    print("V296_CONTROL_ADVANTAGED_PARETO_AUDIT_SELFTEST_PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        raise SystemExit(0)
    if len(sys.argv) != 2:
        raise SystemExit("Usage: audit_control_pareto.py ROOT | --self-test")
    root = Path(sys.argv[1])
    root.mkdir(parents=True, exist_ok=True)
    try:
        result = audit(root)
    except (OSError, ValueError, AssertionError) as exc:
        result = {
            "decision": "CONTROL_PARETO_INCOMPLETE_EVIDENCE",
            "error": str(exc),
            "holdouts": "SEALED",
        }
    (root / "control_pareto_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if result["decision"] != "COMMON_CEILING_PARETO_PASS_NOT_AREA_MATCHED":
        raise SystemExit(3)
