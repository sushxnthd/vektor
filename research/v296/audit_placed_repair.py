#!/usr/bin/env python3
"""Independent, fail-closed audit of V296 matched placement/repair/routing.

No holdout data are read. OpenROAD global-routing parasitics are NOT extracted
detailed-route SPEF, signoff timing, power, or a GPU-level performance claim.
"""
import json
import math
import pathlib
import re
import sys

VARIANTS = ("original", "optimized", "pairwise")
SCENARIOS = ("low", "nominal", "high")
STAGES = ("placed", "repaired", "routed_preclosure", "routed")
PERIOD_NS = 3.5

def parse_stage(log, stage):
    match = re.search(r"V296_STAGE_BEGIN " + stage + r"\s*(.*?)V296_STAGE_END " + stage, log, re.S)
    if not match:
        raise ValueError("missing stage: " + stage)
    block = match.group(1)
    m = re.search(r"V296_METRIC stage=" + stage +
                  r" area_um2=([0-9.eE+-]+) slew=(\d+) cap=(\d+)", block)
    slack = re.search(r"worst slack(?:\s+max)?\s+([-+]?[0-9]+(?:\.[0-9]+)?)", block, re.I)
    if not m or not slack:
        raise ValueError("missing area/electrical/setup metric: " + stage)
    area, slew, cap = float(m.group(1)), int(m.group(2)), int(m.group(3))
    setup_slack = float(slack.group(1))
    if not all(map(math.isfinite, (area, setup_slack))) or area <= 0:
        raise ValueError("nonfinite/invalid physical metric")
    return {"area_um2": area, "max_slew_violations": slew,
            "max_capacitance_violations": cap,
            "setup_slack_ns_at_clock": setup_slack}

def audit(root):
    rows = {}
    for scenario in SCENARIOS:
        rows[scenario] = {}
        for variant in VARIANTS:
            path = root / f"{variant}.{scenario}.log"
            log = path.read_text()
            if "V296_CLOCK_PERIOD_NS 3.5" not in log:
                raise ValueError("clock period does not match frozen 3.5 ns protocol: " + str(path))
            if "V296_PHYSICAL_DONE" not in log or "V296_ROUTE_FAILED" in log:
                raise ValueError("global routing incomplete: " + str(path))
            rows[scenario][variant] = {s: parse_stage(log, s) for s in STAGES}
    nominal = rows["nominal"]
    candidate = nominal["pairwise"]["routed"]
    controls = {v: nominal[v]["routed"] for v in ("original", "optimized")}
    min_area_control = min(controls, key=lambda v: controls[v]["area_um2"])
    # A strict physical comparison must evaluate both controls, not cherry-pick one.
    fastest_control = max(controls, key=lambda v: controls[v]["setup_slack_ns_at_clock"])
    repaired_area_saving = controls[min_area_control]["area_um2"] - candidate["area_um2"]
    clean = all(rows[s][v]["routed"]["max_slew_violations"] == 0 and
                rows[s][v]["routed"]["max_capacitance_violations"] == 0
                for s in SCENARIOS for v in VARIANTS)
    meets_clock = all(rows[s][v]["routed"]["setup_slack_ns_at_clock"] >= 0
                      for s in SCENARIOS for v in VARIANTS)
    faster = all(rows[s]["pairwise"]["routed"]["setup_slack_ns_at_clock"] >
                 max(rows[s][v]["routed"]["setup_slack_ns_at_clock"]
                     for v in ("original", "optimized"))
                 for s in SCENARIOS)
    area_advantage = all(rows[s]["pairwise"]["routed"]["area_um2"] <
                         min(rows[s][v]["routed"]["area_um2"]
                             for v in ("original", "optimized"))
                         for s in SCENARIOS)
    result = {
        "evidence_class": "matched_openroad_placement_repair_global_route_estimated_RC_not_signoff",
        "holdouts": "SEALED",
        "clock_period_ns": PERIOD_NS,
        "protocol": "research/v296/ROUTED_RC_BOUNDARY_AND_3P5NS_PREREG_20261023.md",
        "same_die_core_and_constraints": True,
        "rc_multipliers": {"low": 0.5, "nominal": 1.0, "high": 2.0},
        "rows": rows,
        "nominal_area_min_control": min_area_control,
        "nominal_timing_best_control": fastest_control,
        "nominal_postrepair_area_saving_um2": repaired_area_saving,
        "nominal_area_saving_survives": repaired_area_saving > 0,
        "all_cases_electrically_clean": clean,
        "all_cases_meet_3p5ns": meets_clock,
        "all_cases_pairwise_faster_than_both_controls": faster,
        "all_cases_pairwise_smaller_than_both_controls": area_advantage,
        "decision": ("PROVISIONAL_POST_GLOBAL_ROUTE_PASS" if
                     clean and meets_clock and faster and area_advantage else
                     "PHYSICAL_GATE_FAIL"),
        "not_established": ["detailed-route extraction", "signoff STA",
                            "power", "tile-level throughput", "unseen workload transfer"],
        "retirement_rule": "Retire if matched repaired control removes candidate area/timing benefit; no holdouts before physical gate."
    }
    return result

def self_test():
    sample = ("V296_STAGE_BEGIN routed\nV296_METRIC stage=routed "
              "area_um2=3100.125 slew=0 cap=0\n"
              "worst slack max 0.123456\nV296_STAGE_END routed\n")
    row = parse_stage(sample, "routed")
    assert row["area_um2"] == 3100.125
    assert row["setup_slack_ns_at_clock"] == 0.123456
    assert row["max_slew_violations"] == 0
    for broken in (sample.replace("slew=0", "slew=abc"), sample.replace("V296_STAGE_END", "BROKEN")):
        try:
            parse_stage(broken, "routed")
        except ValueError:
            pass
        else:
            raise AssertionError("corrupt physical report accepted")
    print("V296_PLACED_AUDIT_SELFTEST_PASS")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        sys.exit(0)
    if len(sys.argv) != 2:
        raise SystemExit("Usage: audit_placed_repair.py PATH | --self-test")
    root = pathlib.Path(sys.argv[1])
    try:
        result = audit(root)
    except (ValueError, OSError) as exc:
        result = {"decision": "INCOMPLETE_PHYSICAL_EVIDENCE", "holdouts": "SEALED",
                  "error": str(exc)}
    (root / "placed_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))
    if result["decision"] != "PROVISIONAL_POST_GLOBAL_ROUTE_PASS":
        sys.exit(3)
