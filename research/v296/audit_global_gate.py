#!/usr/bin/env python3
"""Independent fail-closed global-route-only feasibility audit for V296.

An AREA_WITHIN_CEILING result is never a detailed-route, SPEF, CTS, or
matched-area architectural pass. Partial stages are preserved on failure.
"""
import json
import math
from pathlib import Path
import re
import sys

VARIANTS = ("pairwise", "serial_onehot", "parallel_onehot", "original")
AREA_CEILING = 7400.0
STAGES = ("placed", "repaired_first", "routed_first", "repaired_second",
          "routed_final", "repaired_third", "routed_third",
          "pareto_fourth_repaired", "pareto_fourth_routed",
          "pareto_control_fifth_repaired", "pareto_control_fifth_routed",
          "pareto_global_final")
NUM = r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"


def stage_metrics(log, stage):
    pattern = (r"(?ms)^V296_STAGE_BEGIN " + re.escape(stage) +
               r"\r?\n(.*?)^V296_STAGE_END " + re.escape(stage) + r"\r?$")
    match = re.search(pattern, log)
    if not match:
        return None
    block = match.group(1)
    area = re.search(r"(?m)^V296_METRIC stage=" + re.escape(stage) +
                     r" area_um2=" + NUM + r" slew=(\d+) cap=(\d+)\r?$", block)
    slack = re.search(r"(?mi)^worst slack(?:\s+max)?\s+" + NUM + r"\s*$", block)
    if not area or not slack:
        raise ValueError(f"{stage}: malformed area/electrical/setup evidence")
    vals = {
        "area_um2": float(area.group(1)),
        "slew": int(area.group(2)),
        "cap": int(area.group(3)),
        "setup_ns": float(slack.group(1)),
    }
    if not all(math.isfinite(v) for v in vals.values()) or vals["area_um2"] <= 0:
        raise ValueError(f"{stage}: nonfinite/invalid measurement")
    vals["area_headroom_um2"] = AREA_CEILING - vals["area_um2"]
    vals["area_within_ceiling"] = vals["area_headroom_um2"] >= 0
    vals["ideal_clock_electrical_setup_feasible"] = (
        vals["area_within_ceiling"] and vals["slew"] == 0 and
        vals["cap"] == 0 and vals["setup_ns"] >= 0)
    return vals


def parse_log(log, variant, has_def):
    if variant not in VARIANTS:
        raise ValueError("invalid contestant")
    markers = set(log.splitlines())
    extra = 0 if variant == "pairwise" else 1
    expected = (
        f"V296_PARETO_VARIANT {variant}",
        f"V296_PARETO_EXTRA_REPAIR {extra}",
        "V296_CLOCK_PERIOD_NS 3.5",
        "V296_PLACE_DENSITY 0.65",
    )
    # The two physics markers occur before initial placement. Pareto identity
    # markers are absent in legitimately interrupted earlier repair stages.
    for marker in expected[2:]:
        if marker not in markers:
            raise ValueError(f"missing frozen-physics marker {marker}")
    for marker in expected[:2]:
        key = marker.split(" ", 1)[0] + " "
        if any(line.startswith(key) and line != marker for line in markers):
            raise ValueError(f"contradictory contestant/repair marker: {key}")
    stages = {s: v for s in STAGES if (v := stage_metrics(log, s)) is not None}
    full = (all(marker in markers for marker in expected[:2]) and
            "V296_GLOBAL_GATE_ONLY 1" in markers and
            "V296_GLOBAL_GATE_ONLY_COMPLETE_NOT_SIGNOFF" in markers and
            "V296_PARETO_FOURTH_DONE" in markers and
            "V296_PARETO_DETAIL_BEGIN" not in markers and
            has_def and "pareto_global_final" in stages)
    if extra:
        full = full and "V296_PARETO_CONTROL_FIFTH_DONE" in markers and "pareto_control_fifth_routed" in stages
    else:
        full = full and "V296_PARETO_CONTROL_FIFTH_DONE" not in markers
    final = stages.get("pareto_global_final")
    return {
        "variant": variant,
        "evidence_tier": "placed and global-routed ideal-clock estimates only",
        "stages": stages,
        "decision": (
            ("GLOBAL_ONLY_AREA_CEILING_FAIL_NOT_SIGNOFF" if not final["area_within_ceiling"]
             else "GLOBAL_ONLY_ELECTRICAL_OR_SETUP_FAIL_NOT_SIGNOFF"
             if not final["ideal_clock_electrical_setup_feasible"]
             else "GLOBAL_ONLY_FEASIBLE_NOT_SIGNOFF")
            if full else "GLOBAL_GATE_INCOMPLETE_NOT_SIGNOFF"
        ),
        "complete_global_route_record": bool(full),
        "global_only_feasibility": (
            ("PASS_GLOBAL_ONLY" if final["ideal_clock_electrical_setup_feasible"]
             else "FAIL_GLOBAL_ONLY") if full else "NOT_EVALUATED"),
        "last_completed_stage": next((s for s in reversed(STAGES) if s in stages), None),
        "fatal_errors": [line for line in log.splitlines()
                         if line.startswith(("[ERROR", "Error:", "[FATAL", "FATAL:"))][-5:],
        "detailed_route": "NOT_RUN",
        "extracted_spef": "NOT_RUN",
        "cts": "NOT_RUN",
        "workload_holdouts": "SEALED",
        "full_physical_gate": "NOT_EVALUATED",
    }


def self_test():
    def marker(stage, area, slack):
        return (f"V296_STAGE_BEGIN {stage}\n"
                f"V296_METRIC stage={stage} area_um2={area} slew=0 cap=0\n"
                f"worst slack max {slack}\nV296_STAGE_END {stage}\n")
    log = ("V296_PARETO_VARIANT pairwise\nV296_PARETO_EXTRA_REPAIR 0\n"
           "V296_CLOCK_PERIOD_NS 3.5\nV296_PLACE_DENSITY 0.65\n"
           "V296_PARETO_FOURTH_DONE\n" +
           marker("pareto_fourth_routed", 5990, 0.35) +
           "V296_GLOBAL_GATE_ONLY 1\n" +
           marker("pareto_global_final", 5990, 0.35) +
           "V296_GLOBAL_GATE_ONLY_COMPLETE_NOT_SIGNOFF\n")
    row = parse_log(log, "pairwise", True)
    assert row["decision"] == "GLOBAL_ONLY_FEASIBLE_NOT_SIGNOFF"
    assert abs(row["stages"]["pareto_global_final"]["area_headroom_um2"] - 1410) < 1e-9
    assert parse_log(log, "pairwise", False)["decision"] == "GLOBAL_GATE_INCOMPLETE_NOT_SIGNOFF"
    assert parse_log(log.replace("5990", "7990"), "pairwise", True)["decision"] == "GLOBAL_ONLY_AREA_CEILING_FAIL_NOT_SIGNOFF"
    assert parse_log(log.replace("cap=0", "cap=2"), "pairwise", True)["decision"] == "GLOBAL_ONLY_ELECTRICAL_OR_SETUP_FAIL_NOT_SIGNOFF"
    partial = ("V296_CLOCK_PERIOD_NS 3.5\nV296_PLACE_DENSITY 0.65\n" +
               marker("placed", 8223, -4.12) + "[ERROR DPL-0036] Placement failed.\n")
    partial_row = parse_log(partial, "parallel_onehot", False)
    assert partial_row["decision"] == "GLOBAL_GATE_INCOMPLETE_NOT_SIGNOFF"
    assert partial_row["stages"]["placed"]["area_um2"] == 8223
    assert partial_row["fatal_errors"]
    assert parse_log(log.replace("V296_GLOBAL_GATE_ONLY_COMPLETE_NOT_SIGNOFF", "CANCELLED"),
                     "pairwise", True)["decision"] == "GLOBAL_GATE_INCOMPLETE_NOT_SIGNOFF"
    for corrupted in (log.replace("V296_PLACE_DENSITY 0.65", "V296_PLACE_DENSITY 0.45"),
                      log.replace("worst slack max 0.35", "worst slack max nan")):
        try:
            parse_log(corrupted, "pairwise", True)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted corrupted physical evidence")
    print("V296_GLOBAL_GATE_AUDIT_SELFTEST_PASS")


def main(root, variant):
    root = Path(root)
    path = root / f"{variant}.high.log"
    result_path = root / f"{variant}.global_audit.json"
    try:
        log = path.read_text()
        def_path = root / f"{variant}.high.global.def"
        result = parse_log(log, variant, def_path.is_file() and def_path.stat().st_size > 0)
    except (OSError, ValueError) as exc:
        result = {"decision": "GLOBAL_GATE_INCOMPLETE_NOT_SIGNOFF",
                  "error": str(exc), "variant": variant,
                  "workload_holdouts": "SEALED"}
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result.get("complete_global_route_record") or result.get("global_only_feasibility") != "PASS_GLOBAL_ONLY":
        raise SystemExit(3)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        raise SystemExit("Usage: audit_global_gate.py --self-test | ROOT VARIANT")
