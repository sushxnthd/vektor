#!/usr/bin/env python3
"""SHA-pinned independent fourth-round pre-CTS V296 setup-path audit.

Usage: python3 research/v296/fourth_cone_independent_audit.py PAIRWISE.zip SERIAL.zip
No post-CTS, extracted-RC, routed or GPU-performance claim follows.
"""
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

EXPECTED = {
    "pairwise": "0e19aad4f16a01ad513218c8eb21f199f265e2638b5a1c75ae05049d0080a6c4",
    "serial_onehot": "c54f81fe263e94a8f5cd72c08a6c844e45aabf59015bfbf207227085fedac178",
}
ROW = re.compile(r"^\s*(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+[\^v]\s+(\S+)\s+\(([^)]+)\)\s*$")
FLOP = re.compile(r"(?m)^\s*(DFF\w*_X\d+)\s+(\S+)\s*\((.*?)\);", re.S)
PIN = re.compile(r"\.(\w+)\((.*?)\)", re.S)

def flop_q(netlist, instance):
    hits = [dict((k, v.strip()) for k, v in PIN.findall(m.group(3)))
            for m in FLOP.finditer(netlist) if m.group(2) == instance]
    if len(hits) != 1 or not {"Q", "D", "CK"}.issubset(hits[0]):
        raise ValueError("Missing or ambiguous mapped flop: " + instance)
    return hits[0]["Q"]

def analyze(path, variant):
    if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED[variant]:
        raise ValueError("SHA-256 mismatch: " + variant)
    with ZipFile(path) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError("Duplicate ZIP members")
        log = z.read(variant + ".high.log").decode()
        verilog = z.read(variant + ".v").decode()
        manifest = json.loads(z.read("fourth_diag_manifest.json"))
    if (manifest["tier"] != "PRECTS_GLOBAL_ROUTE_ONLY_NOT_SIGNOFF"
        or any(manifest[k] for k in ("postcts", "extracted_rc", "routed"))
        or manifest["clock_ns"] != 3.5
        or not manifest["shared_fourth_stage"]
        or not manifest["serial_fifth_control_repair_excluded"]):
        raise ValueError("Evidence tier or matched physical protocol drift")
    a, b = "V296_FOURTH_CONE_SETUP_PATH_BEGIN", "V296_FOURTH_CONE_SETUP_PATH_END"
    if log.count(a) != 1 or log.count(b) != 1 or log.count("V296_FOURTH_CONE_DONE") != 1:
        raise ValueError("Incomplete or duplicated diagnostic")
    p = log.split(a, 1)[1].split(b, 1)[0]
    def required(pattern):
        m = re.search(pattern, p, re.M)
        if not m:
            raise ValueError("Missing setup-path field: " + pattern)
        return m.group(1)
    start = required(r"^Startpoint: (\S+)")
    end = required(r"^Endpoint: (\S+)")
    slack = float(required(r"^\s*(-?\d+\.\d+)\s+slack \(VIOLATED\)"))
    arrival = float(required(r"^\s*(\d+\.\d+)\s+data arrival time"))
    start_q, end_q = flop_q(verilog, start), flop_q(verilog, end)
    if ".issue.scheduler.rr" not in start_q or not end_q.startswith("executed_data["):
        raise ValueError("Unexpected mapped scheduler-to-execution endpoints")
    rows = []
    for line in p.splitlines():
        m = ROW.match(line)
        if m:
            fan, cap, slew, delay, time, cell, typ = m.groups()
            rows.append({"cell": cell, "type": typ, "fanout": int(fan),
                         "capacitance": float(cap), "delay": float(delay),
                         "buffer": typ.startswith(("BUF", "INV"))})
    if len(rows) < 15 or not rows[0]["cell"].startswith(start + "/"):
        raise ValueError("Invalid path table")
    if abs(sum(r["delay"] for r in rows) - arrival) > 0.0002:
        raise ValueError("Cell-delay sum fails arrival reconciliation")
    buffers = [r for r in rows if r["buffer"]]
    runs, current = [], []
    for r in rows + [{"buffer": False}]:
        if r["buffer"]:
            current.append(r)
        elif current:
            runs.append(current)
            current = []
    longest = max(runs, key=lambda run: sum(r["delay"] for r in run))
    return {
        "artifact_sha256": EXPECTED[variant],
        "start_q": start_q, "end_q": end_q,
        "worst_setup_slack_ns": slack, "data_arrival_ns": arrival,
        "path_cells": len(rows), "buffer_inverter_cells": len(buffers),
        "buffer_inverter_delay_ns": round(sum(r["delay"] for r in buffers), 6),
        "other_cell_delay_ns": round(sum(r["delay"] for r in rows if not r["buffer"]), 6),
        "longest_contiguous_buffer_run": {
            "cells": len(longest),
            "delay_ns": round(sum(r["delay"] for r in longest), 6),
            "first": longest[0]["cell"], "last": longest[-1]["cell"]},
        "highest_capacitance_pin": max(rows, key=lambda r: r["capacitance"]),
    }

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: fourth_cone_independent_audit.py PAIRWISE.zip SERIAL.zip")
    pair = analyze(Path(sys.argv[1]), "pairwise")
    serial = analyze(Path(sys.argv[2]), "serial_onehot")
    print(json.dumps({
        "tier": "PRECTS_ESTIMATED_RC_NO_SIGNOFF",
        "caveat": "Different critical paths: decomposition descriptive, not causal",
        "pairwise": pair, "serial_onehot": serial,
        "slack_lead_ns": round(pair["worst_setup_slack_ns"] - serial["worst_setup_slack_ns"], 6),
        "buffer_delay_gap_ns": round(serial["buffer_inverter_delay_ns"] - pair["buffer_inverter_delay_ns"], 6),
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
