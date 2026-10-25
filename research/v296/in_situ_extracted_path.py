#!/usr/bin/env python3
"""Matched in-situ postroute STA path reporting; never modifies original physical sources."""
import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
import tile_slice_flow as original

ROOT = Path("build/v296/tile_slice")
MARK = "v296_repair_metrics cts45_extracted"
INSERT = """puts "V296_IN_SITU_SETUP_SLACK_BEGIN"
report_worst_slack -max -digits 6
puts "V296_IN_SITU_SETUP_SLACK_END"
puts "V296_IN_SITU_HOLD_SLACK_BEGIN"
report_worst_slack -min -digits 6
puts "V296_IN_SITU_HOLD_SLACK_END"
puts "V296_IN_SITU_SETUP_PATHS_BEGIN"
report_checks -path_delay max -digits 6
puts "V296_IN_SITU_SETUP_PATHS_END"
puts "V296_IN_SITU_HOLD_PATHS_BEGIN"
report_checks -path_delay min -digits 6
puts "V296_IN_SITU_HOLD_PATHS_END"
puts "V296_IN_SITU_DONE"
"""
OBSERVED = {"pairwise": (-1.047895, -0.036622),
            "serial_onehot": (-1.859922, -0.019796)}

def exactly_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Frozen source anchor missing or duplicated: " + old)
    return text.replace(old, new)

def instrument(text):
    if "V296_IN_SITU_" in text:
        raise ValueError("Duplicate instrumentation")
    if text.count("read_spef") != 1 or text.count("write_spef") != 1:
        raise ValueError("Changed extraction protocol")
    if text.count("adjust_rc -res_factor 2.0 -cc_factor 2.0 -gndc_factor 2.0") != 1:
        raise ValueError("Changed 2x RC protocol")
    out = exactly_once(text, MARK, MARK + "\n" + INSERT)
    if not (out.index("read_spef") < out.index("V296_IN_SITU_SETUP_SLACK_BEGIN")
            < out.rfind("write_def")):
        raise ValueError("Instrumentation must follow extracted SPEF")
    return out

def build():
    source = (ROOT / "cts45_tile.tcl").read_text()
    patched = instrument(source)
    (ROOT / "cts45_tile_in_situ.tcl").write_text(patched)
    (ROOT / "in_situ_manifest.json").write_text(json.dumps({
        "original_tcl_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "probe_tcl_sha256": hashlib.sha256(patched.encode()).hexdigest(),
        "only_read_only_reports_added": True, "same_tcl_both_variants": True,
    }, indent=2) + "\n")
    print("V296_IN_SITU_TCL_INSTRUMENTED")

def wrapper():
    source = Path("research/v296/run_tile_slice_cts.sh").read_text()
    source = exactly_once(source, "python3 research/v296/tile_slice_flow.py --build",
                          "python3 research/v296/tile_slice_flow.py --build\npython3 research/v296/in_situ_extracted_path.py --instrument")
    source = exactly_once(source, '"$root/cts45_tile.tcl"', '"$root/cts45_tile_in_situ.tcl"')
    return source

def section(log, name):
    a, b = ("V296_IN_SITU_" + name + "_" + x for x in ("BEGIN", "END"))
    if log.splitlines().count(a) != 1 or log.splitlines().count(b) != 1:
        raise ValueError("Missing or duplicate report markers: " + name)
    first, last = log.index(a) + len(a), log.index(b)
    if last <= first:
        raise ValueError("Reversed report markers")
    return log[first:last]

def parse_slack(text):
    hits = re.findall(r"^worst slack\s+(-?[0-9.]+)$", text, re.M)
    if len(hits) != 1:
        raise ValueError("Ambiguous extracted slack")
    return float(hits[0])

def analyze(root):
    manifest = json.loads((root / "in_situ_manifest.json").read_text())
    src = (root / "cts45_tile.tcl").read_text()
    probe = (root / "cts45_tile_in_situ.tcl").read_text()
    if manifest.get("only_read_only_reports_added") is not True or manifest.get("same_tcl_both_variants") is not True:
        raise ValueError("Unmatched probe configuration")
    if hashlib.sha256(src.encode()).hexdigest() != manifest["original_tcl_sha256"]:
        raise ValueError("Original Tcl changed")
    if hashlib.sha256(probe.encode()).hexdigest() != manifest["probe_tcl_sha256"] or instrument(src) != probe:
        raise ValueError("Unexpected physical Tcl edits")
    rows = {}
    for variant, original_slacks in OBSERVED.items():
        log = (root / (variant + ".high.log")).read_text(errors="replace")
        physical = json.loads((root / (variant + ".tile.audit.json")).read_text())
        if log.splitlines().count("V296_CTS45_DONE") != 1 or log.splitlines().count("V296_IN_SITU_DONE") != 1:
            raise ValueError("Incomplete physical implementation " + variant)
        if physical.get("complete") is not True:
            raise ValueError("Incomplete independent physical audit " + variant)
        s = parse_slack(section(log, "SETUP_SLACK"))
        h = parse_slack(section(log, "HOLD_SLACK"))
        f = physical["final"]
        if not math.isfinite(s) or not math.isfinite(h):
            raise ValueError("Nonfinite extracted slack")
        if abs(s - f["setup_ns"]) > .005 or abs(h - f["hold_ns"]) > .005:
            raise ValueError("In-situ STA disagrees with same-run independent audit")
        paths = {}
        for stage in ("SETUP", "HOLD"):
            block = section(log, stage + "_PATHS")
            starts = re.findall(r"^Startpoint:\s*(.+)$", block, re.M)
            ends = re.findall(r"^Endpoint:\s*(.+)$", block, re.M)
            if not starts or len(starts) != len(ends):
                raise ValueError("Missing path endpoints for " + variant + " " + stage)
            paths[stage.lower()] = [{"start": a.strip(), "end": b.strip()} for a,b in zip(starts[:5], ends[:5])]
        rows[variant] = {"setup_ns": s, "hold_ns": h, "paths": paths,
                         "area_um2": f["area_um2"], "cap_violations": f["cap"],
                         "slew_violations": f["slew"], "feasible": physical["feasible"],
                         "setup_delta_original_ns": s-original_slacks[0],
                         "hold_delta_original_ns": h-original_slacks[1],
                         "within_50ps_original_reproduction_tolerance":
                             abs(s-original_slacks[0]) <= .05 and abs(h-original_slacks[1]) <= .05,
                         "log_sha256": hashlib.sha256(log.encode()).hexdigest()}
    return {"decision": "NEW_RUN_IN_SITU_EXTRACTED_PATHS_IDENTIFIED",
            "original_run": 40156470550, "original_gate": "BOTH_INFEASIBLE",
            "new_run_both_feasible": all(r["feasible"] for r in rows.values()),
            "same_clock_admission_gain": 0.0, "gpu_speedup": "NOT_ESTABLISHED",
            "holdouts": "SEALED", "rows": rows}

def self_test():
    tcl = original.generate()[1]["cts45_tile.tcl"]
    probe = instrument(tcl)
    assert probe.replace(MARK + "\n" + INSERT, MARK) == tcl
    assert probe.count("V296_IN_SITU_DONE") == 1
    assert "-group_path_count" not in probe
    assert "report_checks -path_delay max -digits 6" in probe
    assert "report_checks -path_delay min -digits 6" in probe
    assert "in_situ_extracted_path.py --instrument" in wrapper()
    assert parse_slack(section("V296_IN_SITU_SETUP_SLACK_BEGIN\nworst slack -1.2\nV296_IN_SITU_SETUP_SLACK_END\n", "SETUP_SLACK")) == -1.2
    for bad in (tcl.replace(MARK, ""), tcl.replace(MARK, MARK + MARK)):
        try: instrument(bad)
        except ValueError: pass
        else: raise AssertionError("Fail-open probe generator")
    print("V296_IN_SITU_PATH_SELFTEST_PASS")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--instrument", action="store_true")
    p.add_argument("--run", action="store_true")
    p.add_argument("--audit", type=Path)
    args = p.parse_args()
    if args.self_test: self_test()
    if args.instrument: build()
    if args.run:
        Path("/tmp/v296_in_situ_run.sh").write_text(wrapper())
        subprocess.run(["bash", "/tmp/v296_in_situ_run.sh"], check=True)
    if args.audit:
        try: row = analyze(args.audit)
        except (ValueError, KeyError, OSError, TypeError) as e:
            row = {"decision": "INCOMPLETE_NO_PATH_CLAIM", "error": str(e),
                   "gpu_speedup": "NOT_ESTABLISHED", "holdouts": "SEALED"}
        (args.audit / "in_situ_path_audit.json").write_text(json.dumps(row, indent=2)+"\n")
        print(json.dumps(row, indent=2))
        if row["decision"] == "INCOMPLETE_NO_PATH_CLAIM": raise SystemExit(3)
    if not any((args.self_test, args.instrument, args.run, args.audit)):
        p.error("Select an action")
if __name__ == "__main__":
    main()
