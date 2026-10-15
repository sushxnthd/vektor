#!/usr/bin/env python3
"""Parse pinned OpenSTA timing reports without conflating them with routed silicon."""
import json, pathlib, re, sys
base = pathlib.Path(sys.argv[1])
out = {"evidence_class": "unplaced library-mapped OpenSTA timing (not routed PPA)",
       "library_git_blob": "90e4afb274cfc6514c587c434c77903d554117d1",
       "clock_period_ns": 10.0, "input_delay_ns": 0.05,
       "output_delay_ns": 0.05, "input_transition_ns": 0.02,
       "output_load_library_units": 0.01,
       "lanes": 1, "matched_latency_cycles": 2, "candidates": {}}
for name in ("control", "cutset"):
    log = (base / f"{name}_sta.log").read_text()
    if re.search(r"^Error:", log, flags=re.M):
        raise SystemExit(f"OpenSTA parse error in {name}; reject partial timing report")
    vals = [float(v) for v in re.findall(
        r"^\s*(-?\d+(?:\.\d+)?)\s+slack\s+\((?:MET|VIOLATED)\)",
        log, flags=re.M)]
    if not vals:
        raise SystemExit(f"Missing valid path slack in {name} STA; inspect raw log")
    start = re.findall(r"^Startpoint:\s*(.*)$", log, re.M)
    end = re.findall(r"^Endpoint:\s*(.*)$", log, re.M)
    if not start or not end:
        raise SystemExit(f"Missing timing endpoints for {name}")
    out["candidates"][name] = {
        "worst_reported_path_slack_ns": min(vals),
        "worst_path_startpoint": start[0].strip(),
        "worst_path_endpoint": end[0].strip(),
        "constrained_period_minus_worst_slack_ns": round(10-min(vals), 6),
        "reported_paths": len(vals),
        "mapped_verilog": f"{name}_mapped.v",
        "sta_log": f"{name}_sta.log"}
a = out["candidates"]["control"]["constrained_period_minus_worst_slack_ns"]
b = out["candidates"]["cutset"]["constrained_period_minus_worst_slack_ns"]
out["cutset_constrained_delay_delta_pct"] = round(100*(b/a-1), 3)
out["cutset_constrained_delay_ratio"] = round(b/a, 6)
out["architecture_threshold_10pct_timing_gain"] = b <= 0.90*a
out["warning"] = "Period-minus-slack is a constraint-specific proxy, not extracted Fmax or routed timing."
print(json.dumps(out, indent=2))
