#!/usr/bin/env python3
"""Independent fail-closed audit for prospective symmetric V296 cap-margin experiment."""
import json
import math
import pathlib
import re
import sys

VARIANTS = ("original", "optimized", "pairwise")
SCENARIOS = ("nominal", "high")
STAGES = ("placed", "repaired_first", "routed_first", "repaired_second", "routed_final")

def parse_stage(log, stage):
    pat = (r"(?m)^V296_STAGE_BEGIN " + re.escape(stage) +
           r"\r?\n(.*?)^V296_STAGE_END " + re.escape(stage) + r"(?:\r?\n|\Z)")
    match = re.search(pat, log, re.S | re.M)
    if not match:
        raise ValueError("Missing complete stage " + stage)
    body = match.group(1)
    metric = re.search(
        r"V296_METRIC stage=" + re.escape(stage) +
        r" area_um2=([0-9.eE+-]+) slew=(\d+) cap=(\d+)", body)
    slack = re.search(r"worst slack(?:\s+max)?\s+([-+]?[0-9]+(?:\.[0-9]+)?)", body, re.I)
    if not metric or not slack:
        raise ValueError("Missing metrics in " + stage)
    area = float(metric.group(1))
    setup = float(slack.group(1))
    if not math.isfinite(area) or area <= 0 or not math.isfinite(setup):
        raise ValueError("Invalid area or slack")
    return dict(area_um2=area, setup_slack_ns=setup,
                max_slew=int(metric.group(2)), max_cap=int(metric.group(3)))

def audit(root):
    rows = {}
    for scenario in SCENARIOS:
        rows[scenario] = {}
        for variant in VARIANTS:
            path = root / f"{variant}.{scenario}.log"
            log = path.read_text()
            for token in ("V296_CLOCK_PERIOD_NS 3.5", "V296_CAP_MARGIN_PERCENT 20",
                          "V296_SLEW_MARGIN_PERCENT 10", "V296_MARGIN_PHYSICAL_DONE",
                          "V296_FIRST_CAP_VIOLATORS_BEGIN", "V296_FIRST_CAP_VIOLATORS_END",
                          "V296_FINAL_CAP_VIOLATORS_BEGIN", "V296_FINAL_CAP_VIOLATORS_END"):
                if token not in log:
                    raise ValueError(f"Missing evidence {token}: {path}")
            if "V296_ROUTE_FAILED" in log:
                raise ValueError("Route failed: " + str(path))
            if not (root / f"{variant}.{scenario}.final.def").is_file():
                raise ValueError("Missing final DEF: " + str(path))
            rows[scenario][variant] = {stage: parse_stage(log, stage) for stage in STAGES}
    comparisons = {}
    all_clean = True
    all_timed = True
    all_smaller = True
    all_faster = True
    for scenario in SCENARIOS:
        finals = {v: rows[scenario][v]["routed_final"] for v in VARIANTS}
        cand = finals["pairwise"]
        controls = [finals["original"], finals["optimized"]]
        area_saving = min(c["area_um2"] for c in controls) - cand["area_um2"]
        slack_lead = cand["setup_slack_ns"] - max(c["setup_slack_ns"] for c in controls)
        all_clean &= all(x["max_slew"] == 0 and x["max_cap"] == 0 for x in finals.values())
        all_timed &= all(x["setup_slack_ns"] >= 0 for x in finals.values())
        all_smaller &= area_saving > 0
        all_faster &= slack_lead > 0
        comparisons[scenario] = dict(
            candidate_area_um2=cand["area_um2"],
            smallest_control_area_um2=min(c["area_um2"] for c in controls),
            candidate_area_saving_um2=area_saving,
            candidate_area_saving_pct=100 * area_saving / min(c["area_um2"] for c in controls),
            candidate_slack_lead_ns=slack_lead,
            final_cap_violations={v: finals[v]["max_cap"] for v in VARIANTS},
            final_slew_violations={v: finals[v]["max_slew"] for v in VARIANTS},
            final_setup_slack_ns={v: finals[v]["setup_slack_ns"] for v in VARIANTS},
            cap_violations_before_second_repair={
                v: rows[scenario][v]["routed_first"]["max_cap"] for v in VARIANTS})
    passed = all_clean and all_timed and all_smaller and all_faster
    # Distinguish a scientific kill (equal repair removes candidate advantage)
    # from a physicality failure where candidate advantage still survives.
    killed = not (all_smaller and all_faster)
    decision = ("MARGIN_PROVISIONAL_GLOBAL_ROUTE_PASS" if passed else
                "MARGIN_RETIRE_V296" if killed else "MARGIN_PHYSICAL_GATE_FAIL")
    return dict(decision=decision, holdouts="SEALED",
                evidence_class="global_route_estimated_RC_not_extracted_SPEF_or_signoff",
                period_ns=3.5, cap_margin_percent=20, slew_margin_percent=10,
                all_clean=all_clean, all_timed=all_timed,
                candidate_smaller_both_scenarios=all_smaller,
                candidate_faster_both_scenarios=all_faster,
                comparisons=comparisons, rows=rows,
                limitation="No detailed route, CTS, hold, power, tile or measured GPU throughput.")

def self_test():
    a = ("V296_STAGE_BEGIN routed_final\n"
         "V296_METRIC stage=routed_final area_um2=5000 slew=0 cap=0\n"
         "worst slack max 0.123456\nV296_STAGE_END routed_final\n")
    assert parse_stage(a, "routed_final")["setup_slack_ns"] == 0.123456
    b = a.replace("routed_final", "routed_first").replace("5000", "6000")
    assert parse_stage(b + a, "routed_final")["area_um2"] == 5000
    assert parse_stage(b + a, "routed_first")["area_um2"] == 6000
    for broken in (a.replace("cap=0", "cap=bad"),
                   a.replace("V296_STAGE_END", "MISSING_END")):
        try:
            parse_stage(broken, "routed_final")
        except ValueError:
            pass
        else:
            raise AssertionError("Corrupt physical evidence accepted")
    print("V296_CAP_MARGIN_AUDIT_SELFTEST_PASS")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        raise SystemExit(0)
    if len(sys.argv) != 2:
        raise SystemExit("Usage: audit_cap_margin.py ROOT | --self-test")
    root = pathlib.Path(sys.argv[1])
    try:
        result = audit(root)
    except (OSError, ValueError) as exc:
        result = dict(decision="MARGIN_INCOMPLETE_EVIDENCE", holdouts="SEALED", error=str(exc))
    root.mkdir(parents=True, exist_ok=True)
    (root / "cap_margin_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))
    if result["decision"] != "MARGIN_PROVISIONAL_GLOBAL_ROUTE_PASS":
        raise SystemExit(3)
