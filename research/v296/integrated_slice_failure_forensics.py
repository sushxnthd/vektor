#!/usr/bin/env python3
"""Independent fail-closed forensics for V296 integrated RF-slice evidence.

Parses the original physical log, the mapped netlist and independent audit.
Only the post-CTS extracted metrics determine physical feasibility. Any
reported register-to-register path in the early log is labelled PRE-CTS and
must not be mistaken for the final extracted critical path.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

TARGET = {"setup_ns": 0.050, "hold_ns": 0.0, "cap": 0, "slew": 0,
          "area_um2": 30000.0}


def required(pattern, text, name, flags=0):
    matches = list(re.finditer(pattern, text, flags))
    if len(matches) != 1:
        raise ValueError(f"Expected one {name}, found {len(matches)}")
    return matches[0]


def netlist_ff_q(netlist, cell):
    match = required(r"\bDFF\w*\s+" + re.escape(cell) + r"\s*\((.*?)\);",
                     netlist, f"flip-flop {cell}", re.S)
    return required(r"\.Q\((.*?)\)", match.group(1), f"Q pin {cell}", re.S).group(1).strip()


def extract(log, netlist, audit):
    if log.splitlines().count("V296_CTS45_DONE") != 1:
        raise ValueError("Missing or ambiguous completed extracted physical run")
    required(r"^V296_CTS45_RC_MULTIPLIER 2\.0$", log, "2x extracted RC", re.M)
    metric = required(r"^V296_METRIC stage=cts45_extracted area_um2=([0-9.]+) slew=(\d+) cap=(\d+)$",
                      log, "extracted metric", re.M)
    area, slew, cap = float(metric.group(1)), int(metric.group(2)), int(metric.group(3))
    after = log[metric.end():]
    setup = float(required(r"^worst slack\s+(-?[0-9.]+)$", after,
                           "extracted setup slack", re.M).group(1))
    hold = float(required(r"^V296_CTS45_HOLD_BEGIN\nworst slack\s+(-?[0-9.]+)\nV296_CTS45_HOLD_END$",
                          log, "extracted hold slack", re.M).group(1))
    if audit.get("variant") != "pairwise" or audit.get("complete") is not True:
        raise ValueError("Not a complete independently audited pairwise contestant")
    final = audit.get("final", {})
    for key, actual in (("area_um2", area), ("setup_ns", setup),
                        ("hold_ns", hold), ("slew", slew), ("cap", cap)):
        if abs(final.get(key, float("inf")) - actual) > 1e-6:
            raise ValueError(f"Audit/log mismatch: {key}")
    if audit.get("feasible") is not False:
        raise ValueError("Unexpected audit feasibility status")
    # This is the early pre-CTS path report, NOT the extracted post-CTS path.
    paths = list(re.finditer(r"^Startpoint: (\w+) .*?\nEndpoint: (\w+) .*?\nPath Group: coreclk",
                             log, re.M))
    if not paths:
        raise ValueError("Missing early pre-CTS register path")
    start, end = paths[0].group(1), paths[0].group(2)
    return {
        "evidence_tier": "post-CTS detailed-route extracted RC; not signoff",
        "candidate": "V296 pairwise RF slice",
        "final_extracted": {"area_um2": area, "setup_ns": setup,
                            "hold_ns": hold, "slew": slew, "cap": cap},
        "preregistered_gate": TARGET,
        "failures": {
            "setup_shortfall_ns": round(TARGET["setup_ns"] - setup, 6),
            "hold_shortfall_ns": round(TARGET["hold_ns"] - hold, 6),
            "cap_violation_count": cap,
        },
        "passes_area_limit": area <= TARGET["area_um2"],
        "passes_physical_gate": (area <= TARGET["area_um2"] and
                                  setup >= TARGET["setup_ns"] and
                                  hold >= TARGET["hold_ns"] and cap == 0 and slew == 0),
        "early_path_not_extracted_critical_path": {
            "stage": "pre-CTS report_checks only",
            "startpoint": start, "startpoint_q": netlist_ff_q(netlist, start),
            "endpoint": end, "endpoint_q": netlist_ff_q(netlist, end),
        },
        "same_clock_admission_advantage": 0.0,
        "control_physical_outcome": "PENDING_IN_THIS_REPORT",
        "gpu_fmax_or_speedup": "NOT_MEASURED",
    }


def self_test():
    log = ("Startpoint: _1_ (rising edge-triggered flip-flop clocked by coreclk)\n"
           "Endpoint: _2_ (rising edge-triggered flip-flop clocked by coreclk)\n"
           "Path Group: coreclk\nV296_CTS45_RC_MULTIPLIER 2.0\n"
           "V296_CTS45_HOLD_BEGIN\nworst slack -0.03\nV296_CTS45_HOLD_END\n"
           "V296_METRIC stage=cts45_extracted area_um2=10000.0 slew=0 cap=3\n"
           "worst slack -1.0\nV296_CTS45_DONE\n")
    netlist = "DFFR_X1 _1_ (.Q(\\candidate.issue.scheduler.rr1 [1]));\nDFFR_X1 _2_ (.Q(executed_data[7]));\n"
    audit = {"variant": "pairwise", "complete": True, "feasible": False,
             "final": {"area_um2": 10000.0, "setup_ns": -1.0,
                       "hold_ns": -0.03, "slew": 0, "cap": 3}}
    row = extract(log, netlist, audit)
    assert row["passes_physical_gate"] is False
    assert row["early_path_not_extracted_critical_path"]["endpoint_q"] == "executed_data[7]"
    for bad in (log.replace("V296_CTS45_DONE", ""),
                log.replace("V296_CTS45_RC_MULTIPLIER 2.0", ""),
                log.replace("cap=3", "cap=0")):
        try:
            extract(bad, netlist, audit)
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed or inconsistent evidence passed")
    print("V296_INTEGRATED_FAILURE_FORENSICS_SELFTEST_PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if args.root:
        paths = {"log": args.root / "pairwise.high.log",
                 "netlist": args.root / "pairwise.v",
                 "audit": args.root / "pairwise.tile.audit.json"}
        data = {k: p.read_bytes() for k, p in paths.items()}
        row = extract(data["log"].decode(errors="replace"),
                      data["netlist"].decode(errors="replace"),
                      json.loads(data["audit"]))
        row["source_sha256"] = {k: hashlib.sha256(b).hexdigest()
                                for k, b in data.items()}
        rendered = json.dumps(row, indent=2) + "\n"
        if args.out:
            args.out.write_text(rendered)
        print(rendered)
    if not args.self_test and not args.root:
        parser.error("Specify --self-test or --root")


if __name__ == "__main__":
    main()
