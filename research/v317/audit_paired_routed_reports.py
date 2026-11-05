#!/usr/bin/env python3
"""Fail-closed paired routed-report audit for V317.

Inputs are *measured* JSON records from matched baseline/candidate runs. No
default physical values, no inferred closure, and no synthetic signoff.
Required fields: design, source_sha, liberty_sha, sdc_sha, placement_seed,
area_um2, worst_setup_slack_ns, worst_hold_slack_ns, max_cap_violations,
max_transition_violations, max_fanout_violations, useful_ops, elapsed_ns,
memory_bytes. A positive result is only a report-level screen, NOT signoff.
"""
import argparse
import json
import math
from pathlib import Path

REQUIRED = ("design", "source_sha", "liberty_sha", "sdc_sha",
            "placement_seed", "area_um2", "worst_setup_slack_ns",
            "worst_hold_slack_ns", "max_cap_violations",
            "max_transition_violations", "max_fanout_violations",
            "useful_ops", "elapsed_ns", "memory_bytes")
NUMERIC = ("area_um2", "worst_setup_slack_ns", "worst_hold_slack_ns",
           "max_cap_violations", "max_transition_violations",
           "max_fanout_violations", "useful_ops", "elapsed_ns", "memory_bytes")
COUNTS = ("max_cap_violations", "max_transition_violations",
          "max_fanout_violations")

def check(b, c):
    errors = []
    for tag, record in (("baseline", b), ("candidate", c)):
        for field in REQUIRED:
            if field not in record or record[field] is None:
                errors.append(f"{tag}: missing {field}")
        for field in NUMERIC:
            if field in record and record[field] is not None:
                value = record[field]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                    errors.append(f"{tag}: invalid {field}")
                elif field in COUNTS and (value < 0 or int(value) != value):
                    errors.append(f"{tag}: invalid count {field}")
        for field in ("source_sha", "liberty_sha", "sdc_sha", "design"):
            if field in record and (not isinstance(record[field], str) or not record[field].strip()):
                errors.append(f"{tag}: invalid {field}")
    if errors:
        return {"pass": False, "reasons": errors}
    for field in ("liberty_sha", "sdc_sha", "placement_seed"):
        if b[field] != c[field]:
            errors.append(f"unmatched {field}")
    if b["source_sha"] == c["source_sha"]:
        errors.append("same source SHA: candidate distinction unproven")
    for tag, record in (("baseline", b), ("candidate", c)):
        if record["area_um2"] <= 0 or record["elapsed_ns"] <= 0 or record["useful_ops"] <= 0:
            errors.append(f"{tag}: nonpositive area/time/work")
        if record["memory_bytes"] < 0:
            errors.append(f"{tag}: negative traffic")
        if record["worst_setup_slack_ns"] < 0 or record["worst_hold_slack_ns"] < 0:
            errors.append(f"{tag}: timing violation")
        if any(record[x] for x in COUNTS):
            errors.append(f"{tag}: electrical violation")
    if errors:
        return {"pass": False, "reasons": errors}
    speedup = (c["useful_ops"] / c["elapsed_ns"]) / (b["useful_ops"] / b["elapsed_ns"])
    traffic_ratio = (c["memory_bytes"] / c["useful_ops"]) / max(b["memory_bytes"] / b["useful_ops"], 1e-300)
    area_ratio = c["area_um2"] / b["area_um2"]
    if area_ratio > 1:
        errors.append("candidate area exceeds baseline")
    if speedup <= 1:
        errors.append("no useful-throughput win")
    if traffic_ratio > 1:
        errors.append("traffic per useful operation increased")
    return {"pass": not errors, "reasons": errors, "speedup": speedup,
            "area_ratio": area_ratio, "traffic_ratio": traffic_ratio,
            "scope": "report-level screen only; not physical signoff"}

def selftest():
    b = dict(design="compact", source_sha="base", liberty_sha="lib",
             sdc_sha="constraints", placement_seed=7, area_um2=100,
             worst_setup_slack_ns=.1, worst_hold_slack_ns=.1,
             max_cap_violations=0, max_transition_violations=0,
             max_fanout_violations=0, useful_ops=100, elapsed_ns=100,
             memory_bytes=100)
    c = dict(b, design="candidate", source_sha="new", area_um2=99, elapsed_ns=90)
    assert check(b, c)["pass"]
    for change in ({"max_cap_violations": 1}, {"worst_hold_slack_ns": -.01},
                   {"area_um2": 101}, {"elapsed_ns": 110},
                   {"memory_bytes": 110}, {"liberty_sha": "other"},
                   {"placement_seed": 8}, {"source_sha": "base"},
                   {"elapsed_ns": float("nan")}, {"useful_ops": 0}):
        assert not check(b, dict(c, **change))["pass"], change
    assert not check(b, {k:v for k,v in c.items() if k != "worst_setup_slack_ns"})["pass"]
    print("PASS: positive fixture and 11 independent fail-closed controls")
    print("LIMIT: fixtures are synthetic; no measured signoff supplied")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path)
    p.add_argument("--candidate", type=Path)
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest:
        selftest()
    else:
        if not a.baseline or not a.candidate:
            p.error("provide --baseline and --candidate JSON reports")
        result = check(json.loads(a.baseline.read_text()), json.loads(a.candidate.read_text()))
        print(json.dumps(result, indent=2, allow_nan=False))
        raise SystemExit(0 if result["pass"] else 1)
