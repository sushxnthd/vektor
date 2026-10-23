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
        if "V296_STA_COMPLETE" not in log or "V296_WORST_SLACK_START" not in log:
            raise RuntimeError(f"Incomplete STA: {p}")
        block = log.split("V296_WORST_SLACK_START", 1)[1].split("V296_WORST_SLACK_END", 1)[0]
        match = re.search(r"worst slack(?:\s+max)?\s+([-+]?\d+(?:\.\d+)?)", block, re.I)
        if not match:
            raise RuntimeError(f"Missing finite worst slack: {p}: {block[:300]!r}")
        if re.search(r"(^|\n)\s*(?:ERROR|Error):", log):
            raise RuntimeError(f"STA error in {p}")
        violators = log.split("V296_ELECTRICAL_VIOLATORS_START", 1)[1].split("V296_ELECTRICAL_VIOLATORS_END", 1)[0]
        rows[scenario][variant] = {
            "worst_setup_slack_ns": float(match.group(1)),
            "violation_report": violators.strip()[:4000],
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
        "electrical_reports_require_review": True,
    }
out = {
    "evidence_class": "preplacement_lumped_RC_STA_only",
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
