#!/usr/bin/env python3
"""Strict, reproducible STA summary. Missing/unconstrained evidence is failure, not a win."""
import json, pathlib, re, sys
root = pathlib.Path(sys.argv[1])
variants = ("original", "optimized", "pairwise")
scenarios = ("low", "nominal", "high")
rows = {}
for scenario in scenarios:
    rows[scenario] = {}
    for variant in variants:
        p = root / f"{variant}.{scenario}.sta.log"
        log = p.read_text()
        required = ("V296_STA_COMPLETE", "V296_ALL_PATH_WORST_SLACK_START",
                    "V296_DATA_WORST_SLACK_START", "V296_DATA_PATHS_START",
                    "V296_ELECTRICAL_VIOLATORS_START")
        if any(marker not in log for marker in required):
            raise RuntimeError(f"Incomplete STA: {p}")
        if re.search(r"(^|\n)\s*(?:ERROR|Error):", log):
            raise RuntimeError(f"STA error in {p}")
        def extract(marker):
            return log.split(marker + "_START", 1)[1].split(marker + "_END", 1)[0]
        def worst_slack(marker):
            block = extract(marker)
            match = re.search(r"worst slack(?:\s+max)?\s+([-+]?\d+(?:\.\d+)?)", block, re.I)
            if not match:
                raise RuntimeError(f"Missing finite worst slack: {p}: {block[:300]!r}")
            return float(match.group(1))
        all_slack = worst_slack("V296_ALL_PATH_WORST_SLACK")
        data_slack = worst_slack("V296_DATA_WORST_SLACK")
        paths = extract("V296_DATA_PATHS")
        if "Startpoint:" not in paths or "Path Group: asynchronous" in paths:
            raise RuntimeError(f"Invalid data-path timing group (async/reset or empty): {p}")
        violators = extract("V296_ELECTRICAL_VIOLATORS")
        if "max capacitance" not in violators or "max slew" not in violators:
            raise RuntimeError(f"Missing electrical check categories: {p}")
        slew, cap = violators.split("max capacitance", 1)
        rows[scenario][variant] = {
            "worst_setup_slack_ns": data_slack,
            "all_path_worst_slack_ns_including_reset": all_slack,
            "max_slew_violations": slew.count("(VIOLATED)"),
            "max_capacitance_violations": cap.count("(VIOLATED)"),
            "violation_report": violators.strip()[:4000],
            "data_critical_paths": paths.strip()[:1500],
            "log": str(p),
        }
period_ns = 2.0
results = {}
for scenario, vals in rows.items():
    best = max(("original", "optimized"), key=lambda v: vals[v]["worst_setup_slack_ns"])
    base_slack = vals[best]["worst_setup_slack_ns"]
    pair_slack = vals["pairwise"]["worst_setup_slack_ns"]
    base_period = period_ns - base_slack
    pair_period = period_ns - pair_slack
    if min(base_period, pair_period) <= 0:
        raise RuntimeError("Invalid derived path period; inspect STA")
    results[scenario] = {
        "strongest_timing_control": best,
        "baseline_critical_period_ns": base_period,
        "pairwise_critical_period_ns": pair_period,
        "pairwise_to_control_frequency_ratio": base_period / pair_period,
        "candidate_slack_ns": pair_slack,
        "control_slack_ns": base_slack,
        "candidate_faster": pair_slack > base_slack,
        "electrical_clean": all(vals[v]["max_slew_violations"] == 0 and vals[v]["max_capacitance_violations"] == 0 for v in variants),
        "candidate_max_slew_violations": vals["pairwise"]["max_slew_violations"],
        "candidate_max_capacitance_violations": vals["pairwise"]["max_capacitance_violations"],
    }
out = {
    "evidence_class": "preplacement_lumped_RC_STA_only_not_signoff",
    "critical_path_scope": "issue data paths excluding asynchronous reset recovery; full reset worst slack retained separately",
    "not_valid_for": ["post_route_timing", "true_wire_length", "power", "RTX_5090_comparison"],
    "clock_period_ns": period_ns,
    "per_net_cap_pf": {"low": 0.002, "nominal": 0.004, "high": 0.008},
    "per_net_resistance_kohm": {"low": 0.1, "nominal": 0.2, "high": 0.4},
    "results": results,
    "raw": rows,
    "holdouts": "SEALED",
}
(root / "sta_summary.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"results": results, "holdouts": "SEALED"}, indent=2))
if any(not r["candidate_faster"] for r in results.values()):
    print("V296_TIMING_FALSIFIER: candidate not faster than strongest control in every RC regime")
    sys.exit(2)

if any(not r["electrical_clean"] for r in results.values()):
    print("V296_ELECTRICAL_GATE_FAIL: one or more mapped designs violate max slew or capacitance; no physical win")
    sys.exit(3)
