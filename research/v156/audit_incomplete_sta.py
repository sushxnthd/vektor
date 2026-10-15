#!/usr/bin/env python3
"""Independently reject incomplete V156 STA reports and calculate the timing gates."""
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

def audit(archive):
    data = Path(archive).read_bytes()
    out = {
        "archive_sha256": hashlib.sha256(data).hexdigest(),
        "evidence_class": "unplaced Nangate45 mapped OpenSTA, not routed timing",
        "clock_constraint_ns": 10.0,
        "candidates": {},
    }
    with ZipFile(archive) as z:
        mapping = json.loads(z.read("v155/summary.json"))
        for mode in ("control", "cutset"):
            raw = z.read(f"v156/{mode}_sta.log").decode("utf-8", errors="replace")
            errors = re.findall(r"^Error:.*$", raw, re.M)
            starts = re.findall(r"^Startpoint:\s*(.*)$", raw, re.M)
            ends = re.findall(r"^Endpoint:\s*(.*)$", raw, re.M)
            slacks = [float(x) for x in re.findall(
                r"^\s*(-?\d+(?:\.\d+)?)\s+slack\s+\((?:MET|VIOLATED)\)",
                raw, re.M)]
            valid = not errors and bool(starts and ends and slacks)
            out["candidates"][mode] = {
                "valid": valid,
                "parser_errors": errors,
                "mapped_area_units": mapping[mode]["mapped_area_units"],
                "startpoint": starts[0] if valid else None,
                "endpoint": ends[0] if valid else None,
                "worst_slack_ns": min(slacks) if valid else None,
                "period_minus_slack_ns": round(10.0-min(slacks), 6) if valid else None,
            }
    control, cutset = out["candidates"]["control"], out["candidates"]["cutset"]
    ratio = cutset["mapped_area_units"] / control["mapped_area_units"]
    out["cutset_area_overhead_pct"] = round(100*(ratio-1), 6)
    out["cutset_min_delay_improvement_pct_for_adp_parity"] = round(100*(1-1/ratio), 6)
    out["matched_timing_comparison_valid"] = bool(control["valid"] and cutset["valid"])
    out["smallest_supported_claim"] = (
        "Matched timing unavailable: cutset netlist parse error; valid control proxy only"
        if not out["matched_timing_comparison_valid"] else
        "Both STA logs parsed; evaluate timing and area-delay thresholds separately"
    )
    if control["valid"]:
        out["cutset_max_delay_ns_for_adp_parity"] = round(control["period_minus_slack_ns"]/ratio, 6)
        out["cutset_max_delay_ns_for_architecture_10pct_gate"] = round(0.9*control["period_minus_slack_ns"], 6)
    return out

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python audit_incomplete_sta.py <GitHub artifact zip>")
    result = audit(sys.argv[1])
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["matched_timing_comparison_valid"]:
        raise SystemExit(2)
