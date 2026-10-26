#!/usr/bin/env python3
"""Generate a bounded, matched post-CTS endpoint diagnostic from frozen V296 sources.

No RTL, original Tcl, or historical evidence is changed. This does NOT route or sign off.
"""
import argparse
import hashlib
import json
from pathlib import Path

import tile_slice_flow

ROOT = Path("research/v296")
OUT = Path("build/v296/tile_slice")
TCL_MARKER = 'puts "V296_CTS45_DETAIL_BEGIN"'
RUN_TCL = '"$root/cts45_tile.tcl"'
RUN_AUDIT = 'python3 research/v296/audit_tile_slice.py --single "$root" "$variant" || audit_rc=$?'
RUN_END = 'echo "TILE_SLICE_POSTCTS_EXTRACTED_COMPLETE $variant"'

DIAGNOSTIC = r'''
puts "V296_ENDPOINT_DIAG_BEGIN"
puts "V296_ENDPOINT_DIAG_EVIDENCE_TIER POSTCTS_GLOBAL_ROUTE_ONLY"
puts "V296_ENDPOINT_DIAG_SETUP_PATHS_BEGIN"
report_checks -path_delay max -group_path_count 10 -fields {slew capacitance fanout} -digits 6
puts "V296_ENDPOINT_DIAG_SETUP_PATHS_END"
puts "V296_ENDPOINT_DIAG_SETUP_WORST_BEGIN"
report_worst_slack -max -digits 6
puts "V296_ENDPOINT_DIAG_SETUP_WORST_END"
puts "V296_ENDPOINT_DIAG_ESTIMATED_HOLD_BEGIN"
report_worst_slack -min -digits 6
puts "V296_ENDPOINT_DIAG_ESTIMATED_HOLD_END"
puts "V296_ENDPOINT_DIAG_SLEW_BEGIN"
report_check_types -max_slew -violators -format end -digits 6
puts "V296_ENDPOINT_DIAG_SLEW_END"
puts "V296_ENDPOINT_DIAG_CAP_BEGIN"
report_check_types -max_capacitance -violators -format end -digits 6
puts "V296_ENDPOINT_DIAG_CAP_END"
write_def "$env(V296_OUT).postcts_diag.def"
puts "V296_ENDPOINT_DIAG_DONE"
'''

def replace_once(source, before, after):
    if source.count(before) != 1:
        raise ValueError("Missing or duplicated frozen anchor: " + before)
    return source.replace(before, after)

def derive(tcl, runner):
    if tcl.count(TCL_MARKER) != 1:
        raise ValueError("Detailed-route boundary moved")
    prefix = tcl.split(TCL_MARKER, 1)[0]
    if "v296_repair_metrics cts45_postcts_global" not in prefix:
        raise ValueError("Global-route metrics absent before stop point")
    diagnostic_tcl = prefix + DIAGNOSTIC
    if "detailed_route -output_drc" in diagnostic_tcl or "extract_parasitics -ext_model_file" in diagnostic_tcl:
        raise ValueError("Unexpected post-route command in diagnostic")
    diagnostic_runner = replace_once(runner, RUN_TCL, '"$root/cts45_endpoint_diag.tcl"')
    diagnostic_runner = replace_once(
        diagnostic_runner, RUN_AUDIT,
        'test -s "$root/$variant.high.postcts_diag.def" || audit_rc=$?')
    diagnostic_runner = replace_once(
        diagnostic_runner, RUN_END,
        'echo "V296_ENDPOINT_DIAG_POSTCTS_ONLY_NO_ROUTE $variant"')
    return diagnostic_tcl, diagnostic_runner

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def self_test():
    fake = 'v296_repair_metrics cts45_postcts_global\n' + TCL_MARKER + '\ndetailed_route -output_drc x\n'
    runner = RUN_TCL + '\n' + RUN_AUDIT + '\n' + RUN_END
    a, b = derive(fake, runner)
    assert "V296_ENDPOINT_DIAG_DONE" in a and "detailed_route -output_drc" not in a
    assert "postcts_diag.def" in b and "POSTCTS_ONLY_NO_ROUTE" in b
    for bad in (fake.replace(TCL_MARKER, "missing"), fake + TCL_MARKER, TCL_MARKER):
        try:
            derive(bad, runner)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted changed frozen Tcl")
    for bad in (runner.replace(RUN_AUDIT, ""), runner + RUN_TCL):
        try:
            derive(fake, bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted changed frozen runner")
    print("V296_ENDPOINT_DIAG_GENERATOR_SELFTEST_PASS")

def build():
    tile_slice_flow.build()
    frozen_tcl = (OUT / "cts45_tile.tcl").read_text()
    frozen_runner = (ROOT / "run_tile_slice_return_tree.sh").read_text()
    tcl, runner = derive(frozen_tcl, frozen_runner)
    (OUT / "cts45_endpoint_diag.tcl").write_text(tcl)
    (OUT / "run_endpoint_diag.sh").write_text(runner)
    manifest = {
        "evidence_tier": "POSTCTS_GLOBAL_ROUTE_ONLY_NO_ROUTING_SIGNOFF",
        "preregistration": "research/v296/POSTCTS_ENDPOINT_DIAGNOSTIC_PREREG_20261026.md",
        "source_tcl_sha256": digest(frozen_tcl),
        "source_runner_sha256": digest(frozen_runner),
        "generated_tcl_sha256": digest(tcl),
        "generated_runner_sha256": digest(runner),
        "identical_constraints_for_both": True,
        "clock_period_ns": 3.5,
        "extracted_postroute_sta": False,
    }
    (OUT / "endpoint_diag_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("V296_ENDPOINT_DIAG_GENERATED")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--build", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
    if a.build:
        build()
    if not (a.self_test or a.build):
        p.error("Select --self-test and/or --build")
