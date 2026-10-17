#!/usr/bin/env python3
"""V176 fail-closed matched OpenSTA sweep parser; no routed-silicon claims."""
import json
import re
import sys
from pathlib import Path

DELAYS = ("0.05", "0.5", "1", "2", "3", "4", "5")

def parse_log(path):
    text = Path(path).read_text()
    if re.search(r"(?m)^(?:Error:|Warning:.*(?:unconstrained|not found))", text):
        raise ValueError(f"OpenSTA error or unconstrained path: {path}")
    starts = re.findall(r"(?m)^Startpoint:\s*(.+)$", text)
    ends = re.findall(r"(?m)^Endpoint:\s*(.+)$", text)
    slacks = re.findall(r"(?m)^worst slack\s+(-?\d+(?:\.\d+)?)\s*$", text)
    if len(starts) != 1 or len(ends) != 1 or len(slacks) != 1:
        raise ValueError(f"Incomplete OpenSTA path or summary: {path}")
    s = float(slacks[0])
    if not (-1e5 < s < 1e5):
        raise ValueError(f"Non-finite/unreasonable slack: {path}")
    start = starts[0].strip()
    return {
        "slack_ns": s,
        "constrained_period_minus_slack_ns": round(10 - s, 6),
        "startpoint": start,
        "endpoint": ends[0].strip(),
        "path_class": ("input-to-register" if "input port" in start else
                       "register-to-register" if "flip-flop" in start else "other")
    }

def run(root, areas_file):
    root = Path(root)
    areas = json.loads(Path(areas_file).read_text())
    a = areas["control"]["mapped_area_units"]
    b = areas["cutset"]["mapped_area_units"]
    if a <= 0 or b <= 0:
        raise ValueError("Invalid mapped areas")
    rows = []
    for delay in DELAYS:
        row = {"input_delay_ns": float(delay)}
        for mode in ("control", "cutset"):
            row[mode] = parse_log(root / f"{mode}_input_{delay}.log")
        control = row["control"]["constrained_period_minus_slack_ns"]
        cutset = row["cutset"]["constrained_period_minus_slack_ns"]
        if control <= 0 or cutset <= 0:
            raise ValueError("Invalid period-minus-slack")
        row["cutset_timing_gain_pct"] = round(100 * (1 - cutset/control), 5)
        row["cutset_area_delay_gain_pct"] = round(100 * (1 - b*cutset/(a*control)), 5)
        row["cutset_timing_10pct_gate"] = cutset <= 0.9*control
        row["cutset_area_delay_gate"] = b*cutset < a*control
        rows.append(row)
    return {
        "evidence_class": "unplaced single-lane Nangate45 mapped OpenSTA timing; not routed PPA",
        "reference": "V156 commit 9122cbc3bb9cf0c8a381ef90393ae1c5abb51cdb",
        "area_units": {"control": a, "cutset": b},
        "library_git_blob": "90e4afb274cfc6514c587c434c77903d554117d1",
        "clock_period_ns": 10,
        "output_delay_ns": 0.05,
        "input_slew_ns": 0.02,
        "output_load_library_units": 0.01,
        "rows": rows,
        "novelty": "not established",
        "warning": "Input-delay sensitivity is not a power, placement, routing, or full GPU throughput result."
    }

if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1], sys.argv[2]), indent=2))
